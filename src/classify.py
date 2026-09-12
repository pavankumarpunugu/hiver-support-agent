"""
Intent classification for Spotify support messages.

Taxonomy of 6 intents was derived by manually reading a 30-message sample of
real inbound tweets to @SpotifyCares before writing any code — see
report/DECISION_LOG.md for why these 6 and not more/fewer.
"""
import json

from src.client import CLASSIFY_MODEL, get_client

INTENT_LIST = [
    "playback_technical",
    "account_access",
    "billing_subscription",
    "feature_request",
    "device_platform",
    "general_other",
]

CLASSIFY_PROMPT = """You are classifying customer support messages sent to Spotify on Twitter.

Classify the message into exactly one of these intents:
- playback_technical: app crashes, songs skipping, shuffle/repeat issues, audio quality, playback bugs
- account_access: login problems, password reset, locked or hacked accounts
- billing_subscription: charges, refunds, plan upgrades/downgrades, family plan issues
- feature_request: missing features, product feedback, requests for functionality, content/catalog gaps
- device_platform: not working on a specific device or OS (TV, car, phone model, Windows Mobile, etc.)
- general_other: praise, vague complaints, anything that doesn't clearly fit above

Message: "{message}"

Respond with ONLY valid JSON, no other text:
{{"intent": "<one of the categories above>", "confidence": "<high|medium|low>"}}
"""


def classify_message(client, message: str) -> dict:
    prompt = CLASSIFY_PROMPT.format(message=message)
    response = client.chat.completions.create(
        model=CLASSIFY_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        reasoning_effort="low",
    )
    text = response.choices[0].message.content.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"intent": "general_other", "confidence": "low", "raw": text}


if __name__ == "__main__":
    client = get_client()
    test_msg = "my app keeps crashing every time I try to play a song"
    print(classify_message(client, test_msg))
