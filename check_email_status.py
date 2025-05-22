# Email confirmation status checker
from supabase_utils import get_supabase_admin_client
import os
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

def check_email_status(email):
    """
    Check if a user's email is confirmed
    """
    try:
        print(f"Checking email confirmation status for: {email}")
        admin_client = get_supabase_admin_client()

        # Use admin functions to check user
        if hasattr(admin_client.auth, 'admin') and hasattr(admin_client.auth.admin, 'list_users'):
            users = admin_client.auth.admin.list_users()
            for user in users:
                if hasattr(user, 'email') and user.email == email:
                    # Check email confirmation status
                    confirmed = hasattr(user, 'email_confirmed_at') and user.email_confirmed_at is not None
                    print(f"Found user with email {email}")
                    print(f"Email confirmation status: {'Confirmed' if confirmed else 'Not confirmed'}")
                    if hasattr(user, 'email_confirmed_at'):
                        print(f"Confirmed at: {user.email_confirmed_at}")
                    return confirmed
            
            print(f"No user found with email: {email}")
            return False
        else:
            print("Admin functions not available - can't check email status")
            return False
            
    except Exception as e:
        print(f"Error checking email status: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check email confirmation status")
    parser.add_argument("email", help="Email address to check")
    args = parser.parse_args()
    
    check_email_status(args.email)
