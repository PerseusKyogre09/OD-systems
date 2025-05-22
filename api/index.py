from flask import Flask, request
import sys
import os

# Add parent directory to path so we can import from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from the parent directory
from app import app as flask_app

# This is required for Vercel serverless functions
app = flask_app

# For local development
if __name__ == '__main__':
    app.run(debug=True)
