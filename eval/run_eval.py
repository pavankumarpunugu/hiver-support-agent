"""
Automated metrics + LLM-as-judge for reply quality.

IMPORTANT: this script expects data/golden_set_final.csv to exist, containing
YOUR OWN hand-reviewed labels (true_intent, true_escalate columns). See
data/README.md for how that file is produced — it is not generated here,
because the point of the golden set is that a human (you) reviewed it.
"""
import json

import pandas as pd
from sklearn.metrics import classification_report, precision_recall_fscore_support

from eval.baselines import simple_baseline, trivial_baseline
from src.client import get_client
from src.pipeline import SupportAgent

GOLDEN_SET_PATH = "data/golden_set_final.csv"
CORPUS_PATH = "data/spotify_corpus_labeled.csv"

JUDGE_PROMPT = """You are evaluating a customer support reply for quality.

Customer message: "{message}"
Agent's reply: "{reply}"
Historical grounding context (how the brand has replied to similar issues before):
{grounding}

Rate the reply on a 1-5 scale for each dimension:
- grounded: does it match the brand's actual historical tone/approach?
- correct: is the information/action it suggests appropriate for this issue?
- tone: is it polite, on-brand, appropriately concise for Twitter?

Respond with ONLY valid JSON:
{{"grounded": <1-5>, "correct": <1-5>, "tone": <1-5>}}
"""


def judge_reply(client, message: str, reply: str, grounding: str) -> dict:
    prompt = JUDGE_PROMPT.format(message=message, reply=reply, grounding=grounding)
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        reasoning_effort="low",
    )
    text = response.choices[0].message.content.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"grounded": None, "correct": None, "tone": None}


def run_intent_eval(golden: pd.DataFrame, agent: SupportAgent, majority_intent: str) -> None:
    y_true = golden["true_intent"].tolist()

    agent_preds, trivial_preds, simple_preds = [], [], []
    for msg in golden["customer_message_clean"]:
        agent_preds.append(agent.handle_message(msg)["intent"])
        trivial_preds.append(trivial_baseline(msg, majority_intent)["intent"])
        simple_preds.append(simple_baseline(msg)["intent"])

    for name, preds in [("Agent", agent_preds), ("Trivial baseline", trivial_preds), ("Simple baseline", simple_preds)]:
        print(f"\n=== {name} ===")
        print(classification_report(y_true, preds, zero_division=0))


def run_judge_agreement_check(agent: SupportAgent, sample_df: pd.DataFrame, human_scores_path: str = None) -> None:
    """
    Runs the LLM judge on a sample and, if you provide your own hand-scored
    CSV (human_scores_path), computes agreement between judge and human.
    See report/REPORT.md for how this was done and the resulting agreement rate.
    """
    client = get_client()
    judge_results = []
    for _, row in sample_df.iterrows():
        result = agent.handle_message(row["customer_message_clean"])
        grounding = "\n".join(
            c["brand_reply"] for c in agent.retriever.retrieve(row["customer_message_clean"], top_k=3)
        )
        score = judge_reply(client, row["customer_message_clean"], result["reply"], grounding)
        judge_results.append({**result, **score})
    pd.DataFrame(judge_results).to_csv("eval/judge_results.csv", index=False)
    print("Saved judge_results.csv — hand-score a subset of these yourself and compare, per REPORT.md")


if __name__ == "__main__":
    golden = pd.read_csv(GOLDEN_SET_PATH)
    corpus = pd.read_csv(CORPUS_PATH)
    majority_intent = corpus["intent"].value_counts().idxmax()

    agent = SupportAgent(CORPUS_PATH)
    run_intent_eval(golden, agent, majority_intent)
    run_judge_agreement_check(agent, golden.sample(min(30, len(golden)), random_state=1))
