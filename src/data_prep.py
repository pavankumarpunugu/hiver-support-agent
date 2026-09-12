"""
Filters the full Customer Support on Twitter dataset down to one brand
(SpotifyCares) and reconstructs (customer_message -> brand_reply) pairs
using the response_tweet_id / in_response_to_tweet_id thread links.
"""
import re
import pandas as pd

BRAND = "SpotifyCares"
RAW_PATH = "data/raw/twcs.csv"
OUT_PATH = "data/spotify_pairs.csv"


def clean_text(text: str) -> str:
    text = re.sub(r"@\S+", "", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    df = pd.read_csv(RAW_PATH)
    print(f"Loaded {df.shape[0]} rows")

    brand_tweets = df[df["author_id"] == BRAND].copy()
    customer_ids = brand_tweets["in_response_to_tweet_id"].dropna().unique()
    customer_tweets = df[df["tweet_id"].isin(customer_ids)].copy()
    print(f"Brand replies: {len(brand_tweets)}, Customer messages: {len(customer_tweets)}")

    pairs = brand_tweets.merge(
        customer_tweets,
        left_on="in_response_to_tweet_id",
        right_on="tweet_id",
        suffixes=("_brand", "_customer"),
    )

    pairs = pairs[
        [
            "tweet_id_customer",
            "text_customer",
            "created_at_customer",
            "tweet_id_brand",
            "text_brand",
            "created_at_brand",
        ]
    ].rename(columns={"text_customer": "customer_message", "text_brand": "brand_reply"})

    pairs["customer_message_clean"] = pairs["customer_message"].apply(clean_text)
    pairs["brand_reply_clean"] = pairs["brand_reply"].apply(clean_text)

    pairs.to_csv(OUT_PATH, index=False)
    print(f"Saved {pairs.shape[0]} pairs to {OUT_PATH}")


if __name__ == "__main__":
    main()
