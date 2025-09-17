import os
from dotenv import load_dotenv
from openai import OpenAI

def test_api_key():
    """Test OpenAI API key functionality"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    
    print("🔍 API Key Testing")
    print("=" * 50)
    print(f"API Key found: {bool(api_key)}")
    
    if not api_key:
        print("❌ No API key found in environment")
        return False
    
    print(f"API Key length: {len(api_key)}")
    print(f"API Key starts with: {api_key[:7]}...")
    
    # Test API connection
    print("\n🚀 Testing API Connection...")
    try:
        client = OpenAI(api_key=api_key)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user", 
                "content": "Hello! Please respond with exactly: 'API test successful'"
            }],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        
        print(f"✅ API Response: {result}")
        print(f"✅ Model used: {response.model}")
        print(f"✅ Tokens used: {response.usage.total_tokens}")
        print("\n🎉 API Key is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ API Test Failed: {str(e)}")
        
        # Provide specific error guidance
        error_str = str(e).lower()
        if "authentication" in error_str or "unauthorized" in error_str:
            print("\n💡 Suggestion: Check if your API key is correct")
        elif "quota" in error_str or "billing" in error_str:
            print("\n💡 Suggestion: Check your OpenAI account billing/usage limits")
        elif "model" in error_str:
            print("\n💡 Suggestion: Your account may not have access to GPT-4")
        
        return False

if __name__ == "__main__":
    test_api_key()
