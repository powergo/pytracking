import copy

from pytracking import (
    Configuration, get_click_tracking_url, get_click_tracking_url_path,
    get_open_tracking_url_path,
    get_click_tracking_result, get_open_tracking_url,
    get_open_tracking_result)

from cryptography.fernet import Fernet

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


def test_basic_encrypted_get_open_tracking_url():
    url = get_open_tracking_url(
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL,
        encryption_bytestring_key=DEFAULT_ENCRYPTION_KEY)
    path = get_open_tracking_url_path(
        url, base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL)
    key = Fernet(DEFAULT_ENCRYPTION_KEY)

    # Can decrypt without raising an exception
    value = key.decrypt(path.encode("utf-8"))
    # We can only assert if the value is truthy because the value is encrypted
    # with a different salt each time.
    assert value


def test_minimal_encrypted_get_open_tracking_url():
    url = get_open_tracking_url(
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL,
        metadata=DEFAULT_METADATA,
        encryption_bytestring_key=DEFAULT_ENCRYPTION_KEY)
    path = get_open_tracking_url_path(
        url, base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL)

    tracking_result = get_open_tracking_result(
        path,
        request_data=DEFAULT_REQUEST_DATA,
        default_metadata=DEFAULT_DEFAULT_METADATA,
        webhook_url=DEFAULT_WEBHOOK_URL,
        encryption_bytestring_key=DEFAULT_ENCRYPTION_KEY)

    expected_metadata = copy.copy(DEFAULT_DEFAULT_METADATA)
    expected_metadata.update(DEFAULT_METADATA)

    assert tracking_result.tracked_url is None
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data == DEFAULT_REQUEST_DATA
    assert tracking_result.metadata == expected_metadata
    assert tracking_result.is_open_tracking
    assert not tracking_result.is_click_tracking


def test_basic_encrypted_get_click_tracking_url():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL,
        encryption_bytestring_key=DEFAULT_ENCRYPTION_KEY)
    path = get_click_tracking_url_path(
        url, base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL)
    key = Fernet(DEFAULT_ENCRYPTION_KEY)

    # Can decrypt without raising an exception
    value = key.decrypt(path.encode("utf-8"))
    # We can only assert if the value is truthy because the value is encrypted
    # with a different salt each time.
    assert value


def test_minimal_encrypted_get_click_tracking_url():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL,
        metadata=DEFAULT_METADATA,
        encryption_bytestring_key=DEFAULT_ENCRYPTION_KEY)
    path = get_click_tracking_url_path(
        url, base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL)

    tracking_result = get_click_tracking_result(
        path,
        request_data=DEFAULT_REQUEST_DATA,
        default_metadata=DEFAULT_DEFAULT_METADATA,
        webhook_url=DEFAULT_WEBHOOK_URL,
        encryption_bytestring_key=DEFAULT_ENCRYPTION_KEY)

    expected_metadata = copy.copy(DEFAULT_DEFAULT_METADATA)
    expected_metadata.update(DEFAULT_METADATA)

    assert tracking_result.tracked_url == DEFAULT_URL_TO_TRACK
    assert tracking_result.webhook_url == DEFAULT_WEBHOOK_URL
    assert tracking_result.request_data == DEFAULT_REQUEST_DATA
    assert tracking_result.metadata == expected_metadata
    assert tracking_result.is_click_tracking
    assert not tracking_result.is_open_tracking
