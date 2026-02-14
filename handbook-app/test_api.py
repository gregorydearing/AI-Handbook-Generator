import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Get API key
api_key = os.getenv('DEEPSEEK_API_KEY')
print(f"API Key loaded: {api_key[:10]}..." if api_key else "NO API KEY FOUND!")

# Initialize client
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# Test simple message
print("\nTesting DeepSeek API...")

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"}
        ],
        max_tokens=100
    )

    print("✅ SUCCESS!")
    print(f"Response: {response.choices[0].message.content}")

except Exception as e:
    print(f"❌ ERROR: {e}")
    print(f"\nError type: {type(e)}")
    print(f"\nFull error: {str(e)}")
