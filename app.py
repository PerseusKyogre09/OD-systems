from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
conn = pymysql.connect(host='localhost', user='root', password='perseus', db='od_system_db')
cursor = conn.cursor()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User:
    def __init__(self, id, email, role):
        self.id = id
        self.email = email
        self.role = role

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    query = "SELECT id, email, role FROM users WHERE id=%s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    if result:
        return User(result[0], result[1], result[2])
    return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        query = "SELECT id, email, password, role FROM users WHERE email=%s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()

        if result and check_password_hash(result[2], password):
            user = User(result[0], result[1], result[3])
            login_user(user)
            if user.role == 'student':
                return redirect(url_for('student_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        query = "SELECT email FROM users WHERE email=%s"
        cursor.execute(query, (email,))
        if cursor.fetchone():
            flash('Email is already registered. Please log in or use a different email.')
            return redirect(url_for('login'))

        query = "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)"
        cursor.execute(query, (email, password, role))
        conn.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    query = "SELECT id, name, email, od_reason FROM od_requests WHERE approved IS NULL"
    cursor.execute(query)
    ods = cursor.fetchall()
    return render_template('teacher_dashboard.html', ods=ods)

@app.route('/submit_od', methods=['GET', 'POST'])
@login_required
def submit_od():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        od_reason = request.form['od_reason']
        teachers = request.form.getlist('teachers')

        # Insert OD request into the database
        query = "INSERT INTO od_requests (name, email, od_reason, approved) VALUES (%s, %s, %s, NULL)"
        cursor.execute(query, (name, email, od_reason))
        od_id = cursor.lastrowid  # Get the ID of the last inserted OD request

        # Send email for approval
        for teacher_email in teachers:
            send_email(teacher_email, name, od_reason, email, od_id)

        flash('OD submitted successfully! The concerned teachers have been notified.')
        return redirect(url_for('submit_od'))
    
    return render_template('submit_od.html')

def send_email(to_email, name, od_reason, student_email, od_id):
    sender_email = "your_email@gmail.com"
    sender_password = "your_email_password"
    
    subject = "OD Verification Request"
    body = f"Dear Teacher,\n\nStudent {name} ({student_email}) has submitted an OD for the following reason: {od_reason}.\nPlease verify the OD by clicking the following link:\n\nhttp://localhost:5000/approve_od/{od_id} or http://localhost:5000/reject_od/{od_id}.\n\nBest Regards,\nOD System"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

@app.route('/approve_od/<int:od_id>', methods=['POST'])
@login_required
def approve_od(od_id):
    query = "UPDATE od_requests SET approved = 'yes' WHERE id = %s"
    cursor.execute(query, (od_id,))
    conn.commit()
    flash('OD approved successfully!')
    return redirect(url_for('teacher_dashboard'))

@app.route('/reject_od/<int:od_id>', methods=['POST'])
@login_required
def reject_od(od_id):
    query = "UPDATE od_requests SET approved = 'no' WHERE id = %s"
    cursor.execute(query, (od_id,))
    conn.commit()
    flash('OD rejected successfully!')
    return redirect(url_for('teacher_dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
