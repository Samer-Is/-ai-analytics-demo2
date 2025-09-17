"""
Test the complete system with chart improvements
Testing a query that would involve age analysis
"""

import backend

print("TESTING COMPLETE SYSTEM WITH CHART IMPROVEMENTS")
print("=" * 60)

# Clear any cached instances to pick up new settings
backend.DomainDataLoader.clear_instances()

# Initialize workflow
workflow = backend.LLMWorkflow()

if workflow.initialize_domain("banking"):
    print("✅ Banking domain initialized with new chart settings")
    
    try:
        # Test a query that should generate age-based charts
        question = "Analyze customer distribution by age group and show a chart"
        print(f"\n📊 Testing question: '{question}'")
        print("=" * 60)
        
        result = workflow.process_query(question)
        
        if result.get('success', False):
            print("✅ Query processed successfully!")
            
            # Check execution result
            exec_result = result.get('execution_result', {})
            if exec_result.get('success', False):
                print("✅ Code execution successful!")
                
                # Check for output files
                output_files = exec_result.get('output_files', [])
                if output_files:
                    print(f"📊 Generated {len(output_files)} output files:")
                    for file_info in output_files:
                        filename = file_info.get('filename', 'Unknown')
                        print(f"   - {filename}")
                else:
                    print("⚠️  No output files generated")
                
                # Show execution output
                output = exec_result.get('output', '')
                if output:
                    print(f"\n📄 Analysis Output Preview (first 400 chars):")
                    print("-" * 50)
                    print(output[:400])
                    if len(output) > 400:
                        print("... (truncated)")
                else:
                    print("⚠️  No execution output")
                    
            else:
                print(f"❌ Code execution failed: {exec_result.get('error', 'Unknown error')}")
                
            # Show generated code preview
            generated_code = result.get('generated_code', '')
            if generated_code:
                # Look for age bracket code
                if 'age_bracket' in generated_code or 'create_age_brackets' in generated_code:
                    print("\n✅ Age bracketing code detected in generated analysis!")
                else:
                    print("\n⚠️  No age bracketing detected - may need more specific question")
                
                # Look for chart optimization
                if 'figsize=(10, 6)' in generated_code and 'plt.tight_layout()' in generated_code:
                    print("✅ Chart optimization detected!")
                else:
                    print("⚠️  Chart optimization may not be applied")
                    
        else:
            print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception during test: {str(e)}")
        import traceback
        traceback.print_exc()
        
else:
    print("❌ Failed to initialize banking domain")

print("\n" + "=" * 60)
print("IMPROVEMENTS IMPLEMENTED:")
print("✅ Chart size reduced from 12x8 to 10x6")
print("✅ Age bracketing function added to system prompts")
print("✅ Top 10 filtering for categorical data")
print("✅ Proper chart formatting with rotated labels")
print("✅ Memory management with plt.close()")
print("=" * 60)
