from google.cloud import translate
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")

_translate_client = None

def get_translate_client():
    """Lazy load Translation client (avoids creating new GRPC connection per request)."""
    global _translate_client
    if _translate_client is None:
        print("🔹 Initializing Google Translate client...")
        _translate_client = translate.TranslationServiceClient()
        print("✅ Google Translate client ready")
    return _translate_client


def translate_to_english(text_to_check: str) -> dict:
    if not text_to_check or not text_to_check.strip():
        return {
            "original_text": "",
            "translated_text": "",
            "detected_language": "unknown",
            "was_translated": False
        }

    client = get_translate_client() 
    parent = f"projects/{PROJECT_ID}/locations/global"

    # Detect language (Google auto-detect)
    detection = client.detect_language(
        content=text_to_check,
        parent=parent
    )
    detected_lang = detection.languages[0].language_code

    # Already English → return as-is
    if detected_lang == "en":
        return {
            "original_text": text_to_check,
            "detected_language": detected_lang,
            "translated_text": text_to_check,
            "was_translated": False
        }

    # Translate into English
    response = client.translate_text(
        contents=[text_to_check],
        target_language_code="en",
        parent=parent
    )

    return {
        "original_text": text_to_check,
        "detected_language": detected_lang,
        "translated_text": response.translations[0].translated_text,
        "was_translated": True
    }
