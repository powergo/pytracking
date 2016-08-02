import requests

from pytracking.tracking import get_configuration


def send_webhook(tracking_result, configuration=None, **kwargs):
    """TODO
    """
    configuration = get_configuration(configuration, kwargs)

    payload = {
        "is_click_tracking": tracking_result.is_click_tracking,
        "metadata": tracking_result.metadata,
        "request_data": tracking_result.request_data
    }

    if tracking_result.tracked_url:
        payload["tracked_url"] = tracking_result.tracked_url

    response = requests.post(
        tracking_result.webhook_url, json=payload,
        timeout=configuration.webhook_timeout_seconds)

    return response
