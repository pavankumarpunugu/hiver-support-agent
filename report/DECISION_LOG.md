# Decision Log

Non-obvious decisions made while building this, and why.

1. **Picked SpotifyCares over AmazonHelp/AppleSupport.** AmazonHelp has 4x the
   volume but issues span an enormous surface (orders, devices, Prime, refunds,
   deliveries) that would force either a huge intent taxonomy or a lossy
   `general_other` bucket. Spotify's issue space is narrow enough for 6 clean
   intents to cover real traffic.

2. **Intent taxonomy (6 categories) was derived from reading real data first**,
   not decided top-down. Read a 30-message random sample before writing any
   labels, then finalized: playback_technical, account_access,
   billing_subscription, feature_request, device_platform, general_other.

3. **Switched from Claude API to Groq (free tier) mid-build** after hitting a
   billing wall. Tradeoff: Groq's free tier caps daily tokens (~200k) and rate
   limits requests (~30/min), which directly constrains how large a sample can
   be processed in the 15-minute reproduction window — this is why the labeled
   corpus is ~300 messages, not the full ~43k.

4. **Retrieval grounding uses a local embedding model (all-MiniLM-L6-v2),
   not an API**, to avoid burning API budget/rate limit on embeddings when
   it's only needed for classification and reply drafting.

5. **"Historical resolution" = the brand's actual reply**, not a verified
   resolution. The dataset has no resolved/unresolved flag, so grounding
   assumes Spotify's real historical reply represents a reasonable response —
   not necessarily that the issue was actually fixed.

6. **Escalation is rule-based, not learned.** Chose explicit if/else rules
   (sensitive intents, low confidence, weak retrieval match) over training an
   escalation classifier, so every decision has an inspectable, stated reason
   — matching the assignment's explicit requirement for a stated reason.

7. **account_access always escalates**, regardless of confidence, because
   account/security issues carry outsized risk if handled wrong (could be an
   active hack) — false-negative cost there is much higher than for e.g. a
   playback bug.

8. **Billing escalates conditionally** (only when refund/charge language is
   present), not universally — most billing questions are informational
   ("how do I see if my discount applied") and don't need a human.

9. **Golden set excludes any message already in the labeled retrieval
   corpus**, to avoid evaluating the agent on data it was implicitly grounded
   on.

10. **Golden set labeling used a two-tier review process**: auto-accepted
    rows where the LLM classifier and a simple keyword-rule baseline agreed
    (treating agreement as a proxy for high confidence), and manually
    reviewed every row where they disagreed. This concentrates human review
    time on genuinely ambiguous cases rather than treating all rows equally
    — but is a real methodological choice with a real trade-off: it assumes
    disagreement-with-baseline is a reasonable proxy for "needs review,"
    which may miss cases where the LLM and baseline are both confidently
    wrong in the same direction. Documented so it's inspectable, not hidden.

11. **Didn't fine-tune anything.** Prompt-based classification + retrieval was
    sufficient at this data scale and time budget; fine-tuning would need far
    more labeled data than 150-300 examples to be worth the complexity.

12. **Sample size for the labeled corpus (300) and golden set (150) were
    chosen to fit Groq's free-tier daily token limit** within the assignment's
    <15-minute reproduction constraint — a paid tier or Claude/OpenAI API
    would allow larger samples with no methodology change.

13. **Did not build multi-turn conversation handling.** Threads in the raw
    data often span 3+ tweets; this agent treats each customer message
    independently. Noted as a explicit non-goal, not an oversight — see
    REPORT.md.

14. **Under final time pressure, skipped independent human review of the
    golden set entirely** rather than submit late or fabricate a rushed
    review. `true_intent` in the submitted golden set is a direct copy of
    the model's own `suggested_intent` — meaning the headline "100% agent
    accuracy" in REPORT.md is a measurement artifact, not a real result.
    This is disclosed explicitly in REPORT.md Section 4 rather than hidden.
    Chose transparency about an incomplete result over a polished but
    misleading one.

15. **Reduced corpus and golden set sizes from 300/150 to 60/60** during
    the same time crunch, to fit a full pipeline rebuild after a Kaggle
    session restart within the remaining time. Baselines (trivial, simple)
    were still computed independently and are the only trustworthy
    quantitative results in this submission — see REPORT.md Section 2.
