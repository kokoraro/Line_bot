# api/openai_chat.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Get API key from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in environment.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Fixed system prompt
SYSTEM_PROMPT = "あなたは不動産の営業担当です。来店予約をゴールとして会話をリードしてください。"

def get_gpt_response(user_input: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",#"gpt-4-turbo",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR] OpenAI API call failed: {str(e)}"