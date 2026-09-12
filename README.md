# Spotify Support Agent — Hiver SDE Intern Take-Home

An AI support agent built on the [Customer Support on Twitter](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter)
dataset, focused on **@SpotifyCares**. Classifies incoming customer messages into
intents, drafts a reply grounded in how Spotify has historically resolved similar
issues, and decides whether to auto-handle or escalate — with a stated reason.

## Why Spotify?

Out of the brands in the dataset (AmazonHelp, AppleSupport, Uber_Support, Delta,
etc.), SpotifyCares (~43k replies) hit a sweet spot: enough volume to have real
recurring patterns, but a narrow enough product surface that a 6-intent taxonomy
covers the vast majority of traffic without becoming a junk-drawer `general_other`
category.

## Architecture

```
Customer message
      │
      ▼
[1] Classify intent  ──── LLM (few-shot prompt) → one of 6 intents + confidence
      │
      ▼
[2] Retrieve grounding ── embed message → cosine similarity vs. historical
      │                   (customer message → Spotify's actual reply) pairs
      ▼
[3] Draft reply ────────  LLM, prompted with top-3 retrieved historical replies
      │                   as style/content grounding
      ▼
[4] Decide escalation ──  rules (sensitive intents, low confidence, weak
      │                   grounding) → auto-handle or escalate + reason
      ▼
Output: {intent, reply, escalate, reason}
```

## Reproducing this (under 15 minutes)

**You need:** a free [Groq](https://console.groq.com) API key (no credit card
required) and the Kaggle dataset attached (or downloaded locally).

1. `pip install -r requirements.txt`
2. Set your Groq key: `export GROQ_API_KEY=your_key_here`
3. Place `twcs.csv` in `data/raw/` (from the Kaggle dataset), or run in a Kaggle
   Notebook with the dataset attached at the default path.
4. Run the pipeline end to end — **note the `-m` flag and running from the repo
   root**; this project uses package-style imports (`from src.x import y`),
   which only resolve correctly when Python is invoked this way, not as
   `python src/pipeline.py`:
   ```
   python -m src.data_prep      # filters to SpotifyCares, builds message/reply pairs
   python -m src.build_corpus   # labels a retrieval corpus + a separate golden-set candidate pool
   python -m eval.sample_review_loop  # interactive: review/correct labels -> golden_set_final.csv
   python -m src.pipeline       # runs classify + retrieve + draft + escalate on a sample input
   python -m eval.run_eval      # scores against golden set + baselines
   ```
5. See `eval/results.md` for the generated metrics table.

Full run on the provided subsample takes under 15 minutes on Groq's free tier
(rate-limited to ~30 req/min — see Decision Log for why this bounds sample sizes).

## Repo structure

```
src/            Core pipeline: data prep, classification, retrieval, reply drafting, escalation
eval/           Eval harness: baselines, metrics, LLM-judge, golden set
data/           Raw + processed data (small subsample only, not full 3M-row dataset)
report/         REPORT.md (problem framing, results, failure analysis) and DECISION_LOG.md
```

## What this does NOT do (by design — see REPORT.md "what I chose not to build")

- No multi-turn conversation handling (treats each message independently)
- No multilingual-specific handling (dataset includes non-English tweets; model
  handles them but this wasn't specifically evaluated)
- No fine-tuning — prompt-based classification + retrieval only
- Not tested on the full 3M-row dataset — a brand-filtered subsample only, as
  explicitly permitted by the assignment

## Credits / borrowed material

- Dataset: [Customer Support on Twitter](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter) (Kaggle, thoughtvector)
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (open-source, Hugging Face)
- LLM: Groq-hosted `openai/gpt-oss-120b` / `openai/gpt-oss-20b`
- Built with AI coding assistance (Claude) for pipeline scaffolding and debugging,
  per the assignment's rules. All labeling in the golden evaluation set is
  human-reviewed by the author.
