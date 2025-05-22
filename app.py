from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from forms import LoginForm, RegistrationForm, ODRequestForm, CommentForm
from config import get_config
from supabase_utils import (
    sign_up_user, sign_in_user, sign_out_user, get_user,
    insert_record, update_record, get_record, get_records, delete_record,
    upload_file, get_file_url
)
from models import SupabaseUser
import json


app = Flask(__name__)
app.config.from_object(get_config())


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    token = session.get('access_token')
    if not token:
        return None
    
    try:
        user_response = get_user(token)
        if not user_response or not user_response.get('user'):
            app.logger.warning("No user found in token response, session may be expired")
            
            session.pop('access_token', None)
            return None
        
        user_data = user_response['user']
        return SupabaseUser(user_data)
    except Exception as e:
        app.logger.error(f"Error loading user: {str(e)}")
        
        session.pop('access_token', None)
        return None

@app.route('/')
def index():
    """Home page route."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route."""
    if current_user.is_authenticated:
        return redirect_based_on_role()

    form = LoginForm()
    if form.validate_on_submit():
        try:
            app.logger.info(f"Attempting login for {form.email.data}")
            
            
            response = sign_in_user(form.email.data, form.password.data)
            
            app.logger.info(f"Login response received: {response}")
            
            
            if response.get('error') and response.get('email_confirmed') is False:
                app.logger.warning(f"Email not confirmed for {form.email.data}")
                flash('Please confirm your email address before logging in. Check your inbox for the confirmation link.', 'warning')
                return render_template('login.html', form=form, email_confirmation_needed=True, email=form.email.data)
            
            if response and response.get('user'):
                try:
                    
                    session_token = None
                    
                    
                    session_data = response.get('session')
                    
                    
                    if session_data:
                        if isinstance(session_data, dict):
                            
                            session_token = session_data.get('access_token')
                        elif hasattr(session_data, 'access_token'):
                            
                            session_token = session_data.access_token
                            app.logger.info(f"Found access_token as attribute")
                        else:
                            
                            app.logger.info(f"Session data type: {type(session_data)}")
                            app.logger.info(f"Session data dir: {dir(session_data)}")
                            
                            if str(session_data) and 'token' in str(session_data).lower():
                                app.logger.info(f"Raw session data: {str(session_data)}")
                    
                    if session_token:
                        app.logger.info("Got access token, setting session")
                        session['access_token'] = session_token
                    else:
                        app.logger.warning("No access token found in response")
                    
                    
                    user_data = None
                    user_obj = response.get('user')
                    
                    if isinstance(user_obj, dict):
                        user_data = user_obj
                    elif hasattr(user_obj, '__dict__'):
                        
                        try:
                            user_data = vars(user_obj)
                        except:
                            pass
                    
                    if not user_data and hasattr(user_obj, 'id'):
                        
                        user_data = {'id': user_obj.id, 'email': getattr(user_obj, 'email', form.email.data)}
                    
                    user = SupabaseUser(user_data)
                    login_user(user)
                    
                    app.logger.info(f"User logged in: {user.email}")
                    
                    
                    return redirect_based_on_role()
                    
                except Exception as e:
                    app.logger.error(f"Error processing login response: {str(e)}")
                    flash('Error processing login information. Please try again.', 'danger')
            else:                
                app.logger.warning("Login failed - no user in response")
                error_msg = "Login failed. "
                
                
                if isinstance(response, dict) and response.get('error'):
                    error_msg = str(response.get('error'))
                    
                    
                    if "Email not confirmed" in error_msg:
                        flash('Please confirm your email address before logging in. Check your inbox for the confirmation link.', 'warning')
                        return render_template('login.html', form=form, email_confirmation_needed=True, email=form.email.data)                
                    else:
                        error_msg += "Please check your credentials."
                    
                flash(error_msg, 'danger')
        except Exception as e:
            error_str = str(e)
            app.logger.error(f"Login error: {error_str}")
            if "Could not find working sign-in method" in error_str:
                flash('The login system is currently experiencing technical difficulties. Please try again later.', 'danger')
            elif "Failed to sign in" in error_str:
                if "sign_in_with_password" in error_str:
                    flash('Invalid email or password. Please check your credentials and try again.', 'danger')
                else:
                    flash('Login failed. Please try again.', 'danger')
            elif "For security purposes, you can only request this" in error_str:
                flash('Too many login attempts. Please wait a minute before trying again.', 'warning')
            elif "Email not confirmed" in error_str:
                flash('Please confirm your email address before logging in. Check your inbox for the confirmation link.', 'warning')
                return render_template('login.html', form=form, email_confirmation_needed=True, email=form.email.data)
            else:
                flash('An error occurred during login. Please try again.', 'danger')

    return render_template('login.html', form=form)

@app.route('/resend_verification', methods=['POST'])
def resend_verification():
    """Resend verification email route."""
    email = request.form.get('email')
    if not email:
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
        
    if not email:
        flash('Email address is required.', 'danger')
        return redirect(url_for('login'))
    
    try:
        
        
        from supabase_utils import get_supabase_admin_client
        admin_client = get_supabase_admin_client()
        
        
        if hasattr(admin_client.auth, 'admin') and hasattr(admin_client.auth.admin, 'invite_user_by_email'):
            admin_client.auth.admin.invite_user_by_email(email)
            flash('Verification email has been resent. Please check your inbox.', 'success')
        else:
            
            
            
            flash('Please try registering again with the same email to receive a new verification link.', 'info')
        
    except Exception as e:
        app.logger.error(f"Error resending verification: {str(e)}")
        flash('An error occurred while trying to resend the verification email.', 'danger')
    
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    """Logout route."""
    token = session.get('access_token')
    if token:
        try:
            sign_out_user(token)
        except Exception as e:
            app.logger.error(f"Logout error: {str(e)}")
    
    logout_user()
    session.pop('access_token', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route."""
    if current_user.is_authenticated:
        return redirect_based_on_role()
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            app.logger.info("Starting user registration process")
            
            
            user_metadata = {
                'name': form.name.data,
                'role': form.role.data
            }
            
            
            base_url = request.host_url.rstrip('/')
            redirect_url = f"{base_url}/login"
            
            app.logger.info(f"Attempting to register: {form.email.data} with role: {form.role.data}")
            app.logger.info(f"Using redirect URL: {redirect_url}")
            
            
            response = sign_up_user(
                form.email.data, 
                form.password.data, 
                user_metadata,
                redirect_url
            )
            
            app.logger.info(f"Registration response received: {response}")
            
            
            if response and response.get('user'):
                app.logger.info("Registration successful")
                flash('Registration successful! Please check your email to verify your account.', 'success')
                return redirect(url_for('login'))
            else:
                app.logger.warning("Registration failed - no user in response")
                
                if "For security purposes, you can only request this after" in str(response):
                    flash('Too many attempts. Please wait for a minute before trying again.', 'warning')
                else:
                    flash('Registration failed. Please try again.', 'danger')
        except Exception as e:
            error_msg = str(e)
            app.logger.error(f"Registration error: {error_msg}")
            
            
            if "security purposes" in error_msg and "request this after" in error_msg:
                flash('Too many registration attempts. Please wait for a minute before trying again.', 'warning')
            else:
                flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('register.html', form=form)

def redirect_based_on_role():
    """Redirect user based on their role."""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    if current_user.is_teacher():
        return redirect(url_for('teacher_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    """Student dashboard route."""
    if not current_user.is_authenticated or current_user.is_teacher():
        return redirect(url_for('login'))
    
    try:
        
        if not current_user.id:
            app.logger.error("No valid user ID found for student dashboard")
            flash('Your session appears to be invalid. Please login again.', 'danger')
            return redirect(url_for('logout'))
        
        
        from supabase_utils import get_supabase_admin_client
        admin_client = get_supabase_admin_client()
        response = admin_client.table('od_requests').select('*').eq('student_id', current_user.id).execute()
        od_requests = response.data
        
        
        for req in od_requests:
            
            if 'date' in req and req['date'] and 'T' in req['date']:
                req['date'] = req['date'].split('T')[0]
                
            
            if 'created_at' in req and req['created_at'] and 'T' in req['created_at']:
                req['created_at'] = req['created_at'].replace('T', ' ').split('.')[0]
    except Exception as e:
        app.logger.error(f"Error fetching OD requests: {str(e)}")
        od_requests = []
    
    return render_template('student_dashboard.html', od_requests=od_requests)

@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    """Teacher dashboard route."""
    if not current_user.is_authenticated or not current_user.is_teacher():
        return redirect(url_for('login'))
    try:
        
        from supabase_utils import get_supabase_admin_client
        admin_client = get_supabase_admin_client()
        
        
        all_requests_response = admin_client.table('od_requests').select('*').execute()
        all_requests = all_requests_response.data
        
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        
        od_requests = [req for req in all_requests if req['status'].lower() == 'pending']
        
        
        for req in od_requests:
            
            if not req.get('student_name'):
                req['student_name'] = req.get('student_email', 'Unknown Student')
            
            
            if 'date' in req and req['date'] and 'T' in req['date']:
                req['date'] = req['date'].split('T')[0]
                
            
            if 'created_at' in req and req['created_at'] and 'T' in req['created_at']:
                req['created_at'] = req['created_at'].replace('T', ' ').split('.')[0]
                
        pending_count = len(od_requests)
        
        
        todays_requests = []
        for req in all_requests:
            created_at = req.get('created_at', '')
            
            if isinstance(created_at, str) and created_at.startswith(today):
                todays_requests.append(req)
        todays_count = len(todays_requests)
        
        
        processed_requests = [req for req in all_requests if req['status'].lower() != 'pending']
        total_actions = len(processed_requests)    
    except Exception as e:
        app.logger.error(f"Error fetching OD requests: {str(e)}")
        od_requests = []
        pending_count = 0
        todays_count = 0
        total_actions = 0
    
    return render_template('teacher_dashboard.html', 
                           od_requests=od_requests, 
                           pending_count=pending_count, 
                           todays_count=todays_count, 
                           total_actions=total_actions, 
                           today=datetime.now().strftime("%B %d, %Y"))

@app.route('/submit_od', methods=['GET', 'POST'])
@login_required
def submit_od():
    """Submit OD request route."""
    if not current_user.is_authenticated or current_user.is_teacher():
        return redirect(url_for('login'))
    
    form = ODRequestForm()
    if form.validate_on_submit():
        try:
            
            document_url = None
            if form.document.data:
                file = form.document.data
                filename = secure_filename(file.filename)
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                
                file.save(temp_path)
                
                
                timestamp = int(time.time())
                file_key = f"{current_user.id}_{timestamp}_{filename}"
                upload_file('od-documents', temp_path, file_key)
                
                
                document_url = get_file_url('od-documents', file_key)
                
                
                os.remove(temp_path)
              
            od_data = {
                'event_name': form.event_name.data,
                'date': form.date.data.isoformat(),
                'description': form.description.data,
                'document_url': document_url,
                'student_id': current_user.id,
                'student_name': current_user.name,
                'student_email': current_user.email,
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            
            from supabase_utils import get_supabase_admin_client
            admin_client = get_supabase_admin_client()
            response = admin_client.table('od_requests').insert(od_data).execute()
            request_id = response.data[0]['id']
            
            
            notify_teachers(current_user.name, form.event_name.data, request_id)
            
            flash('OD request submitted successfully!', 'success')
            return redirect(url_for('student_dashboard'))
            
        except Exception as e:
            app.logger.error(f"Error submitting OD request: {str(e)}")
            flash('An error occurred while submitting your request. Please try again.', 'danger')
    
    return render_template('submit_od.html', form=form)

def notify_teachers(student_name, event_name, od_id):
    """Send email notifications to all teachers about a new OD request."""
    try:        
        from supabase_utils import get_supabase_admin_client
        admin_client = get_supabase_admin_client()
        response = admin_client.table('teacher_notifications').select('*').execute()
        teachers = response.data
        
        if not teachers:
            app.logger.warning("No teachers found for notification")
            return
            
        
        sender_email = app.config['MAIL_USERNAME']
        sender_password = app.config['MAIL_PASSWORD']
        
        for teacher in teachers:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = teacher['email']
            msg['Subject'] = f"New OD Request from {student_name}"
            
            body = f"""
            Dear Teacher,
            
            A new OD request has been submitted:
            
            Student: {student_name}
            Event: {event_name}
            
            Please login to review this request:
            {request.host_url}view_request/{od_id}
            
            Thank you,
            OD System Admin
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            
            with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                
    except Exception as e:
        app.logger.error(f"Error sending teacher notifications: {str(e)}")

@app.route('/view_request/<string:request_id>')
@login_required
def view_request(request_id):
    """View OD request details."""
    try:
        
        from supabase_utils import get_supabase_admin_client
        admin_client = get_supabase_admin_client()
        od_response = admin_client.table('od_requests').select('*').eq('id', request_id).execute()
        od_request = od_response.data[0] if od_response.data else None
        
        if not od_request:
            flash('Request not found.', 'danger')
            return redirect_based_on_role()
            
        
        if not current_user.is_teacher() and od_request['student_id'] != current_user.id:
            flash('You do not have permission to view this request.', 'danger')
            return redirect_based_on_role()
            
        
        from supabase_utils import get_supabase_admin_client
        admin_client = get_supabase_admin_client()
        comments_response = admin_client.table('comments').select('*').eq('od_request_id', request_id).execute()
        comments = comments_response.data
        
        
        form = CommentForm()
        
        return render_template(
            'view_request.html', 
            request=od_request, 
            comments=comments, 
            form=form
        )
        
    except Exception as e:
        app.logger.error(f"Error viewing request: {str(e)}")
        flash('An error occurred while retrieving the request.', 'danger')
        return redirect_based_on_role()

@app.route('/add_comment/<string:request_id>', methods=['POST'])
@login_required
def add_comment(request_id):
    """Add a comment to an OD request."""
    form = CommentForm()    
    if form.validate_on_submit():
        try:
            comment_data = {
                'od_request_id': request_id,
                'user_id': current_user.id,
                'user_name': current_user.name,
                'user_role': current_user.role,
                'content': form.content.data,
                'created_at': datetime.now().isoformat()
            }
            
            
            from supabase_utils import get_supabase_admin_client
            admin_client = get_supabase_admin_client()
            admin_client.table('comments').insert(comment_data).execute()
            flash('Comment added successfully.', 'success')
            
        except Exception as e:
            app.logger.error(f"Error adding comment: {str(e)}")
            flash('An error occurred while adding your comment.', 'danger')
            
    return redirect(url_for('view_request', request_id=request_id))

@app.route('/approve_od/<string:od_id>', methods=['GET', 'POST'])
@login_required
def approve_od(od_id):
    """Approve an OD request."""
    if not current_user.is_authenticated or not current_user.is_teacher():
        flash('You do not have permission to approve requests.', 'danger')
        return redirect(url_for('login'))
        
    try:
        
        from supabase_utils import get_supabase_admin_client
        admin_client = get_supabase_admin_client()        
        admin_client.table('od_requests').update({
            'status': 'approved',
            'approved_by': current_user.id,
            'approved_at': datetime.now().isoformat()
        }).eq('id', od_id).execute()
        
        flash('Request approved successfully.', 'success')
        
    except Exception as e:
        app.logger.error(f"Error approving request: {str(e)}")
        flash('An error occurred while approving the request.', 'danger')
        
    return redirect(url_for('teacher_dashboard'))

@app.route('/reject_od/<string:od_id>', methods=['GET', 'POST'])
@login_required
def reject_od(od_id):
    """Reject an OD request."""
    if not current_user.is_authenticated or not current_user.is_teacher():
        flash('You do not have permission to reject requests.', 'danger')
        return redirect(url_for('login'))
        
    try:
        
        from supabase_utils import get_supabase_admin_client
        admin_client = get_supabase_admin_client()        
        admin_client.table('od_requests').update({
            'status': 'rejected',
            'approved_by': current_user.id,
            'approved_at': datetime.now().isoformat()
        }).eq('id', od_id).execute()
        
        flash('Request rejected.', 'info')
        
    except Exception as e:
        app.logger.error(f"Error rejecting request: {str(e)}")
        flash('An error occurred while rejecting the request.', 'danger')
        
    return redirect(url_for('teacher_dashboard'))

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
