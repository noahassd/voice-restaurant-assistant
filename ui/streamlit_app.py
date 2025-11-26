import streamlit as st
import sys
import os

# Chemin de la racine du projet
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from agents.orchestrator import Orchestrator
from app.stt_client import LocalWhisperSTT
from app.tts_client import LocalTTS


def main():
    st.title("🍽️ Voice-Enabled GenAI Restaurant Assistant (Voix)")

    # Initialisation
    if "orch" not in st.session_state:
        st.session_state["orch"] = Orchestrator()
    if "stt" not in st.session_state:
        st.session_state["stt"] = None
    if "tts" not in st.session_state:
        st.session_state["tts"] = LocalTTS()

    orch = st.session_state["orch"]
    stt = st.session_state["stt"]
    tts = st.session_state["tts"]

    # Résultat interactif
    user_text = st.text_input("Ou tape ton message :")

    if st.button("Envoyer"):
        resp = orch.handle_user_input(user_text)
        st.session_state["assistant_text"] = resp.assistant_text

    if st.button("🎤 Parler"):
        with st.spinner("Écoute en cours..."):
            if st.session_state["stt"] is None:
                st.session_state["stt"] = LocalWhisperSTT()

            text = st.session_state["stt"].transcribe_from_microphone()
            if not text:
                st.warning("Je n'ai rien entendu, pouvez-vous répéter ?")
            else:
                st.write(f"**Vous (voix) :** {text}")
                resp = orch.handle_user_input(text)
                st.session_state["assistant_text"] = resp.assistant_text


    # Affichage de la réponse
    if "assistant_text" in st.session_state:
        st.write(f"**Assistant :** {st.session_state['assistant_text']}")

        # 🔊 Synthèse vocale
        # ...existing code...
        if st.button("🔊 Lire la réponse"):
            audio_path = tts.synthesize(st.session_state["assistant_text"])
            with open(audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/wav")


if __name__ == "__main__":
    main()
