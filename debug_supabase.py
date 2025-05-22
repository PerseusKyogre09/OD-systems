from supabase_utils import get_supabase_client
import inspect

def inspect_supabase():
    """Inspect Supabase client to find available methods"""
    try:
        print("Getting Supabase client...")
        supabase = get_supabase_client()
        
        print("\n=== Supabase Auth Methods ===")
        auth_methods = dir(supabase.auth)
        for method in auth_methods:
            if not method.startswith('_'):
                print(f"Method: {method}")
                try:
                    # Try to get the signature
                    attr = getattr(supabase.auth, method)
                    if callable(attr):
                        try:
                            sig = str(inspect.signature(attr))
                            print(f"  Signature: {sig}")
                        except:
                            print("  Signature: Could not determine")
                except Exception as e:
                    print(f"  Error accessing: {str(e)}")
                    
        print("\n=== Supabase Auth Object Type ===")
        print(f"Type: {type(supabase.auth)}")
        
        print("\n=== Supabase Client Type ===")
        print(f"Type: {type(supabase)}")
        
    except Exception as e:
        print(f"Error inspecting Supabase: {str(e)}")

if __name__ == "__main__":
    inspect_supabase()
