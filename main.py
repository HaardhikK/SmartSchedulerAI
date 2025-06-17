from voice_utils import record_audio, speech_to_text, text_to_speech
from llm_utils import ask_llm
from calendar_integration import create_event
import dateparser
from datetime import datetime, timedelta
import json
import warnings
import pytz

# Ignore FP16 warning
warnings.filterwarnings("ignore", category=UserWarning, message="FP16 is not supported on CPU; using FP32 instead")

# Set timezone
IST = pytz.timezone('Asia/Kolkata')

def get_next_weekday(weekday_name):
    """Get the next occurrence of a specific weekday"""
    weekdays = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    # Use naive datetime, then localize
    today = datetime.now()
    target_weekday = weekdays.get(weekday_name.lower())
    
    if target_weekday is None:
        return None
    
    days_ahead = target_weekday - today.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    
    target_date = today + timedelta(days=days_ahead)
    return IST.localize(target_date)

def parse_natural_date(date_str):
    """Parse natural language dates with better accuracy"""
    # Handle specific cases first
    date_str_lower = date_str.lower()
    
    # Handle "next [weekday]"
    if date_str_lower.startswith("next "):
        weekday = date_str_lower.replace("next ", "").strip()
        next_date = get_next_weekday(weekday)
        if next_date:
            return next_date
    
    # Handle "this [weekday]" or just "[weekday]"
    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
        if day in date_str_lower and not date_str_lower.startswith("next"):
            next_date = get_next_weekday(day)
            if next_date:
                return next_date
    
    # Fall back to dateparser
    settings = {
        "TIMEZONE": "Asia/Kolkata",
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "future"
    }
    parsed = dateparser.parse(date_str, settings=settings)
    return parsed

def parse_datetime(date_str, time_str):
    """Parse date and time strings into datetime object"""
    parsed_date = parse_natural_date(date_str)
    if not parsed_date:
        return None
    
    try:
        # Parse time - handle 24h format from LLM
        if ':' in time_str:
            hour, minute = map(int, time_str.split(':'))
        else:
            hour = int(time_str)
            minute = 0
        
        # Create time object properly
        from datetime import time
        time_obj = time(hour, minute)
        
        # Create naive datetime then localize to IST  
        naive_dt = datetime.combine(parsed_date.date(), time_obj)
        # Remove any existing timezone info before localizing
        naive_dt = naive_dt.replace(tzinfo=None)
        return IST.localize(naive_dt)
            
    except Exception as e:
        print(f"Time parsing error: {e}")
        return None

def extract_event_info(text, conversation_context=""):
    """Extract event information using LLM with better context"""
    current_date = datetime.now(IST).strftime("%Y-%m-%d")
    current_day = datetime.now(IST).strftime("%A")
    
    extraction_prompt = f"""
Today is {current_day}, {current_date}. Extract event information from: "{text}"

Context from conversation: {conversation_context}

Return JSON with extracted info. If information is missing, use "unknown" for that field.
Make reasonable assumptions for missing details.

For dates: Convert "next Friday", "tomorrow", etc. to actual dates.
For times: Convert "4 PM", "evening", "morning" to 24-hour format.

{{
  "title": "Meeting title",
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "location": "location or unknown",
  "participants": "people involved or unknown",
  "action": "schedule" or "chat"
}}

If the user is just chatting (not scheduling), set action to "chat".
"""
    
    try:
        response = ask_llm(extraction_prompt)
        return json.loads(response)
    except:
        return {"action": "chat"}

def main():
    print("🎙️ Smart Scheduler Voice Agent (Say 'stop' to exit)")
    print("You can chat naturally - just mention scheduling when you want to create events!\n")
    
    conversation_context = ""
    
    while True:
        try:
            # Record and transcribe
            audio_file = record_audio(duration=8)
            user_input = speech_to_text(audio_file)
            print(f"🗣️ You: {user_input}")
            
            # Check for exit commands
            if any(cmd in user_input.lower() for cmd in ["stop", "exit", "quit", "goodbye"]):
                text_to_speech("Goodbye! Have a great day!")
                break
            
            # Add to conversation context
            conversation_context += f"User: {user_input}\n"
            
            # Extract event information
            event_info = extract_event_info(user_input, conversation_context)
            
            if event_info.get("action") == "schedule":
                # Try to schedule the event
                if (event_info.get("date") != "unknown" and 
                    event_info.get("start_time") != "unknown"):
                    
                    # Parse the datetime
                    start_dt = parse_datetime(event_info["date"], event_info["start_time"])
                    
                    # Calculate end time if not provided
                    if event_info.get("end_time") == "unknown":
                        end_dt = start_dt + timedelta(hours=1)  # Default 1 hour
                    else:
                        end_dt = parse_datetime(event_info["date"], event_info["end_time"])
                    
                    if start_dt and end_dt:
                        # Create the event
                        event = create_event(
                            event_info.get("title", "Scheduled Meeting"),
                            start_dt,
                            end_dt,
                            location=event_info.get("location", ""),
                            description=f"Participants: {event_info.get('participants', 'Not specified')}"
                        )
                        
                        # Format the confirmation
                        day_name = start_dt.strftime("%A")
                        date_str = start_dt.strftime("%B %d")
                        time_str = start_dt.strftime("%I:%M %p")
                        
                        reply = f"Perfect! I've scheduled '{event_info['title']}' for {day_name}, {date_str} at {time_str}."
                        text_to_speech(reply)
                        conversation_context += f"Assistant: {reply}\n"
                    else:
                        reply = "I couldn't understand the date or time. Could you please repeat that?"
                        text_to_speech(reply)
                else:
                    # Ask for missing information
                    missing = []
                    if event_info.get("date") == "unknown":
                        missing.append("date")
                    if event_info.get("start_time") == "unknown":
                        missing.append("time")
                    
                    reply = f"I'd be happy to schedule that! Could you tell me the {' and '.join(missing)}?"
                    text_to_speech(reply)
                    conversation_context += f"Assistant: {reply}\n"
            
            else:
                # Handle as normal conversation
                chat_prompt = f"""
You are a helpful scheduling assistant. The user said: "{user_input}"

Recent conversation:
{conversation_context}

Respond naturally and helpfully. If they mention scheduling something, guide them gently.
Keep responses conversational and brief.
"""
                
                response = ask_llm(chat_prompt)
                # Clean up any JSON artifacts from response
                if response.startswith('{') and response.endswith('}'):
                    try:
                        parsed = json.loads(response)
                        response = parsed.get('response', response)
                    except:
                        pass
                
                text_to_speech(response)
                conversation_context += f"Assistant: {response}\n"
            
            # Keep conversation context manageable
            if len(conversation_context) > 1000:
                conversation_context = conversation_context[-800:]
                
        except KeyboardInterrupt:
            text_to_speech("Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            text_to_speech("Sorry, I encountered an error. Please try again.")

if __name__ == "__main__":
    main()