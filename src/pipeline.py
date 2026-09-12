"""End-to-end pipeline: classify -> retrieve -> draft -> escalate."""
from src.classify import classify_message
from src.client import get_client
from src.escalate import decide_escalation
from src.reply import draft_reply
from src.retrieval import Retriever


class SupportAgent:
    def __init__(self, corpus_path: str = "data/spotify_corpus_labeled.csv"):
        self.client = get_client()
        self.retriever = Retriever(corpus_path)

    def handle_message(self, message: str) -> dict:
        classification = classify_message(self.client, message)
        intent = classification.get("intent", "general_other")
        confidence = classification.get("confidence", "low")

        similar_cases = self.retriever.retrieve(message, top_k=3)
        reply = draft_reply(self.client, message, intent, similar_cases)
        escalate, reason = decide_escalation(intent, similar_cases, confidence)

        return {
            "message": message,
            "intent": intent,
            "confidence": confidence,
            "reply": reply,
            "escalate": escalate,
            "reason": reason,
        }


if __name__ == "__main__":
    agent = SupportAgent()
    result = agent.handle_message("my app keeps crashing every time I try to play a song")
    for k, v in result.items():
        print(f"{k}: {v}\n")
