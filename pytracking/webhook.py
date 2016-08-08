import requests

from pytracking.tracking import get_configuration


def send_webhook(tracking_result, configuration=None, **kwargs):
    """Sends a POST request to the webhook URL specified in tracking_result.

    The POST request will have a body of type application/json that contains a
    json representation of the tracking result:

    ::

        {
            "is_open_tracking": False,
            "is_click_tracking": True,
            "metadata": {...},
            "request_data": None,
            "tracked_url": "http://...",
            "timestamp": 1389177318
        }

    :param tracking_result: The TrackingResult instance to post to a webhook.
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)

    payload = {
        "is_open_tracking": tracking_result.is_open_tracking,
        "is_click_tracking": tracking_result.is_click_tracking,
        "metadata": tracking_result.metadata,
        "request_data": tracking_result.request_data,
        "timestamp": tracking_result.timestamp
    }

    if tracking_result.tracked_url:
        payload["tracked_url"] = tracking_result.tracked_url

    response = requests.post(
        tracking_result.webhook_url, json=payload,
        timeout=configuration.webhook_timeout_seconds)

    return response
