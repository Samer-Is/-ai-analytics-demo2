#!/usr/bin/env python3
"""
Debug Script for LLM Workflow Issues
Investigate why the LLM is not generating any code or analysis
"""

import os
from backend import LLMWorkflow, DomainDataLoader

def debug_llm_workflow():
    """Debug the LLM workflow to identify the root cause"""
    
    print("🔍 DEBUGGING LLM WORKFLOW")
    print("="*50)
    
    # 1. Check API Key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ No API Key found!")
        return
    
    # 2. Test Domain Loader
    try:
        loader = DomainDataLoader('banking')
        print(f"✅ Domain Loader working: {len(loader.schema_data['tables'])} tables")
    except Exception as e:
        print(f"❌ Domain Loader failed: {e}")
        return
    
    # 3. Test LLM Workflow initialization
    try:
        workflow = LLMWorkflow()
        print(f"✅ LLM Workflow initialized")
        print(f"   Model: {workflow.model}")
        print(f"   Client: {type(workflow.client)}")
    except Exception as e:
        print(f"❌ LLM Workflow initialization failed: {e}")
        return
    
    # 4. Test simple query
    print(f"\n🧪 Testing simple query...")
    try:
        simple_question = "How many customers are there in total?"
        result = workflow.process_query('banking', simple_question)
        
        print(f"Result keys: {list(result.keys())}")
        
        if 'error' in result:
            print(f"❌ Error found: {result['error']}")
            
        print(f"Generated code length: {len(result.get('generated_code', ''))}")
        print(f"Output length: {len(result.get('output', ''))}")
        
        if result.get('generated_code'):
            print(f"✅ Code generated successfully")
            print(f"First 200 chars: {result['generated_code'][:200]}...")
        else:
            print(f"❌ No code generated")
            
        if result.get('output'):
            print(f"✅ Output generated successfully")
            print(f"First 200 chars: {result['output'][:200]}...")
        else:
            print(f"❌ No output generated")
            
    except Exception as e:
        print(f"❌ Query processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_llm_workflow()
