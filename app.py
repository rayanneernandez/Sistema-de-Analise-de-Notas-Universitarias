from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
from flask_wtf.csrf import CSRFProtect
import secrets
import json
from models import db, User, Course, Student, Grade, Department, Term
from forms import LoginForm, UploadForm, ReportForm
from utils import allowed_file, generate_report, calculate_statistics

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grades.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
csrf = CSRFProtect(app)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get basic statistics for dashboard
    total_students = Student.query.count()
    total_courses = Course.query.count()
    recent_grades = Grade.query.order_by(Grade.date_added.desc()).limit(5).all()
    
    # Create summary statistics
    stats = calculate_statistics()
    
    # Get department distribution for chart
    dept_data = db.session.query(Department.name, db.func.count(Student.id))\
        .join(Student, Student.department_id == Department.id)\
        .group_by(Department.name).all()
    
    # Grade distribution data
    grade_distribution = db.session.query(Grade.letter_grade, db.func.count(Grade.id))\
        .group_by(Grade.letter_grade).all()
    
    return render_template('dashboard.html', 
                          total_students=total_students,
                          total_courses=total_courses,
                          recent_grades=recent_grades,
                          stats=stats,
                          dept_data=json.dumps([x[0] for x in dept_data]),
                          dept_counts=json.dumps([x[1] for x in dept_data]),
                          grade_labels=json.dumps([x[0] for x in grade_distribution]),
                          grade_counts=json.dumps([x[1] for x in grade_distribution]))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Process the uploaded file
                if filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                elif filename.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(filepath)
                else:
                    flash('Unsupported file format', 'danger')
                    return redirect(request.url)
                
                # Import data to database
                term_id = form.term.data
                import_count = import_grade_data(df, term_id)
                
                flash(f'Successfully imported {import_count} grade records', 'success')
                return redirect(url_for('dashboard'))
            
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')
                return redirect(request.url)
    
    # Get terms for dropdown
    terms = Term.query.all()
    return render_template('upload.html', form=form, terms=terms)

@app.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    form = ReportForm()
    # Populate form dropdowns
    form.department.choices = [(d.id, d.name) for d in Department.query.all()]
    form.course.choices = [(c.id, c.code + ' - ' + c.name) for c in Course.query.all()]
    form.term.choices = [(t.id, t.name) for t in Term.query.all()]
    
    if form.validate_on_submit():
        report_type = form.report_type.data
        department_id = form.department.data if form.department.data else None
        course_id = form.course.data if form.course.data else None
        term_id = form.term.data if form.term.data else None
        
        # Generate the report
        report_data = generate_report(report_type, department_id, course_id, term_id)
        
        if report_data:
            # For downloadable reports
            if form.format.data == 'csv':
                output = io.StringIO()
                report_data.to_csv(output, index=False)
                output.seek(0)
                
                return send_file(
                    io.BytesIO(output.getvalue().encode()),
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=f'report_{report_type}_{datetime.now().strftime("%Y%m%d")}.csv'
                )
            
            # For visualization
            return render_template('report_results.html', 
                                  report_type=report_type,
                                  tables=[report_data.to_html(classes='table table-striped')],
                                  titles=report_data.columns.values,
                                  visualization=create_visualization(report_data, report_type))
    
    return render_template('reports.html', form=form)

@app.route('/courses')
@login_required
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/students')
@login_required
def students():
    page = request.args.get('page', 1, type=int)
    students = Student.query.paginate(page=page, per_page=20)
    return render_template('students.html', students=students)

@app.route('/api/grade_distribution')
@login_required
def api_grade_distribution():
    course_id = request.args.get('course_id', type=int)
    term_id = request.args.get('term_id', type=int)
    
    query = db.session.query(Grade.letter_grade, db.func.count(Grade.id))
    
    if course_id:
        query = query.filter(Grade.course_id == course_id)
    if term_id:
        query = query.filter(Grade.term_id == term_id)
        
    distribution = query.group_by(Grade.letter_grade).all()
    
    # Format for Chart.js
    labels = [grade[0] for grade in distribution]
    data = [grade[1] for grade in distribution]
    
    return jsonify({
        'labels': labels,
        'datasets': [{
            'label': 'Grade Distribution',
            'data': data,
            'backgroundColor': [
                '#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#FF9800', '#FF5722'
            ]
        }]
    })

def import_grade_data(df, term_id):
    """Import grades from DataFrame to database"""
    count = 0
    for _, row in df.iterrows():
        try:
            # Check if student exists, create if not
            student = Student.query.filter_by(student_id=row['student_id']).first()
            if not student:
                # Get or create department
                dept = Department.query.filter_by(name=row['department']).first()
                if not dept:
                    dept = Department(name=row['department'])
                    db.session.add(dept)
                    db.session.flush()
                
                student = Student(
                    student_id=row['student_id'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    email=row['email'] if 'email' in row else f"{row['student_id']}@university.edu",
                    department_id=dept.id
                )
                db.session.add(student)
                db.session.flush()
            
            # Check if course exists, create if not
            course = Course.query.filter_by(code=row['course_code']).first()
            if not course:
                course = Course(
                    code=row['course_code'],
                    name=row['course_name'] if 'course_name' in row else row['course_code'],
                    credits=row['credits'] if 'credits' in row else 3
                )
                db.session.add(course)
                db.session.flush()
            
            # Add grade
            grade = Grade(
                student_id=student.id,
                course_id=course.id,
                term_id=term_id,
                numeric_grade=float(row['grade']),
                letter_grade=calculate_letter_grade(float(row['grade'])),
                date_added=datetime.now()
            )
            db.session.add(grade)
            count += 1
        
        except Exception as e:
            print(f"Error importing row: {e}")
            continue
    
    db.session.commit()
    return count

def calculate_letter_grade(numeric_grade):
    """Convert numeric grade to letter grade"""
    if numeric_grade >= 90:
        return 'A'
    elif numeric_grade >= 80:
        return 'B'
    elif numeric_grade >= 70:
        return 'C'
    elif numeric_grade >= 60:
        return 'D'
    else:
        return 'F'

def create_visualization(data, report_type):
    """Create visualization based on report type and data"""
    plt.figure(figsize=(10, 6))
    
    if report_type == 'grade_distribution':
        sns.barplot(x='letter_grade', y='count', data=data)
        plt.title('Grade Distribution')
        plt.xlabel('Grade')
        plt.ylabel('Count')
    
    elif report_type == 'department_performance':
        sns.barplot(x='department', y='average_grade', data=data)
        plt.title('Average Grade by Department')
        plt.xlabel('Department')
        plt.ylabel('Average Grade')
        plt.xticks(rotation=45)
    
    elif report_type == 'course_trend':
        sns.lineplot(x='term', y='average_grade', data=data)
        plt.title('Course Performance Trend')
        plt.xlabel('Term')
        plt.ylabel('Average Grade')
        plt.xticks(rotation=45)
    
    # Save plot to a temporary buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Convert to base64 for embedding in HTML
    image_png = buffer.getvalue()
    buffer.close()
    encoded = base64.b64encode(image_png)
    
    return 'data:image/png;base64,' + encoded.decode('utf-8')

with app.app_context():
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin = User.query.filter_by(email='admin@university.edu').first()
    if not admin:
        admin = User(
            name='Admin',
            email='admin@university.edu',
            password=generate_password_hash('adminpass'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)