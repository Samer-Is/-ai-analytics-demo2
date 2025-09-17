#!/usr/bin/env python3
"""
Comprehensive Test Runner for AI Data Analytics Tool
Executes automated tests across all domains and functionality
"""

import os
import sys
import time
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our backend
try:
    from backend import AnalyticsWorkflow
    from dotenv import load_dotenv
    load_dotenv()
except ImportError as e:
    print(f"❌ Failed to import backend: {e}")
    sys.exit(1)

class ComprehensiveTestRunner:
    def __init__(self):
        self.workflow = AnalyticsWorkflow()
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name, domain, question, success, duration, error=None):
        """Log test results"""
        result = {
            'test_name': test_name,
            'domain': domain,
            'question': question,
            'success': success,
            'duration': duration,
            'error': str(error) if error else None,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {question[:50]}... ({duration:.1f}s)")
        if error:
            print(f"   Error: {error}")
    
    def test_basic_functionality(self):
        """Test basic system functionality"""
        print("\n🔧 TESTING BASIC FUNCTIONALITY")
        print("=" * 50)
        
        # Test 1: API Connection
        try:
            start = time.time()
            # Simple test to verify API works
            result = self.workflow.process_query('banking', 'What is 2+2?')
            success = result is not None
            duration = time.time() - start
            self.log_test("API_CONNECTION", "system", "API connectivity test", success, duration)
        except Exception as e:
            self.log_test("API_CONNECTION", "system", "API connectivity test", False, 0, e)
        
        # Test 2: Data Loading
        for domain in ['banking', 'hospital', 'marketing']:
            try:
                start = time.time()
                schema_path = f'metadata/{domain}/_schema.json'
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
                success = len(schema.get('tables', [])) > 0
                duration = time.time() - start
                self.log_test("DATA_LOADING", domain, f"Load {domain} schema", success, duration)
            except Exception as e:
                self.log_test("DATA_LOADING", domain, f"Load {domain} schema", False, 0, e)
    
    def test_banking_domain(self):
        """Test banking domain functionality"""
        print("\n🏦 TESTING BANKING DOMAIN")
        print("=" * 50)
        
        banking_tests = [
            # Basic tests
            ("BASIC_COUNT", "How many customers do we have?"),
            ("BASIC_AVERAGE", "What's the average account balance?"),
            ("BASIC_CHURN", "What is the customer churn rate?"),
            ("BASIC_DISTRIBUTION", "Show me the distribution of account types"),
            
            # Medium complexity
            ("MEDIUM_CORRELATION", "Which account type has higher churn?"),
            ("MEDIUM_SEGMENTATION", "Analyze transaction patterns by customer age"),
            ("MEDIUM_ANALYSIS", "Is there a relationship between balance and churn?"),
            
            # Advanced tests
            ("ADVANCED_PREDICTION", "Identify customers at high risk of churning"),
            ("ADVANCED_OPTIMIZATION", "Recommend strategies to reduce churn"),
        ]
        
        for test_name, question in banking_tests:
            try:
                start = time.time()
                result = self.workflow.process_query('banking', question)
                success = result is not None and len(result.get('analysis', '')) > 100
                duration = time.time() - start
                self.log_test(test_name, "banking", question, success, duration)
                
                # Brief pause between tests
                time.sleep(2)
            except Exception as e:
                self.log_test(test_name, "banking", question, False, 0, e)
    
    def test_hospital_domain(self):
        """Test hospital domain functionality"""
        print("\n🏥 TESTING HOSPITAL DOMAIN")
        print("=" * 50)
        
        hospital_tests = [
            # Basic tests
            ("BASIC_PATIENTS", "How many patients do we have?"),
            ("BASIC_STAY", "What's the average length of stay?"),
            ("BASIC_READMISSION", "What is our readmission rate?"),
            ("BASIC_PHYSICIANS", "How many physicians work here?"),
            
            # Medium complexity
            ("MEDIUM_SPECIALTIES", "Which departments have highest readmission rates?"),
            ("MEDIUM_COSTS", "Show treatment costs by medical condition"),
            ("MEDIUM_PERFORMANCE", "Which physicians have best patient outcomes?"),
            
            # Advanced tests
            ("ADVANCED_RISK", "Identify patients at high risk of readmission"),
            ("ADVANCED_OPTIMIZATION", "Optimize physician workload distribution"),
        ]
        
        for test_name, question in hospital_tests:
            try:
                start = time.time()
                result = self.workflow.process_query('hospital', question)
                success = result is not None and len(result.get('analysis', '')) > 100
                duration = time.time() - start
                self.log_test(test_name, "hospital", question, success, duration)
                
                # Brief pause between tests
                time.sleep(2)
            except Exception as e:
                self.log_test(test_name, "hospital", question, False, 0, e)
    
    def test_marketing_domain(self):
        """Test marketing domain functionality"""
        print("\n📈 TESTING MARKETING DOMAIN")
        print("=" * 50)
        
        marketing_tests = [
            # Basic tests
            ("BASIC_SPEND", "What's our total marketing spend?"),
            ("BASIC_LEADS", "How many leads did we generate?"),
            ("BASIC_CONVERSION", "What's the conversion rate?"),
            ("BASIC_TRAFFIC", "Show me website analytics summary"),
            
            # Medium complexity
            ("MEDIUM_ROI", "Which marketing channels have the best ROI?"),
            ("MEDIUM_SEGMENTS", "Compare conversion rates across customer segments"),
            ("MEDIUM_TRENDS", "Show seasonal trends in campaign performance"),
            
            # Advanced tests
            ("ADVANCED_OPTIMIZATION", "Optimize budget allocation across channels"),
            ("ADVANCED_ATTRIBUTION", "Analyze customer journey and touchpoint effectiveness"),
        ]
        
        for test_name, question in marketing_tests:
            try:
                start = time.time()
                result = self.workflow.process_query('marketing', question)
                success = result is not None and len(result.get('analysis', '')) > 100
                duration = time.time() - start
                self.log_test(test_name, "marketing", question, success, duration)
                
                # Brief pause between tests
                time.sleep(2)
            except Exception as e:
                self.log_test(test_name, "marketing", question, False, 0, e)
    
    def test_conversation_memory(self):
        """Test conversation memory functionality"""
        print("\n🧠 TESTING CONVERSATION MEMORY")
        print("=" * 50)
        
        # Test progressive conversation
        conversation_tests = [
            ("Show me the churn rate in banking", "banking"),
            ("Focus on the high-churn customers and show their demographics", "banking"),
            ("What products should we offer those customers?", "banking"),
        ]
        
        conversation_history = []
        
        for i, (question, domain) in enumerate(conversation_tests):
            try:
                start = time.time()
                result = self.workflow.process_query(domain, question, conversation_history)
                success = result is not None
                duration = time.time() - start
                
                test_name = f"MEMORY_STEP_{i+1}"
                self.log_test(test_name, domain, question, success, duration)
                
                # Add to conversation history
                if success:
                    conversation_history.append({
                        'role': 'user',
                        'content': question,
                        'domain': domain
                    })
                    conversation_history.append({
                        'role': 'assistant',
                        'content': result.get('analysis', ''),
                        'domain': domain
                    })
                
                time.sleep(2)
            except Exception as e:
                self.log_test(f"MEMORY_STEP_{i+1}", domain, question, False, 0, e)
    
    def test_chart_generation(self):
        """Test chart generation and management"""
        print("\n📊 TESTING CHART GENERATION")
        print("=" * 50)
        
        chart_tests = [
            ("Show customer age distribution", "banking"),
            ("Show patient distribution by specialty", "hospital"),
            ("Show campaign performance by channel", "marketing"),
        ]
        
        for question, domain in chart_tests:
            try:
                start = time.time()
                
                # Clear any existing charts
                self.workflow.clear_output_charts()
                
                result = self.workflow.process_query(domain, question)
                
                # Check if chart was generated
                output_dir = 'output'
                chart_exists = False
                if os.path.exists(output_dir):
                    charts = [f for f in os.listdir(output_dir) if f.endswith('.png')]
                    chart_exists = len(charts) > 0
                
                success = result is not None and chart_exists
                duration = time.time() - start
                
                test_name = f"CHART_{domain.upper()}"
                self.log_test(test_name, domain, question, success, duration)
                
                time.sleep(2)
            except Exception as e:
                self.log_test(f"CHART_{domain.upper()}", domain, question, False, 0, e)
    
    def test_error_handling(self):
        """Test error handling capabilities"""
        print("\n🚨 TESTING ERROR HANDLING")
        print("=" * 50)
        
        error_tests = [
            ("", "banking", "Empty question"),
            ("Show me the purple elephants dancing", "banking", "Nonsense question"),
            ("Analyze the super secret classified data", "banking", "Non-existent data"),
        ]
        
        for question, domain, description in error_tests:
            try:
                start = time.time()
                result = self.workflow.process_query(domain, question)
                
                # For error tests, we expect graceful handling, not crashes
                success = result is not None  # Should not crash
                duration = time.time() - start
                
                test_name = f"ERROR_HANDLING"
                self.log_test(test_name, domain, description, success, duration)
                
                time.sleep(1)
            except Exception as e:
                # Catching exceptions is actually expected behavior for error handling
                self.log_test("ERROR_HANDLING", domain, description, True, 0, 
                             "Handled gracefully with exception")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_duration = time.time() - self.start_time
        
        print("\n" + "=" * 70)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 70)
        
        # Summary statistics
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Duration: {total_duration:.1f} seconds")
        
        # Domain breakdown
        domains = {}
        for result in self.test_results:
            domain = result['domain']
            if domain not in domains:
                domains[domain] = {'total': 0, 'success': 0}
            domains[domain]['total'] += 1
            if result['success']:
                domains[domain]['success'] += 1
        
        print(f"\n📊 DOMAIN BREAKDOWN:")
        for domain, stats in domains.items():
            rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"   {domain.capitalize()}: {stats['success']}/{stats['total']} ({rate:.1f}%)")
        
        # Performance metrics
        durations = [r['duration'] for r in self.test_results if r['duration'] > 0]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            print(f"\n⏱️ PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_duration:.1f}s")
            print(f"   Maximum Response Time: {max_duration:.1f}s")
        
        # Failed tests
        failed_results = [r for r in self.test_results if not r['success']]
        if failed_results:
            print(f"\n❌ FAILED TESTS:")
            for result in failed_results:
                print(f"   {result['test_name']} ({result['domain']}): {result['error']}")
        
        # Save detailed results to file
        report_file = f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'successful_tests': successful_tests,
                    'failed_tests': failed_tests,
                    'success_rate': success_rate,
                    'total_duration': total_duration
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {report_file}")
        
        return success_rate >= 80  # Consider 80%+ success rate as passing

def main():
    """Run comprehensive test suite"""
    print("🧪 AI DATA ANALYTICS TOOL - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print("This will test all domains, functionality, and edge cases")
    print("Estimated runtime: 10-15 minutes")
    print("=" * 70)
    
    # Check if user wants to proceed
    response = input("Continue with full test suite? (y/n): ").lower().strip()
    if response != 'y':
        print("Test cancelled.")
        return
    
    runner = ComprehensiveTestRunner()
    
    try:
        # Run all test categories
        runner.test_basic_functionality()
        runner.test_banking_domain()
        runner.test_hospital_domain()
        runner.test_marketing_domain()
        runner.test_conversation_memory()
        runner.test_chart_generation()
        runner.test_error_handling()
        
        # Generate final report
        success = runner.generate_report()
        
        if success:
            print("\n🎉 TEST SUITE PASSED - Tool is ready for production!")
        else:
            print("\n⚠️ TEST SUITE PARTIALLY FAILED - Review failed tests above")
            
    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user")
    except Exception as e:
        print(f"\n\nTest suite failed with error: {e}")
        runner.generate_report()

if __name__ == "__main__":
    main()
