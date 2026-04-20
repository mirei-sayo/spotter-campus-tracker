from server.database import supabase
try:
    res = supabase.table("profiles").select("*").limit(1).execute()
    print("Profiles table exists and is accessible.")
except Exception as e:
    print(f"Error accessing profiles table: {e}")
