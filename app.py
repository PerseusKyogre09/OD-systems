from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from config import Config

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to MySQL
conn = pymysql.connect(
    host=Config.MYSQL_HOST,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    db=Config.MYSQL_DB
)
cursor = conn.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_od', methods=['GET', 'POST'])
def submit_od():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        od_reason = request.form['od_reason']

        query = "INSERT INTO students (name, email, subject, od_reason) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, email, subject, od_reason))
        conn.commit()

        student_id = cursor.lastrowid
        # For this example, static mentor/HOD emails are used
        mentor_email = 'mentor@example.com'
        hod_email = 'hod@example.com'

        verification_query = "INSERT INTO verifications (student_id, mentor_email, hod_email) VALUES (%s, %s, %s)"
        cursor.execute(verification_query, (student_id, mentor_email, hod_email))
        conn.commit()

        flash("OD Request Submitted Successfully!")
        return redirect(url_for('index'))

    return render_template('od_submission.html')

@app.route('/verify/<int:student_id>/<string:user_type>', methods=['GET', 'POST'])
def verify(student_id, user_type):
    if request.method == 'POST':
        query = "UPDATE verifications SET {}_verified = TRUE WHERE student_id = %s".format(user_type)
        cursor.execute(query, (student_id,))
        conn.commit()

        flash(f"{user_type.capitalize()} verification completed!")
        return redirect(url_for('index'))

    return render_template('verification.html', student_id=student_id, user_type=user_type)

if __name__ == '__main__':
    app.run(debug=True)
