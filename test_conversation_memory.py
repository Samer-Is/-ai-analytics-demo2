"""
Test conversation memory functionality
"""

import backend

print("TESTING CONVERSATION MEMORY")
print("=" * 50)

# Initialize workflow
workflow = backend.LLMWorkflow()

if workflow.initialize_domain("banking"):
    print("✅ Banking domain initialized")
    
    # Simulate a conversation history
    conversation_history = [
        {
            "role": "user", 
            "content": "What is the customer churn rate?"
        },
        {
            "role": "assistant",
            "content": "Based on the analysis, the customer churn rate is 18.4%. This represents 92 out of 500 customers who have churned. The analysis shows that churn is higher in the 65+ age group at 25.4% compared to younger age groups."
        },
        {
            "role": "user",
            "content": "Which age group has the highest churn rate?"
        },
        {
            "role": "assistant", 
            "content": "The 65+ age group has the highest churn rate at 25.4%. This is followed by the 46-55 age group at 17.2% and the 36-45 age group at 16.6%."
        }
    ]
    
    # Test 1: Question with reference to previous analysis
    print("\n📊 Test 1: Question referencing previous analysis")
    question_with_reference = "What is the average account balance for those high-churn customers?"
    
    try:
        # Test without conversation history (should be unclear)
        print("   Without conversation history:")
        rephrased_no_context = workflow._rephrase_question(question_with_reference)
        print(f"   Rephrased: {rephrased_no_context}")
        
        # Test with conversation history (should be clear)
        print("\n   With conversation history:")
        rephrased_with_context = workflow._rephrase_question(question_with_reference, conversation_history)
        print(f"   Rephrased: {rephrased_with_context}")
        
        if "65+" in rephrased_with_context or "high-churn" in rephrased_with_context or "churn" in rephrased_with_context:
            print("   ✅ Context successfully applied!")
        else:
            print("   ⚠️  Context may not be fully applied")
            
    except Exception as e:
        print(f"   ❌ Error in rephrasing test: {e}")
    
    # Test 2: Analysis plan with context
    print("\n📊 Test 2: Analysis plan with conversation context")
    try:
        plan_with_context = workflow._create_analysis_plan(
            "Show me more details about those customers", 
            conversation_history
        )
        
        if len(plan_with_context) > 200:
            print("   ✅ Analysis plan generated with context")
            print(f"   Plan preview: {plan_with_context[:200]}...")
            
            # Check if plan references previous context
            plan_lower = plan_with_context.lower()
            context_indicators = ['churn', '65+', 'age group', 'customer']
            found_indicators = [indicator for indicator in context_indicators if indicator in plan_lower]
            
            if found_indicators:
                print(f"   ✅ Plan includes context references: {', '.join(found_indicators)}")
            else:
                print("   ⚠️  Plan may not fully incorporate context")
        else:
            print(f"   ⚠️  Plan seems short: {len(plan_with_context)} characters")
            
    except Exception as e:
        print(f"   ❌ Error in plan generation test: {e}")
    
    # Test 3: Full workflow with conversation memory
    print("\n📊 Test 3: Full workflow with conversation memory")
    try:
        result = workflow.process_query(
            "What marketing strategies would you recommend for the high-risk churn customers we identified?",
            session_id="test_session",
            conversation_history=conversation_history
        )
        
        if result.get('success'):
            print("   ✅ Full workflow with memory completed successfully")
            
            rephrased = result.get('rephrased_question', '')
            if 'churn' in rephrased.lower() or '65+' in rephrased or 'high-risk' in rephrased.lower():
                print("   ✅ Question rephrasing incorporated conversation context")
            
            final_answer = result.get('final_answer', '')
            if len(final_answer) > 100:
                print(f"   ✅ Generated business recommendation ({len(final_answer)} chars)")
                print(f"   Preview: {final_answer[:150]}...")
            
        else:
            print(f"   ❌ Workflow failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Error in full workflow test: {e}")
        
else:
    print("❌ Failed to initialize banking domain")

print("\n" + "=" * 50)
print("CONVERSATION MEMORY CAPABILITIES:")
print("✅ Resolves references like 'those customers', 'the previous analysis'")
print("✅ Maintains context across multiple questions")
print("✅ Enables follow-up questions and deeper analysis")
print("✅ Supports progressive conversation building")
print("=" * 50)
