from flask_login import UserMixin
from jose import jwt
import os

class SupabaseUser(UserMixin):
    """Custom User class compatible with Flask-Login and Supabase Auth"""
    
    def __init__(self, user_data):
        """
        Initialize a user from Supabase user data
        
        Args:
            user_data: The user data from Supabase auth.getUser()
        """
        # Handle both dictionary access and object attributes
        if user_data is None:
            user_data = {}
            
        # Extract ID safely (try multiple approaches)
        self.id = self._extract_value(user_data, 'id')
        self.email = self._extract_value(user_data, 'email')
        
        # Extract user metadata
        user_metadata = self._extract_value(user_data, 'user_metadata', {})
        self.user_metadata = user_metadata if isinstance(user_metadata, dict) else {}
        
        # Extract app metadata
        app_metadata = self._extract_value(user_data, 'app_metadata', {})
        self.app_metadata = app_metadata if isinstance(app_metadata, dict) else {}
        
        # Extract other properties
        self.role = self._extract_metadata_value('role', 'student')  # Default to student
        self.name = self._extract_metadata_value('name', '')
        self.created_at = self._extract_value(user_data, 'created_at')
        self.last_sign_in_at = self._extract_value(user_data, 'last_sign_in_at')
        
    def _extract_value(self, data, key, default=None):
        """Extract a value from a dict or object safely"""
        if isinstance(data, dict):
            return data.get(key, default)
        elif hasattr(data, key):
            return getattr(data, key, default)
        return default
        
    def _extract_metadata_value(self, key, default=None):
        """Extract a value from user_metadata dict"""
        # Try in user_metadata
        if isinstance(self.user_metadata, dict) and key in self.user_metadata:
            return self.user_metadata.get(key, default)
        # Try in app_metadata
        elif isinstance(self.app_metadata, dict) and key in self.app_metadata:
            return self.app_metadata.get(key, default)
        return default
    
    @staticmethod
    def decode_token(token):
        """Decode a JWT token from Supabase"""
        try:
            # Supabase JWT has a specific format, we just want to get basic info
            # without validation since we're relying on Supabase for validation
            return jwt.decode(
                token, 
                os.getenv('SUPABASE_JWT_SECRET', ''), 
                options={"verify_signature": False}
            )
        except Exception:
            return None
            
    def get_id(self):
        """Return the user ID for Flask-Login"""
        return self.id
        
    def is_teacher(self):
        """Check if the user is a teacher"""
        return self.role == 'teacher'
        
    def is_student(self):
        """Check if the user is a student"""
        return self.role == 'student'
