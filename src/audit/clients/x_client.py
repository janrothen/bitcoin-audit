import tweepy

from audit.config import env


class XClient:
    def post(self, text: str) -> None:
        client = tweepy.Client(
            consumer_key=env("X_CONSUMER_KEY"),
            consumer_secret=env("X_CONSUMER_SECRET"),
            access_token=env("X_ACCESS_TOKEN"),
            access_token_secret=env("X_ACCESS_TOKEN_SECRET"),
        )
        client.create_tweet(text=text)
