# Online OD (On-Duty) Management System

This project is an Online OD (On-Duty) Management System built with Flask, Tailwind CSS, and modern JavaScript. It enables students to submit OD requests, which can be reviewed and approved or rejected by teachers. The system includes features like user authentication, email notifications, and separate dashboards for students and teachers.

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: 
  - Tailwind CSS for styling
  - ScrollCue.js for animations
  - Custom JavaScript for interactivity
- **Security**: 
  - Flask-Login for authentication
  - Werkzeug for password hashing
  - CSRF protection

## Team Matrix
This project was created by **Team Matrix**:
- **Team Leader**: [Pradeepto Pal](https://github.com/PerseusKyogre09)
- **Frontend Developer**: [Shivaditya](https://github.com/SHIVADITYA2005)

![Team Matrix](https://imgur.com/Xe6GCKB.png)

## About the Project
This project was a collective effort for **B Inventors**, a hackathon organized by SRM Connect and BitBucks. We worked hard during this 24-hour hackathon to create a functional and efficient OD management system.

Please see the LICENSE.md for terms and conditions.

## Features

### Core Features
- 🎨 Modern, responsive UI with Tailwind CSS
- ✨ Smooth animations with ScrollCue.js
- 🔒 Secure authentication system with role-based access (Students and Teachers)
- 📑 Easy OD request submission with file attachments
- 📝 Real-time status tracking
- 💬 Comment system for discussion
- 📧 Email notifications
- 📊 Dashboard with statistics

1. User Authentication: Registration, login, and logout functionalities with role-based access control for students and teachers.
2. Role-Based Dashboards: Separate views for students and teachers:
- Student Dashboard: Submit new OD requests.
- Teacher Dashboard: View pending OD requests and approve or reject them.
3. Email Notifications: Automatic email notifications are sent to teachers when students submit new OD requests.
4. OD Approval: Teachers can approve or reject OD requests from their dashboard.

## Prerequisites
- Python 3.x
- MySQL Server
- Required Python packages (listed in requirements.txt)
### Python Packages
Install the necessary packages using:
```bash
pip install -r requirements.txt
```
### Requirements
Add these lines to requirements.txt:
```plaintext
Flask
Flask-Login
PyMySQL
Werkzeug
python-dotenv
```
## Database Setup
1. Create Database: Create a MySQL database named `od_system_db`.
2. Users Table: Create a users table with the following structure:
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'teacher') NOT NULL
);
```
3. OD Requests Table: Create an `od_requests` table:
```sql
CREATE TABLE od_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    od_reason TEXT,
    approved TINYINT(1) NULL
);
```
## Environment Variables
Store sensitive data in a `.env` file:
```plaintext
RECIEVE=recieve@email.com
EMAIL_USER=sender@email.com
EMAIL_PASS=password
```
Load these variables at the start of the app using `python-dotenv`.

## Running the Application
1. Start MySQL Server and ensure the database is configured.
2. Run the Flask App:
```bash
python app.py
```
3. Access the app at `http://localhost:5000`.

## Usage
1. Register as a Student or Teacher on the registration page.
2. Login with the registered email and password.
3. Student Dashboard: Students can submit OD requests specifying the reason and selecting the teachers for approval.
4. Teacher Dashboard: Teachers can view OD requests and approve or reject them.

### Email Notifications
The system uses Gmail’s SMTP server for email notifications. Ensure you have enabled “less secure app access” in your Gmail account, or use an app-specific password if 2FA is enabled.

## Screenshots
![S-1](https://imgur.com/tFOK8YE.png)
![S-2](https://imgur.com/7vcri2D.png)
![S-3](https://imgur.com/aGaX8pf.png)
![S-4](https://imgur.com/6jPyBzd.png)
![S-5](https://imgur.com/38HtozP.png)
![S-6](https://imgur.com/LqvCIZG.png)
![S-7](https://imgur.com/ptkbvx8.png)

## Security Considerations
- Sensitive Data: Keep `.env` in `.gitignore` to avoid exposing sensitive data.
- SQL Injection Protection: Always use parameterized queries.
- Password Security: Passwords are hashed using `generate_password_hash` before storing in the database.