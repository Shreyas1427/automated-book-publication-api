import whisper
import logging
import os

try:
    logging.info("Loading Whisper speech-to-text model...")
    model = whisper.load_model("base")
    logging.info("Whisper model loaded successfully.")
except Exception as e:
    logging.error(f"Could not load Whisper model: {e}")
    model = None

def transcribe_audio_to_text(audio_file_path: str) -> str | None:
    if not model:
        logging.error("Whisper model is not available. Cannot transcribe.")
        return None
    
    try:
        logging.info(f"Transcribing audio file: {audio_file_path}")
        result = model.transcribe(audio_file_path)
        transcribed_text = result['text']
        logging.info(f"Transcription successful. Text: '{transcribed_text}'")
        return transcribed_text
    except Exception as e:
        logging.error(f"An error occurred during transcription: {e}")
        return None
    finally:
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
            logging.info(f"Removed temporary audio file: {audio_file_path}")