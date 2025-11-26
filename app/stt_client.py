# app/stt_client.py

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


class LocalWhisperSTT:
    def __init__(self, model_size: str = "base") -> None:
        """
        STT local basé sur faster-whisper.
        model_size : tiny, base, small, medium, large-v2.
        'base' est un bon compromis sur Mac M4.
        """
        self.model = WhisperModel(model_size, device="cpu")

    def transcribe_from_microphone(self, duration: float = 4.0) -> str:
        samplerate = 16000
        channels = 1

        print("🎤 Enregistrement… Parlez maintenant.")

        audio = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=channels,
            dtype=np.float32,
        )
        sd.wait()

        audio = audio.flatten()

        # 🔒 Sécurité : si audio vide ou quasi silencieux, on ne transcrit pas
        if audio.size == 0 or np.max(np.abs(audio)) < 1e-4:
            print("⚠️ Audio silencieux détecté, pas de transcription.")
            return ""

        # Transcription avec filtre VAD interne de faster-whisper
        segments, _ = self.model.transcribe(
            audio,
            language="fr",
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
            ),
        )

        text = " ".join(seg.text for seg in segments).strip()
        return text
