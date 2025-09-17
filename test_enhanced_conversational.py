"""
Test the enhanced conversational style with strategic formatting
Tests multiple questions to see how bullet points and headers are used appropriately
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.getcwd())

from backend import LLMWorkflow

def test_enhanced_conversational_style():
    """Test the enhanced conversational style with strategic formatting"""
    
    print("🎯 Testing Enhanced Conversational Style with Strategic Formatting")
    print("=" * 70)
    
    # Initialize workflow
    workflow = LLMWorkflow()
    
    test_questions = [
        {
            "domain": "education",
            "question": "What's the relationship between class size and student performance?",
            "expectation": "Should use natural conversation with strategic formatting for key insights"
        },
        {
            "domain": "education", 
            "question": "Show me the top 5 courses with highest failure rates",
            "expectation": "Should use bullet points for listing the top 5 courses"
        }
    ]
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n{'='*50}")
        print(f"TEST {i}: {test['domain'].upper()} DOMAIN")
        print(f"{'='*50}")
        
        # Initialize domain
        print(f"Initializing {test['domain']} domain...")
        success = workflow.initialize_domain(test['domain'])
        
        if not success:
            print(f"❌ Failed to initialize {test['domain']} domain")
            continue
        
        print(f"✅ {test['domain']} domain initialized")
        
        print(f"\n📝 Question: {test['question']}")
        print(f"🎯 Expected: {test['expectation']}")
        print("\n" + "-" * 50)
        
        try:
            result = workflow.process_query(
                user_message=test['question'],
                session_id=f"enhanced_test_{i}",
                conversation_history=[]
            )
            
            if result.get('success'):
                final_answer = result.get('final_answer', '')
                print(f"\n📋 ENHANCED RESPONSE:")
                print("=" * 40)
                print(final_answer)
                print("=" * 40)
                
                # Analyze formatting usage
                print(f"\n🔍 Formatting Analysis:")
                
                bullet_count = final_answer.count('•') + final_answer.count('*') + final_answer.count('-')
                header_count = final_answer.count('**')
                
                print(f"   • Bullet points used: {bullet_count}")
                print(f"   • Headers used: {header_count // 2}")  # Divide by 2 since ** appears twice per header
                
                # Check for conversational elements
                conversational_indicators = [
                    "I found", "What's interesting", "What's fascinating", "Looking at",
                    "It turns out", "I discovered", "The data shows", "Here's what", "So,"
                ]
                
                found_conversational = [indicator for indicator in conversational_indicators 
                                     if indicator.lower() in final_answer.lower()]
                
                if found_conversational:
                    print(f"   ✅ Conversational tone maintained: {len(found_conversational)} indicators")
                else:
                    print(f"   ⚠️  May need more conversational language")
                
                # Check for appropriate structure
                if bullet_count > 0 or header_count > 0:
                    print(f"   ✅ Strategic formatting used appropriately")
                else:
                    print(f"   ⚠️  No formatting used - may need structure for complex data")
                    
            else:
                print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n{'='*70}")
    print("🎯 SUMMARY: Enhanced conversational style should:")
    print("   ✅ Use natural, engaging language")
    print("   ✅ Add bullet points when listing multiple items")
    print("   ✅ Use headers when organizing complex information")
    print("   ✅ Maintain professional but approachable tone")
    print("   ✅ Make data insights easy to follow and actionable")

if __name__ == "__main__":
    test_enhanced_conversational_style()
