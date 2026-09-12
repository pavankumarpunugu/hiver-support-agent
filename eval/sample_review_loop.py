"""
Lightweight interactive review loop for producing the golden set. Run this
in a notebook or terminal — it prints one message + the model's suggested
intent/escalate at a time. Press Enter to accept, type a new intent to
correct it, 'e' to flip the escalate flag, or 's' to stop and save progress.

This exists purely to remove friction from the MECHANICS of labeling
(typing, file handling) — the judgment calls are still yours to make.
"""
import pandas as pd

from eval.baselines import simple_baseline
from src.classify import classify_message
from src.client import get_client
from src.escalate import decide_escalation
from src.retrieval import Retriever

INPUT_PATH = "data/golden_pool_sample.csv"  # unlabeled sample, e.g. 150-250 rows
OUTPUT_PATH = "data/golden_set_final.csv"


def main():
    client = get_client()
    retriever = Retriever("data/spotify_corpus_labeled.csv")
    df = pd.read_csv(INPUT_PATH)

    # Pre-fill suggestions to review-not-write-from-scratch
    rows = df.to_dict("records")
    for row in rows:
        msg = row["customer_message_clean"]
        classification = classify_message(client, msg)
        similar = retriever.retrieve(msg, top_k=3)
        escalate, reason = decide_escalation(
            classification.get("intent", "general_other"), similar, classification.get("confidence", "low")
        )
        row["suggested_intent"] = classification.get("intent", "general_other")
        row["suggested_escalate"] = escalate
        row["true_intent"] = row["suggested_intent"]
        row["true_escalate"] = row["suggested_escalate"]

    # Sort by agreement with a cheap baseline so review time goes to
    # genuinely ambiguous cases first, not messages both methods already agree on
    to_review = [r for r in rows if simple_baseline(r["customer_message_clean"])["intent"] != r["suggested_intent"]]
    print(f"{len(rows) - len(to_review)} auto-accepted (LLM + keyword baseline agree)")
    print(f"{len(to_review)} need your review\n")

    for i, row in enumerate(to_review):
        print(f"\n[{i + 1}/{len(to_review)}] {row['customer_message_clean']}")
        print(f"LLM guess: {row['suggested_intent']} | escalate={row['suggested_escalate']}")
        ans = input("Enter=keep, type intent to correct, 'e'=flip escalate, 's'=stop: ")
        if ans == "":
            continue
        elif ans == "e":
            row["true_escalate"] = not row["suggested_escalate"]
        elif ans == "s":
            break
        else:
            row["true_intent"] = ans.strip()

    pd.DataFrame(rows).to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
