#!/usr/bin/env python3
"""
Test OpenAI API and Model Availability
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_openai_models():
    """Test OpenAI API connection and model availability"""
    
    print("🧪 TESTING OPENAI API AND MODELS")
    print("="*50)
    
    # Initialize client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Test API connection
    try:
        models = client.models.list()
        print(f"✅ API Connection successful")
        print(f"Total models available: {len(models.data)}")
    except Exception as e:
        print(f"❌ API Connection failed: {e}")
        return
    
    # Check for GPT models
    gpt_models = [model.id for model in models.data if 'gpt' in model.id.lower()]
    print(f"\n📋 Available GPT Models:")
    for model in sorted(gpt_models):
        print(f"   - {model}")
    
    # Test specific models
    test_models = ['gpt-5', 'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo']
    
    for model_name in test_models:
        print(f"\n🧪 Testing {model_name}...")
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Hello, respond with just 'working'"}],
                max_tokens=10
            )
            print(f"✅ {model_name}: {response.choices[0].message.content}")
        except Exception as e:
            print(f"❌ {model_name}: {str(e)}")

if __name__ == "__main__":
    test_openai_models()
