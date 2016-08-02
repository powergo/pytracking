import pytest

from pytracking.tracking import (
    get_open_tracking_url, get_click_tracking_url, get_open_tracking_url_path,
    get_click_tracking_url_path, TRACKING_PIXEL, PNG_MIME_TYPE)
from test_pytracking import (
    DEFAULT_BASE_OPEN_TRACKING_URL, DEFAULT_BASE_CLICK_TRACKING_URL,
    DEFAULT_METADATA, DEFAULT_WEBHOOK_URL, DEFAULT_DEFAULT_METADATA,
    DEFAULT_URL_TO_TRACK)

DEFAULT_ENCODED_URL_TO_TRACK =\
    "https://www.bob.com/hello-world/?token=value%C3%A9%C3%A9%C3%A9"

try:
    import ipware  # noqa

    # Must call configure before importing tracking_django
    from django.conf import settings
    from django.http import Http404
    settings.configure()

    import pytracking.django as tracking_django

    support_django = True
except ImportError:
    support_django = False


pytestmark = pytest.mark.skipif(
    not support_django, reason="Django-support lib not installed")

DEFAULT_SETTINGS = {
    "webhook_url": DEFAULT_WEBHOOK_URL,
    "base_open_tracking_url": DEFAULT_BASE_OPEN_TRACKING_URL,
    "base_click_tracking_url": DEFAULT_BASE_CLICK_TRACKING_URL,
    "default_metadata": DEFAULT_DEFAULT_METADATA
}


class FakeDjangoRequest(object):
    def __init__(self):
        self.META = {}
        self.method = "GET"


@pytest.fixture
def setup_django():
    settings.PYTRACKING_CONFIGURATION = DEFAULT_SETTINGS


def test_get_django_request_data(setup_django):
    request = FakeDjangoRequest()
    request.META["HTTP_X_REAL_IP"] = "10.10.240.22"
    request.META["HTTP_USER_AGENT"] = "Firefox"

    request_data = tracking_django.get_request_data(request)

    assert request_data == {"user_agent": "Firefox", "user_ip": "10.10.240.22"}


def test_get_tracking_result(setup_django):
    configuration = tracking_django.get_configuration_from_settings()

    url = get_open_tracking_url(
        base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL,
        metadata=DEFAULT_METADATA)
    path = get_open_tracking_url_path(
        url, base_open_tracking_url=DEFAULT_BASE_OPEN_TRACKING_URL)

    request = FakeDjangoRequest()
    request.META["HTTP_X_REAL_IP"] = "10.10.240.22"
    request.META["HTTP_USER_AGENT"] = "Firefox"

    tracking_result = tracking_django.get_tracking_result(
        request, path, True, configuration)

    expected_metadata = {}
    expected_metadata.update(DEFAULT_DEFAULT_METADATA)
    expected_metadata.update(DEFAULT_METADATA)

    assert tracking_result.request_data ==\
        {"user_agent": "Firefox", "user_ip": "10.10.240.22"}
    assert tracking_result.metadata == expected_metadata


def test_valid_click_tracking_view(setup_django):
    result_metadata = {}
    request_data = {}

    class TestClickView(tracking_django.ClickTrackingView):

        def notify_tracking_event(self, tracking_result):
            result_metadata.update(tracking_result.metadata)
            request_data.update(tracking_result.request_data)

    configuration = tracking_django.get_configuration_from_settings()

    url = get_click_tracking_url(
        DEFAULT_URL_TO_TRACK, metadata=DEFAULT_METADATA,
        configuration=configuration)
    path = get_click_tracking_url_path(url, configuration=configuration)

    request = FakeDjangoRequest()
    request.META["HTTP_X_REAL_IP"] = "10.10.240.22"
    request.META["HTTP_USER_AGENT"] = "Firefox"

    response = TestClickView.as_view()(request, path)

    expected_metadata = {}
    expected_metadata.update(DEFAULT_DEFAULT_METADATA)
    expected_metadata.update(DEFAULT_METADATA)

    assert expected_metadata == result_metadata
    assert request_data ==\
        {"user_agent": "Firefox", "user_ip": "10.10.240.22"}
    assert response.status_code == 302
    assert response["Location"] == DEFAULT_ENCODED_URL_TO_TRACK


def test_empty_click_tracking_view(setup_django):
    result_metadata = {}
    request_data = {}

    class TestClickView(tracking_django.ClickTrackingView):

        def notify_tracking_event(self, tracking_result):
            result_metadata.update(tracking_result.metadata)
            request_data.update(tracking_result.request_data)

    configuration = tracking_django.get_configuration_from_settings()

    url = get_click_tracking_url(
        "", metadata=DEFAULT_METADATA,
        configuration=configuration)
    path = get_click_tracking_url_path(url, configuration=configuration)

    request = FakeDjangoRequest()

    with pytest.raises(Http404):
        TestClickView.as_view()(request, path)

    # No tracking
    assert not result_metadata
    assert not request_data


def test_invalid_click_tracking_view(setup_django):
    result_metadata = {}
    request_data = {}

    class TestClickView(tracking_django.ClickTrackingView):

        def notify_tracking_event(self, tracking_result):
            result_metadata.update(tracking_result.metadata)
            request_data.update(tracking_result.request_data)

    configuration = tracking_django.get_configuration_from_settings()

    url = get_click_tracking_url(
        "", metadata=DEFAULT_METADATA,
        configuration=configuration)
    path = get_click_tracking_url_path(url, configuration=configuration)

    request = FakeDjangoRequest()

    with pytest.raises(Http404):
        TestClickView.as_view()(request, path + "bbb")

    # No tracking
    assert not result_metadata
    assert not request_data


def test_valid_open_tracking_view(setup_django):
    result_metadata = {}
    request_data = {}

    class TestOpenView(tracking_django.OpenTrackingView):

        def notify_tracking_event(self, tracking_result):
            result_metadata.update(tracking_result.metadata)
            request_data.update(tracking_result.request_data)

    configuration = tracking_django.get_configuration_from_settings()

    url = get_open_tracking_url(
        metadata=DEFAULT_METADATA, configuration=configuration)
    path = get_open_tracking_url_path(url, configuration=configuration)

    request = FakeDjangoRequest()
    request.META["HTTP_X_REAL_IP"] = "10.10.240.22"
    request.META["HTTP_USER_AGENT"] = "Firefox"

    response = TestOpenView.as_view()(request, path)

    expected_metadata = {}
    expected_metadata.update(DEFAULT_DEFAULT_METADATA)
    expected_metadata.update(DEFAULT_METADATA)

    assert expected_metadata == result_metadata
    assert request_data ==\
        {"user_agent": "Firefox", "user_ip": "10.10.240.22"}
    assert response.status_code == 200
    assert response.content == TRACKING_PIXEL
    assert response["Content-Type"] == PNG_MIME_TYPE


def test_invalid_open_tracking_view(setup_django):
    result_metadata = {}
    request_data = {}

    class TestOpenView(tracking_django.OpenTrackingView):

        def notify_tracking_event(self, tracking_result):
            result_metadata.update(tracking_result.metadata)
            request_data.update(tracking_result.request_data)

    configuration = tracking_django.get_configuration_from_settings()

    url = get_open_tracking_url(
        metadata=DEFAULT_METADATA, configuration=configuration)
    path = get_open_tracking_url_path(url, configuration=configuration)

    request = FakeDjangoRequest()

    with pytest.raises(Http404):
        TestOpenView.as_view()(request, path + "bbb")

    assert not result_metadata
    assert not request_data
