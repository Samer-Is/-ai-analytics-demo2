"""
Comprehensive Data Generation Script for Multi-Domain Analytics Tool
Generates realistic, interconnected datasets for Banking, Hospital, and Education domains.
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os
import json

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

def create_directories():
    """Create necessary directories if they don't exist"""
    domains = ['banking', 'hospital', 'education']
    for domain in domains:
        data_dir = f'data/{domain}'
        os.makedirs(data_dir, exist_ok=True)

def generate_banking_data():
    """Generate realistic banking domain data with proper relationships"""
    print("Generating Banking domain data...")
    
    # Generate customers
    n_customers = 1000
    customers_data = {
        'customer_id': [f'CUST_{i:06d}' for i in range(1, n_customers + 1)],
        'name': [fake.name() for _ in range(n_customers)],
        'age': np.random.randint(18, 80, n_customers),
        'city': [fake.city() for _ in range(n_customers)],
        'join_date': [fake.date_between(start_date='-5y', end_date='-1d') for _ in range(n_customers)],
        'income_level': np.random.choice(['Low', 'Medium', 'High'], n_customers, p=[0.3, 0.5, 0.2]),
        'employment_status': np.random.choice(['Employed', 'Unemployed', 'Retired', 'Student'], n_customers, p=[0.65, 0.1, 0.15, 0.1])
    }
    customers_df = pd.DataFrame(customers_data)
    
    # Generate accounts (1-3 accounts per customer)
    accounts_data = []
    account_id = 1
    for _, customer in customers_df.iterrows():
        n_accounts = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
        for _ in range(n_accounts):
            account_type = np.random.choice(['Savings', 'Checking', 'Investment'], p=[0.5, 0.4, 0.1])
            balance = np.random.exponential(5000) if account_type == 'Savings' else np.random.exponential(2000)
            open_date = customer['join_date'] + timedelta(days=np.random.randint(1, 180))
            churned = np.random.choice([True, False], p=[0.15, 0.85])
            status = 'Inactive' if churned else np.random.choice(['Active', 'Suspended'], p=[0.9, 0.1])
            
            accounts_data.append({
                'account_id': f'ACC_{account_id:08d}',
                'customer_id': customer['customer_id'],
                'account_type': account_type,
                'balance': round(balance, 2),
                'open_date': open_date,
                'churned': churned,
                'status': status
            })
            account_id += 1
    
    accounts_df = pd.DataFrame(accounts_data)
    
    # Generate transactions (5-50 per account)
    transactions_data = []
    transaction_id = 1
    merchants = ['Amazon', 'Walmart', 'Starbucks', 'Shell', 'Home Depot', 'Target', 'McDonalds', 'Costco']
    
    for _, account in accounts_df.iterrows():
        if account['status'] == 'Active':
            n_transactions = np.random.randint(5, 51)
            for _ in range(n_transactions):
                amount = np.random.choice(
                    [np.random.exponential(50), -np.random.exponential(75)], 
                    p=[0.3, 0.7]
                )
                transaction_type = 'Deposit' if amount > 0 else np.random.choice(['Withdrawal', 'Payment'], p=[0.3, 0.7])
                merchant = np.random.choice(merchants) if transaction_type == 'Payment' else None
                # Ensure transaction date is after account open date and before today
                end_date = datetime.now().date() - timedelta(days=1)
                if account['open_date'] >= end_date:
                    transaction_date = account['open_date'] + timedelta(days=1)
                else:
                    transaction_date = fake.date_between(start_date=account['open_date'], end_date=end_date)
                
                transactions_data.append({
                    'transaction_id': f'TXN_{transaction_id:010d}',
                    'account_id': account['account_id'],
                    'amount': round(amount, 2),
                    'transaction_date': transaction_date,
                    'transaction_type': transaction_type,
                    'merchant': merchant
                })
                transaction_id += 1
    
    transactions_df = pd.DataFrame(transactions_data)
    
    # Generate loans (20% of customers have loans)
    loans_data = []
    loan_customers = customers_df.sample(n=int(n_customers * 0.2))
    loan_id = 1
    
    for _, customer in loan_customers.iterrows():
        n_loans = np.random.choice([1, 2], p=[0.8, 0.2])
        for _ in range(n_loans):
            loan_amount = np.random.uniform(5000, 100000)
            interest_rate = np.random.uniform(3.5, 12.0)
            loan_term = np.random.choice([12, 24, 36, 48, 60])
            defaulted = np.random.choice([True, False], p=[0.08, 0.92])
            loan_status = 'Default' if defaulted else np.random.choice(['Active', 'Paid'], p=[0.7, 0.3])
            
            loans_data.append({
                'loan_id': f'LOAN_{loan_id:06d}',
                'customer_id': customer['customer_id'],
                'loan_amount': round(loan_amount, 2),
                'interest_rate': round(interest_rate, 2),
                'loan_term': loan_term,
                'defaulted': defaulted,
                'loan_status': loan_status
            })
            loan_id += 1
    
    loans_df = pd.DataFrame(loans_data)
    
    # Save to CSV
    customers_df.to_csv('data/banking/customers.csv', index=False)
    accounts_df.to_csv('data/banking/accounts.csv', index=False)
    transactions_df.to_csv('data/banking/transactions.csv', index=False)
    loans_df.to_csv('data/banking/loans.csv', index=False)
    
    print(f"Banking data generated: {len(customers_df)} customers, {len(accounts_df)} accounts, {len(transactions_df)} transactions, {len(loans_df)} loans")

def generate_hospital_data():
    """Generate realistic hospital domain data with proper relationships"""
    print("Generating Hospital domain data...")
    
    # Generate physicians
    n_physicians = 50
    specialties = ['Cardiology', 'Orthopedics', 'Emergency Medicine', 'Internal Medicine', 'Surgery']
    departments = ['Cardiology', 'Orthopedics', 'Emergency', 'Internal Medicine', 'Surgery', 'Radiology', 'Laboratory']
    
    physicians_data = {
        'physician_id': [f'PHYS_{i:04d}' for i in range(1, n_physicians + 1)],
        'name': [f'Dr. {fake.name()}' for _ in range(n_physicians)],
        'specialty': [np.random.choice(specialties) for _ in range(n_physicians)],
        'years_experience': np.random.randint(1, 35, n_physicians),
        'department': [np.random.choice(departments) for _ in range(n_physicians)]
    }
    physicians_df = pd.DataFrame(physicians_data)
    
    # Generate patients
    n_patients = 800
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    insurance_types = ['Private', 'Medicare', 'Medicaid', 'Uninsured']
    
    patients_data = {
        'patient_id': [f'PAT_{i:06d}' for i in range(1, n_patients + 1)],
        'name': [fake.name() for _ in range(n_patients)],
        'age': np.random.randint(0, 95, n_patients),
        'gender': np.random.choice(['Male', 'Female'], n_patients),
        'blood_type': np.random.choice(blood_types, n_patients, p=[0.35, 0.06, 0.12, 0.02, 0.04, 0.01, 0.38, 0.02]),
        'insurance_type': np.random.choice(insurance_types, n_patients, p=[0.55, 0.25, 0.15, 0.05])
    }
    patients_df = pd.DataFrame(patients_data)
    
    # Generate admissions
    admissions_data = []
    admission_id = 1
    diagnoses = ['Heart Disease', 'Pneumonia', 'Diabetes', 'Hypertension', 'Fracture', 'Appendicitis', 'Stroke', 'Cancer']
    
    # Each patient has 1-3 admissions
    for _, patient in patients_df.iterrows():
        n_admissions = np.random.choice([1, 2, 3], p=[0.7, 0.25, 0.05])
        for _ in range(n_admissions):
            physician = physicians_df.sample(1).iloc[0]
            admission_date = fake.date_between(start_date='-1y', end_date=datetime.now().date() - timedelta(days=7))
            length_of_stay = np.random.poisson(4) + 1  # Average 5 days
            discharge_date = admission_date + timedelta(days=length_of_stay)
            diagnosis = np.random.choice(diagnoses)
            readmitted = np.random.choice([True, False], p=[0.12, 0.88])  # 12% readmission rate
            
            admissions_data.append({
                'admission_id': f'ADM_{admission_id:08d}',
                'patient_id': patient['patient_id'],
                'physician_id': physician['physician_id'],
                'admission_date': admission_date,
                'discharge_date': discharge_date,
                'diagnosis': diagnosis,
                'readmitted': readmitted,
                'length_of_stay': length_of_stay
            })
            admission_id += 1
    
    admissions_df = pd.DataFrame(admissions_data)
    
    # Generate treatments
    treatments_data = []
    treatment_id = 1
    treatment_names = ['Surgery', 'Medication', 'Physical Therapy', 'X-Ray', 'Blood Test', 'MRI', 'CT Scan', 'Consultation']
    outcomes = ['Successful', 'Partial', 'Failed', 'Complications']
    
    for _, admission in admissions_df.iterrows():
        n_treatments = np.random.randint(1, 5)  # 1-4 treatments per admission
        for _ in range(n_treatments):
            treatment_name = np.random.choice(treatment_names)
            cost = np.random.exponential(1500) + 100  # Varying costs
            # Ensure treatment date is within admission period
            if admission['admission_date'] == admission['discharge_date']:
                treatment_date = admission['admission_date']
            else:
                treatment_date = fake.date_between(start_date=admission['admission_date'], end_date=admission['discharge_date'])
            outcome = np.random.choice(outcomes, p=[0.75, 0.15, 0.05, 0.05])
            
            treatments_data.append({
                'treatment_id': f'TREAT_{treatment_id:08d}',
                'admission_id': admission['admission_id'],
                'treatment_name': treatment_name,
                'cost': round(cost, 2),
                'treatment_date': treatment_date,
                'outcome': outcome
            })
            treatment_id += 1
    
    treatments_df = pd.DataFrame(treatments_data)
    
    # Save to CSV
    physicians_df.to_csv('data/hospital/physicians.csv', index=False)
    patients_df.to_csv('data/hospital/patients.csv', index=False)
    admissions_df.to_csv('data/hospital/admissions.csv', index=False)
    treatments_df.to_csv('data/hospital/treatments.csv', index=False)
    
    print(f"Hospital data generated: {len(physicians_df)} physicians, {len(patients_df)} patients, {len(admissions_df)} admissions, {len(treatments_df)} treatments")

def generate_education_data():
    """Generate realistic university education domain data with proper relationships"""
    print("Generating Education domain data...")
    
    # Generate professors/faculty
    n_professors = 80
    departments = ['Computer Science', 'Engineering', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Business', 'Literature', 'History', 'Psychology']
    academic_ranks = ['Assistant Professor', 'Associate Professor', 'Professor', 'Lecturer', 'Adjunct Professor']
    
    professors_data = {
        'professor_id': [f'PROF_{i:04d}' for i in range(1, n_professors + 1)],
        'name': [f'Prof. {fake.name()}' for _ in range(n_professors)],
        'department': [np.random.choice(departments) for _ in range(n_professors)],
        'academic_rank': [np.random.choice(academic_ranks, p=[0.3, 0.25, 0.2, 0.15, 0.1]) for _ in range(n_professors)],
        'years_experience': np.random.randint(1, 30, n_professors),
        'research_grants': [round(np.random.exponential(50000), 2) for _ in range(n_professors)],
        'publications_count': np.random.poisson(15, n_professors),
        'student_rating': [max(1, min(5, round(np.random.normal(4.2, 0.8), 1))) for _ in range(n_professors)]
    }
    professors_df = pd.DataFrame(professors_data)
    
    # Generate students
    n_students = 2500
    degree_programs = ['Bachelor', 'Master', 'PhD']
    enrollment_status = ['Full-time', 'Part-time', 'Exchange']
    majors = departments + ['Undeclared']
    
    students_data = {
        'student_id': [f'STU_{i:06d}' for i in range(1, n_students + 1)],
        'name': [fake.name() for _ in range(n_students)],
        'age': np.random.randint(17, 45, n_students),
        'gender': np.random.choice(['Male', 'Female', 'Other'], n_students, p=[0.48, 0.49, 0.03]),
        'degree_program': np.random.choice(degree_programs, n_students, p=[0.7, 0.25, 0.05]),
        'major': [np.random.choice(majors) for _ in range(n_students)],
        'enrollment_status': np.random.choice(enrollment_status, n_students, p=[0.85, 0.12, 0.03]),
        'enrollment_year': np.random.randint(2020, 2026, n_students),
        'gpa': [max(0, min(4, np.random.normal(3.2, 0.6))) for _ in range(n_students)],
        'tuition_paid': [round(np.random.uniform(8000, 45000), 2) for _ in range(n_students)],
        'scholarship_amount': [round(np.random.exponential(3000), 2) if np.random.random() < 0.3 else 0 for _ in range(n_students)]
    }
    students_df = pd.DataFrame(students_data)
    
    # Generate courses
    courses_data = []
    course_id = 1
    course_names = [
        'Introduction to Programming', 'Data Structures', 'Database Systems', 'Machine Learning',
        'Calculus I', 'Calculus II', 'Linear Algebra', 'Statistics',
        'Physics I', 'Physics II', 'Quantum Mechanics',
        'Organic Chemistry', 'Biochemistry', 'Molecular Biology',
        'Financial Accounting', 'Marketing Principles', 'Operations Management',
        'World Literature', 'Creative Writing', 'Linguistics',
        'World History', 'Political Science', 'International Relations',
        'Cognitive Psychology', 'Social Psychology', 'Research Methods'
    ]
    
    for dept in departments:
        # Each department offers 8-15 courses
        n_courses = np.random.randint(8, 16)
        dept_courses = np.random.choice(course_names, n_courses, replace=False)
        
        for course_name in dept_courses:
            professor = professors_df[professors_df['department'] == dept].sample(1).iloc[0]
            credit_hours = np.random.choice([3, 4], p=[0.7, 0.3])
            enrollment_capacity = np.random.randint(25, 150)
            current_enrollment = np.random.randint(15, enrollment_capacity)
            
            courses_data.append({
                'course_id': f'COURSE_{course_id:06d}',
                'course_name': course_name,
                'department': dept,
                'professor_id': professor['professor_id'],
                'credit_hours': credit_hours,
                'enrollment_capacity': enrollment_capacity,
                'current_enrollment': current_enrollment,
                'semester': np.random.choice(['Fall 2024', 'Spring 2025', 'Summer 2025']),
                'room_cost': round(np.random.uniform(500, 2000), 2),  # Room/facility cost per semester
                'lab_required': np.random.choice([True, False], p=[0.4, 0.6])
            })
            course_id += 1
    
    courses_df = pd.DataFrame(courses_data)
    
    # Generate enrollments (student-course relationships with grades)
    enrollments_data = []
    enrollment_id = 1
    
    for _, student in students_df.iterrows():
        # Each student enrolled in 3-7 courses
        n_enrollments = np.random.randint(3, 8)
        student_courses = courses_df.sample(n_enrollments)
        
        for _, course in student_courses.iterrows():
            # Grade distribution based on professor rating and student GPA
            professor = professors_df[professors_df['professor_id'] == course['professor_id']].iloc[0]
            base_grade = student['gpa'] + (professor['student_rating'] - 3.0) * 0.2
            final_grade = max(0, min(4, np.random.normal(base_grade, 0.3)))
            
            letter_grade = 'F'
            if final_grade >= 3.7: letter_grade = 'A'
            elif final_grade >= 3.3: letter_grade = 'A-'
            elif final_grade >= 3.0: letter_grade = 'B+'
            elif final_grade >= 2.7: letter_grade = 'B'
            elif final_grade >= 2.3: letter_grade = 'B-'
            elif final_grade >= 2.0: letter_grade = 'C+'
            elif final_grade >= 1.7: letter_grade = 'C'
            elif final_grade >= 1.3: letter_grade = 'C-'
            elif final_grade >= 1.0: letter_grade = 'D'
            
            enrollments_data.append({
                'enrollment_id': f'ENROLL_{enrollment_id:08d}',
                'student_id': student['student_id'],
                'course_id': course['course_id'],
                'semester': course['semester'],
                'final_grade': round(final_grade, 2),
                'letter_grade': letter_grade,
                'attendance_rate': round(max(0, min(1, np.random.normal(0.85, 0.15))), 2),
                'assignment_scores': round(max(0, min(1, np.random.normal(0.82, 0.18))), 2),
                'midterm_score': round(max(0, min(1, np.random.normal(0.78, 0.2))), 2),
                'final_exam_score': round(max(0, min(1, np.random.normal(0.80, 0.19))), 2)
            })
            enrollment_id += 1
    
    enrollments_df = pd.DataFrame(enrollments_data)
    
    # Save to CSV
    professors_df.to_csv('data/education/professors.csv', index=False)
    students_df.to_csv('data/education/students.csv', index=False)
    courses_df.to_csv('data/education/courses.csv', index=False)
    enrollments_df.to_csv('data/education/enrollments.csv', index=False)
    
    print(f"Education data generated: {len(professors_df)} professors, {len(students_df)} students, {len(courses_df)} courses, {len(enrollments_df)} enrollments")

def print_summary():
    """Print summary of generated data"""
    print("\\n" + "="*60)
    print("DATA GENERATION COMPLETE")
    print("="*60)
    
    domains = ['banking', 'hospital', 'education']
    for domain in domains:
        print(f"\\n{domain.upper()} Domain:")
        data_path = f'data/{domain}'
        if os.path.exists(data_path):
            for filename in os.listdir(data_path):
                if filename.endswith('.csv'):
                    df = pd.read_csv(os.path.join(data_path, filename))
                    print(f"  {filename}: {len(df):,} records")
        else:
            print(f"  Directory not found: {data_path}")
    
    print("\\n" + "="*60)
    print("Next steps:")
    print("1. Verify data quality and relationships")
    print("2. Run: python app.py")
    print("3. Test with sample questions from each domain")
    print("="*60)

if __name__ == "__main__":
    print("Starting comprehensive data generation for Multi-Domain Analytics Tool...")
    print("This may take a few minutes to generate realistic, interconnected datasets.\\n")
    
    create_directories()
    generate_banking_data()
    generate_hospital_data() 
    generate_education_data()
    print_summary()
