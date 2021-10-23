from django.conf import settings
from django.http import (
    HttpResponseRedirect, Http404, HttpResponse)
from django.views.generic import View
from ipware import get_client_ip
from pytracking.tracking import (
    get_configuration, TRACKING_PIXEL, PNG_MIME_TYPE)


class TrackingView(View):
    """Base Tracking View.

    Subclasses should override notify_* methods.
    """

    def notify_tracking_event(self, tracking_result):
        """Called once the tracking link has been decoded, and before
        responding with a redirect or a tracking pixel.

        :param tracking_result: An instance of TrackingResult.
        """
        pass

    def notify_decoding_error(self, exception, request):
        """Called when a decoding error occurs, and before
        responding with a 404.

        :param exception: The exception that was raised when trying to decode a
            tracking link.
        """
        pass

    def get_configuration(self):
        """Returns a Configuration instance built from
        settings.PYTRACKING_CONFIGURATION.

        Override this method if you want to build your own Configuration
        instance.
        """
        return get_configuration_from_settings()


class ClickTrackingView(TrackingView):
    """View that decodes a URL, call notify_tracking_event, and then sends a
    302 redirect to the tracked URL.

    This view captures the user agent and the ip of the client that makes a
    request and puts this information in the request_data dictionary under the
    ``user_agent`` and ``user_ip`` keys.

    If a decoding error occurs, notify_decoding_error is called and a 404 is
    returned.

    If no tracking url is present in the decoded URL, a 404 is returned.
    """

    def get(self, request, path):
        configuration = self.get_configuration()

        try:
            tracking_result = get_tracking_result(
                request, path, False, configuration)
        except Exception as e:
            self.notify_decoding_error(e, request)
            raise Http404

        if not tracking_result.tracked_url:
            raise Http404

        self.notify_tracking_event(tracking_result)

        return HttpResponseRedirect(tracking_result.tracked_url)


class OpenTrackingView(TrackingView):
    """View that decodes a URL, call notify_tracking_event, and then returns a
    1x1 transparent PNG file with a image/png mime type.

    This view captures the user agent and the ip of the client that makes a
    request and puts this information in the request_data dictionary under the
    ``user_agent`` and ``user_ip`` keys.

    If a decoding error occurs, notify_decoding_error is called and a 404 is
    returned.
    """

    def get(self, request, path):
        configuration = self.get_configuration()

        try:
            tracking_result = get_tracking_result(
                request, path, True, configuration)
        except Exception as e:
            self.notify_decoding_error(e, request)
            raise Http404

        self.notify_tracking_event(tracking_result)

        return HttpResponse(TRACKING_PIXEL, content_type=PNG_MIME_TYPE)


def get_request_data(request):
    """Retrieves the user agent and the ip of the client from the Django
    request.

    We use ipware to retrieve the "real" IP (e.g., load balancer will often put
    the client IP in X-Forwarded-For header).
    """
    user_agent = request.META.get("HTTP_USER_AGENT")
    ip = get_client_ip(request)[0]
    return {
        "user_agent": user_agent,
        "user_ip": ip
    }


def get_configuration_from_settings(settings_name="PYTRACKING_CONFIGURATION"):
    """Builds a Configuration instance from the parameters in
    settings.PYTRACKING_CONFIGURATION.
    """
    kwargs = getattr(settings, settings_name)
    return get_configuration(None, kwargs)


def get_tracking_result(request, path, is_open, configuration=None, **kwargs):
    """Builds a tracking result from a Django request.

    :param request: A Django request
    :param path: The path of the URL that is encoded (usually possible to
        distinguish this path using a URL parameter).
    :param is_open: If this is an open tracking link request.
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)
    request_data = get_request_data(request)
    return configuration.get_tracking_result(
        path, request_data, is_open)
