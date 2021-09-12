from zalo_tts import ZaloTTS
import os
from dotenv import load_dotenv

load_dotenv()


key = os.getenv("ZALO_TTS_API_KEY")

def speak(text):
    try:
        tts = ZaloTTS(speaker=ZaloTTS.SOUTH_WOMEN, api_key=key)
        tts.text_to_speech(text)
    except Exception:
        print("Speak có vấn đề")

