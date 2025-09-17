"""
Simplified Data Generation Script for Testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set seeds for reproducibility
np.random.seed(42)
random.seed(42)

def create_directories():
    """Create necessary directories if they don't exist"""
    domains = ['banking', 'hospital', 'marketing']
    for domain in domains:
        data_dir = f'data/{domain}'
        os.makedirs(data_dir, exist_ok=True)

def generate_dates(start_days_ago, end_days_ago, n):
    """Generate random dates between start and end days ago"""
    start_date = datetime.now() - timedelta(days=start_days_ago)
    end_date = datetime.now() - timedelta(days=end_days_ago)
    
    dates = []
    for _ in range(n):
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        random_date = start_date + timedelta(days=random_days)
        dates.append(random_date.date())
    
    return dates

def generate_banking_data():
    print("Generating Banking domain data...")
    
    # Customers
    n_customers = 500
    names = [f"Customer_{i}" for i in range(1, n_customers + 1)]
    customers_df = pd.DataFrame({
        'customer_id': [f'CUST_{i:06d}' for i in range(1, n_customers + 1)],
        'name': names,
        'age': np.random.randint(18, 80, n_customers),
        'city': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'], n_customers),
        'join_date': generate_dates(1800, 30, n_customers),
        'income_level': np.random.choice(['Low', 'Medium', 'High'], n_customers, p=[0.3, 0.5, 0.2]),
        'employment_status': np.random.choice(['Employed', 'Unemployed', 'Retired', 'Student'], n_customers, p=[0.65, 0.1, 0.15, 0.1])
    })
    
    # Accounts
    accounts_data = []
    account_id = 1
    for _, customer in customers_df.iterrows():
        n_accounts = np.random.choice([1, 2], p=[0.7, 0.3])
        for _ in range(n_accounts):
            accounts_data.append({
                'account_id': f'ACC_{account_id:08d}',
                'customer_id': customer['customer_id'],
                'account_type': np.random.choice(['Savings', 'Checking'], p=[0.6, 0.4]),
                'balance': round(np.random.exponential(3000), 2),
                'open_date': customer['join_date'],
                'churned': np.random.choice([True, False], p=[0.15, 0.85]),
                'status': np.random.choice(['Active', 'Inactive'], p=[0.85, 0.15])
            })
            account_id += 1
    
    accounts_df = pd.DataFrame(accounts_data)
    
    # Transactions
    transactions_data = []
    transaction_id = 1
    merchants = ['Amazon', 'Walmart', 'Starbucks', 'Shell']
    
    for _, account in accounts_df.iterrows():
        if account['status'] == 'Active':
            n_transactions = np.random.randint(5, 21)
            for _ in range(n_transactions):
                transactions_data.append({
                    'transaction_id': f'TXN_{transaction_id:010d}',
                    'account_id': account['account_id'],
                    'amount': round(np.random.uniform(-200, 100), 2),
                    'transaction_date': random.choice(generate_dates(90, 1, 1)),
                    'transaction_type': np.random.choice(['Deposit', 'Withdrawal', 'Payment']),
                    'merchant': np.random.choice(merchants + [None])
                })
                transaction_id += 1
    
    transactions_df = pd.DataFrame(transactions_data)
    
    # Loans
    loans_data = []
    loan_customers = customers_df.sample(n=int(n_customers * 0.3))
    loan_id = 1
    
    for _, customer in loan_customers.iterrows():
        loans_data.append({
            'loan_id': f'LOAN_{loan_id:06d}',
            'customer_id': customer['customer_id'],
            'loan_amount': round(np.random.uniform(5000, 50000), 2),
            'interest_rate': round(np.random.uniform(3.5, 12.0), 2),
            'loan_term': np.random.choice([12, 24, 36, 48, 60]),
            'defaulted': np.random.choice([True, False], p=[0.08, 0.92]),
            'loan_status': np.random.choice(['Active', 'Paid', 'Default'], p=[0.7, 0.22, 0.08])
        })
        loan_id += 1
    
    loans_df = pd.DataFrame(loans_data)
    
    # Save files
    customers_df.to_csv('data/banking/customers.csv', index=False)
    accounts_df.to_csv('data/banking/accounts.csv', index=False)
    transactions_df.to_csv('data/banking/transactions.csv', index=False)
    loans_df.to_csv('data/banking/loans.csv', index=False)
    
    print(f"Banking: {len(customers_df)} customers, {len(accounts_df)} accounts, {len(transactions_df)} transactions, {len(loans_df)} loans")

def generate_hospital_data():
    print("Generating Hospital domain data...")
    
    # Physicians
    n_physicians = 25
    physicians_df = pd.DataFrame({
        'physician_id': [f'PHYS_{i:04d}' for i in range(1, n_physicians + 1)],
        'name': [f'Dr. Smith_{i}' for i in range(1, n_physicians + 1)],
        'specialty': np.random.choice(['Cardiology', 'Emergency', 'Surgery'], n_physicians),
        'years_experience': np.random.randint(1, 25, n_physicians),
        'department': np.random.choice(['Cardiology', 'Emergency', 'Surgery'], n_physicians)
    })
    
    # Patients
    n_patients = 300
    patients_df = pd.DataFrame({
        'patient_id': [f'PAT_{i:06d}' for i in range(1, n_patients + 1)],
        'name': [f'Patient_{i}' for i in range(1, n_patients + 1)],
        'age': np.random.randint(0, 90, n_patients),
        'gender': np.random.choice(['Male', 'Female'], n_patients),
        'blood_type': np.random.choice(['A+', 'B+', 'O+', 'AB+'], n_patients),
        'insurance_type': np.random.choice(['Private', 'Medicare', 'Medicaid'], n_patients)
    })
    
    # Admissions
    admissions_data = []
    admission_id = 1
    diagnoses = ['Heart Disease', 'Pneumonia', 'Diabetes', 'Fracture']
    
    for _, patient in patients_df.sample(n=200).iterrows():  # 200 admissions
        physician = physicians_df.sample(1).iloc[0]
        admission_date = random.choice(generate_dates(365, 1, 1))
        length_of_stay = np.random.randint(1, 10)
        discharge_date = admission_date + timedelta(days=length_of_stay)
        
        admissions_data.append({
            'admission_id': f'ADM_{admission_id:08d}',
            'patient_id': patient['patient_id'],
            'physician_id': physician['physician_id'],
            'admission_date': admission_date,
            'discharge_date': discharge_date,
            'diagnosis': np.random.choice(diagnoses),
            'readmitted': np.random.choice([True, False], p=[0.12, 0.88]),
            'length_of_stay': length_of_stay
        })
        admission_id += 1
    
    admissions_df = pd.DataFrame(admissions_data)
    
    # Treatments
    treatments_data = []
    treatment_id = 1
    treatment_names = ['Surgery', 'Medication', 'X-Ray', 'Blood Test']
    
    for _, admission in admissions_df.iterrows():
        n_treatments = np.random.randint(1, 4)
        for _ in range(n_treatments):
            treatments_data.append({
                'treatment_id': f'TREAT_{treatment_id:08d}',
                'admission_id': admission['admission_id'],
                'treatment_name': np.random.choice(treatment_names),
                'cost': round(np.random.uniform(100, 5000), 2),
                'treatment_date': admission['admission_date'],
                'outcome': np.random.choice(['Successful', 'Partial', 'Failed'], p=[0.8, 0.15, 0.05])
            })
            treatment_id += 1
    
    treatments_df = pd.DataFrame(treatments_data)
    
    # Save files
    physicians_df.to_csv('data/hospital/physicians.csv', index=False)
    patients_df.to_csv('data/hospital/patients.csv', index=False)
    admissions_df.to_csv('data/hospital/admissions.csv', index=False)
    treatments_df.to_csv('data/hospital/treatments.csv', index=False)
    
    print(f"Hospital: {len(physicians_df)} physicians, {len(patients_df)} patients, {len(admissions_df)} admissions, {len(treatments_df)} treatments")

def generate_marketing_data():
    print("Generating Marketing domain data...")
    
    # Campaigns
    n_campaigns = 10
    campaigns_df = pd.DataFrame({
        'campaign_id': [f'CAMP_{i:04d}' for i in range(1, n_campaigns + 1)],
        'campaign_name': [f'Campaign_{i}' for i in range(1, n_campaigns + 1)],
        'start_date': generate_dates(180, 30, n_campaigns),
        'end_date': generate_dates(90, 1, n_campaigns),
        'budget': np.random.uniform(5000, 30000, n_campaigns).round(2),
        'campaign_type': np.random.choice(['Email', 'Social', 'Search'], n_campaigns),
        'target_audience': np.random.choice(['Young Adults', 'Professionals'], n_campaigns)
    })
    
    # Ad Spend
    ad_spend_data = []
    spend_id = 1
    channels = ['Google', 'Facebook', 'Instagram']
    
    for _, campaign in campaigns_df.iterrows():
        n_records = 5  # 5 ad spend records per campaign
        for _ in range(n_records):
            ad_spend_data.append({
                'spend_id': f'SPEND_{spend_id:08d}',
                'campaign_id': campaign['campaign_id'],
                'date': random.choice(generate_dates(90, 1, 1)),
                'channel': np.random.choice(channels),
                'spend_amount': round(np.random.uniform(100, 1000), 2),
                'impressions': np.random.randint(1000, 10000),
                'clicks': np.random.randint(50, 500)
            })
            spend_id += 1
    
    ad_spend_df = pd.DataFrame(ad_spend_data)
    
    # Web Analytics
    web_analytics_data = []
    session_id = 1
    
    for _, campaign in campaigns_df.iterrows():
        n_sessions = 20  # 20 sessions per campaign
        for _ in range(n_sessions):
            web_analytics_data.append({
                'session_id': f'SESS_{session_id:010d}',
                'campaign_id': campaign['campaign_id'],
                'visit_date': random.choice(generate_dates(90, 1, 1)),
                'pages_viewed': np.random.randint(1, 10),
                'time_on_site_seconds': np.random.randint(30, 600),
                'bounce_rate': round(np.random.uniform(0.2, 0.8), 2),
                'device_type': np.random.choice(['Desktop', 'Mobile', 'Tablet'])
            })
            session_id += 1
    
    web_analytics_df = pd.DataFrame(web_analytics_data)
    
    # Leads
    leads_data = []
    lead_id = 1
    
    for _, campaign in campaigns_df.iterrows():
        n_leads = 15  # 15 leads per campaign
        for _ in range(n_leads):
            converted = np.random.choice([True, False], p=[0.15, 0.85])
            leads_data.append({
                'lead_id': f'LEAD_{lead_id:08d}',
                'campaign_id': campaign['campaign_id'],
                'lead_date': random.choice(generate_dates(90, 1, 1)),
                'converted': converted,
                'conversion_value': round(np.random.uniform(100, 1000), 2) if converted else 0,
                'lead_source': np.random.choice(['Paid Search', 'Social', 'Email']),
                'lead_score': np.random.randint(1, 101)
            })
            lead_id += 1
    
    leads_df = pd.DataFrame(leads_data)
    
    # Save files
    campaigns_df.to_csv('data/marketing/campaigns.csv', index=False)
    ad_spend_df.to_csv('data/marketing/ad_spend.csv', index=False)
    web_analytics_df.to_csv('data/marketing/web_analytics.csv', index=False)
    leads_df.to_csv('data/marketing/leads.csv', index=False)
    
    print(f"Marketing: {len(campaigns_df)} campaigns, {len(ad_spend_df)} ad spend, {len(web_analytics_df)} sessions, {len(leads_df)} leads")

if __name__ == "__main__":
    print("Starting simplified data generation...")
    
    create_directories()
    generate_banking_data()
    generate_hospital_data()
    generate_marketing_data()
    
    print("\nData generation complete! ✅")
    print("Next steps:")
    print("1. Ensure Docker is running")
    print("2. Build Docker image: docker build -t ai_analytics_sandbox .")
    print("3. Set OpenAI API key in .env file")
    print("4. Run: streamlit run app.py")
