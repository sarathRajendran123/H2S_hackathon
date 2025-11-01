from google.cloud import translate
import os
from dotenv import load_dotenv

load_dotenv()

key_path = os.getenv("SERVICE_ACCOUNT_PATH", "gen-ai-h2s-project-562ce7c50fcf-vertex-ai.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

def translate_to_english(text_to_check: str) -> dict:
    client = translate.TranslationServiceClient()

    project_id = os.getenv("PROJECT_ID", "gen-ai-h2s-project-562ce7c50fcf")
    parent = f"projects/{project_id}/locations/global"

    # Detect language
    detection = client.detect_language(
        content=text_to_check,
        parent=parent
    )
    detected_lang = detection.languages[0].language_code

    # If already English
    if detected_lang == "en":
        return {
            "original_text": text_to_check,
            "detected_language": detected_lang,
            "translated_text": text_to_check,
            "was_translated": False
        }

    # Translate to English
    response = client.translate_text(
        contents=[text_to_check],
        target_language_code="en",
        parent=parent
    )

    translated_text = response.translations[0].translated_text

    return {
        "original_text": text_to_check,
        "detected_language": detected_lang,
        "translated_text": translated_text,
        "was_translated": True
    }