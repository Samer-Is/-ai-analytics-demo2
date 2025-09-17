#!/usr/bin/env python3
"""
Quick Assessment Test - Single Domain
Test one question from each domain to verify system functionality
"""

import time
from backend import LLMWorkflow

def quick_assessment_test():
    print("🚀 QUICK ASSESSMENT TEST - SYSTEM VERIFICATION")
    print("="*60)
    
    # Test questions - one per domain
    test_cases = [
        {
            "domain": "banking",
            "question": "What is the customer churn rate and which demographic segments have the highest churn?"
        },
        {
            "domain": "hospital", 
            "question": "What is the average patient readmission rate by physician specialty?"
        },
        {
            "domain": "education",
            "question": "What is the correlation between professor experience and student performance?"
        }
    ]
    
    workflow = LLMWorkflow()
    
    for i, test_case in enumerate(test_cases, 1):
        domain = test_case["domain"]
        question = test_case["question"]
        
        print(f"\n{'='*60}")
        print(f"TEST {i}/3: {domain.upper()} DOMAIN")
        print(f"Question: {question}")
        print("="*60)
        
        start_time = time.time()
        
        try:
            # Initialize domain
            if not workflow.initialize_domain(domain):
                print(f"❌ Failed to initialize {domain} domain")
                continue
                
            # Process query
            result = workflow.process_query(question)
            execution_time = time.time() - start_time
            
            if result.get('success'):
                code_results = result.get('code_results', {})
                generated_code = code_results.get('generated_code', '')
                analysis_output = result.get('final_answer', '')
                
                # Check for charts by looking for PNG files in output directory
                import glob
                chart_files = glob.glob('output/*.png')
                chart_generated = len(chart_files) > 0
                
                print(f"✅ SUCCESS in {execution_time:.1f}s")
                print(f"📝 Code Length: {len(generated_code)} chars")
                print(f"📊 Output Length: {len(analysis_output)} chars") 
                print(f"📈 Chart: {'Yes' if chart_generated else 'No'}")
                
                # Show preview of analysis
                if analysis_output:
                    print(f"\n📋 ANALYSIS PREVIEW:")
                    preview = analysis_output[:400] + "..." if len(analysis_output) > 400 else analysis_output
                    print(preview)
                    
                # Simple quality assessment
                quality_score = 0
                if len(generated_code) > 200:
                    quality_score += 25
                if len(analysis_output) > 300:
                    quality_score += 25
                if chart_generated:
                    quality_score += 25
                if any(word in analysis_output.lower() for word in ['analysis', 'finding', 'insight', 'recommendation']):
                    quality_score += 25
                    
                print(f"🎯 Quality Score: {quality_score}/100")
                
            else:
                print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ ERROR in {execution_time:.1f}s: {str(e)}")
            
        # Small delay between tests
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print("🏁 QUICK ASSESSMENT COMPLETE")
    print("="*60)

if __name__ == "__main__":
    quick_assessment_test()
