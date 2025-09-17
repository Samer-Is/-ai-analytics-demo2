#!/usr/bin/env python3
"""
Quick Validation Test - Core Functionality Check
Tests essential components without requiring API calls
"""

import os
import sys
import traceback

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())

def quick_validation_test():
    """Run essential validation tests"""
    print("🔍 QUICK VALIDATION TEST - CORE FUNCTIONALITY")
    print("=" * 55)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Backend Import
    print("\n1. Testing Backend Import...")
    try:
        from backend import LLMWorkflow, DomainDataLoader
        print("   ✅ Backend classes imported successfully")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Backend import failed: {e}")
        tests_failed += 1
    
    # Test 2: Data Loader Functionality
    print("\n2. Testing Data Loader...")
    try:
        loader = DomainDataLoader('banking')
        schema = loader._load_schema()
        if schema and 'tables' in schema:
            print(f"   ✅ Banking schema loaded: {len(schema['tables'])} tables")
            tests_passed += 1
        else:
            print("   ❌ Schema loading failed")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Data loader failed: {e}")
        tests_failed += 1
    
    # Test 3: Code Generation
    print("\n3. Testing Code Generation...")
    try:
        loader = DomainDataLoader('banking')
        code = loader.get_dataframes_loading_code()
        if 'import pandas as pd' in code and 'figsize=(9, 5)' in code:
            print("   ✅ Code generation working with 9x5 charts")
            tests_passed += 1
        else:
            print("   ❌ Code generation missing required elements")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Code generation failed: {e}")
        tests_failed += 1
    
    # Test 4: All Domains
    print("\n4. Testing All Domains...")
    domains = ['banking', 'hospital', 'marketing']
    domain_success = 0
    for domain in domains:
        try:
            loader = DomainDataLoader(domain)
            schema = loader._load_schema()
            if schema:
                print(f"   ✅ {domain.title()} domain loaded")
                domain_success += 1
            else:
                print(f"   ❌ {domain.title()} domain failed")
        except Exception as e:
            print(f"   ❌ {domain.title()} domain error: {e}")
    
    if domain_success == 3:
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 5: Data Files Check
    print("\n5. Testing Data Files...")
    data_files_found = 0
    total_expected = 12  # 4 files per domain × 3 domains
    
    domain_files = {
        'banking': ['customers.csv', 'accounts.csv', 'transactions.csv', 'loans.csv'],
        'hospital': ['patients.csv', 'physicians.csv', 'admissions.csv', 'treatments.csv'],
        'marketing': ['campaigns.csv', 'leads.csv', 'web_analytics.csv', 'ad_spend.csv']
    }
    
    for domain, files in domain_files.items():
        for file in files:
            if os.path.exists(f'data/{domain}/{file}'):
                data_files_found += 1
    
    print(f"   📊 Data files found: {data_files_found}/{total_expected}")
    if data_files_found >= total_expected * 0.8:  # At least 80% of files
        print("   ✅ Sufficient data files present")
        tests_passed += 1
    else:
        print("   ❌ Missing required data files")
        tests_failed += 1
    
    # Test 6: Output Directory
    print("\n6. Testing Output Management...")
    try:
        os.makedirs('output', exist_ok=True)
        if os.path.exists('output'):
            print("   ✅ Output directory ready")
            tests_passed += 1
        else:
            print("   ❌ Output directory creation failed")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Output directory error: {e}")
        tests_failed += 1
    
    # Summary
    total_tests = tests_passed + tests_failed
    success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print("\n" + "=" * 55)
    print("📊 QUICK VALIDATION RESULTS")
    print("=" * 55)
    print(f"✅ Tests Passed: {tests_passed}")
    print(f"❌ Tests Failed: {tests_failed}")
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🟢 STATUS: EXCELLENT - Core functionality working!")
        print("🚀 Ready for API key configuration and full testing")
    elif success_rate >= 70:
        print("🟡 STATUS: GOOD - Minor issues detected")
        print("🔧 Address failed tests before proceeding")
    else:
        print("🔴 STATUS: POOR - Major issues need fixing")
        print("🛠️ Check installation and file dependencies")
    
    return success_rate >= 70

if __name__ == "__main__":
    success = quick_validation_test()
    if success:
        print("\n🎉 Core system validation PASSED!")
        print("💡 Next step: Configure OpenAI API key and run full tests")
    else:
        print("\n⚠️ Core system validation FAILED!")
        print("🔧 Fix the issues above before proceeding")
    
    exit(0 if success else 1)
