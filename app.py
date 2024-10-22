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
    
    return render_template('index.html')

@app.route('/register', methods=['POST'])
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

@app.route('/student_dashboard')
@login_required
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    return render_template('teacher_dashboard.html')

@app.route('/submit_od', methods=['GET', 'POST'])
@login_required
def submit_od():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        od_reason = request.form['od_reason']
        teachers = request.form.getlist('teachers')

        # Send email for approval
        for teacher_email in teachers:
            send_email(teacher_email, name, od_reason, email)

        flash('OD submitted successfully! The concerned teachers have been notified.')
        return redirect(url_for('submit_od'))
    
    return render_template('submit_od.html')

def send_email(to_email, name, od_reason, student_email):
    sender_email = "your_email@gmail.com"
    sender_password = "your_email_password"
    
    subject = "OD Verification Request"
    body = f"Dear Teacher,\n\nStudent {name} ({student_email}) has submitted an OD for the following reason: {od_reason}.\n\nPlease verify the OD.\n\nBest Regards,\nOD System"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

if __name__ == '__main__':
    app.run(debug=True)
