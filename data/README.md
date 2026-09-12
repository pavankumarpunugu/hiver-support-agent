# Data folder

This repo does not ship the raw dataset (large, and Kaggle's terms prefer
linking rather than redistributing). To reproduce:

## 1. Raw data
Download `twcs.csv` from [Kaggle](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter)
and place it at `data/raw/twcs.csv`. Or run everything inside a Kaggle Notebook
with the dataset attached (no download needed).

## 2. Generated files (produced by running the pipeline)
- `spotify_pairs.csv` — all SpotifyCares (customer_message -> brand_reply) pairs
  (~43k rows), produced by `src/data_prep.py`
- `spotify_corpus_labeled.csv` — a ~300-message subset, LLM-classified, used
  for retrieval grounding
- `golden_set_final.csv` — **the hand-labeled evaluation set**. This is the one
  file in this project that must be produced by a human, not a script.

## Producing golden_set_final.csv

1. Sample 150-250 messages NOT already in the labeled corpus (avoid
   contamination — see `src/build_corpus.py` for the pool-exclusion logic).
2. Get model-suggested intent + escalate labels as a starting point (saves
   typing, speeds up review).
3. **Review each one yourself.** Correct any wrong intent or escalate flag.
   This is what makes it a golden set rather than just more model output —
   and it's the piece you need to be able to explain and defend, since the
   assignment explicitly says these must be labels "you built yourself."
4. Save the corrected file here as `golden_set_final.csv` with columns:
   `customer_message_clean`, `true_intent`, `true_escalate`.

There's a `sample_review_loop.py` script in `eval/` that runs this
interactively in a notebook (prints one message + model suggestion at a
time; you just accept or correct it) if you want to speed up the mechanics
without skipping the judgment part.
