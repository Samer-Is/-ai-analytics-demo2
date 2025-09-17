import pandas as pd
import matplotlib.pyplot as plt
import os

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

# Load banking data
print("📊 Banking Customer Churn Analysis")
print("=" * 50)

# Load accounts data
accounts = pd.read_csv('data/banking/accounts.csv')
customers = pd.read_csv('data/banking/customers.csv')

print(f"Total accounts: {len(accounts)}")
print(f"Unique customers: {accounts['customer_id'].nunique()}")

# Analyze churn at account level
churned_accounts = accounts[accounts['churned'] == True]
not_churned_accounts = accounts[accounts['churned'] == False]

churn_rate_accounts = (len(churned_accounts) / len(accounts)) * 100

print(f"\n📈 Account-Level Churn Analysis:")
print(f"Churned accounts: {len(churned_accounts)}")
print(f"Active accounts: {len(not_churned_accounts)}")
print(f"Account churn rate: {churn_rate_accounts:.1f}%")

# Analyze churn at customer level (more meaningful)
# Group by customer and check if ANY of their accounts are churned
customer_churn = accounts.groupby('customer_id')['churned'].any().reset_index()
churned_customers = customer_churn[customer_churn['churned'] == True]
total_customers = len(customer_churn)
churn_rate_customers = (len(churned_customers) / total_customers) * 100

print(f"\n👥 Customer-Level Churn Analysis:")
print(f"Total customers: {total_customers}")
print(f"Churned customers: {len(churned_customers)}")
print(f"Customer churn rate: {churn_rate_customers:.1f}%")

# Analyze churn by account type
churn_by_type = accounts.groupby('account_type').agg({
    'churned': ['count', 'sum']
}).round(2)
churn_by_type.columns = ['Total_Accounts', 'Churned_Accounts']
churn_by_type['Churn_Rate_%'] = (churn_by_type['Churned_Accounts'] / churn_by_type['Total_Accounts'] * 100).round(1)

print(f"\n🏦 Churn Rate by Account Type:")
print(churn_by_type)

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Customer churn pie chart
labels = ['Active Customers', 'Churned Customers']
sizes = [total_customers - len(churned_customers), len(churned_customers)]
colors = ['#2E8B57', '#DC143C']
ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
ax1.set_title('Customer Churn Rate')

# Churn by account type bar chart
churn_by_type['Churn_Rate_%'].plot(kind='bar', ax=ax2, color=['#4682B4', '#32CD32', '#FFD700'])
ax2.set_title('Churn Rate by Account Type')
ax2.set_ylabel('Churn Rate (%)')
ax2.set_xlabel('Account Type')
ax2.tick_params(axis='x', rotation=0)

plt.tight_layout()
plt.savefig('output/churn_analysis.png', dpi=300, bbox_inches='tight')
print(f"\n💾 Chart saved to: output/churn_analysis.png")

# Business insights
print(f"\n🎯 Key Business Insights:")
print(f"• Customer churn rate is {churn_rate_customers:.1f}%, which means {len(churned_customers)} out of {total_customers} customers have churned")
print(f"• Account churn rate is {churn_rate_accounts:.1f}%, affecting {len(churned_accounts)} accounts")

if churn_rate_customers > 15:
    print(f"⚠️  High churn rate alert: {churn_rate_customers:.1f}% exceeds industry benchmark of ~15%")
    print("📋 Recommended actions:")
    print("   - Conduct customer satisfaction surveys")
    print("   - Review pricing and service offerings")
    print("   - Implement customer retention programs")
    print("   - Analyze competitor strategies")
elif churn_rate_customers > 10:
    print(f"⚡ Moderate churn rate: {churn_rate_customers:.1f}% is within acceptable range but monitor closely")
else:
    print(f"✅ Low churn rate: {churn_rate_customers:.1f}% indicates good customer retention")

# Account type analysis
highest_churn_type = churn_by_type['Churn_Rate_%'].idxmax()
highest_churn_rate = churn_by_type['Churn_Rate_%'].max()
print(f"• Highest churn is in {highest_churn_type} accounts ({highest_churn_rate}%)")
print(f"• Focus retention efforts on {highest_churn_type} account holders")
