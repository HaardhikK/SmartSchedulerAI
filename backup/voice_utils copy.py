from gtts import gTTS
import whisper
import os

import sounddevice as sd
import soundfile as sf

import speech_recognition as sr

def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        audio = r.listen(source, timeout=15)
    try:
        text = r.recognize_google(audio)  # Uses Google's free web API
        return text
    except Exception as e:
        print(f"Error: {e}")
        return ""

# Text-to-Speech (TTS) with gTTS
def text_to_speech(text, output_path="response.mp3"):
    tts = gTTS(text=text, lang='en')
    tts.save(output_path)
    os.system(f"start {output_path}")  # Play audio (Windows)

if __name__ == "__main__":
    # Test STT (record your voice)
    print("Speak now... (say something like 'hello')")
    text = speech_to_text()  # Requires a recorded audio file (see below)
    print(f"You said: {text}")

    # Test TTS (robot voice reply)
    text_to_speech(f"I heard: {text}")