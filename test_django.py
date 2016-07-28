import pytest

try:
    import ipware  # noqa
    support_django = True
except ImportError:
    support_django = False


pytestmark = pytest.mark.skipif(
    not support_django, reason="Django-support lib not installed")


class FakeDjangoRequest(object):
    def __init__(self):
        self.META = {}


@pytest.fixture
def tracking_django():
    # Must call configure before importing tracking_django
    from django.conf import settings
    settings.configure()

    from pytracking import django as tracking_django

    return tracking_django


def test_get_django_request_data(tracking_django):
    request = FakeDjangoRequest()
    request.META["HTTP_X_REAL_IP"] = "10.10.240.22"
    request.META["HTTP_USER_AGENT"] = "Firefox"

    request_data = tracking_django.get_request_data(request)

    assert request_data == {"user_agent": "Firefox", "user_ip": "10.10.240.22"}
