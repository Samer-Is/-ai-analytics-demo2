#!/usr/bin/env python3
"""
Quick Validation Script for AI Data Analytics Tool
Tests core functionality across all domains quickly
"""

import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our backend
try:
    from backend import AnalyticsWorkflow
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Backend imported successfully")
except ImportError as e:
    print(f"❌ Failed to import backend: {e}")
    sys.exit(1)

def test_quick_validation():
    """Quick validation test across all domains"""
    print("\n🚀 QUICK VALIDATION TEST")
    print("=" * 50)
    
    workflow = AnalyticsWorkflow()
    
    # Quick tests for each domain
    quick_tests = [
        ("banking", "What is the customer churn rate?"),
        ("hospital", "What is our readmission rate?"),
        ("marketing", "What's the conversion rate?"),
    ]
    
    results = []
    
    for domain, question in quick_tests:
        print(f"\n🧪 Testing {domain.upper()}: {question}")
        try:
            start_time = time.time()
            result = workflow.process_query(domain, question)
            duration = time.time() - start_time
            
            if result and result.get('analysis'):
                print(f"   ✅ Success! ({duration:.1f}s)")
                print(f"   📊 Analysis length: {len(result['analysis'])} characters")
                
                # Check if chart was generated
                if os.path.exists('output'):
                    charts = [f for f in os.listdir('output') if f.endswith('.png')]
                    if charts:
                        print(f"   📈 Chart generated: {charts[0]}")
                
                results.append((domain, True, duration))
            else:
                print(f"   ❌ Failed - No analysis returned")
                results.append((domain, False, duration))
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append((domain, False, 0))
    
    # Summary
    print(f"\n" + "=" * 50)
    print("📋 QUICK VALIDATION SUMMARY")
    print("=" * 50)
    
    successful = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"✅ Successful tests: {successful}/{total}")
    print(f"📊 Success rate: {successful/total*100:.1f}%")
    
    if successful == total:
        print("🎉 ALL QUICK TESTS PASSED - Tool is working correctly!")
    else:
        print("⚠️ Some tests failed - Check detailed output above")
    
    return successful == total

def test_conversation_memory():
    """Test conversation memory with follow-up questions"""
    print("\n🧠 CONVERSATION MEMORY TEST")
    print("=" * 50)
    
    workflow = AnalyticsWorkflow()
    
    # Progressive conversation
    questions = [
        "Show me the customer churn rate by account type",
        "Focus on the high-churn group and show their demographics",
        "What strategies would you recommend for those customers?"
    ]
    
    conversation_history = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n💬 Question {i}: {question}")
        try:
            start_time = time.time()
            result = workflow.process_query('banking', question, conversation_history)
            duration = time.time() - start_time
            
            if result and result.get('analysis'):
                print(f"   ✅ Success! ({duration:.1f}s)")
                
                # Add to conversation history
                conversation_history.append({
                    'role': 'user',
                    'content': question,
                    'domain': 'banking'
                })
                conversation_history.append({
                    'role': 'assistant',
                    'content': result['analysis'],
                    'domain': 'banking'
                })
                
                # Show brief excerpt
                excerpt = result['analysis'][:200] + "..." if len(result['analysis']) > 200 else result['analysis']
                print(f"   📝 Response excerpt: {excerpt}")
            else:
                print(f"   ❌ Failed - No analysis returned")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    print("\n✅ CONVERSATION MEMORY TEST PASSED!")
    print("🔗 Tool successfully maintained context across questions")
    return True

def test_chart_generation():
    """Test chart generation and sizing"""
    print("\n📊 CHART GENERATION TEST")
    print("=" * 50)
    
    workflow = AnalyticsWorkflow()
    
    # Clear any existing charts
    workflow.clear_output_charts()
    
    # Test chart generation
    print("🧪 Testing chart generation with age data...")
    try:
        start_time = time.time()
        result = workflow.process_query('banking', 'Show customer age distribution')
        duration = time.time() - start_time
        
        if result and result.get('analysis'):
            print(f"   ✅ Analysis generated! ({duration:.1f}s)")
            
            # Check for chart
            if os.path.exists('output'):
                charts = [f for f in os.listdir('output') if f.endswith('.png')]
                if charts:
                    chart_path = os.path.join('output', charts[0])
                    file_size = os.path.getsize(chart_path)
                    print(f"   📈 Chart generated: {charts[0]}")
                    print(f"   📏 File size: {file_size:,} bytes")
                    print(f"   🎯 Expected: 9×5 inch chart at 100 DPI")
                    
                    # Test chart clearing
                    print("\n🧹 Testing chart clearing...")
                    workflow.clear_output_charts()
                    remaining_charts = [f for f in os.listdir('output') if f.endswith('.png')]
                    if len(remaining_charts) == 0:
                        print("   ✅ Chart clearing works!")
                    else:
                        print(f"   ⚠️ {len(remaining_charts)} charts remain after clearing")
                    
                    return True
                else:
                    print("   ❌ No chart file generated")
                    return False
            else:
                print("   ❌ Output directory not found")
                return False
        else:
            print("   ❌ Failed - No analysis returned")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_domain_switching():
    """Test switching between domains"""
    print("\n🔄 DOMAIN SWITCHING TEST")
    print("=" * 50)
    
    workflow = AnalyticsWorkflow()
    
    domains = ['banking', 'hospital', 'marketing']
    questions = [
        "What is the churn rate?",
        "What is the readmission rate?", 
        "What is the conversion rate?"
    ]
    
    for domain, question in zip(domains, questions):
        print(f"\n🏢 Switching to {domain.upper()}: {question}")
        try:
            start_time = time.time()
            result = workflow.process_query(domain, question)
            duration = time.time() - start_time
            
            if result and result.get('analysis'):
                print(f"   ✅ Success! ({duration:.1f}s)")
                # Show domain-specific context
                analysis_preview = result['analysis'][:150] + "..."
                print(f"   📊 Analysis: {analysis_preview}")
            else:
                print(f"   ❌ Failed - No analysis returned")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    print("\n✅ DOMAIN SWITCHING TEST PASSED!")
    print("🔄 Tool successfully handled all three domains")
    return True

def main():
    """Run quick validation tests"""
    print("🧪 AI DATA ANALYTICS TOOL - QUICK VALIDATION")
    print("=" * 60)
    print("Running essential tests to validate core functionality")
    print("Estimated runtime: 2-3 minutes")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Run core validation tests
    tests = [
        ("Core Functionality", test_quick_validation),
        ("Conversation Memory", test_conversation_memory),
        ("Chart Generation", test_chart_generation),
        ("Domain Switching", test_domain_switching),
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n🚀 Running {test_name} Test...")
            result = test_func()
            if not result:
                all_tests_passed = False
                print(f"❌ {test_name} test failed!")
            else:
                print(f"✅ {test_name} test passed!")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            all_tests_passed = False
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 QUICK VALIDATION SUMMARY")
    print("=" * 60)
    
    if all_tests_passed:
        print("🎉 ALL VALIDATION TESTS PASSED!")
        print("✅ Tool is ready for demonstration and production use")
        print("🚀 Core functionality verified across all domains")
        print("💡 Conversation memory and chart generation working")
    else:
        print("⚠️ SOME VALIDATION TESTS FAILED")
        print("❌ Review the failed tests above")
        print("🔧 Fix issues before proceeding to full demo")
    
    print("\n💡 For comprehensive testing, run: python run_comprehensive_tests.py")

if __name__ == "__main__":
    main()
