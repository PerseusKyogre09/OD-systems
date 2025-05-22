from supabase import create_client, Client
import os
from dotenv import load_dotenv


load_dotenv()


def get_supabase_client() -> Client:
    """Get a Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    return create_client(url, key)


def get_supabase_admin_client() -> Client:
    """Get a Supabase client instance with service key (admin privileges)"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    
    return create_client(url, key)


def sign_up_user(email, password, user_metadata=None, redirect_url=None):
    """Register a new user with Supabase Auth"""
    try:
        
        supabase = get_supabase_client()
        
        print("Using sign_up with correct dictionary format...")
        
        
        signup_data = {
            'email': email,
            'password': password,
            'options': {
                
                'data': user_metadata if user_metadata else {}
            }
        }
        
        
        if redirect_url:
            signup_data['options']['emailRedirectTo'] = redirect_url
        
        
        if user_metadata:
            signup_data['data'] = user_metadata
            
        
        response = supabase.auth.sign_up(signup_data)
        print(f"Sign-up response type: {type(response)}")
        
        
        standardized_response = {
            'user': None,
            'session': None
        }
        
        
        if hasattr(response, 'user') and response.user is not None:
            print("User found in response")
            standardized_response['user'] = response.user
            
            
            if hasattr(response.user, 'email_confirmed_at') and not response.user.email_confirmed_at:
                print("Email confirmation required")
                
                standardized_response['email_confirmed'] = False
            else:
                standardized_response['email_confirmed'] = True
        else:
            print("No user in response")
        
        
        if hasattr(response, 'session') and response.session is not None:
            print("Session found in response")
            standardized_response['session'] = response.session
        else:
            print("No session in response")
        
        
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
        
        
        if "User already registered" in error_msg:
            return {'user': {'email': email}, 'session': None, 'registered_already': True}
        
        
        return {'user': None, 'session': None, 'error': error_msg}

def sign_in_user(email, password):
    """Sign in a user with Supabase Auth"""
    try:
        
        supabase = get_supabase_client()
        
        print("Attempting to sign in with password...")
        
        
        if hasattr(supabase.auth, 'sign_in_with_password'):
            try:
                print("Using sign_in_with_password with correct format...")
                
                
                response = supabase.auth.sign_in_with_password({
                    'email': email,
                    'password': password
                })
                print(f"Sign-in response type: {type(response)}")
                
                
                standardized_response = {
                    'user': None,
                    'session': None
                }
                
                
                if hasattr(response, 'user') and response.user is not None:
                    print("User found in response")
                    standardized_response['user'] = response.user
                    
                    
                    if hasattr(response.user, 'email_confirmed_at'):
                        if response.user.email_confirmed_at:
                            print("Email is confirmed")
                            standardized_response['email_confirmed'] = True
                        else:
                            print("Email is NOT confirmed")
                            standardized_response['email_confirmed'] = False
                    else:
                        print("No email_confirmed_at attribute found")
                        
                        standardized_response['email_confirmed'] = True
                else:
                    print("No user in response")
                
                
                if hasattr(response, 'session') and response.session is not None:
                    print("Session found in response")
                    standardized_response['session'] = response.session
                else:
                    print("No session in response")
                    
                return standardized_response
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error with sign_in_with_password: {error_msg}")
                
                
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
            
            return {'user': None, 'session': None, 'error': error_msg}

def sign_out_user(access_token=None):
    """Sign out a user with Supabase Auth"""
    supabase = get_supabase_client()
    
    return supabase.auth.sign_out()

def get_user(access_token):
    """Get user data from Supabase Auth"""
    try:
        supabase = get_supabase_client()
        
        
        try:
            response = supabase.auth.get_user(access_token)
            print(f"get_user response type: {type(response)}")
            
            
            standardized_response = {'user': None}
            
            
            if hasattr(response, 'user'):
                print("Response has 'user' attribute")
                standardized_response['user'] = response.user
                return standardized_response
                
            
            if hasattr(response, '__getitem__'):
                try:
                    standardized_response['user'] = response['user']
                    return standardized_response
                except:
                    pass
                    
            
            
            return response
            
        except Exception as e:
            print(f"Error getting user with token: {str(e)}")
            
            try:
                
                response = supabase.auth.user()
                print("Retrieved user with no parameters")
                
                
                if hasattr(response, 'user'):
                    return {'user': response.user}
                else:
                    return response
            except Exception as e2:
                print(f"Error with alternative user method: {str(e2)}")
                
                return {'user': None}
        
    except Exception as e:
        print(f"Critical error in get_user: {str(e)}")
        return {'user': None}


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


def upload_file(bucket, file_path, file_name):
    """Upload a file to Supabase Storage"""
    supabase = get_supabase_client()
    with open(file_path, 'rb') as f:
        return supabase.storage.from_(bucket).upload(file_name, f)

def get_file_url(bucket, file_name):
    """Get public URL for a file in Supabase Storage"""
    supabase = get_supabase_client()
    return supabase.storage.from_(bucket).get_public_url(file_name)
