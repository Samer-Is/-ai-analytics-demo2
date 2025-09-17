#!/usr/bin/env python3
"""
Single Question Deep Assessment
Test one comprehensive question to verify full workflow
"""

from comprehensive_assessment import AnalyticsAssessment

def single_question_test():
    print("🔬 SINGLE QUESTION DEEP ASSESSMENT")
    print("="*60)
    
    assessor = AnalyticsAssessment()
    
    # Test one challenging banking question
    banking_question = {
        "id": "banking_deep_test",
        "difficulty": "hard",
        "question": "Analyze customer churn patterns by demographics and account behavior to identify high-risk segments and recommend retention strategies.",
        "expected_analysis": ["Churn analysis", "Demographics", "Risk scoring", "Retention strategies"],
        "business_impact": "Customer retention optimization"
    }
    
    print(f"Testing: {banking_question['question']}")
    print("-" * 60)
    
    result = assessor.run_question_test('banking', banking_question)
    
    if result['success']:
        assessment = result['assessment']
        print(f"\n📊 DETAILED RESULTS:")
        print(f"Generated Code Length: {len(result['generated_code'])}")
        print(f"Analysis Output Length: {len(result['analysis_output'])}")
        print(f"Chart Generated: {result['chart_generated']}")
        print(f"Execution Time: {result['execution_time']:.1f}s")
        print(f"Overall Score: {assessment['overall_score']:.1f}/100")
        print(f"Grade: {assessment['grade']}")
        
        print(f"\n🔧 QUALITY BREAKDOWN:")
        for criteria, details in assessment.items():
            if isinstance(details, dict) and 'score' in details:
                print(f"  {criteria.replace('_', ' ').title()}: {details['score']}/100")
        
        # Show code preview if available
        if result['generated_code']:
            print(f"\n💻 GENERATED CODE PREVIEW:")
            print(result['generated_code'][:500] + "..." if len(result['generated_code']) > 500 else result['generated_code'])
        
        # Show analysis preview
        if result['analysis_output']:
            print(f"\n📋 ANALYSIS PREVIEW:")
            print(result['analysis_output'][:500] + "..." if len(result['analysis_output']) > 500 else result['analysis_output'])
            
    else:
        print(f"❌ TEST FAILED: {result['error']}")

if __name__ == "__main__":
    single_question_test()
