import pandas as pd
import numpy as np
from models import db, Student, Course, Grade, Department, Term

def allowed_file(filename):
    """Check if file type is allowed"""
    ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_statistics():
    """Calculate summary statistics for dashboard"""
    # Overall GPA
    avg_grade = db.session.query(db.func.avg(Grade.numeric_grade)).scalar() or 0
    
    # Department with highest average
    dept_avg = db.session.query(
        Department.name, 
        db.func.avg(Grade.numeric_grade).label('avg_grade')
    ).join(Student, Student.department_id == Department.id)\
     .join(Grade, Grade.student_id == Student.id)\
     .group_by(Department.name)\
     .order_by(db.desc('avg_grade'))\
     .first()
    
    # Course with highest average
    course_avg = db.session.query(
        Course.name,
        db.func.avg(Grade.numeric_grade).label('avg_grade')
    ).join(Grade, Grade.course_id == Course.id)\
     .group_by(Course.name)\
     .order_by(db.desc('avg_grade'))\
     .first()
    
    # At-risk student count (below 70 average)
    at_risk_count = db.session.query(db.func.count(db.func.distinct(Student.id)))\
        .join(Grade, Grade.student_id == Student.id)\
        .group_by(Student.id)\
        .having(db.func.avg(Grade.numeric_grade) < 70)\
        .count()
    
    return {
        'average_grade': round(avg_grade, 2),
        'top_department': dept_avg[0] if dept_avg else 'N/A',
        'top_department_avg': round(dept_avg[1], 2) if dept_avg else 0,
        'top_course': course_avg[0] if course_avg else 'N/A',
        'top_course_avg': round(course_avg[1], 2) if course_avg else 0,
        'at_risk_count': at_risk_count
    }

def generate_report(report_type, department_id=None, course_id=None, term_id=None):
    """Generate report data based on parameters"""
    if report_type == 'grade_distribution':
        # Grade distribution report
        query = db.session.query(
            Grade.letter_grade,
            db.func.count(Grade.id).label('count')
        )
        
        if department_id:
            query = query.join(Student, Student.id == Grade.student_id)\
                         .filter(Student.department_id == department_id)
        if course_id:
            query = query.filter(Grade.course_id == course_id)
        if term_id:
            query = query.filter(Grade.term_id == term_id)
            
        results = query.group_by(Grade.letter_grade).all()
        df = pd.DataFrame(results, columns=['letter_grade', 'count'])
        
        return df
        
    elif report_type == 'department_performance':
        # Department performance report
        query = db.session.query(
            Department.name.label('department'),
            db.func.avg(Grade.numeric_grade).label('average_grade'),
            db.func.count(db.func.distinct(Student.id)).label('student_count')
        ).join(Student, Student.department_id == Department.id)\
         .join(Grade, Grade.student_id == Student.id)
         
        if term_id:
            query = query.filter(Grade.term_id == term_id)
            
        results = query.group_by(Department.name).all()
        df = pd.DataFrame(results, columns=['department', 'average_grade', 'student_count'])
        df['average_grade'] = df['average_grade'].round(2)
        
        return df
        
    elif report_type == 'course_comparison':
        # Course comparison report
        query = db.session.query(
            Course.code.label('course_code'),
            Course.name.label('course_name'),
            db.func.avg(Grade.numeric_grade).label('average_grade'),
            db.func.count(Grade.id).label('enrollment')
        ).join(Grade, Grade.course_id == Course.id)
        
        if department_id:
            query = query.filter(Course.department_id == department_id)
        if term_id:
            query = query.filter(Grade.term_id == term_id)
            
        results = query.group_by(Course.id).all()
        df = pd.DataFrame(results, columns=['course_code', 'course_name', 'average_grade', 'enrollment'])
        df['average_grade'] = df['average_grade'].round(2)
        
        return df
        
    elif report_type == 'term_trends':
        # Term trends report
        query = db.session.query(
            Term.name.label('term'),
            db.func.avg(Grade.numeric_grade).label('average_grade')
        ).join(Grade, Grade.term_id == Term.id)
        
        if department_id:
            query = query.join(Student, Student.id == Grade.student_id)\
                         .filter(Student.department_id == department_id)
        if course_id:
            query = query.filter(Grade.course_id == course_id)
            
        results = query.group_by(Term.name).order_by(Term.id).all()
        df = pd.DataFrame(results, columns=['term', 'average_grade'])
        df['average_grade'] = df['average_grade'].round(2)
        
        return df
        
    elif report_type == 'student_performance':
        # Student performance report
        query = db.session.query(
            Student.student_id,
            Student.first_name,
            Student.last_name,
            Department.name.label('department'),
            db.func.avg(Grade.numeric_grade).label('average_grade')
        ).join(Grade, Grade.student_id == Student.id)\
         .join(Department, Department.id == Student.department_id)
        
        if department_id:
            query = query.filter(Student.department_id == department_id)
        if course_id:
            query = query.filter(Grade.course_id == course_id)
        if term_id:
            query = query.filter(Grade.term_id == term_id)
            
        results = query.group_by(Student.id).all()
        df = pd.DataFrame(results, columns=[
            'student_id', 'first_name', 'last_name', 'department', 'average_grade'
        ])
        df['average_grade'] = df['average_grade'].round(2)
        df['full_name'] = df['first_name'] + ' ' + df['last_name']
        
        return df
        
    elif report_type == 'at_risk_students':
        # At-risk students report (below 70 average)
        query = db.session.query(
            Student.student_id,
            Student.first_name,
            Student.last_name,
            Department.name.label('department'),
            db.func.avg(Grade.numeric_grade).label('average_grade')
        ).join(Grade, Grade.student_id == Student.id)\
         .join(Department, Department.id == Student.department_id)
        
        if department_id:
            query = query.filter(Student.department_id == department_id)
        if term_id:
            query = query.filter(Grade.term_id == term_id)
            
        # Having clause for students with average below 70
        query = query.group_by(Student.id).having(db.func.avg(Grade.numeric_grade) < 70)
        
        results = query.all()
        df = pd.DataFrame(results, columns=[
            'student_id', 'first_name', 'last_name', 'department', 'average_grade'
        ])
        df['average_grade'] = df['average_grade'].round(2)
        df['full_name'] = df['first_name'] + ' ' + df['last_name']
        
        return df
        
    return None

def get_performance_trend(course_id=None, department_id=None):
    """Get performance trend data for visualization"""
    query = db.session.query(
        Term.name.label('term'),
        db.func.avg(Grade.numeric_grade).label('average_grade')
    ).join(Grade, Grade.term_id == Term.id)
    
    if course_id:
        query = query.filter(Grade.course_id == course_id)
    if department_id:
        query = query.join(Student, Student.id == Grade.student_id)\
                     .filter(Student.department_id == department_id)
                     
    results = query.group_by(Term.name).order_by(Term.id).all()
    
    terms = [result[0] for result in results]
    averages = [result[1] for result in results]
    
    return {
        'terms': terms,
        'averages': averages
    }