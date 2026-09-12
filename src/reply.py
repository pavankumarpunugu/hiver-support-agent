"""Drafts a reply grounded in retrieved historical (message -> reply) cases."""
from src.client import REPLY_MODEL

REPLY_PROMPT = """You are a Spotify customer support agent replying on Twitter.

Customer message: "{message}"
Detected intent: {intent}

Here are similar past cases and how Spotify actually replied to them:
{examples}

Write a reply in Spotify's tone and style based on these past examples. Keep it
under 280 characters (Twitter limit). Be helpful and specific, don't just say
"DM us" unless the past examples show that's the standard response for this
kind of issue.

Respond with ONLY the reply text, no other formatting.
"""


def format_examples(similar_cases: list[dict]) -> str:
    formatted = ""
    for i, case in enumerate(similar_cases, 1):
        formatted += (
            f"{i}. Customer: \"{case['customer_message'][:100]}\"\n"
            f"   Spotify replied: \"{case['brand_reply'][:150]}\"\n\n"
        )
    return formatted


def draft_reply(client, message: str, intent: str, similar_cases: list[dict]) -> str:
    prompt = REPLY_PROMPT.format(
        message=message, intent=intent, examples=format_examples(similar_cases)
    )
    response = client.chat.completions.create(
        model=REPLY_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        reasoning_effort="low",
    )
    return response.choices[0].message.content.strip()
