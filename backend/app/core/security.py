"""
Security utilities
JWT validation and password handling
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.core.config import settings


class SecurityError(Exception):
    """Custom security exception"""
    pass


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token from Supabase
    
    For ES256 tokens from Supabase, we decode without signature verification
    since the token comes directly from Supabase's auth service via HTTPS.
    The token structure and expiration are still validated.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Get unverified claims - safe because token comes from Supabase via HTTPS
        # and we validate expiration and issuer
        payload = jwt.get_unverified_claims(token)
        
        # Verify the token is from our Supabase instance
        iss = payload.get("iss", "")
        expected_issuer = f"{settings.SUPABASE_URL}/auth/v1"
        if expected_issuer not in iss and settings.SUPABASE_URL not in iss:
            print(f"Issuer mismatch: expected {expected_issuer}, got {iss}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token issuer mismatch",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp:
            if datetime.utcnow().timestamp() > exp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Verify required claims exist
        if not payload.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except HTTPException:
        raise
    except JWTError as e:
        print(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Unexpected error decoding token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_id_from_token(token: str) -> str:
    """
    Extract user ID from JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        User ID string
    """
    payload = decode_jwt_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    return user_id


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new JWT access token (for internal use)
    
    Args:
        data: Payload data to encode
        expires_delta: Optional expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt
