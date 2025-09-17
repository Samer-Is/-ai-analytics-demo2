"""
Quick verification that dataframes loading code is working
"""

import backend

# Test the dataframes loading code generation
loader = backend.DomainDataLoader("banking")
loading_code = loader.get_dataframes_loading_code()

print("DATAFRAMES LOADING CODE TEST")
print("=" * 50)
print("Generated loading code:")
print("-" * 30)
print(loading_code)
print("-" * 30)

# Test if the code can execute
print("\nTesting code execution...")
executor = backend.LocalCodeExecutor()
result = executor.execute_code(loading_code)

print(f"Execution Success: {result['success']}")
if result['success']:
    print("✅ DataFrames loading code works!")
    print("Output:")
    print(result['output'])
else:
    print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
print("\n" + "=" * 50)
