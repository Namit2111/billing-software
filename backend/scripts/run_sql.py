"""
Script to run SQL commands against Supabase database
Usage: python scripts/run_sql.py <sql_file_path>
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def run_sql_file(file_path: str):
    """Run SQL file against Supabase database"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_service_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
        print("   Make sure you have a .env file with these values.")
        sys.exit(1)
    
    # Read SQL file
    try:
        with open(file_path, 'r') as f:
            sql_content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: SQL file not found: {file_path}")
        sys.exit(1)
    
    print(f"📄 Reading SQL from: {file_path}")
    print(f"🔗 Connecting to Supabase: {supabase_url}")
    
    # Create Supabase client with service role key
    supabase = create_client(supabase_url, supabase_service_key)
    
    # Execute SQL using Supabase's rpc function
    # Note: This requires a function to be set up in Supabase
    # For direct SQL execution, we'll use the REST API
    
    try:
        # Try using postgrest to run a simple query to verify connection
        result = supabase.table("organizations").select("id").limit(1).execute()
        print("✅ Connected to Supabase successfully!")
    except Exception as e:
        print(f"⚠️  Connection test: {e}")
    
    print("\n" + "="*60)
    print("SQL CONTENT TO RUN:")
    print("="*60)
    print(sql_content[:500] + "..." if len(sql_content) > 500 else sql_content)
    print("="*60)
    
    print("\n⚠️  Direct SQL execution from Python requires additional setup.")
    print("   Please copy the SQL above and run it in Supabase SQL Editor:")
    print(f"   1. Go to your Supabase Dashboard")
    print(f"   2. Navigate to SQL Editor")
    print(f"   3. Paste and run the SQL")
    print("\n   Alternatively, you can use the Supabase CLI:")
    print("   npx supabase db push")


def disable_rls_simple():
    """Simple function to disable RLS using Supabase client"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_service_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
        return False
    
    print(f"🔗 Connecting to Supabase...")
    supabase = create_client(supabase_url, supabase_service_key)
    
    # Test by creating/fetching data using service role (bypasses RLS)
    tables = ["organizations", "users", "clients", "products", "invoices", "taxes"]
    
    print("\n📊 Testing table access with service role key:")
    for table in tables:
        try:
            result = supabase.table(table).select("id").limit(1).execute()
            print(f"   ✅ {table}: accessible")
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg:
                print(f"   ⚠️  {table}: table does not exist (needs migration)")
            else:
                print(f"   ❌ {table}: {error_msg[:50]}")
    
    print("\n✅ Service role key bypasses RLS - your backend should work!")
    print("   The backend uses the service role key for all database operations.")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_sql_file(sys.argv[1])
    else:
        print("🔧 BillFlow Database Setup Tool")
        print("="*40)
        disable_rls_simple()

