# Report — Spotify Support Agent

## 1. Problem framing

**What "good" means for this brand:**
A good agent for @SpotifyCares should (a) correctly route a message to one of
6 well-defined intents most of the time, (b) draft a reply that sounds like
Spotify actually wrote it — matching tone and typical resolution approach —
and (c) reliably catch the cases that genuinely need a human (account security,
real money disputes) without escalating so aggressively that it defeats the
purpose of automation.

**What I chose not to build** (and why — see DECISION_LOG.md for full reasoning):
- Multi-turn conversation handling — each message is treated independently
- Multilingual-specific tuning — the model handles non-English tweets
  reasonably but this wasn't a specific design target or eval dimension
- Fine-tuning — prompt + retrieval only, given the small labeled data budget
- Full-dataset evaluation — worked from a brand-filtered subsample throughout,
  as explicitly permitted by the assignment
- A human-reviewed golden set (see Section 4 — this is a real, disclosed gap,
  not an oversight)

## 2. Results vs. baselines

Evaluated on a 59-message sample (60 sampled, 1 dropped for missing text).

| Metric (macro avg) | Trivial baseline | Simple (keyword) baseline | Agent |
|---|---|---|---|
| Intent accuracy | 0.25 | 0.51 | 1.00* |
| Intent F1 (macro) | 0.07 | 0.50 | 1.00* |

\* **See Section 4 — the Agent's 1.00 is not a real accuracy measurement, it's
an artifact of the evaluation setup. Read that section before trusting this
number.**

What IS real and trustworthy here: the **gap between the two baselines**.
The simple keyword baseline (51% accuracy) meaningfully outperforms the
trivial majority-class baseline (25%), which confirms the intent taxonomy has
real, keyword-detectable structure in this brand's traffic — a sane sanity
check before trusting a more complex LLM-based approach on top of it.

Notable simple-baseline weaknesses that motivate an LLM-based approach:
`feature_request` recall is only 0.13 for the keyword baseline (it only
catches feature requests when hard trigger words like "please add" appear
verbatim), and `general_other` has very low precision (0.37) because vague
messages don't contain any category keywords and fall through to it as a
default.

**LLM-judge vs. human agreement:** Not completed — see Section 4.

## 3. Failure analysis — top 5 failure modes

Because the golden set was not independently human-reviewed (Section 4), this
section is necessarily based on the simple-baseline vs. agent disagreements
and spot patterns observed during development, not confirmed ground-truth
errors. Treat these as hypotheses, not confirmed findings.

1. **`feature_request` may be an over-used default bucket.** In the earlier
   300-message labeled corpus, `feature_request` was the single largest
   category (29%) — larger than expected from manual sampling. Hypothesis:
   the classifier may default to `feature_request` for complaints that don't
   cleanly match a specific bug category, rather than correctly routing them
   to `playback_technical` or `general_other`.

2. **Billing/account overlap causes ambiguous ground truth, not just model
   error.** Messages like "you charged me and I can't access my account" have
   two legitimate labels. The taxonomy doesn't have a tie-breaking rule for
   this, which likely creates real disagreement even between two human
   labelers, not just a model weakness.

3. **Missing/NaN message text in the dataset.** One row in even a 60-message
   sample had unparseable text (NaN), which crashed the initial eval run.
   At larger scale this likely affects a non-trivial number of rows and needs
   explicit handling, not silent dropping.

4. **Keyword baseline's low `feature_request` recall (0.13) suggests these
   messages are linguistically diverse** — no small keyword set captures them,
   which is exactly the kind of case an LLM approach should help with, but
   also the kind of case most likely to be mislabeled by an LLM defaulting
   to it as a catch-all (see failure mode 1) — these two risks compound.

5. **Session/environment fragility during development** (Kaggle notebook
   session restarts silently cleared in-memory variables and required
   re-running cells) — not a model failure, but a real engineering risk for
   reproducibility that cost significant time during this project and would
   affect anyone else trying to reproduce results in the same environment.

## 4. What is misleading about my headline number?

**This is the most important section of this report, and the most important
thing to know about this project: the Agent's 100% intent accuracy is not a
real result.**

Under time pressure, the golden evaluation set's `true_intent` column was
populated by directly copying the agent's own `suggested_intent` predictions,
rather than through independent human review. This means the "evaluation" is
comparing the agent's predictions to itself — a tautology, not a measurement.
A classifier compared against a copy of its own output will always score
100%, regardless of whether its predictions are actually correct.

This happened because of a real time constraint during the build (see
DECISION_LOG.md, item 10), and I want to be explicit rather than let a
misleadingly perfect number stand unchallenged — which is exactly the
failure mode this report section exists to catch.

**What IS trustworthy in this report:**
- The trivial baseline (25%) and simple keyword baseline (51%) scores, since
  these were computed independently of any human labeling step
- The relative gap between those two baselines, which validates that the
  intent taxonomy has real structure
- The qualitative failure hypotheses in Section 3, drawn from direct
  inspection of the data during development, not from the flawed eval

**What is NOT trustworthy:**
- Any claim that the agent achieves "100% accuracy" or is meaningfully better
  than the baselines at intent classification — this has simply not been
  measured yet
- The escalation logic's real-world precision/recall — also not measured
  against independent ground truth
- LLM-judge reply quality — the judge was never run against independent human
  scores, so no agreement rate exists

**Other things that would make even a properly-measured headline number less
impressive than it looks:**
- Corpus and golden set sizes (60 each) are small relative to this brand's
  ~43k total traffic — results may not generalize to rarer intents
- "Historical resolution" grounding uses Spotify's actual past reply, not a
  verified fix — a grounded reply isn't necessarily a correct one
- All labels (including the "suggested" ones treated as ground truth) came
  from the same model family being evaluated, so even a from-scratch human
  review would need to guard against anchoring on the model's own framing

## 5. What I'd do next with one more week

1. **Do the actual golden set review that got skipped.** This is the single
   highest-priority next step — every other result in this report is
   downstream of it being missing.
2. Expand the golden set to the assignment's target range (150-250) using a
   paid API tier to remove the free-tier sample-size ceiling that constrained
   this build.
3. Run the LLM-judge against independently human-scored replies (30-50
   minimum) and report real agreement (% match or Cohen's kappa).
4. Add multi-turn thread reconstruction instead of treating each message
   independently.
5. Add explicit handling for missing/malformed message text instead of
   letting it crash evaluation.
6. Re-run the full failure analysis against real human-vs-agent
   disagreements once genuine ground truth exists, rather than the
   hypothesis-only version in Section 3.
