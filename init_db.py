import os
import pymysql
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

def init_db():
    # Database connection
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        db=os.getenv('DB_NAME')
    )
    cursor = conn.cursor()

    # Read and execute schema
    with open('schema.sql', 'r') as f:
        schema = f.read()
        # Split into individual statements
        statements = schema.split(';')
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)

    # Create a default teacher account if it doesn't exist
    cursor.execute("SELECT id FROM users WHERE email = %s", (os.getenv('ADMIN_EMAIL'),))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'teacher')",
            (
                'Admin Teacher',
                os.getenv('ADMIN_EMAIL'),
                generate_password_hash(os.getenv('ADMIN_PASSWORD'))
            )
        )

    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
