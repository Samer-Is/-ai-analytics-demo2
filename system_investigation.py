"""
Comprehensive System Investigation for Demo Readiness
Test all critical system components against demo requirements
"""

import json
import os
import pandas as pd
from pathlib import Path
import backend

print("=" * 80)
print("AI DATA ANALYST TOOL - COMPREHENSIVE SYSTEM INVESTIGATION")
print("=" * 80)

# Test 1: Environment Validation
print("\n1. ENVIRONMENT VALIDATION:")
env_checks = backend.validate_environment()
for check, status in env_checks.items():
    status_symbol = "✅" if status else "❌"
    print(f"   {status_symbol} {check}: {status}")

if not all(env_checks.values()):
    print("   ⚠️  Some environment checks failed!")

# Test 2: Schema Loading and Consistency
print("\n2. SCHEMA VALIDATION:")
domains = ['banking', 'hospital', 'marketing']
schema_issues = []

for domain in domains:
    try:
        loader = backend.DomainDataLoader(domain)
        schema = loader.schema_data
        print(f"   ✅ {domain}: {len(schema['tables'])} tables loaded")
        
        # Check for required fields
        required_fields = ['domain_name', 'domain_description', 'tables']
        for field in required_fields:
            if field not in schema:
                schema_issues.append(f"{domain}: Missing {field}")
        
        # Check table structure
        for table in schema['tables']:
            if 'name' not in table or 'columns' not in table:
                schema_issues.append(f"{domain}.{table.get('name', 'unknown')}: Missing name or columns")
                
    except Exception as e:
        print(f"   ❌ {domain}: {str(e)}")
        schema_issues.append(f"{domain}: {str(e)}")

if schema_issues:
    print(f"   ⚠️  Schema Issues Found: {len(schema_issues)}")
    for issue in schema_issues:
        print(f"      - {issue}")

# Test 3: Data Loading Verification
print("\n3. DATA LOADING VERIFICATION:")
data_issues = []

for domain in domains:
    try:
        loader = backend.DomainDataLoader(domain)
        dataframes = loader.dataframes
        
        print(f"   ✅ {domain}: {len(dataframes)} dataframes loaded")
        
        # Check data sizes
        for table_name, df in dataframes.items():
            if df.empty:
                data_issues.append(f"{domain}.{table_name}: Empty dataframe")
            elif len(df) < 10:
                data_issues.append(f"{domain}.{table_name}: Very small dataset ({len(df)} rows)")
            else:
                print(f"      - {table_name}: {len(df)} rows, {len(df.columns)} columns")
                
    except Exception as e:
        print(f"   ❌ {domain}: {str(e)}")
        data_issues.append(f"{domain}: {str(e)}")

if data_issues:
    print(f"   ⚠️  Data Issues Found: {len(data_issues)}")
    for issue in data_issues:
        print(f"      - {issue}")

# Test 4: Code Execution System
print("\n4. CODE EXECUTION SYSTEM:")
try:
    executor = backend.LocalCodeExecutor()
    
    # Test simple code execution
    test_code = """
import pandas as pd
print("Test execution successful")
print(f"Pandas version: {pd.__version__}")
"""
    
    result = executor.execute_code(test_code)
    
    if result['success']:
        print("   ✅ Local code execution working")
        print(f"   Output: {result['output'].strip()}")
    else:
        print(f"   ❌ Code execution failed: {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"   ❌ Code executor initialization failed: {str(e)}")

# Test 5: API Connection Test
print("\n5. API CONNECTION TEST:")
try:
    # Test basic API connectivity
    processor = backend.LLMWorkflow()
    
    # Simple test message
    test_result = processor._classify_message("Hello")
    print(f"   ✅ API connection successful, classification: {test_result}")
    
except Exception as e:
    print(f"   ❌ API connection failed: {str(e)}")

# Test 6: Business Question Coverage Analysis
print("\n6. BUSINESS QUESTION COVERAGE:")

# Sample of demo questions to test capabilities
demo_questions = {
    "banking": [
        "What is the customer churn rate?",
        "Which customers have the highest account balances?",
        "Show the transaction volume by month",
        "What is the loan default rate?",
        "Analyze customer segmentation by age and balance"
    ],
    "hospital": [
        "What is the readmission rate?",
        "Which physician has the most admissions?",
        "Show treatment costs by diagnosis",
        "What is the average length of stay?",
        "Analyze patient demographics"
    ],
    "marketing": [
        "What is the conversion rate by campaign?",
        "Which channel has the best ROI?",
        "Show lead generation trends",
        "What is the cost per acquisition?",
        "Analyze campaign performance by budget"
    ]
}

coverage_issues = []

for domain, questions in demo_questions.items():
    print(f"\n   {domain.upper()} Questions:")
    
    try:
        loader = backend.DomainDataLoader(domain)
        schema = loader.schema_data
        
        # Check if schema has necessary information for these questions
        table_names = [t['name'] for t in schema['tables']]
        
        # Banking specific checks
        if domain == "banking":
            if "customers" not in table_names or "accounts" not in table_names:
                coverage_issues.append(f"{domain}: Missing core customer/account tables")
            
            # Check for churn-related fields
            accounts_table = next((t for t in schema['tables'] if t['name'] == 'accounts'), None)
            if accounts_table and 'churned' not in accounts_table['columns']:
                coverage_issues.append(f"{domain}: Missing churn indicator in accounts table")
        
        # Hospital specific checks
        elif domain == "hospital":
            if "patients" not in table_names or "admissions" not in table_names:
                coverage_issues.append(f"{domain}: Missing core patient/admission tables")
                
            # Check for readmission fields
            admissions_table = next((t for t in schema['tables'] if t['name'] == 'admissions'), None)
            if admissions_table and 'readmitted' not in admissions_table['columns']:
                coverage_issues.append(f"{domain}: Missing readmission indicator")
        
        # Marketing specific checks
        elif domain == "marketing":
            if "campaigns" not in table_names or "leads" not in table_names:
                coverage_issues.append(f"{domain}: Missing core campaign/leads tables")
                
            # Check for conversion fields
            leads_table = next((t for t in schema['tables'] if t['name'] == 'leads'), None)
            if leads_table and 'converted' not in leads_table['columns']:
                coverage_issues.append(f"{domain}: Missing conversion indicator")
        
        for q in questions:
            print(f"      - {q}")
            
    except Exception as e:
        coverage_issues.append(f"{domain}: Schema loading error - {str(e)}")

if coverage_issues:
    print(f"\n   ⚠️  Business Question Coverage Issues: {len(coverage_issues)}")
    for issue in coverage_issues:
        print(f"      - {issue}")

# Test 7: Token Limit and Code Generation
print("\n7. CODE GENERATION CAPACITY:")

try:
    # Test with a complex question
    processor = backend.LLMWorkflow()
    processor.initialize_domain("banking")
    
    # Test plan creation
    plan = processor._create_analysis_plan("What is the customer churn rate by age group and account type?")
    
    if len(plan) > 100:
        print("   ✅ Analysis plan generation working")
        print(f"      Plan length: {len(plan)} characters")
    else:
        print(f"   ⚠️  Analysis plan seems short: {len(plan)} characters")
        
except Exception as e:
    print(f"   ❌ Code generation test failed: {str(e)}")

# Test 8: Output Directory and File Handling
print("\n8. OUTPUT SYSTEM:")

output_dir = Path("output")
if output_dir.exists():
    print("   ✅ Output directory exists")
    
    # Check permissions
    test_file = output_dir / "test_write.tmp"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print("   ✅ Output directory writable")
    except Exception as e:
        print(f"   ❌ Output directory not writable: {str(e)}")
else:
    print("   ❌ Output directory missing")
    try:
        output_dir.mkdir()
        print("   ✅ Created output directory")
    except Exception as e:
        print(f"   ❌ Cannot create output directory: {str(e)}")

# Final Summary
print("\n" + "=" * 80)
print("INVESTIGATION SUMMARY:")
print("=" * 80)

total_issues = len(schema_issues) + len(data_issues) + len(coverage_issues)

if total_issues == 0:
    print("✅ System appears ready for demo!")
    print("   All core components are functioning properly.")
else:
    print(f"⚠️  Found {total_issues} potential issues that should be addressed:")
    
    if schema_issues:
        print(f"\n📋 Schema Issues ({len(schema_issues)}):")
        for issue in schema_issues:
            print(f"   - {issue}")
    
    if data_issues:
        print(f"\n📊 Data Issues ({len(data_issues)}):")
        for issue in data_issues:
            print(f"   - {issue}")
    
    if coverage_issues:
        print(f"\n❓ Business Question Coverage Issues ({len(coverage_issues)}):")
        for issue in coverage_issues:
            print(f"   - {issue}")

print("\n🎯 DEMO READINESS STATUS:")
if total_issues == 0:
    print("   STATUS: READY ✅")
elif total_issues <= 3:
    print("   STATUS: MOSTLY READY ⚠️  (Minor issues)")
else:
    print("   STATUS: NEEDS ATTENTION ❌ (Multiple issues)")

print("\n" + "=" * 80)
