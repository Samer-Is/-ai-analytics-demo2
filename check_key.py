import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if api_key:
    print(f'API key found: Yes')
    print(f'API key length: {len(api_key)}')
    print(f'API key ending: {api_key[-10:]}')
    print(f'Expected ending: ...aQQA')
    print(f'Correct key: {api_key.endswith("aQQA")}')
else:
    print('No API key found in environment')
