from functools import cached_property

import tweepy

from audit.config import env


class XClient:
    @cached_property
    def _client(self):
        return tweepy.Client(
            consumer_key=env("X_CONSUMER_KEY"),
            consumer_secret=env("X_CONSUMER_SECRET"),
            access_token=env("X_ACCESS_TOKEN"),
            access_token_secret=env("X_ACCESS_TOKEN_SECRET"),
        )

    def post(self, text: str) -> None:
        response = self._client.create_tweet(text=text)
        if response.errors is not None and len(response.errors) > 0:
            raise RuntimeError(f"X API error: {response.errors}")
