from unittest.mock import patch

import pytest

from pytracking import (
    get_click_tracking_url, get_click_tracking_url_path,
    get_click_tracking_result, DEFAULT_TIMEOUT_SECONDS)
from test_pytracking import (
    DEFAULT_URL_TO_TRACK, DEFAULT_BASE_CLICK_TRACKING_URL, DEFAULT_WEBHOOK_URL,
    DEFAULT_METADATA)

try:
    import requests  # noqa
    import pytracking.webhook
    support_requests = True
except ImportError:
    support_requests = False


pytestmark = pytest.mark.skipif(
    not support_requests, reason="Requests lib not installed")


def test_send_webhook():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL,
        metadata=DEFAULT_METADATA)
    path = get_click_tracking_url_path(
        url, base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL)

    tracking_result = get_click_tracking_result(
        path, webhook_url=DEFAULT_WEBHOOK_URL)

    payload = {
        "is_open_tracking": False,
        "is_click_tracking": True,
        "metadata": DEFAULT_METADATA,
        "request_data": None,
        "tracked_url": DEFAULT_URL_TO_TRACK,
        "timestamp": tracking_result.timestamp,
    }

    with patch("pytracking.webhook.requests.post") as mocked_post:
        pytracking.webhook.send_webhook(tracking_result)

        mocked_post.assert_called_once_with(
            DEFAULT_WEBHOOK_URL, json=payload, timeout=DEFAULT_TIMEOUT_SECONDS)
