import pandas as pd
import os

# Load banking data
data_path = "data/banking"
customers_df = pd.read_csv(f"{data_path}/customers.csv")

# Calculate average customer age
average_age = customers_df['age'].mean()

print(f"📊 Customer Age Analysis")
print(f"=" * 40)
print(f"Total customers: {len(customers_df)}")
print(f"Average customer age: {average_age:.1f} years")
print(f"Youngest customer: {customers_df['age'].min()} years")
print(f"Oldest customer: {customers_df['age'].max()} years")

# Age distribution
print(f"\n📈 Age Distribution:")
age_groups = pd.cut(customers_df['age'], bins=[0, 30, 40, 50, 60, 100], labels=['18-30', '31-40', '41-50', '51-60', '60+'])
age_distribution = age_groups.value_counts().sort_index()

for group, count in age_distribution.items():
    percentage = (count / len(customers_df)) * 100
    print(f"{group}: {count} customers ({percentage:.1f}%)")
