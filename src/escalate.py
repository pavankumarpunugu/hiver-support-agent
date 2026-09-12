"""
Rule-based escalation decision. Deliberately simple and inspectable (not an
LLM call) so the reason for every escalation is traceable to an explicit rule
— see report/DECISION_LOG.md for why this is rules, not a learned classifier.
"""


def decide_escalation(intent: str, similar_cases: list[dict], confidence: str) -> tuple[bool, str]:
    if intent == "account_access":
        return True, "Account access issues may involve security/hacking — needs human verification"

    if intent == "billing_subscription" and any(
        "refund" in c["customer_message"].lower() or "charge" in c["customer_message"].lower()
        for c in similar_cases
    ):
        return True, "Billing disputes involving charges/refunds require human judgment"

    if confidence == "low":
        return True, "Low classification confidence — human review needed"

    if not similar_cases or similar_cases[0]["similarity"] < 0.4:
        return True, "No sufficiently similar historical case found to ground a reply"

    return False, "High-confidence intent with strong grounding from similar past cases"
