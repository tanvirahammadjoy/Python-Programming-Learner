from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("WEATHER_API_KEY")

if api_key:
    print(f"✅ API key loaded: {api_key[:5]}...")  # Shows first 5 chars only
else:
    print("❌ API key not found! Check your .env file")