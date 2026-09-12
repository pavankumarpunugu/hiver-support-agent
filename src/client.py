"""
Shared Groq client setup. Reads GROQ_API_KEY from environment (or Kaggle
Secrets if running in a Kaggle Notebook — see the try/except below).
"""
import os

from groq import Groq

CLASSIFY_MODEL = "openai/gpt-oss-120b"
REPLY_MODEL = "openai/gpt-oss-120b"


def get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            from kaggle_secrets import UserSecretsClient  # type: ignore

            api_key = UserSecretsClient().get_secret("GROQ_API_KEY")
        except Exception:
            pass
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY not found. Set it as an environment variable, "
            "or as a Kaggle Secret named GROQ_API_KEY if running in a Notebook."
        )
    return Groq(api_key=api_key)
