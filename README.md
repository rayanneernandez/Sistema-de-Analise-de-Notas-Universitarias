# University Grade Analysis System

A comprehensive Python web application designed to help universities track, analyze, and visualize student academic performance.

## Features

- **Data Management**:
  - Import grade data from CSV/Excel files
  - Track students, courses, departments, and terms
  - Secure data handling with proper authentication

- **Analytics**:
  - Interactive grade distribution visualizations
  - Department performance comparisons
  - Course performance trends over time
  - Student performance tracking with early warning indicators

- **Reporting**:
  - Customizable reports by course, department, or term
  - Export capabilities for reports and visualizations
  - Identify at-risk students

- **Security**:
  - Role-based access control
  - Secure authentication
  - Data privacy protection

## Technology Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite (can be upgraded to PostgreSQL)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn, Chart.js
- **Frontend**: Bootstrap 5, JavaScript

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```

## Initial Setup

The system creates a default admin user with the following credentials:
- **Email**: admin@university.edu
- **Password**: adminpass

Use these credentials to log in for the first time and then you can add additional users.

## Data Import Format

To import grade data, prepare a CSV or Excel file with the following columns:
- student_id (required)
- first_name (required)
- last_name (required)
- email (optional)
- department (required)
- course_code (required)
- course_name (optional)
- credits (optional)
- grade (required) - numeric value

## Reports

The system offers the following report types:
- Grade Distribution
- Department Performance
- Course Comparison
- Term Trends
- Student Performance
- At-Risk Students

## Development

This project uses Flask's development server for testing purposes. For production deployment, consider using a production-ready WSGI server like Gunicorn.

## License

MIT License