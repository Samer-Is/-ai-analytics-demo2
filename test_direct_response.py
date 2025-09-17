#!/usr/bin/env python3
"""
Test Direct Response - No Templates
Verify the system responds to actual user questions without predefined text
"""

from backend import LLMWorkflow

def test_direct_response():
    print("🔬 TESTING DIRECT AI RESPONSES (NO TEMPLATES)")
    print("="*60)
    
    workflow = LLMWorkflow()
    
    # Test different types of questions
    test_cases = [
        {
            "domain": "banking",
            "question": "Hello, what can you do?"
        },
        {
            "domain": "banking", 
            "question": "How many customers do we have?"
        },
        {
            "domain": "education",
            "question": "What's the student enrollment trend?"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        domain = test_case["domain"]
        question = test_case["question"]
        
        print(f"\n{'='*60}")
        print(f"TEST {i}/3: {domain.upper()}")
        print(f"Question: '{question}'")
        print("-" * 60)
        
        try:
            # Initialize domain
            if not workflow.initialize_domain(domain):
                print(f"❌ Failed to initialize {domain} domain")
                continue
                
            # Process query
            result = workflow.process_query(question)
            
            if result.get('success'):
                analysis_output = result.get('final_answer', '')
                message_type = result.get('message_type', '')
                
                print(f"✅ SUCCESS")
                print(f"Message Type: {message_type}")
                print(f"Response Length: {len(analysis_output)} chars")
                
                # Check if response contains template text
                template_indicators = [
                    "Hello! I'm your AI Data Analytics Assistant",
                    "Feel free to ask me questions about:",
                    "What would you like to explore?",
                    "interconnected tables:",
                    "domain_description"
                ]
                
                has_template = any(indicator in analysis_output for indicator in template_indicators)
                
                if has_template:
                    print("❌ TEMPLATE TEXT DETECTED!")
                    print("Response contains predefined template content")
                else:
                    print("✅ DIRECT AI RESPONSE!")
                    print("No template text detected")
                
                # Show response preview
                print(f"\n📋 RESPONSE PREVIEW:")
                preview = analysis_output[:300] + "..." if len(analysis_output) > 300 else analysis_output
                print(preview)
                
            else:
                print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print(f"\n{'='*60}")
    print("🏁 DIRECT RESPONSE TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_direct_response()
