from django.conf import settings
from django.http import (
    HttpResponseRedirect, Http404, HttpResponse)
from django.views.generic import View
from ipware.ip import get_ip
from pytracking.tracking import (
    get_configuration, TRACKING_PIXEL, PNG_MIME_TYPE)


class TrackingView(View):
    """TODO
    """

    def notify_tracking_event(self, tracking_result):
        pass

    def notify_decoding_error(self, exception):
        pass

    def get_configuration(self):
        return get_configuration_from_settings()


class ClickTrackingView(TrackingView):
    """TODO
    """

    def get(self, request, path):
        configuration = self.get_configuration()

        try:
            tracking_result = get_tracking_result(
                request, path, False, configuration)
        except Exception as e:
            self.notify_decoding_error(e)
            raise Http404

        if not tracking_result.tracked_url:
            raise Http404

        self.notify_tracking_event(tracking_result)

        return HttpResponseRedirect(tracking_result.tracked_url)


class OpenTrackingView(TrackingView):
    """TODO
    """

    def get(self, request, path):
        configuration = self.get_configuration()

        try:
            tracking_result = get_tracking_result(
                request, path, False, configuration)
        except Exception as e:
            self.notify_decoding_error(e)
            raise Http404

        self.notify_tracking_event(tracking_result)

        return HttpResponse(TRACKING_PIXEL, content_type=PNG_MIME_TYPE)


def get_request_data(request):
    """TODO
    """
    user_agent = request.META.get("HTTP_USER_AGENT")
    ip = get_ip(request)
    return {
        "user_agent": user_agent,
        "user_ip": ip
    }


def get_configuration_from_settings():
    """TODO
    """
    kwargs = getattr(settings, "PYTRACKING_CONFIGURATION")
    return get_configuration(None, kwargs)


def get_tracking_result(request, path, is_open, configuration=None, **kwargs):
    """TODO
    """
    configuration = get_configuration(configuration, kwargs)
    request_data = get_request_data(request)
    return configuration.get_tracking_result(
        path, request_data, is_open)
