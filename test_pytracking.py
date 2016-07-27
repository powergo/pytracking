import pytest

from pytracking import get_click_tracking_url


try:
    from cryptography.fernet import Fernet
    support_crypto = True
except ImportError:
    support_crypto = False

DEFAULT_URL_TO_TRACK = "https://www.bob.com/hello-world/?token=valueééé"

DEFAULT_BASE_CLICK_TRACKING_URL = "https://a.b.com/tracking/"

DEFAULT_ENCRYPTION_KEY = b'XdhWbQZnqCIPLBL0ViPIW2vBTsmUNxAS-7mOtTdu6ZM='


def test_basic_get_click_tracking_url():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL)
    assert url ==\
        "https://a.b.com/tracking/eyJ1cmwiOiAiaHR0cHM6Ly93d3cuYm9iLmNvbS9oZWxsby13b3JsZC8_dG9rZW49dmFsdWVcdTAwZTlcdTAwZTlcdTAwZTkifQ=="  # noqa


@pytest.mark.skipif(
    not support_crypto, reason="Cryptography lib not installed")
def test_basic_encrypted_get_click_tracking_url():
    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK,
        base_click_tracking_url=DEFAULT_BASE_CLICK_TRACKING_URL,
        encryption_bytestring_key=DEFAULT_ENCRYPTION_KEY)
    path = url[len(DEFAULT_BASE_CLICK_TRACKING_URL):]
    key = Fernet(DEFAULT_ENCRYPTION_KEY)

    # Can decrypt without raison an exception
    value = key.decrypt(path.encode("utf-8"))
    assert value
