"""
Script to decode a JWT token and see its header/algorithm
"""
import sys
import base64
import json

def decode_token_parts(token: str):
    """Decode JWT token parts without verification"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            print("❌ Invalid token format (should have 3 parts)")
            return
        
        # Decode header
        header_b64 = parts[0]
        # Add padding if needed
        header_b64 += '=' * (4 - len(header_b64) % 4) if len(header_b64) % 4 else ''
        header = json.loads(base64.urlsafe_b64decode(header_b64))
        
        print("=" * 60)
        print("JWT Token Analysis")
        print("=" * 60)
        
        print("\n📋 HEADER:")
        print(f"   Algorithm (alg): {header.get('alg')}")
        print(f"   Type (typ): {header.get('typ')}")
        
        # Decode payload
        payload_b64 = parts[1]
        payload_b64 += '=' * (4 - len(payload_b64) % 4) if len(payload_b64) % 4 else ''
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        
        print("\n📋 PAYLOAD:")
        for key, value in payload.items():
            if key == "exp":
                from datetime import datetime
                try:
                    exp_time = datetime.fromtimestamp(value)
                    print(f"   {key}: {exp_time}")
                except:
                    print(f"   {key}: {value}")
            elif key == "sub":
                print(f"   {key}: {value} (User ID)")
            else:
                val_str = str(value)[:60]
                print(f"   {key}: {val_str}")
        
        print("\n" + "=" * 60)
        print(f"✅ Token uses algorithm: {header.get('alg')}")
        print("   Update your backend to use this algorithm!")
        print("=" * 60)
        
        return header.get('alg')
        
    except Exception as e:
        print(f"❌ Error decoding token: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        decode_token_parts(sys.argv[1])
    else:
        print("Usage: python scripts/decode_token.py <jwt-token>")
        print("\nGet your token from browser DevTools:")
        print("  Application → Local Storage → access_token")

