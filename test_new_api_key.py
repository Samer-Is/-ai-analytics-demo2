#!/usr/bin/env python3
"""
Test OpenAI API with new key and check available models
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

def test_new_api_key():
    """Test the new API key and check available models"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"🔑 Testing API Key: {api_key[:20]}...{api_key[-10:] if api_key else 'None'}")
    
    if not api_key:
        print("❌ No API key found!")
        return False
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Test basic API connection
        print("\n📡 Testing API connection...")
        
        # List available models
        models = client.models.list()
        print(f"✅ API connection successful! Found {len(models.data)} models")
        
        # Check for specific models we need
        model_names = [model.id for model in models.data]
        
        print("\n🤖 Checking for required models:")
        
        required_models = ['gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-3.5-turbo']
        available_required = []
        
        for model in required_models:
            if model in model_names:
                available_required.append(model)
                print(f"   ✅ {model} - Available")
            else:
                print(f"   ❌ {model} - Not Available")
        
        # Check for GPT-5
        gpt5_models = [m for m in model_names if 'gpt-5' in m.lower()]
        if gpt5_models:
            print(f"\n🚀 GPT-5 Models Found:")
            for model in gpt5_models:
                print(f"   ✅ {model}")
        else:
            print(f"\n⚠️  No GPT-5 models found")
        
        # Test with a simple completion
        print(f"\n🧪 Testing with simple completion...")
        
        test_model = 'gpt-4o' if 'gpt-4o' in available_required else available_required[0] if available_required else 'gpt-3.5-turbo'
        
        response = client.chat.completions.create(
            model=test_model,
            messages=[
                {"role": "user", "content": "Say 'API Test Successful' and nothing else."}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        print(f"   Model: {test_model}")
        print(f"   Response: {result}")
        
        if "API Test Successful" in result:
            print("   ✅ Test completion successful!")
            return True, test_model, available_required
        else:
            print("   ⚠️  Unexpected response")
            return True, test_model, available_required
            
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False, None, []

def main():
    print("🔬 TESTING NEW OPENAI API KEY")
    print("="*50)
    
    success, best_model, available_models = test_new_api_key()
    
    if success:
        print(f"\n✅ SUCCESS! API key is working")
        print(f"📝 Recommended model: {best_model}")
        print(f"📋 Available models: {', '.join(available_models)}")
        
        # Update backend to use working model
        if best_model:
            print(f"\n🔧 Updating backend to use: {best_model}")
            return best_model
    else:
        print(f"\n❌ FAILED! API key is not working")
        return None

if __name__ == "__main__":
    main()
