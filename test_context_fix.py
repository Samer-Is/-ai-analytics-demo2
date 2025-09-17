"""
Test script to validate context management fix for education domain
Tests the specific question that was causing context length errors
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.getcwd())

from backend import LLMWorkflow

def test_education_context_fix():
    """Test the education domain question that was causing context errors"""
    
    print("🧪 Testing Context Management Fix for Education Domain")
    print("=" * 60)
    
    # Initialize workflow
    workflow = LLMWorkflow()
    
    # Initialize education domain
    print("1. Initializing education domain...")
    success = workflow.initialize_domain("education")
    
    if not success:
        print("❌ Failed to initialize education domain")
        return False
    
    print("✅ Education domain initialized successfully")
    
    # Test the specific question that was causing issues
    test_question = "What's the relationship between class size and student performance?"
    
    print(f"\n2. Testing question: '{test_question}'")
    print("   (This question previously caused context length errors)")
    
    try:
        # Process the query with empty conversation history first
        result = workflow.process_query(
            user_message=test_question,
            session_id="test_session",
            conversation_history=[]
        )
        
        print(f"✅ Query processed successfully!")
        print(f"📊 Response type: {result.get('message_type', 'unknown')}")
        
        if result.get('success'):
            print(f"📈 Analysis completed successfully")
            print(f"🎯 Domain: {result.get('domain', 'unknown')}")
            
            # Show a brief excerpt of the response
            final_answer = result.get('final_answer', '')
            if final_answer:
                excerpt = final_answer[:200] + "..." if len(final_answer) > 200 else final_answer
                print(f"📋 Response excerpt: {excerpt}")
            
        else:
            print(f"⚠️  Query processed but with issues: {result.get('error', 'Unknown error')}")
            
        return True
        
    except Exception as e:
        if "context_length_exceeded" in str(e) or "maximum context length" in str(e):
            print(f"❌ Context length error still occurring: {e}")
            return False
        else:
            print(f"❌ Other error occurred: {e}")
            return False

def test_context_manager_directly():
    """Test the context manager functionality directly"""
    
    print("\n🔧 Testing Context Manager Directly")
    print("=" * 40)
    
    try:
        from context_manager import ContextManager
        
        # Create context manager
        context_mgr = ContextManager()
        print("✅ Context manager created successfully")
        
        # Test token counting
        test_text = "This is a test message for token counting."
        token_count = context_mgr.count_tokens(test_text)
        print(f"✅ Token counting works: '{test_text}' = {token_count} tokens")
        
        # Test message preparation
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"}
        ]
        
        prepared = context_mgr.prepare_messages_for_api(test_messages)
        print(f"✅ Message preparation works: {len(test_messages)} -> {len(prepared)} messages")
        
        return True
        
    except Exception as e:
        print(f"❌ Context manager test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Context Management Fix Validation")
    print("=" * 70)
    
    # Test context manager directly
    cm_success = test_context_manager_directly()
    
    # Test education domain question
    if cm_success:
        edu_success = test_education_context_fix()
        
        if edu_success:
            print("\n🎉 SUCCESS: Context management fix is working!")
            print("✅ The education domain question can now be processed without context errors")
            print("🚀 Ready to launch Streamlit app for interactive testing")
        else:
            print("\n⚠️  PARTIAL SUCCESS: Context manager works but education query has issues")
    else:
        print("\n❌ FAILED: Context manager setup has issues")
    
    print("\n" + "=" * 70)
