from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    file = FileField('Grade Data File', validators=[
        FileRequired(), 
        FileAllowed(['csv', 'xls', 'xlsx'], 'Only CSV and Excel files are allowed')
    ])
    term = SelectField('Term', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Upload')

class ReportForm(FlaskForm):
    report_type = SelectField('Report Type', choices=[
        ('grade_distribution', 'Grade Distribution'),
        ('department_performance', 'Department Performance'),
        ('course_comparison', 'Course Comparison'),
        ('term_trends', 'Term Trends'),
        ('student_performance', 'Student Performance'),
        ('at_risk_students', 'At-Risk Students')
    ], validators=[DataRequired()])
    
    department = SelectField('Department', coerce=int, validators=[Optional()])
    course = SelectField('Course', coerce=int, validators=[Optional()])
    term = SelectField('Term', coerce=int, validators=[Optional()])
    
    format = SelectField('Format', choices=[
        ('web', 'Web View'),
        ('csv', 'CSV Download'),
        ('pdf', 'PDF Download')
    ], default='web')
    
    submit = SubmitField('Generate Report')

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired() if True else Optional(),  # New user vs existing
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[
        ('admin', 'Administrator'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff')
    ])
    department = SelectField('Department', coerce=int)
    submit = SubmitField('Save')