# OD (On-Duty) Management System

A modern web application for managing student On-Duty requests in educational institutions. Built with Flask, Tailwind CSS, and modern JavaScript.

## Features

- 🎨 Modern, responsive UI with Tailwind CSS
- ✨ Smooth animations with ScrollCue.js
- 🔒 Secure authentication system
- 📑 Easy OD request submission with file attachments
- 👥 Role-based access (Students and Teachers)
- 📝 Real-time status tracking
- 💬 Comment system for discussion
- 📧 Email notifications
- 📊 Dashboard with statistics

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/od-system.git
   cd od-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create the .env file:
   ```bash
   cp .env.example .env
   ```
   Then edit .env with your configuration.

5. Initialize the database:
   ```bash
   python init_db.py
   ```

6. Run the application:
   ```bash
   python app.py
   ```

## Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

- `FLASK_SECRET_KEY`: Secret key for Flask sessions
- `DB_*`: Database configuration
- `EMAIL_*`: Email server configuration
- `ADMIN_*`: Initial admin account credentials

## Directory Structure

```
od-system/
├── app/
│   └── ...
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
├── templates/
│   ├── base.html
│   ├── index.html
│   └── ...
├── app.py
├── init_db.py
├── schema.sql
├── requirements.txt
└── README.md
```

## Team

This project was created by **Team Matrix**:
- **Team Leader**: [Pradeepto Pal](https://github.com/PerseusKyogre09)
- **Frontend Developer**: [Shivaditya](https://github.com/SHIVADITYA2005)
- **Database Handler**: [Vansh Rattan](https://github.com/rattanvansh)

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

## Screenshots

![Login Page](static/images/screenshots/login.png)
![Student Dashboard](static/images/screenshots/student-dashboard.png)
![Submit OD](static/images/screenshots/submit-od.png)
![Teacher Dashboard](static/images/screenshots/teacher-dashboard.png)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email your-email@example.com or open an issue in the GitHub repository.

## Security Considerations

1. **Environment Variables**: 
   - Keep sensitive data in `.env`
   - Never commit `.env` to version control

2. **Database Security**:
   - Use parameterized queries to prevent SQL injection
   - Encrypt sensitive data before storing
   - Regularly backup the database

3. **File Upload Security**:
   - Validate file types and sizes
   - Use secure filenames
   - Store files outside web root

4. **Authentication**:
   - Passwords are hashed using Werkzeug's security features
   - Session management with Flask-Login
   - CSRF protection on all forms

5. **Production Deployment**:
   - Set DEBUG=False
   - Enable SSL/TLS
   - Use secure session cookies
   - Configure proper CORS policies
