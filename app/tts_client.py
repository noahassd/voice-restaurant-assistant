from huggingface_hub import InferenceClient
import os
import tempfile

class LocalTTS:
    def __init__(self):
        self.client = InferenceClient(
            token="",
        )

    def synthesize(self, text: str) -> str:
        audio_bytes = self.client.text_to_speech(
            text=text,
            model="facebook/mms-tts-fra",
        )

        fd, path = tempfile.mkstemp(suffix=".wav")
        with open(path, "wb") as f:
            f.write(audio_bytes)

        return path
