"""
Script to check JWT configuration and test token validation
Usage: python scripts/check_jwt.py [token]
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def check_jwt_config():
    """Check JWT configuration"""
    jwt_secret = os.getenv("JWT_SECRET", "")
    supabase_url = os.getenv("SUPABASE_URL", "")
    
    print("=" * 60)
    print("JWT Configuration Check")
    print("=" * 60)
    
    if not jwt_secret:
        print("❌ JWT_SECRET is not set in .env file!")
        print("\nTo fix this:")
        print("1. Go to your Supabase Dashboard")
        print("2. Navigate to: Settings → API → JWT Settings")
        print("3. Copy the 'JWT Secret' value")
        print("4. Add it to your .env file as: JWT_SECRET=your-secret-here")
        return False
    
    print(f"✅ JWT_SECRET is set ({len(jwt_secret)} characters)")
    print(f"   First 20 chars: {jwt_secret[:20]}...")
    
    # Check if it looks like a Supabase JWT secret
    if len(jwt_secret) < 32:
        print("⚠️  Warning: JWT_SECRET seems too short. Supabase secrets are typically 40+ characters")
    
    if supabase_url:
        project_id = supabase_url.replace("https://", "").replace(".supabase.co", "")
        print(f"\n📦 Supabase Project: {project_id}")
        print(f"   Dashboard: https://supabase.com/dashboard/project/{project_id}/settings/api")
    
    return True


def test_token(token: str):
    """Test decoding a JWT token"""
    from jose import jwt, JWTError
    
    jwt_secret = os.getenv("JWT_SECRET", "")
    
    print("\n" + "=" * 60)
    print("Token Validation Test")
    print("=" * 60)
    
    if not token:
        print("No token provided. Usage: python scripts/check_jwt.py <token>")
        return
    
    # First, decode without verification to see the payload
    try:
        unverified = jwt.get_unverified_claims(token)
        print("\n📋 Token Claims (unverified):")
        for key, value in unverified.items():
            if key == "exp":
                from datetime import datetime
                exp_time = datetime.fromtimestamp(value)
                print(f"   {key}: {value} ({exp_time})")
            elif key == "sub":
                print(f"   {key}: {value} (User ID)")
            else:
                val_str = str(value)
                if len(val_str) > 50:
                    val_str = val_str[:50] + "..."
                print(f"   {key}: {val_str}")
    except Exception as e:
        print(f"❌ Failed to decode token: {e}")
        return
    
    # Now try to verify with our secret
    try:
        verified = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False, "verify_iss": False}
        )
        print("\n✅ Token is VALID with current JWT_SECRET!")
        print(f"   User ID: {verified.get('sub')}")
    except JWTError as e:
        print(f"\n❌ Token verification FAILED: {e}")
        print("\n🔧 This means your JWT_SECRET doesn't match Supabase's JWT secret.")
        print("   To fix:")
        print("   1. Go to Supabase Dashboard → Settings → API")
        print("   2. Find 'JWT Secret' (click 'Reveal' if hidden)")
        print("   3. Copy it and update your .env file")
        print("   4. Restart the backend server")


if __name__ == "__main__":
    if check_jwt_config():
        if len(sys.argv) > 1:
            test_token(sys.argv[1])
        else:
            print("\n💡 To test a specific token, run:")
            print("   python scripts/check_jwt.py <your-access-token>")
            print("\n   You can find your token in browser DevTools:")
            print("   Application → Local Storage → access_token")

