"""Two baselines the agent must beat: a trivial one and a simple one."""

CANNED_REPLY = "Hey! Thanks for reaching out. Please DM us your account details so we can look into this."

KEYWORD_RULES = {
    "account_access": ["login", "log in", "password", "locked", "hacked", "access my account"],
    "billing_subscription": ["charge", "refund", "subscription", "premium", "billed", "payment"],
    "playback_technical": ["crash", "skip", "stutter", "shuffle", "repeat", "won't play", "stopped working"],
    "device_platform": ["iphone", "android", "tv", "car", "windows", "device"],
    "feature_request": ["wish", "please add", "why can't", "feature", "would be nice"],
}


def trivial_baseline(message: str, majority_intent: str) -> dict:
    """Always predicts the majority class and sends one canned reply."""
    return {"intent": majority_intent, "reply": CANNED_REPLY, "escalate": False}


def simple_baseline(message: str) -> dict:
    """Keyword/regex rules, no LLM, no retrieval."""
    msg_lower = message.lower()
    for intent, keywords in KEYWORD_RULES.items():
        if any(kw in msg_lower for kw in keywords):
            return {"intent": intent, "reply": CANNED_REPLY, "escalate": intent == "account_access"}
    return {"intent": "general_other", "reply": CANNED_REPLY, "escalate": False}
