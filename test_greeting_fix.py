"""
Test script to verify that greeting handling works correctly
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from backend import LLMWorkflow
import traceback

def test_greeting_handling():
    """Test that greetings get appropriate responses"""
    print("Testing Greeting Handling Fix")
    print("=" * 50)
    
    # Initialize workflow with banking domain
    workflow = LLMWorkflow()
    
    # Test greeting responses
    greeting_tests = [
        "Hi",
        "Hello",
        "Hey there",
        "Good morning",
        "How are you?"
    ]
    
    # Test analysis questions to ensure they still work
    analysis_tests = [
        "What is the average account balance?",
        "How many customers do we have?",
        "Show me customer demographics"
    ]
    
    # Initialize domain
    print("Initializing banking domain...")
    success = workflow.initialize_domain("banking")
    if not success:
        print("❌ Failed to initialize domain")
        return
    
    print("✅ Domain initialized successfully\n")
    
    # Test greetings
    print("Testing Greeting Responses:")
    print("-" * 30)
    
    for greeting in greeting_tests:
        try:
            print(f"\nTest: '{greeting}'")
            result = workflow.process_query(greeting)
            
            if result.get("message_type") == "greeting":
                print(f"✅ Correctly identified as greeting")
                print(f"Response: {result.get('final_answer', 'No response')}")
            else:
                print(f"❌ Incorrectly classified as: {result.get('message_type', 'unknown')}")
                if 'error' in result:
                    print(f"Error: {result['error']}")
                    
        except Exception as e:
            print(f"❌ Error testing '{greeting}': {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Testing Analysis Questions (should still work):")
    print("-" * 30)
    
    # Test one analysis question to ensure it still works
    test_question = "What is the total number of customers?"
    try:
        print(f"\nTest: '{test_question}'")
        result = workflow.process_query(test_question)
        
        if result.get("success") and "final_answer" in result:
            print("✅ Analysis question processed correctly")
            # Show just first 200 chars of response
            response = result.get("final_answer", "")
            preview = response[:200] + "..." if len(response) > 200 else response
            print(f"Response preview: {preview}")
        else:
            print(f"❌ Analysis failed")
            if 'error' in result:
                print(f"Error: {result['error']}")
                
    except Exception as e:
        print(f"❌ Error testing analysis: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Greeting Fix Test Complete!")

if __name__ == "__main__":
    test_greeting_handling()
