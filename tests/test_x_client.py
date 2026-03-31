from unittest.mock import MagicMock, patch

import pytest

from audit.clients.x_client import XClient


def test_post():
    with patch("audit.clients.x_client.tweepy.Client") as mock_client:
        mock_client.return_value.create_tweet.return_value = MagicMock(errors=[])
        XClient().post("hello world")
        mock_client.return_value.create_tweet.assert_called_once_with(
            text="hello world"
        )


def test_post_raises_on_api_error():
    with patch("audit.clients.x_client.tweepy.Client") as mock_client:
        mock_client.return_value.create_tweet.return_value = MagicMock(
            errors=[{"message": "Forbidden"}]
        )
        with pytest.raises(RuntimeError, match="X API error"):
            XClient().post("hello world")
