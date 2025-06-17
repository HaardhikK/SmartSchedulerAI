# SmartSchedulerAI 🧠📅

SmartSchedulerAI is an intelligent voice-activated scheduling assistant that understands natural language inputs like “Schedule a meeting next Friday at 3 PM” and automatically creates events on your Google Calendar. It combines Speech Recognition, LLMs (via Groq), natural date parsing, and Google Calendar API to provide a seamless scheduling experience.

---

## 🚀 Features

- 🎙️ Voice-based interaction using Speech-to-Text (STT)
- 🤖 LLM-powered understanding via Groq API (e.g., LLaMA3-70B)
- 📅 Natural language date and time parsing (e.g., "next Monday evening")
- 📆 Google Calendar integration for real-time event creation
- 🔁 TTS responses for conversational flow
- 📂 Modular and easy-to-extend Python codebase

---

## 🛠️ Tech Stack

- **Python 3**
- **Google Calendar API**
- **Groq API** (LLaMA3-70B)
- **`dateparser`** – Natural language to datetime
- **`SpeechRecognition`, `pyttsx3`** – For STT and TTS
- **Function calling-style prompts** for structured event creation

---

## 📁 Project Structure

```

SmartSchedulerAI/
├── main.py                  # Main orchestration logic
├── voice\_utils.py          # Voice input/output (STT + TTS)
├── calendar\_integration.py # Google Calendar API logic
├── llm\_utils.py            # Groq API integration (LLM + function calling)
├── prompts/
│   └── scheduler\_prompt.txt # Prompt template for LLM
├── .env                    # API keys and secrets
└── requirements.txt

````

---

## 🔧 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/SmartSchedulerAI.git
   cd SmartSchedulerAI
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your `.env` file**
   Add the following:

   ```env
   GROQ_API_KEY=your_groq_api_key
   GOOGLE_CREDENTIALS_PATH=path_to_your_service_account.json
   ```

4. **Run the application**

   ```bash
   python main.py
   ```

---

## ✨ Example Command

> 🗣️ *"Schedule a meeting with Anjali next Tuesday at 4 PM for 2 hours"*

* The LLM interprets the intent and fills structured data.
* `dateparser` converts the natural language into a proper datetime.
* Google Calendar API creates the event.
* TTS confirms the event:
  **"Scheduled meeting with Anjali on Tuesday, 18 June at 4:00 PM."**

---

## ✅ TODO

* [ ] Add conflict detection with existing events
* [ ] UI version with Streamlit
* [ ] Support for recurring events
* [ ] Multi-user and authentication support

---


