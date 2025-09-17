"""
Quick test of the banking churn analysis with the fixes
"""

import backend

print("Testing Banking Churn Analysis with Fixes")
print("=" * 50)

# Initialize workflow
workflow = backend.LLMWorkflow()

# Initialize banking domain
if workflow.initialize_domain("banking"):
    print("✅ Banking domain initialized")
    
    try:
        # Test the churn rate question
        result = workflow.process_query("What is the customer churn rate?")
        
        print(f"\n📊 Query Success: {result.get('success', False)}")
        
        if result.get('success'):
            # Check execution result
            exec_result = result.get('execution_result', {})
            if exec_result.get('success'):
                print("✅ Code execution successful")
                output = exec_result.get('output', '')
                print(f"📄 Output length: {len(output)} characters")
                
                # Show first 500 characters of output
                if output:
                    print(f"\n🔍 Analysis Output Preview:")
                    print("-" * 40)
                    print(output[:500])
                    if len(output) > 500:
                        print("... (truncated)")
                else:
                    print("⚠️  No execution output found")
            else:
                print(f"❌ Code execution failed: {exec_result.get('error', 'Unknown error')}")
                
            # Show final answer
            final_answer = result.get('final_answer', '')
            if final_answer:
                print(f"\n📋 Final Answer Preview:")
                print("-" * 40)
                print(final_answer[:300])
                if len(final_answer) > 300:
                    print("... (truncated)")
        else:
            print(f"❌ Query processing failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception during test: {str(e)}")
        import traceback
        traceback.print_exc()
        
else:
    print("❌ Failed to initialize banking domain")

print("\n" + "=" * 50)
print("Test Complete")
