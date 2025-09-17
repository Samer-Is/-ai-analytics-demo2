"""
Test the new conversational analysis style
Tests the same education question with improved natural language responses
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.getcwd())

from backend import LLMWorkflow

def test_conversational_style():
    """Test the new conversational analysis style"""
    
    print("🎭 Testing New Conversational Analysis Style")
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
    
    # Test the question with new conversational style
    test_question = "What's the relationship between class size and student performance?"
    
    print(f"\n2. Testing question with NEW conversational style:")
    print(f"   '{test_question}'")
    print("\n   Expected: Natural, conversational response instead of rigid template")
    print("   " + "-" * 50)
    
    try:
        result = workflow.process_query(
            user_message=test_question,
            session_id="conversational_test",
            conversation_history=[]
        )
        
        if result.get('success'):
            print("✅ Query processed successfully!")
            
            final_answer = result.get('final_answer', '')
            if final_answer:
                print("\n📋 NEW CONVERSATIONAL RESPONSE:")
                print("=" * 50)
                print(final_answer)
                print("=" * 50)
                
                # Analyze the response style
                print(f"\n🔍 Response Analysis:")
                
                # Check for template indicators (old style)
                template_indicators = [
                    "Executive Summary:",
                    "Key Findings:",
                    "Business Implications:",
                    "Recommendations:",
                    "Conclusion:",
                    "Strategic Planning:"
                ]
                
                found_templates = [indicator for indicator in template_indicators if indicator in final_answer]
                
                if found_templates:
                    print(f"⚠️  Still contains template elements: {found_templates}")
                    print("   Response may still be too structured")
                else:
                    print("✅ No rigid template structure detected!")
                
                # Check for conversational indicators (new style)
                conversational_indicators = [
                    "I found",
                    "What's interesting",
                    "What's fascinating",
                    "Looking at",
                    "It turns out",
                    "I discovered",
                    "The data shows",
                    "Here's what",
                    "So,"
                ]
                
                found_conversational = [indicator for indicator in conversational_indicators if indicator.lower() in final_answer.lower()]
                
                if found_conversational:
                    print(f"✅ Conversational elements found: {found_conversational}")
                else:
                    print("⚠️  May need more conversational language")
                
                # Check response length and variety
                sentences = final_answer.split('.')
                avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
                
                print(f"📊 Style metrics:")
                print(f"   - Total length: {len(final_answer)} characters")
                print(f"   - Sentences: {len(sentences)}")
                print(f"   - Avg sentence length: {avg_sentence_length:.1f} words")
                
        else:
            print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎭 Conversational Style Improvement Test")
    print("=" * 70)
    
    success = test_conversational_style()
    
    if success:
        print("\n🎉 Test completed! Check the response style above.")
        print("✨ The goal is natural, engaging conversation instead of rigid templates")
    else:
        print("\n❌ Test failed - need to investigate issues")
    
    print("\n" + "=" * 70)
