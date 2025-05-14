from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
import os
from datetime import date

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required")
    ])

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(message="Full name is required"),
        Length(min=2, max=50, message="Name must be between 2 and 50 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo('password', message="Passwords must match")
    ])
    role = SelectField('Role', choices=[
        ('student', 'Student'),
        ('teacher', 'Teacher')
    ], validators=[DataRequired(message="Please select a role")])

class ODRequestForm(FlaskForm):
    event_name = StringField('Event Name', validators=[
        DataRequired(message="Event name is required"),
        Length(min=3, max=100, message="Event name must be between 3 and 100 characters")
    ])
    date = DateField('Date', validators=[
        DataRequired(message="Date is required")
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message="Description is required"),
        Length(min=10, max=1000, message="Description must be between 10 and 1000 characters")
    ])
    document = FileField('Supporting Document')

    def validate_date(self, field):
        if field.data < date.today():
            raise ValidationError("OD request date cannot be in the past")

    def validate_document(self, field):
        if field.data:
            filename = field.data.filename
            if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'doc', 'docx'}):
                raise ValidationError("Only PDF and DOC files are allowed")

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[
        DataRequired(message="Comment cannot be empty"),
        Length(max=500, message="Comment must not exceed 500 characters")
    ])
