import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-70b-8192"

def get_system_prompt():
    """Generate dynamic system prompt with current date/time"""
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    current_date = now.strftime("%Y-%m-%d")
    current_day = now.strftime("%A")
    
    return f"""You are a helpful, conversational scheduling assistant. 

CURRENT CONTEXT:
- Today is {current_date} ({current_day})
- Timezone: Asia/Kolkata (IST)

INSTRUCTIONS:
1. Respond naturally and conversationally
2. Extract scheduling information when mentioned
3. Make reasonable assumptions for missing details
4. Convert natural language dates/times accurately

DATE CONVERSION RULES:
- "next Friday" = the upcoming Friday (not this week if today is Friday)
- "Friday" = the next occurring Friday  
- "tomorrow" = the next day
- "this weekend" = upcoming Saturday/Sunday

TIME CONVERSION:
- "5 PM", "5pm", "17:00" → "17:00"
- "4 PM", "4pm", "16:00" → "16:00" 
- "morning" → "09:00" 
- "afternoon" → "14:00"
- "evening" → "18:00"

RESPONSE FORMAT:
For scheduling requests, return JSON:
{{
  "action": "schedule",
  "title": "extracted or inferred title",
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM", 
  "end_time": "HH:MM",
  "location": "location or unknown",
  "participants": "people or unknown"
}}

For normal conversation, return JSON:
{{
  "action": "chat",
  "response": "your natural response"
}}

Be helpful, friendly, and make scheduling easy!"""

def ask_llm(prompt, messages=None):
    """Send request to LLM with dynamic system prompt"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Build messages with current system prompt
    full_messages = [{"role": "system", "content": get_system_prompt()}]
    
    if messages:
        full_messages.extend(messages)
    elif prompt:
        full_messages.append({"role": "user", "content": prompt})

    data = {
        "model": MODEL,
        "messages": full_messages,
        "temperature": 0.3,
        "max_tokens": 1000
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"LLM API error: {e}")
        return '{"action": "chat", "response": "I apologize, but I encountered an error. Please try again."}'
