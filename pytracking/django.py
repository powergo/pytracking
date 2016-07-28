try:
    from ipware.ip import get_ip
except ImportError:
    pass


def get_request_data(request):
    """TODO
    """
    user_agent = request.META.get("HTTP_USER_AGENT")
    ip = get_ip(request)
    return {
        "user_agent": user_agent,
        "user_ip": ip
    }
