"""
Retrieval grounding: embeds a labeled corpus of historical
(customer_message -> brand_reply) pairs, and retrieves the top-k most similar
past cases for a new incoming message. This is what lets drafted replies
reflect how Spotify has actually responded historically, rather than generic
LLM knowledge.
"""
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"


class Retriever:
    def __init__(self, corpus_path: str):
        self.corpus = pd.read_csv(corpus_path)
        self.embedder = SentenceTransformer(EMBED_MODEL_NAME)
        self.corpus_embeddings = self.embedder.encode(
            self.corpus["customer_message_clean"].tolist(), show_progress_bar=False
        )

    def retrieve(self, message: str, top_k: int = 3) -> list[dict]:
        query_embedding = self.embedder.encode([message])
        similarities = cosine_similarity(query_embedding, self.corpus_embeddings)[0]
        top_indices = similarities.argsort()[-top_k:][::-1]

        results = []
        for idx in top_indices:
            results.append(
                {
                    "customer_message": self.corpus.iloc[idx]["customer_message_clean"],
                    "brand_reply": self.corpus.iloc[idx]["brand_reply_clean"],
                    "intent": self.corpus.iloc[idx].get("intent", "unknown"),
                    "similarity": float(similarities[idx]),
                }
            )
        return results


if __name__ == "__main__":
    retriever = Retriever("data/spotify_corpus_labeled.csv")
    for r in retriever.retrieve("my app keeps crashing when I try to play a song"):
        print(f"[{r['similarity']:.2f}] {r['customer_message'][:70]} -> {r['brand_reply'][:70]}")
