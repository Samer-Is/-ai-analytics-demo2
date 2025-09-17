import os

# Clear any existing environment variable
if 'OPENAI_API_KEY' in os.environ:
    del os.environ['OPENAI_API_KEY']

# Read directly from the .env file
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('OPENAI_API_KEY='):
            api_key = line.split('=', 1)[1].strip()
            os.environ['OPENAI_API_KEY'] = api_key
            break

# Check the result
api_key = os.getenv('OPENAI_API_KEY')
print(f'API key ending: {api_key[-10:] if api_key else "None"}')
print(f'Expected ending: ...aQQA')
print(f'Correct: {api_key.endswith("aQQA") if api_key else False}')
