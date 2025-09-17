import os
from openai import OpenAI

# Read the API key directly from the .env file
with open('.env', 'r') as f:
    content = f.read()
    for line in content.split('\n'):
        if line.startswith('OPENAI_API_KEY='):
            api_key = line.split('=', 1)[1].strip()
            break

print(f"API Key from file: {api_key[:20]}...")
print(f"API Key length: {len(api_key)}")

# Test the API key
try:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say: API working perfectly"}],
        max_tokens=10
    )
    print(f"✅ SUCCESS: {response.choices[0].message.content}")
    print(f"✅ Model: {response.model}")
    print(f"✅ Tokens used: {response.usage.total_tokens}")
except Exception as e:
    print(f"❌ ERROR: {e}")
