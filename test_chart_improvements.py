"""
Test improved chart generation with age bracketing and size optimization
"""

import backend
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

print("TESTING IMPROVED CHART GENERATION")
print("=" * 50)

# Test age bracketing function
def create_age_brackets(age_series):
    """Create age brackets for better chart readability"""
    age_brackets = []
    for age in age_series:
        if age < 18:
            age_brackets.append("Under 18")
        elif age < 26:
            age_brackets.append("18-25")
        elif age < 36:
            age_brackets.append("26-35")
        elif age < 46:
            age_brackets.append("36-45")
        elif age < 56:
            age_brackets.append("46-55")
        elif age < 66:
            age_brackets.append("56-65")
        else:
            age_brackets.append("65+")
    return age_brackets

# Load banking data to test
try:
    customers = pd.read_csv('data/banking/customers.csv')
    print(f"✅ Loaded {len(customers)} customers")
    
    # Test 1: Age Distribution with Brackets
    print("\n📊 Test 1: Age Distribution with Brackets")
    
    # Create age brackets
    customers['age_bracket'] = create_age_brackets(customers['age'])
    age_distribution = customers['age_bracket'].value_counts()
    
    # Create optimized chart
    plt.figure(figsize=(10, 6))  # Smaller size
    age_distribution.plot(kind='bar', color='skyblue')
    plt.title('Customer Distribution by Age Bracket', fontsize=14)
    plt.xlabel('Age Bracket', fontsize=12)
    plt.ylabel('Number of Customers', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    plt.savefig('output/age_distribution_test.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    print("✅ Age bracket chart created")
    print("Age distribution:")
    for bracket, count in age_distribution.items():
        print(f"  {bracket}: {count} customers ({count/len(customers)*100:.1f}%)")
    
    # Test 2: Top 10 Cities (if there are many cities)
    print("\n📊 Test 2: Top 10 Cities Distribution")
    
    city_distribution = customers['city'].value_counts().head(10)  # Top 10 only
    
    plt.figure(figsize=(10, 6))
    city_distribution.plot(kind='bar', color='lightcoral')
    plt.title('Top 10 Cities by Customer Count', fontsize=14)
    plt.xlabel('City', fontsize=12)
    plt.ylabel('Number of Customers', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('output/top_cities_test.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    print("✅ Top 10 cities chart created")
    print("Top cities:")
    for city, count in city_distribution.head(5).items():
        print(f"  {city}: {count} customers")
    
    print(f"\n📁 Charts saved to 'output/' directory")
    print("   - age_distribution_test.png")
    print("   - top_cities_test.png")
    
except Exception as e:
    print(f"❌ Error during test: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Chart optimization test complete!")
print("Charts should now be:")
print("• Smaller size (10x6 instead of 12x8)")
print("• Age data grouped into brackets")
print("• Categorical data limited to top 10")
print("• Better formatted with rotated labels")
