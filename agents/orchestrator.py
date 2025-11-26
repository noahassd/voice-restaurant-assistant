from dataclasses import dataclass
from typing import Literal, Optional
import re

from agents.reservation_agent import ReservationAgent   
from app.llm_client import get_llm_client

Intent = Literal["reservation", "menu", "order", "info", "unknown"]


@dataclass
class OrchestratorResponse:
    intent: Intent
    assistant_text: str


class Orchestrator:
    """
    Orchestrateur très simple V1 :
    - détecte un intent basique via des mots-clés
    - appelle le LLM pour formuler la réponse
    """

    def __init__(self) -> None:
        self.llm = get_llm_client()
        self.reservation_agent = ReservationAgent()

    def _detect_intent(self, user_text: str) -> Intent:
        text = user_text.lower()

        if any(w in text for w in ["réserver", "reservation", "table", "book", "booking"]):
            return "reservation"
        if any(w in text for w in ["menu", "plat", "dish", "allergène", "allergen"]):
            return "menu"
        if any(w in text for w in ["à emporter", "emporter", "take away", "takeaway", "commande"]):
            return "order"
        if any(w in text for w in ["horaire", "heures", "ouvert", "adresse", "location"]):
            return "info"
        return "unknown"


    def _extract_via_llm(self, user_text: str) -> Optional[int]:
        messages = [
            {
                "role": "system",
                "content": (
                    "Analyse le message utilisateur et renvoie STRICTEMENT un JSON de la forme : "
                    "{\"people\": <nombre ou null>}.\n"
                    "N'invente rien. Si le nombre n'est pas clair, people = null."
                )
            },
            {
                "role": "user",
                "content": user_text
            }
        ]

        raw = self.llm.generate(messages)

        # Exemple reçu : {"people": 4}
        raw = raw.strip()

        try:
            import json
            data = json.loads(raw)
            return data.get("people", None)
        except Exception:
            return None



    def _extract_number(self, text: str) -> int | None:
        text = text.lower()

        # 🔥 1. On ignore "une table", "un table", "une réservation", etc.
        if "une table" in text or "un table" in text or "une reservation" in text or "une réservation" in text:
            # On continue l'extraction mais sans compter "une"
            pass

        # 2. Extraction chiffres explicites
        m = re.search(r'\b(\d+)\b', text)
        if m:
            return int(m.group(1))

        # 3. Mots → chiffres mais AVEC FILTRE
        words_to_num = {
            "deux": 2, "trois": 3, "quatre": 4, "cinq": 5,
            "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10
        }

        # 🔥 On retire "un" et "une" pour éviter "une table" = 1 personne
        tokens = text.split()
        for w, n in words_to_num.items():
            if w in tokens:
                return n

        # Si on arrive ici : pas de nombre détecté
        return None


    def handle_user_input(self, user_text: str) -> OrchestratorResponse:
        intent = self._detect_intent(user_text)

        system_prompt = (
    "Tu es un assistant virtuel de restaurant. "
    "Tu reformules la réponse que je t’envoie, en français, de manière claire et polie. "
    "⚠️ Très important : tu ne dois JAMAIS confirmer une réservation, ni inventer une disponibilité, "
    "ni proposer spontanément une table. "
    "Tu ne fais QUE reformuler le texte fourni. "
    "Tu ne dois rien ajouter, rien déduire, rien inventer."
)


        if intent == "reservation":
            # extraction basique : on cherche un chiffre dans la phrase
            num_people = self._extract_via_llm(user_text)

            if num_people is None:
                result_text = "Pour quelle taille de groupe souhaitez-vous réserver ?"
            else:
                res = self.reservation_agent.find_table(num_people)
                if getattr(res, "success", False):
                    table_id = getattr(res, "table_id", "inconnue")
                    result_text = f"Très bien, j’ai une table disponible pour {num_people} personnes : la table {table_id}. Souhaitez-vous confirmer ?"
                else:
                    alt = getattr(res, "alternative", None)
                    if alt:
                        result_text = f"Je n’ai pas de table parfaite pour {num_people} personnes, mais une table alternative est disponible : table {alt}. Souhaitez-vous la réserver ?"
                    else:
                        result_text = "Je suis désolé, aucune table n’est disponible pour le moment."

            # On laisse le LLM reformuler plus naturellement
            messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                "Reformule ce texte sans rien ajouter ni interpréter :\n"
                f"{result_text}"
                ),
            },
            ]

            answer = self.llm.generate(messages)

            return OrchestratorResponse(intent=intent, assistant_text=answer)

        # Pour les autres intents, on laisse le LLM répondre directement, en lui indiquant l’intent détecté.
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Intent détecté : {intent}. Demande du client : {user_text}",
            },
        ]

        answer = self.llm.generate(messages)
        return OrchestratorResponse(intent=intent, assistant_text=answer)