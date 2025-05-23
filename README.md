# Online OD (On-Duty) Management System

This project is an Online OD (On-Duty) Management System built with Flask, Tailwind CSS, and modern JavaScript. It enables students to submit OD requests, which can be reviewed and approved or rejected by teachers. The system includes features like user authentication, email notifications, separate dashboards for students and teachers, and a comment system for discussion on OD requests.

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: PostgreSQL with Supabase
- **Deployment**: Vercel
- **Frontend**: 
  - Tailwind CSS for styling
  - ScrollCue.js for animations
  - Custom JavaScript for interactivity
- **Security**: 
  - Supabase Auth for authentication
  - JWT token handling
  - CSRF protection

## Team Matrix
This project was created by **Team Matrix**:
- **Pradeepto Pal** &nbsp;[<img src="https://cdn.simpleicons.org/github/white" width="20" height="20">](https://github.com/PerseusKyogre09) &nbsp;[<img src="https://www.linkedin.com/favicon.ico" width="20" height="20">](https://www.linkedin.com/in/pradeeptopal)
- **Shivaditya** &nbsp;[<img src="https://cdn.simpleicons.org/github/white" width="20" height="20">](https://github.com/SHIVADITYA2005) &nbsp;[<img src="https://www.linkedin.com/favicon.ico" width="20" height="20">](https://www.linkedin.com/in/shivaditya-58095b251)


## About the Project
This project was a collective effort for **B Inventors**, a hackathon organized by SRM Connect and BitBucks. We worked hard during this 24-hour hackathon to create a functional and efficient OD management system.

Please see the LICENSE.md for terms and conditions.

## Features

### Core Features
-  Modern, responsive UI with Tailwind CSS
-  Smooth animations with ScrollCue.js
-  Secure authentication system with Supabase Auth and role-based access (Students and Teachers)
-  Easy OD request submission with document attachments
-  Real-time status tracking
-  Comment system for discussion on OD requests
-  Email notifications
-  Dashboard with statistics

1. User Authentication: Registration, login, and logout functionalities with role-based access control for students and teachers.
2. Role-Based Dashboards: Separate views for students and teachers:
   - Student Dashboard: Submit new OD requests and track their status.
   - Teacher Dashboard: View pending OD requests and approve or reject them with comments.
3. Email Notifications: Automatic email notifications are sent to teachers when students submit new OD requests.
4. OD Approval: Teachers can approve or reject OD requests with comments.

## Prerequisites
- Python 3.x
- Required Python packages (listed in requirements.txt)

### Python Packages
Install the necessary packages using:
```bash
pip install -r requirements.txt
```

### Current Requirements
The application uses the following major dependencies:

```plaintext
Flask==3.0.0
Flask-Login==0.6.3
Werkzeug==3.0.1
python-dotenv==1.0.0
cryptography==41.0.7
flask-assets==2.1.0
email-validator==2.1.0.post1
Flask-WTF==1.2.1
Pillow==10.1.0
supabase==1.2.0
psycopg2-binary==2.9.9
python-jose==3.3.0
httpx==0.24.1
```

## Database Setup
The project uses Supabase, a PostgreSQL-based backend-as-a-service. The schema includes:

1. Auth Users - Handled by Supabase Auth
2. OD Requests Table:

```sql
CREATE TABLE od_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES auth.users(id),
    student_name TEXT NOT NULL,
    student_email TEXT NOT NULL,
    event_name TEXT NOT NULL,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    document_url TEXT,
    status TEXT DEFAULT 'pending',
    approved_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

3. Comments Table:

```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    od_request_id UUID NOT NULL REFERENCES od_requests(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    user_name TEXT NOT NULL,
    user_role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

4. Teacher Notifications Table:

```sql
CREATE TABLE teacher_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Environment Variables
Store sensitive data in a .env file:

```plaintext
# Flask
FLASK_SECRET_KEY=your_secret_key
FLASK_ENV=development
DEBUG=True

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
SUPABASE_JWT_SECRET=your_jwt_secret

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password

# Security
SESSION_COOKIE_SECURE=False
REMEMBER_COOKIE_SECURE=False
```

Load these variables at the start of the app using python-dotenv.

## Running the Application

### Local Development
1. Ensure your Supabase project is configured with the proper schema.
2. Run the Flask App:
```bash
python app.py
```
3. Access the app at http://localhost:5000.

### Deployment on Vercel
The project is configured for Vercel deployment using the vercel.json configuration. To deploy:

1. Install Vercel CLI:
```bash
npm i -g vercel
```
2. Run vercel from the project root.
3. Follow the prompts to link to your Vercel account and project.

## Usage
1. Register as a Student or Teacher on the registration page.
2. Verify your email address through the confirmation link.
3. Login with the registered email and password.
4. Student Dashboard:
   - Submit new OD requests with detailed information.
   - Attach supporting documents.
   - Track status of submitted requests.
   - Add comments for discussion.
5. Teacher Dashboard:
   - View pending OD requests from students.
   - Review details and attached documents.
   - Approve or reject requests with comments.
   - Filter and search through requests.

### Email Notifications
The system uses SMTP for email notifications. Ensure you have configured the correct SMTP server details and have an app-specific password if using Gmail with 2FA enabled.

## Screenshots

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="https://i.imgur.com/mEvSPbg.jpeg" width="500px"><br>
        <strong>Light Mode</strong>
      </td>
      <td align="center">
        <img src="https://i.imgur.com/Bd7ZZXH.jpeg" width="500px"><br>
        <strong>Dark Mode</strong>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="https://i.imgur.com/j8Zwpm0.jpeg" width="500px"><br>
        <strong>Sign In / Login</strong>
      </td>
      <td align="center">
        <img src="https://i.imgur.com/eUG9wuh.jpeg" width="500px"><br>
        <strong>Sign Up / Register</strong>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="https://i.imgur.com/5bKKtbs.jpeg" width="500px"><br>
        <strong>Student Dashboard</strong>
      </td>
      <td align="center">
        <img src="https://i.imgur.com/rVxtKaj.jpeg" width="500px"><br>
        <strong>Teacher Dashboard</strong>
      </td>
    </tr>
  </table>
</div>

## Security Considerations
- Sensitive Data: Keep .env in .gitignore to avoid exposing sensitive data.
- SQL Injection Protection: Supabase provides protection against SQL injection with parameterized queries.
- Password Security: Passwords are securely handled by Supabase Auth.
- Row Level Security: Database tables have row-level security policies to ensure users can only access appropriate data.
