import os
import io
from groq import Groq
from gtts import gTTS
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ClinicalAudioVoiceService:
    def __init__(self):
        # Establish direct client connection to Groq hardware clusters
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)

    def transcribe_audio_stream(self, audio_bytes: bytes, file_name: str = "input_audio.wav") -> str:
        """
        Dispatches a raw binary audio file to the Groq Whisper cloud endpoint.
        Returns a highly accurate, punctuated plaintext transcription string.
        """
        try:
            # Wrap raw binary file arrays into an in-memory file object
            audio_file = (file_name, audio_bytes, "audio/wav")
            
            # Execute ultra-low-latency speech-to-text transcription
            transcription = self.groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language="en",
                response_format="json"
            )
            return transcription.text
        except Exception as e:
            logger.error(f"Groq Whisper transcription pipeline failure: {str(e)}")
            return f"[Transcription Layer Processing Error: {str(e)}]"

    def synthesize_speech_bytes(self, text_content: str) -> io.BytesIO:
        """
        Converts a text string into an MP3 audio byte stream using gTTS.
        Perfect for running locally without needing massive CUDA model files.
        """
        try:
            # Strip markdown formatting symbols out before reading aloud
            clean_text = text_content.replace("**", "").replace("*", "").replace("`", "")
            
            audio_io_buffer = io.BytesIO()
            tts = gTTS(text=clean_text, lang="en", slow=False)
            tts.write_to_fp(audio_io_buffer)
            
            # Reset internal buffer pointer back to the beginning of the file stream
            audio_io_buffer.seek(0)
            return audio_io_buffer
        except Exception as e:
            logger.error(f"Speech synthesis processing exception: {str(e)}")
            return io.BytesIO()