import requests
import os
from dotenv import load_dotenv

# check if this code works properly

load_dotenv()
API_KEY = os.getenv("SONAR_API_KEY")

def ask_sonar(prompt):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "sonar-small-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful study assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]
