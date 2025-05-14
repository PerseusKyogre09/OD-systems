from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pymysql
import smtplib
import os
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from forms import LoginForm, RegistrationForm, ODRequestForm, CommentForm
from config import get_config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(get_config())

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database connection
conn = pymysql.connect(
    host=app.config['DB_HOST'],
    user=app.config['DB_USER'],
    password=app.config['DB_PASSWORD'],
    db=app.config['DB_NAME']
)
cursor = conn.cursor(pymysql.cursors.DictCursor)  # Use dictionary cursor for named fields

# Helper Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class User:
    def __init__(self, id, email, role, name=None):
        self.id = id
        self.email = email
        self.role = role
        self.name = name

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)  # Flask-Login requires this to return a string

@login_manager.user_loader
def load_user(user_id):
    query = "SELECT id, email, role, name FROM users WHERE id=%s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    if result:
        return User(
            id=result['id'],
            email=result['email'],
            role=result['role'],
            name=result['name']
        )
    return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}_dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        query = "SELECT id, name, email, password, role FROM users WHERE email=%s"
        cursor.execute(query, (form.email.data,))
        result = cursor.fetchone()

        if not result or not check_password_hash(result['password'], form.password.data):
            flash('Invalid email or password', 'error')
            return render_template('login.html', form=form)

        user = User(id=result['id'], name=result['name'], email=result['email'], role=result['role'])
        login_user(user, remember=True)
        next_page = request.args.get('next')
        
        if not next_page or not next_page.startswith('/'):
            next_page = url_for(f'{user.role}_dashboard')
            
        flash('Login successful!', 'success')
        return redirect(next_page)
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}_dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            name = form.name.data.strip()
            email = form.email.data.strip().lower()
            password = generate_password_hash(form.password.data)
            role = form.role.data

            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                flash('Email is already registered. Please log in or use a different email.', 'danger')
                return redirect(url_for('login'))

            # Insert new user
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, password, role)
            )
            conn.commit()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

        except pymysql.Error as e:
            conn.rollback()
            app.logger.error(f"Database error during registration: {str(e)}")
            flash('A database error occurred. Please try again.', 'danger')
        except Exception as e:
            conn.rollback()
            app.logger.error(f"Unexpected error during registration: {str(e)}")
            flash('An unexpected error occurred. Please try again.', 'danger')
        finally:
            cursor.close()

    return render_template('register.html', form=form)

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    # Get pending requests count
    cursor.execute("SELECT COUNT(*) FROM od_requests WHERE student_id = %s AND status = 'Pending'", (current_user.id,))
    pending_count = cursor.fetchone()['COUNT(*)']

    # Get approved requests count
    cursor.execute("SELECT COUNT(*) FROM od_requests WHERE student_id = %s AND status = 'Approved'", (current_user.id,))
    approved_count = cursor.fetchone()['COUNT(*)']

    # Get total requests count
    cursor.execute("SELECT COUNT(*) FROM od_requests WHERE student_id = %s", (current_user.id,))
    total_count = cursor.fetchone()['COUNT(*)']

    # Get recent requests
    cursor.execute("""
        SELECT id, event_name, date, status 
        FROM od_requests 
        WHERE student_id = %s 
        ORDER BY date DESC 
        LIMIT 5
    """, (current_user.id,))
    od_requests = cursor.fetchall()

    return render_template('student_dashboard.html',
                         pending_count=pending_count,
                         approved_count=approved_count,
                         total_count=total_count,
                         od_requests=od_requests)

@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('You are not authorized to access this page.', 'error')
        return redirect(url_for('student_dashboard'))

    # Get pending requests
    cursor.execute("""
        SELECT o.id, u.name as student_name, u.email, o.event_name, o.description, o.date 
        FROM od_requests o
        JOIN users u ON o.student_id = u.id
        WHERE o.status = 'Pending' AND u.role = 'student'
        ORDER BY o.date ASC
    """)
    od_requests = cursor.fetchall()

    # Get pending count
    cursor.execute("SELECT COUNT(*) FROM od_requests WHERE status = 'Pending'")
    pending_count = cursor.fetchone()['COUNT(*)']

    # Get today's requests count
    cursor.execute("SELECT COUNT(*) FROM od_requests WHERE DATE(created_at) = CURDATE()")
    todays_count = cursor.fetchone()['COUNT(*)']

    # Get total actions (approved + rejected)
    cursor.execute("SELECT COUNT(*) FROM od_requests WHERE status IN ('Approved', 'Rejected')")
    total_actions = cursor.fetchone()['COUNT(*)']    # Add today's date for the dashboard
    from datetime import datetime
    today = datetime.now()
    
    return render_template('teacher_dashboard.html',
                         od_requests=od_requests,
                         pending_count=pending_count,
                         todays_count=todays_count,
                         total_actions=total_actions,
                         today=today)

@app.route('/submit_od', methods=['GET', 'POST'])
@login_required
def submit_od():
    form = ODRequestForm()
    if form.validate_on_submit():
        event_name = form.event_name.data
        date = form.date.data
        description = form.description.data
        
        # Handle file upload
        document = None
        if form.document.data:
            file = form.document.data
            if file.filename:
                if allowed_file(file.filename):
                    # Ensure the upload folder exists
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    
                    # Create a safe filename
                    base = os.path.splitext(file.filename)[1]
                    document = f"{current_user.id}_{int(time.time())}{base}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], document)
                    file.save(file_path)
                else:
                    flash('Invalid file type. Please upload a PDF or DOC file.', 'danger')
                    return render_template('submit_od.html', form=form)

        # Insert OD request into the database
        query = """
            INSERT INTO od_requests 
            (student_id, event_name, date, description, document_path, status, created_at) 
            VALUES (%s, %s, %s, %s, %s, 'Pending', NOW())
        """
        try:
            cursor.execute(query, (current_user.id, event_name, date, description, document))
            od_id = cursor.lastrowid
            conn.commit()
            
            # Send email notification to teachers
            notify_teachers(current_user.name, description, od_id)
            
            flash('Your OD request has been submitted successfully!', 'success')
            return redirect(url_for('student_dashboard'))
            
        except Exception as e:
            conn.rollback()
            app.logger.error(f"Database error in submit_od: {str(e)}")
            flash('An error occurred while submitting your request. Please try again.', 'danger')
    
    return render_template('submit_od.html', form=form)

def notify_teachers(student_name, description, od_id):
    """Send email notifications to all teachers about a new OD request."""
    try:
        # Get all teacher emails
        cursor.execute("SELECT email FROM users WHERE role = 'teacher'")
        teachers = cursor.fetchall()
        
        for teacher in teachers:
            subject = "New OD Request"
            body = f"""
            <html>
            <body>
                <p>Dear Teacher,</p>
                <p>Student <strong>{student_name}</strong> has submitted a new OD request:</p>
                <blockquote style="margin: 10px 0; padding: 10px; border-left: 3px solid #007bff; background-color: #f8f9fa;">
                    {description}
                </blockquote>
                <p>Please review this request at your earliest convenience.</p>
                <p>
                    <a href="{url_for('view_request', request_id=od_id, _external=True)}" 
                       style="display: inline-block; padding: 10px 20px; background-color: #007bff; 
                              color: white; text-decoration: none; border-radius: 5px;">
                        Review Request
                    </a>
                </p>
                <p style="color: #666; font-size: 0.9em;">
                    This is an automated message from the OD System.
                </p>
            </body>
            </html>
            """
            
            msg = MIMEMultipart("alternative")
            msg['Subject'] = subject
            msg['From'] = app.config['EMAIL_USER']
            msg['To'] = teacher['email']
            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(app.config['EMAIL_USER'], app.config['EMAIL_PASS'])
                server.send_message(msg)
                
    except Exception as e:
        app.logger.error(f"Email notification error: {str(e)}")
        # Don't raise the exception - we don't want to fail the OD submission if email fails
        pass

@app.route('/view_request/<int:request_id>')
@login_required
def view_request(request_id):
    # Get request details
    if current_user.role == 'student':
        query = """
            SELECT r.*, u.name as student_name, u.email,
                   d.name as decided_by, 
                   DATE_FORMAT(r.updated_at, '%%Y-%%m-%%d %%H:%%i') as decided_at
            FROM od_requests r
            JOIN users u ON r.student_id = u.id
            LEFT JOIN users d ON r.decided_by_id = d.id
            WHERE r.id = %s AND r.student_id = %s
        """
        cursor.execute(query, (request_id, current_user.id))
    else:  # teacher
        query = """
            SELECT r.*, u.name as student_name, u.email,
                   d.name as decided_by,
                   DATE_FORMAT(r.updated_at, '%%Y-%%m-%%d %%H:%%i') as decided_at
            FROM od_requests r
            JOIN users u ON r.student_id = u.id
            LEFT JOIN users d ON r.decided_by_id = d.id
            WHERE r.id = %s
        """
        cursor.execute(query, (request_id,))
    
    request = cursor.fetchone()
    if not request:
        flash('Request not found or access denied.', 'danger')
        return redirect(url_for(f'{current_user.role}_dashboard'))
    
    # Get comments
    query = """
        SELECT c.*, u.name as author, DATE_FORMAT(c.created_at, '%%Y-%%m-%%d %%H:%%i') as formatted_date
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.request_id = %s
        ORDER BY c.created_at DESC
    """
    cursor.execute(query, (request_id,))
    comments = cursor.fetchall()
    
    return render_template('view_request.html', request=request, comments=comments)

@app.route('/add_comment/<int:request_id>', methods=['POST'])
@login_required
def add_comment(request_id):
    form = CommentForm()
    if form.validate_on_submit():
        content = form.comment.data
        try:
            query = """
                INSERT INTO comments (request_id, user_id, content, created_at)
                VALUES (%s, %s, %s, NOW())
            """
            cursor.execute(query, (request_id, current_user.id, content))
            conn.commit()
            flash('Comment added successfully.', 'success')
        except Exception as e:
            conn.rollback()
            app.logger.error(f"Error adding comment: {str(e)}")
            flash('An error occurred while adding your comment.', 'danger')
    
    return redirect(url_for('view_request', request_id=request_id))

# Update approve_od route to include who approved
@app.route('/approve_od/<int:od_id>', methods=['POST'])
@login_required
def approve_od(od_id):
    if current_user.role != 'teacher':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('student_dashboard'))
        
    try:
        query = """
            UPDATE od_requests 
            SET status = 'Approved', 
                decided_by_id = %s,
                updated_at = NOW() 
            WHERE id = %s
        """
        cursor.execute(query, (current_user.id, od_id))
        conn.commit()
        flash('OD request approved successfully!', 'success')
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error approving OD: {str(e)}")
        flash('An error occurred while processing your request.', 'danger')
    
    return redirect(url_for('teacher_dashboard'))

# Update reject_od route to include who rejected
@app.route('/reject_od/<int:od_id>', methods=['POST'])
@login_required
def reject_od(od_id):
    if current_user.role != 'teacher':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('student_dashboard'))
        
    try:
        query = """
            UPDATE od_requests 
            SET status = 'Rejected', 
                decided_by_id = %s,
                updated_at = NOW() 
            WHERE id = %s
        """
        cursor.execute(query, (current_user.id, od_id))
        conn.commit()
        flash('OD request rejected.', 'success')
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error rejecting OD: {str(e)}")
        flash('An error occurred while processing your request.', 'danger')
    
    return redirect(url_for('teacher_dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route to display team.html page
@app.route('/team')
def team():
    return render_template('team.html')

if __name__ == '__main__':
    app.run(debug=True)
