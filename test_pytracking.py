from pytracking import (
    Configuration, get_click_tracking_url, get_click_tracking_url_path,
    get_open_tracking_url_path,
    get_click_tracking_result, get_open_tracking_pixel, get_open_tracking_url,
    get_open_tracking_result)


DEFAULT_URL_TO_TRACK = "https://www.bob.com/hello-world/?token=valueééé"

DEFAULT_BASE_CLICK_TRACKING_URL = "https://a.b.com/tracking/"

DEFAULT_BASE_OPEN_TRACKING_URL = "https://a.b.com/tracking/open/"

DEFAULT_ENCRYPTION_KEY = b'XdhWbQZnqCIPLBL0ViPIW2vBTsmUNxAS-7mOtTdu6ZM='

DEFAULT_METADATA = {
    "param1": "val1",
    "param3": "val3b",
    "nested": {"param2": "val2"}}

DEFAULT_DEFAULT_METADATA = {
    "key1": True,
    "keyéé": "valèèè",
    "param3": "val3"
}


EXPECTED_METADATA = {}
EXPECTED_METADATA.update(DEFAULT_DEFAULT_METADATA)
EXPECTED_METADATA.update(DEFAULT_METADATA)

DEFAULT_WEBHOOK_URL = "https://webhook.com/tracking/"

DEFAULT_REQUEST_DATA = {
    "user_agent": "Firefox",
    "user_ip": "127.0.0.1"
}

DEFAULT_CONFIGURATION = Configuration(
    webhook_url=DEFAULT_WEBHOOK_URL,
    base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL,
    base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL,
    default_metadata=DEFAULT_DEFAULT_METADATA)


def test_get_open_tracking_pixel():
    (pixel, mime) = get_open_tracking_pixel()
    assert len(pixel) == 68
    assert mime == "image/png"


def test_basic_get_open_tracking_url():
    url = get_open_tracking_url(
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL)
    assert url == "https://a.b.com/tracking/open/e30="


def test_in_config_open_tracking_url():
    url = get_open_tracking_url(
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL,
        metadata=DEFAULT_METADATA)
    path = get_open_tracking_url_path(
        url, base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL)

    tracking_result = get_open_tracking_result(
        path, webhook_url=DEFAULT_WEBHOOK_URL)
    assert tracking_result.tracked_url is None
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data is None
    assert tracking_result.metadata == DEFAULT_METADATA
    assert tracking_result.is_open_tracking
    assert not tracking_result.is_click_tracking


def test_in_config_open_tracking_url_to_json():
    url = get_open_tracking_url(
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL,
        metadata=DEFAULT_METADATA)
    path = get_open_tracking_url_path(
        url, base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL)

    tracking_result = get_open_tracking_result(
        path, webhook_url=DEFAULT_WEBHOOK_URL).to_json_dict()
    assert tracking_result.tracked_url is None
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data is None
    assert tracking_result.metadata == DEFAULT_METADATA
    assert tracking_result.is_open_tracking
    assert not tracking_result.is_click_tracking


def test_in_config_open_tracking_full_url():
    url = get_open_tracking_url(
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL,
        metadata=DEFAULT_METADATA)

    tracking_result = get_open_tracking_result(
        url, webhook_url=DEFAULT_WEBHOOK_URL,
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL)

    assert tracking_result.tracked_url is None
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data is None
    assert tracking_result.metadata == DEFAULT_METADATA
    assert tracking_result.is_open_tracking
    assert not tracking_result.is_click_tracking


def test_embedded_open_tracking_url():
    url = get_open_tracking_url(
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL,
        webhook_url=DEFAULT_WEBHOOK_URL,
        include_webhook_url=True,
        default_metadata=DEFAULT_DEFAULT_METADATA,
        include_default_metadata=True,
        metadata=DEFAULT_METADATA)
    path = get_open_tracking_url_path(
        url, base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL)

    tracking_result = get_open_tracking_result(
        path, request_data=DEFAULT_REQUEST_DATA,
        include_default_metadata=True,
        include_webhook_url=True)

    assert tracking_result.tracked_url is None
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data == DEFAULT_REQUEST_DATA
    assert tracking_result.metadata == EXPECTED_METADATA
    assert tracking_result.is_open_tracking
    assert not tracking_result.is_click_tracking


def test_basic_get_click_tracking_url():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL)
    assert url ==\
        "https://a.b.com/tracking/eyJ1cmwiOiAiaHR0cHM6Ly93d3cuYm9iLmNvbS9oZWxsby13b3JsZC8_dG9rZW49dmFsdWVcdTAwZTlcdTAwZTlcdTAwZTkifQ=="  # noqa


def test_in_config_click_tracking_url():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL,
        metadata=DEFAULT_METADATA)
    path = get_click_tracking_url_path(
        url, base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL)

    tracking_result = get_click_tracking_result(
        path, webhook_url=DEFAULT_WEBHOOK_URL)
    assert tracking_result.tracked_url == DEFAULT_URL_TO_TRACK
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data is None
    assert tracking_result.metadata == DEFAULT_METADATA
    assert tracking_result.is_click_tracking
    assert not tracking_result.is_open_tracking


def test_in_config_click_tracking_full_url():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL,
        metadata=DEFAULT_METADATA)

    tracking_result = get_click_tracking_result(
        url, webhook_url=DEFAULT_WEBHOOK_URL,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL)
    assert tracking_result.tracked_url == DEFAULT_URL_TO_TRACK
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data is None
    assert tracking_result.metadata == DEFAULT_METADATA
    assert tracking_result.is_click_tracking
    assert not tracking_result.is_open_tracking


def test_embedded_click_tracking_url():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL,
        webhook_url=DEFAULT_WEBHOOK_URL,
        include_webhook_url=True,
        default_metadata=DEFAULT_DEFAULT_METADATA,
        include_default_metadata=True,
        metadata=DEFAULT_METADATA)
    path = get_click_tracking_url_path(
        url, base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL)

    tracking_result = get_click_tracking_result(
        path, request_data=DEFAULT_REQUEST_DATA,
        include_default_metadata=True,
        include_webhook_url=True)

    assert tracking_result.tracked_url == DEFAULT_URL_TO_TRACK
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data == DEFAULT_REQUEST_DATA
    assert tracking_result.metadata == EXPECTED_METADATA
    assert tracking_result.is_click_tracking
    assert not tracking_result.is_open_tracking
