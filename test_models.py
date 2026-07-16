import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}&pageSize=1000"
response = requests.get(url)
models = response.json().get('models', [])
for m in models:
    print(m['name'])
