"""
Builds the labeled corpus used for retrieval grounding, and a separate
golden-set candidate pool that explicitly excludes anything already in the
corpus (to avoid evaluating the agent on data it was grounded on).
"""
import time

import pandas as pd

from src.classify import classify_message
from src.client import get_client

PAIRS_PATH = "data/spotify_pairs.csv"
CORPUS_OUT_PATH = "data/spotify_corpus_labeled.csv"
GOLDEN_POOL_OUT_PATH = "data/golden_pool_sample.csv"

CORPUS_SIZE = 300
GOLDEN_POOL_SIZE = 200
REQUEST_DELAY_SECONDS = 1.5  # keep under Groq free-tier rate limit


def label_corpus(client, pairs: pd.DataFrame, n: int) -> pd.DataFrame:
    corpus = pairs.sample(n, random_state=42).copy().reset_index(drop=True)
    intents = []
    for i, msg in enumerate(corpus["customer_message_clean"]):
        result = classify_message(client, msg)
        intents.append(result.get("intent", "general_other"))
        if i % 25 == 0:
            print(f"{i}/{n} corpus messages labeled")
        time.sleep(REQUEST_DELAY_SECONDS)
    corpus["intent"] = intents
    return corpus


def main():
    client = get_client()
    pairs = pd.read_csv(PAIRS_PATH)

    corpus = label_corpus(client, pairs, CORPUS_SIZE)
    corpus.to_csv(CORPUS_OUT_PATH, index=False)
    print(f"Saved corpus: {corpus.shape} -> {CORPUS_OUT_PATH}")
    print(corpus["intent"].value_counts())

    # Golden pool excludes anything already in the corpus, so the agent isn't
    # evaluated on data it was implicitly grounded on.
    golden_pool = pairs[~pairs["tweet_id_customer"].isin(corpus["tweet_id_customer"])]
    golden_sample = golden_pool.sample(GOLDEN_POOL_SIZE, random_state=99).copy().reset_index(drop=True)
    golden_sample.to_csv(GOLDEN_POOL_OUT_PATH, index=False)
    print(f"Saved golden pool sample: {golden_sample.shape} -> {GOLDEN_POOL_OUT_PATH}")
    print("Next: run eval/sample_review_loop.py to review and produce golden_set_final.csv")


if __name__ == "__main__":
    main()
