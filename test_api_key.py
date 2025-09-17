#!/usr/bin/env python3
"""
API Key Validation Test
Quick test to verify the new OpenAI API key is working correctly
"""

import os
import sys
from dotenv import load_dotenv

def test_api_key():
    """Test the OpenAI API key functionality"""
    print("🔑 TESTING NEW OPENAI API KEY")
    print("=" * 40)
    
    # Load environment variables
    print("1. Loading environment variables...")
    load_dotenv(override=True)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"   ✅ API key loaded: {api_key[:20]}...{api_key[-10:]}")
    else:
        print("   ❌ API key not found in environment")
        return False
    
    # Test OpenAI import
    print("2. Testing OpenAI import...")
    try:
        from openai import OpenAI
        print("   ✅ OpenAI library imported successfully")
    except ImportError as e:
        print(f"   ❌ OpenAI import failed: {e}")
        return False
    
    # Test client initialization
    print("3. Testing OpenAI client initialization...")
    try:
        client = OpenAI(api_key=api_key)
        print("   ✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"   ❌ Client initialization failed: {e}")
        return False
    
    # Test API connection (simple call)
    print("4. Testing API connection...")
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )
        result = response.choices[0].message.content.strip()
        print(f"   ✅ API test successful: {result}")
        return True
    except Exception as e:
        print(f"   ❌ API call failed: {e}")
        return False

def test_backend_integration():
    """Test backend integration with new API key"""
    print("\n🔧 TESTING BACKEND INTEGRATION")
    print("=" * 40)
    
    try:
        # Test backend import
        print("1. Testing backend import...")
        from backend import LLMWorkflow, DomainDataLoader
        print("   ✅ Backend imported successfully")
        
        # Test workflow initialization
        print("2. Testing workflow initialization...")
        workflow = LLMWorkflow()
        print("   ✅ LLMWorkflow initialized")
        
        return True
    except Exception as e:
        print(f"   ❌ Backend integration failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 AI DATA ANALYTICS TOOL - API KEY VALIDATION")
    print("=" * 50)
    
    # Test API key
    api_success = test_api_key()
    
    # Test backend integration
    backend_success = test_backend_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION RESULTS")
    print("=" * 50)
    
    if api_success and backend_success:
        print("🟢 STATUS: SUCCESS!")
        print("✅ New API key is working correctly")
        print("✅ Backend integration successful")
        print("🚀 Ready to run the AI Data Analytics Tool!")
        print("\nNext step: streamlit run app.py")
    else:
        print("🔴 STATUS: ISSUES DETECTED")
        if not api_success:
            print("❌ API key validation failed")
        if not backend_success:
            print("❌ Backend integration failed")
        print("🔧 Please check the issues above")
    
    exit(0 if (api_success and backend_success) else 1)
