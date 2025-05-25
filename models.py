from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='faculty')
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    department = db.relationship('Department', backref='users')

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(10), nullable=True)
    
    students = db.relationship('Student', backref='department', lazy=True)
    courses = db.relationship('Course', backref='department', lazy=True)

class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    
    grades = db.relationship('Grade', backref='term', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    date_enrolled = db.Column(db.DateTime, default=datetime.utcnow)
    
    grades = db.relationship('Grade', backref='student', lazy=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def gpa(self):
        """Calculate student's GPA"""
        grades = Grade.query.filter_by(student_id=self.id).all()
        if not grades:
            return 0.0
            
        total_points = 0.0
        total_credits = 0.0
        
        for grade in grades:
            course_credits = grade.course.credits
            total_credits += course_credits
            total_points += grade.grade_points * course_credits
            
        return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Float, default=3.0)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    
    grades = db.relationship('Grade', backref='course', lazy=True)
    
    @property
    def average_grade(self):
        """Calculate course average grade"""
        grades = Grade.query.filter_by(course_id=self.id).all()
        if not grades:
            return 0.0
            
        total = sum(grade.numeric_grade for grade in grades)
        return round(total / len(grades), 2)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), nullable=False)
    numeric_grade = db.Column(db.Float, nullable=False)
    letter_grade = db.Column(db.String(2), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def grade_points(self):
        """Convert letter grade to grade points for GPA calculation"""
        grade_map = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'D-': 0.7,
            'F': 0.0
        }
        return grade_map.get(self.letter_grade, 0.0)