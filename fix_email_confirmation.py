# Email confirmation fix for Supabase
from supabase_utils import get_supabase_client, get_supabase_admin_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_verification():
    """
    Test and fix email verification issues
    """
    try:
        print("Getting Supabase client...")
        client = get_supabase_client()
        admin_client = get_supabase_admin_client()
        
        # Option 1: Check if we can disable email confirmation in settings
        print("\nChecking authentication settings...")
        # This would typically be done in the Supabase dashboard, not via code
        print("NOTE: Email confirmation settings must be modified in the Supabase dashboard")
        print("Go to Authentication > Providers > Email > Confirm email: Set to 'No'")
        
        # Option 2: Check if we can manually confirm a user
        print("\nTesting admin functions...")
        # Admin operations require service_role key with higher privileges
        admin = client.auth.admin
        if admin:
            print("Admin functions available. You can potentially modify email verification.")
            print("Available admin methods:", [m for m in dir(admin) if not m.startswith('_')])
        else:
            print("Admin functions not available with current API key.")
        
        # Option 3: Create a way to bypass confirmation check during login
        print("\nImplementing bypass method...")
        print("You'll need to modify the login flow to bypass email confirmation.")
        print("This can be done by:")
        print("1. Modifying the sign_in_user function in supabase_utils.py")
        print("2. Adding a 'emailRedirectTo' parameter during signup")
        print("3. Handling the error status and providing clear instructions")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_email_verification()
