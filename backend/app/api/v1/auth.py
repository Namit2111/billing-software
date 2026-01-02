"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.core.dependencies import get_supabase_admin_client, get_current_user
from app.services.auth import AuthService
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    PasswordResetRequest,
    ChangePasswordRequest,
    UserResponse,
    UserUpdateRequest
)
from app.schemas.common import SuccessResponse, MessageResponse

router = APIRouter()


@router.post("/register", response_model=SuccessResponse)
async def register(
    data: RegisterRequest,
    supabase: Client = Depends(get_supabase_admin_client)
):
    """
    Register a new user account
    
    Creates a new user with optional organization.
    """
    auth_service = AuthService(supabase)
    
    result = await auth_service.register(
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        company_name=data.company_name
    )
    
    return SuccessResponse(
        data={
            "user": result["user"],
            "access_token": result["session"]["access_token"],
            "refresh_token": result["session"]["refresh_token"],
            "expires_in": result["session"]["expires_in"]
        },
        message="Registration successful"
    )


@router.post("/login", response_model=SuccessResponse)
async def login(
    data: LoginRequest,
    supabase: Client = Depends(get_supabase_admin_client)
):
    """
    Login with email and password
    
    Returns access token and user data.
    """
    auth_service = AuthService(supabase)
    
    result = await auth_service.login(
        email=data.email,
        password=data.password
    )
    
    return SuccessResponse(
        data={
            "user": result["user"],
            "access_token": result["session"]["access_token"],
            "refresh_token": result["session"]["refresh_token"],
            "expires_in": result["session"]["expires_in"]
        },
        message="Login successful"
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Logout current user"""
    auth_service = AuthService(supabase)
    await auth_service.logout()
    
    return MessageResponse(message="Logged out successfully")


@router.post("/password-reset", response_model=MessageResponse)
async def request_password_reset(
    data: PasswordResetRequest,
    supabase: Client = Depends(get_supabase_admin_client)
):
    """
    Request password reset email
    
    Sends a password reset link to the provided email.
    """
    auth_service = AuthService(supabase)
    await auth_service.request_password_reset(data.email)
    
    return MessageResponse(
        message="If an account exists with this email, a password reset link has been sent"
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Change password for authenticated user"""
    auth_service = AuthService(supabase)
    await auth_service.update_password(current_user["id"], data.new_password)
    
    return MessageResponse(message="Password changed successfully")


@router.get("/me", response_model=SuccessResponse[UserResponse])
async def get_current_user_profile(
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Get current user profile"""
    auth_service = AuthService(supabase)
    profile = await auth_service.get_user_profile(current_user["id"])
    
    return SuccessResponse(data=profile)


@router.patch("/me", response_model=SuccessResponse[UserResponse])
async def update_current_user_profile(
    data: UserUpdateRequest,
    supabase: Client = Depends(get_supabase_admin_client),
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile"""
    auth_service = AuthService(supabase)
    
    update_data = data.model_dump(exclude_unset=True)
    updated = await auth_service.update_profile(current_user["id"], update_data)
    
    return SuccessResponse(data=updated, message="Profile updated successfully")

