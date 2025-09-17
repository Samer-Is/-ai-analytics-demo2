#!/usr/bin/env python3
"""
Test Backend with Working API Key
"""

import os
from backend import LLMWorkflow

# Test the LLM workflow with a simple question
def test_backend():
    print("🔬 TESTING BACKEND WITH WORKING API KEY")
    print("="*50)
    
    # Initialize workflow
    workflow = LLMWorkflow()
    
    # Test simple question
    test_question = "What is the total number of customers in the banking domain?"
    
    print(f"📋 Testing Question: {test_question}")
    print("🚀 Running analysis...")
    
    try:
        # Initialize domain first
        if not workflow.initialize_domain('banking'):
            print("❌ Failed to initialize banking domain")
            return False
            
        result = workflow.process_query(test_question)
        
        print(f"✅ SUCCESS!")
        
        # Extract results from new workflow structure
        if result.get('success'):
            code_results = result.get('code_results', {})
            generated_code = code_results.get('generated_code', '')
            analysis_output = result.get('final_answer', '')
            
            # Check for charts
            import glob
            chart_files = glob.glob('output/*.png')
            chart_generated = len(chart_files) > 0
        else:
            generated_code = ''
            analysis_output = f"Error: {result.get('error', 'Unknown error')}"
            chart_generated = False
        
        print(f"📝 Generated Code Length: {len(generated_code)}")
        print(f"📊 Analysis Output Length: {len(analysis_output)}")
        print(f"📈 Chart Generated: {chart_generated}")
        
        # Show first part of output
        if analysis_output:
            print(f"\n📋 Output Preview (first 300 chars):")
            print(analysis_output[:300] + "..." if len(analysis_output) > 300 else analysis_output)
        
        # Show first part of code
        if generated_code:
            print(f"\n💻 Generated Code Preview (first 300 chars):")
            print(generated_code[:300] + "..." if len(generated_code) > 300 else generated_code)
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_backend()
