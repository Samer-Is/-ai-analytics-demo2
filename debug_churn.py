import pandas as pd

# Load the data
accounts = pd.read_csv('data/banking/accounts.csv')

print("🔍 Debugging Churn Rate Calculation")
print("=" * 50)

# Check the accounts data structure
print("Accounts data info:")
print(f"Total accounts: {len(accounts)}")
print(f"Columns: {list(accounts.columns)}")
print()

# Check the 'churned' column specifically
print("Churned column analysis:")
print(f"Data type: {accounts['churned'].dtype}")
print(f"Unique values: {accounts['churned'].unique()}")
print(f"Value counts:")
print(accounts['churned'].value_counts())
print()

# Calculate churn rate step by step
total_accounts = len(accounts)
churned_accounts = accounts[accounts['churned'] == True]
num_churned = len(churned_accounts)

churn_rate = (num_churned / total_accounts) * 100

print("Churn Rate Calculation:")
print(f"Total accounts: {total_accounts}")
print(f"Churned accounts: {num_churned}")
print(f"Churn rate: {churn_rate:.2f}%")

# Customer-level churn rate
unique_customers = accounts['customer_id'].nunique()
customer_churn = accounts.groupby('customer_id')['churned'].any()
churned_customers = customer_churn.sum()
customer_churn_rate = (churned_customers / unique_customers) * 100

print(f"\nCustomer-level analysis:")
print(f"Total customers: {unique_customers}")
print(f"Customers with churned accounts: {churned_customers}")
print(f"Customer churn rate: {customer_churn_rate:.2f}%")

print("\n✅ Churn calculation completed successfully!")
