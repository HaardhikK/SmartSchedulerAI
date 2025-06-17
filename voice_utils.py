import whisper
import sounddevice as sd
from scipy.io.wavfile import write
import pyttsx3
import warnings

# Suppress FP16 CPU warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Initialize Whisper model and TTS engine once
model = whisper.load_model("base")
tts_engine = pyttsx3.init()

def record_audio(filename="input.wav", duration=10, fs=44100):
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, recording)
    print(f"Saved recording to {filename}")
    return filename

def speech_to_text(audio_path: str) -> str:
    print("Transcribing audio...")
    result = model.transcribe(audio_path)
    return result["text"]

def text_to_speech(text: str):
    print("Speaking:", text)
    tts_engine.say(text)
    tts_engine.runAndWait()

