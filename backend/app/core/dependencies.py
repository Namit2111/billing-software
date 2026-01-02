"""
FastAPI Dependencies
Authentication and database dependencies
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client

from app.core.config import settings
from app.core.security import decode_jwt_token

# HTTP Bearer security scheme
security = HTTPBearer()


def get_supabase_client() -> Client:
    """
    Get Supabase client instance
    
    Returns:
        Supabase client
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def get_supabase_admin_client() -> Client:
    """
    Get Supabase admin client with service role key
    
    Returns:
        Supabase admin client
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = decode_jwt_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        # Use admin client to bypass RLS policies
        admin_client = get_supabase_admin_client()
        
        # Get user details from Supabase
        response = admin_client.table("users").select("*").eq("id", user_id).limit(1).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


async def get_current_user_organization(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get current user's organization
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Organization data dictionary
    """
    org_id = current_user.get("organization_id")
    
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any organization"
        )
    
    # Use admin client to bypass RLS policies
    admin_client = get_supabase_admin_client()
    response = admin_client.table("organizations").select("*").eq("id", org_id).limit(1).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return response.data[0]


def require_role(allowed_roles: list):
    """
    Dependency factory for role-based access control
    
    Args:
        allowed_roles: List of allowed role names
        
    Returns:
        Dependency function that validates user role
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "member")
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {allowed_roles}"
            )
        
        return current_user
    
    return role_checker


# Convenience dependencies
require_owner = require_role(["owner"])
require_member = require_role(["owner", "member"])

