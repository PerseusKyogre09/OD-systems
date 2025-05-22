from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
def get_supabase_client() -> Client:
    """Get a Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    # Simple initialization without extra options that could cause errors
    return create_client(url, key)

# Initialize admin Supabase client (with service key for more privileges)
def get_supabase_admin_client() -> Client:
    """Get a Supabase client instance with service key (admin privileges)"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    # Simple initialization without extra options that could cause errors
    return create_client(url, key)

# Auth functions
def sign_up_user(email, password, user_metadata=None, redirect_url=None):
    """Register a new user with Supabase Auth"""
    try:
        # Get client instance
        supabase = get_supabase_client()
        
        print("Using sign_up with correct dictionary format...")
        
        # Include user metadata directly in the sign-up dictionary
        signup_data = {
            'email': email,
            'password': password,
            'options': {
                # Set data here to ensure it's included in Auth API call
                'data': user_metadata if user_metadata else {}
            }
        }
        
        # Add email redirect URL if provided
        if redirect_url:
            signup_data['options']['emailRedirectTo'] = redirect_url
        
        # Only add metadata if provided (at top level too for compatibility)
        if user_metadata:
            signup_data['data'] = user_metadata
            
        # Sign up with Supabase
        response = supabase.auth.sign_up(signup_data)
        print(f"Sign-up response type: {type(response)}")
        
        # Create a standardized response structure
        standardized_response = {
            'user': None,
            'session': None
        }
        
        # Extract user data - direct attribute access for AuthResponse object
        if hasattr(response, 'user') and response.user is not None:
            print("User found in response")
            standardized_response['user'] = response.user
            
            # Check if email confirmation is needed
            if hasattr(response.user, 'email_confirmed_at') and not response.user.email_confirmed_at:
                print("Email confirmation required")
                # Store that the user exists but needs verification
                standardized_response['email_confirmed'] = False
            else:
                standardized_response['email_confirmed'] = True
        else:
            print("No user in response")
        
        # Extract session data
        if hasattr(response, 'session') and response.session is not None:
            print("Session found in response")
            standardized_response['session'] = response.session
        else:
            print("No session in response")
        
        # If user is a teacher, add to notifications
        if user_metadata and user_metadata.get('role') == 'teacher' and standardized_response['user']:
            try:
                print("Adding teacher to notifications...")
                admin_client = get_supabase_admin_client()
                admin_client.table('teacher_notifications').insert({
                    'email': email
                }).execute()
            except Exception as e:
                print(f"Error adding teacher to notifications: {str(e)}")
        
        return standardized_response
    except Exception as e:
        print(f"Supabase sign-up critical error: {str(e)}")
        error_msg = str(e)
        
        # Check if it's a user already registered error (which is actually good)
        if "User already registered" in error_msg:
            return {'user': {'email': email}, 'session': None, 'registered_already': True}
        
        # Return a valid structure even in case of error to prevent app crashes
        return {'user': None, 'session': None, 'error': error_msg}

def sign_in_user(email, password):
    """Sign in a user with Supabase Auth"""
    try:
        # Get client instance
        supabase = get_supabase_client()
        
        print("Attempting to sign in with password...")
        
        # In Supabase v1.2.0, the correct method for password login is sign_in_with_password
        if hasattr(supabase.auth, 'sign_in_with_password'):
            try:
                print("Using sign_in_with_password with correct format...")
                
                # For supabase-py v1.2.0, the format is:
                response = supabase.auth.sign_in_with_password({
                    'email': email,
                    'password': password
                })
                print(f"Sign-in response type: {type(response)}")
                
                # Create a standardized response structure
                standardized_response = {
                    'user': None,
                    'session': None
                }
                
                # Extract user data
                if hasattr(response, 'user') and response.user is not None:
                    print("User found in response")
                    standardized_response['user'] = response.user
                    
                    # Check if email has been confirmed
                    if hasattr(response.user, 'email_confirmed_at'):
                        if response.user.email_confirmed_at:
                            print("Email is confirmed")
                            standardized_response['email_confirmed'] = True
                        else:
                            print("Email is NOT confirmed")
                            standardized_response['email_confirmed'] = False
                    else:
                        print("No email_confirmed_at attribute found")
                        # Default to True if the attribute doesn't exist to avoid blocking login
                        standardized_response['email_confirmed'] = True
                else:
                    print("No user in response")
                
                # Extract session data
                if hasattr(response, 'session') and response.session is not None:
                    print("Session found in response")
                    standardized_response['session'] = response.session
                else:
                    print("No session in response")
                    
                return standardized_response
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error with sign_in_with_password: {error_msg}")
                
                # Check if this is an email confirmation error
                if "Email not confirmed" in error_msg:
                    return {
                        'user': {'email': email},
                        'session': None,
                        'error': "Email not confirmed. Please check your inbox and click the confirmation link.",
                        'email_confirmed': False
                    }
                    
                raise Exception(f"Failed to sign in: {str(e)}")
        else:
            print("sign_in_with_password method not found")
            auth_methods = [m for m in dir(supabase.auth) if not m.startswith('_')]
            print(f"Available auth methods: {auth_methods}")
            raise Exception("sign_in_with_password method not available in this version of Supabase")
        
    except Exception as e:
        error_msg = str(e)
        print(f"Supabase sign-in critical error: {error_msg}")
        
        # Provide specific error handling for common issues
        if "Email not confirmed" in error_msg:
            return {
                'user': {'email': email},
                'session': None,
                'error': "Email not confirmed. Please check your inbox and click the confirmation link.",
                'email_confirmed': False
            }
        elif "Invalid login credentials" in error_msg:
            return {
                'user': None, 
                'session': None, 
                'error': "Invalid email or password. Please try again."
            }
        elif "User not found" in error_msg:
            return {
                'user': None, 
                'session': None, 
                'error': "No account found with this email. Please register first."
            }
        else:
            # Return a valid structure even in case of error to prevent app crashes
            return {'user': None, 'session': None, 'error': error_msg}

def sign_out_user(access_token=None):
    """Sign out a user with Supabase Auth"""
    supabase = get_supabase_client()
    # In older versions, token is not needed
    return supabase.auth.sign_out()

def get_user(access_token):
    """Get user data from Supabase Auth"""
    try:
        supabase = get_supabase_client()
        
        # Try to get user with token
        try:
            response = supabase.auth.get_user(access_token)
            print(f"get_user response type: {type(response)}")
            
            # Handle AuthResponse object
            standardized_response = {'user': None}
            
            # Try accessing as attributes
            if hasattr(response, 'user'):
                print("Response has 'user' attribute")
                standardized_response['user'] = response.user
                return standardized_response
                
            # Try dictionary access
            if hasattr(response, '__getitem__'):
                try:
                    standardized_response['user'] = response['user']
                    return standardized_response
                except:
                    pass
                    
            # If we still don't have user data, return the raw response
            # which might be structured differently
            return response
            
        except Exception as e:
            print(f"Error getting user with token: {str(e)}")
            # Supabase client v1.2.0 might need different approach
            try:
                # Some versions might use a method without parameters, relying on session cookie
                response = supabase.auth.user()
                print("Retrieved user with no parameters")
                
                # Try to extract user data
                if hasattr(response, 'user'):
                    return {'user': response.user}
                else:
                    return response
            except Exception as e2:
                print(f"Error with alternative user method: {str(e2)}")
                # Create a default response to prevent errors
                return {'user': None}
        
    except Exception as e:
        print(f"Critical error in get_user: {str(e)}")
        return {'user': None}

# Database functions
def insert_record(table_name, data):
    """Insert a record into a Supabase table"""
    supabase = get_supabase_client()
    return supabase.table(table_name).insert(data).execute()

def update_record(table_name, id, data):
    """Update a record in a Supabase table"""
    supabase = get_supabase_client()
    return supabase.table(table_name).update(data).eq('id', id).execute()

def get_record(table_name, id):
    """Get a record from a Supabase table by ID"""
    supabase = get_supabase_client()
    return supabase.table(table_name).select('*').eq('id', id).execute()

def get_records(table_name, filters=None):
    """Get records from a Supabase table with optional filters"""
    supabase = get_supabase_client()
    query = supabase.table(table_name).select('*')
    
    if filters:
        for column, value in filters.items():
            query = query.eq(column, value)
    
    return query.execute()

def delete_record(table_name, id):
    """Delete a record from a Supabase table"""
    supabase = get_supabase_client()
    return supabase.table(table_name).delete().eq('id', id).execute()

# Storage functions
def upload_file(bucket, file_path, file_name):
    """Upload a file to Supabase Storage"""
    supabase = get_supabase_client()
    with open(file_path, 'rb') as f:
        return supabase.storage.from_(bucket).upload(file_name, f)

def get_file_url(bucket, file_name):
    """Get public URL for a file in Supabase Storage"""
    supabase = get_supabase_client()
    return supabase.storage.from_(bucket).get_public_url(file_name)
