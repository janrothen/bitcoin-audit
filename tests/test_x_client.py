from unittest.mock import patch

from audit.clients.x_client import XClient


def test_post():
    with patch("audit.clients.x_client.tweepy.Client") as mock_client:
        XClient().post("hello world")
        mock_client.return_value.create_tweet.assert_called_once_with(
            text="hello world"
        )
