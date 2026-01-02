"""
Authentication service
"""
from typing import Optional, Dict, Any
from supabase import Client, create_client
from postgrest.exceptions import APIError

from app.repositories.user import UserRepository
from app.repositories.organization import OrganizationRepository
from app.core.exceptions import UnauthorizedError, ConflictError, NotFoundError, BadRequestError
from app.core.config import settings


class AuthService:
    """Service for authentication operations"""

    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.user_repo = UserRepository(supabase)
        self.org_repo = OrganizationRepository(supabase)
        # Admin client for operations that bypass RLS
        self.admin_supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    
    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
        company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user with optional organization
        
        Args:
            email: User email
            password: User password
            full_name: User's full name
            company_name: Optional company name to create organization
            
        Returns:
            Dict with user and session data
        """
        try:
            # Check if user already exists in our users table
            user_repo_admin = UserRepository(self.admin_supabase)
            existing_user = await user_repo_admin.get_by_email(email)
            if existing_user:
                raise ConflictError("An account with this email already exists")
            
            # Register with Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"full_name": full_name}
                }
            })
            
            if not auth_response.user:
                raise ConflictError("Failed to create user account")
            
            user_id = str(auth_response.user.id)
            
            # Create organization if company name provided (use admin client to bypass RLS)
            organization_id = None
            if company_name:
                try:
                    org_repo_admin = OrganizationRepository(self.admin_supabase)
                    org = await org_repo_admin.create({
                        "name": company_name
                    })
                    organization_id = org["id"]
                except APIError as e:
                    # If org creation fails, still continue with user creation
                    print(f"Warning: Failed to create organization: {e}")

            # Create user record in our database (use admin client to bypass RLS)
            try:
                user = await user_repo_admin.create({
                    "id": user_id,
                    "email": email,
                    "full_name": full_name,
                    "organization_id": organization_id,
                    "role": "owner" if organization_id else "member"
                })
            except APIError as e:
                if "duplicate key" in str(e):
                    # User already exists, fetch and return it
                    user = await user_repo_admin.get_by_id(user_id)
                    if not user:
                        raise ConflictError("User registration failed - please try again")
                else:
                    raise
            
            return {
                "user": user,
                "session": {
                    "access_token": auth_response.session.access_token if auth_response.session else None,
                    "refresh_token": auth_response.session.refresh_token if auth_response.session else None,
                    "expires_in": auth_response.session.expires_in if auth_response.session else None
                }
            }
        except ConflictError:
            raise
        except Exception as e:
            error_message = str(e).lower()
            if "already registered" in error_message or "already exists" in error_message:
                raise ConflictError("An account with this email already exists")
            elif "invalid email" in error_message:
                raise BadRequestError("Please provide a valid email address")
            elif "password" in error_message:
                raise BadRequestError("Password does not meet requirements (minimum 6 characters)")
            else:
                print(f"Registration error: {e}")
                raise BadRequestError(f"Registration failed: {str(e)}")
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login a user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dict with user and session data
        """
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                raise UnauthorizedError("Invalid email or password")
            
            user_id = str(auth_response.user.id)
            
            # Get user from our database using admin client to bypass RLS
            user_repo_admin = UserRepository(self.admin_supabase)
            user = await user_repo_admin.get_by_id(user_id)
            
            if not user:
                # User exists in Supabase Auth but not in our database
                # Create user record using admin client
                try:
                    user = await user_repo_admin.create({
                        "id": user_id,
                        "email": email,
                        "full_name": auth_response.user.user_metadata.get("full_name", email.split("@")[0])
                    })
                except APIError:
                    # Try to fetch again in case of race condition
                    user = await user_repo_admin.get_by_id(user_id)
                    if not user:
                        raise UnauthorizedError("User account not properly configured")
            
            # Update last login
            try:
                await user_repo_admin.update_last_login(user["id"])
            except Exception:
                pass  # Don't fail login if last_login update fails
            
            return {
                "user": user,
                "session": {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_in": auth_response.session.expires_in
                }
            }
        except UnauthorizedError:
            raise
        except Exception as e:
            error_message = str(e).lower()
            if "invalid login" in error_message or "invalid credentials" in error_message:
                raise UnauthorizedError("Invalid email or password")
            elif "email not confirmed" in error_message:
                raise UnauthorizedError("Please verify your email address before logging in")
            else:
                print(f"Login error: {e}")
                raise UnauthorizedError("Login failed. Please check your credentials.")
    
    async def logout(self) -> bool:
        """Logout current user"""
        try:
            self.supabase.auth.sign_out()
        except Exception:
            pass  # Ignore logout errors
        return True
    
    async def request_password_reset(self, email: str) -> bool:
        """
        Request password reset email
        
        Args:
            email: User email
            
        Returns:
            True if email sent
        """
        try:
            self.supabase.auth.reset_password_email(email)
        except Exception:
            pass  # Don't reveal if email exists or not
        return True
    
    async def update_password(
        self,
        user_id: str,
        new_password: str
    ) -> bool:
        """
        Update user password
        
        Args:
            user_id: User UUID
            new_password: New password
            
        Returns:
            True if updated
        """
        try:
            self.supabase.auth.update_user({
                "password": new_password
            })
            return True
        except Exception as e:
            raise BadRequestError(f"Failed to update password: {str(e)}")
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile with organization"""
        user_repo_admin = UserRepository(self.admin_supabase)
        user = await user_repo_admin.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        
        # Get organization if exists
        if user.get("organization_id"):
            org_repo_admin = OrganizationRepository(self.admin_supabase)
            org = await org_repo_admin.get_by_id(user["organization_id"])
            user["organization"] = org
        
        return user
    
    async def update_profile(
        self,
        user_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user profile"""
        user_repo_admin = UserRepository(self.admin_supabase)
        return await user_repo_admin.update(user_id, data)
