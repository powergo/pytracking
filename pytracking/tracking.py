import base64
from collections import namedtuple
from copy import deepcopy
import json
import time
from urllib.parse import urljoin

try:
    # Optional Import
    from cryptography.fernet import Fernet
except ImportError:
    pass


TRACKING_PIXEL = base64.b64decode(
    b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=')  # noqa

PNG_MIME_TYPE = "image/png"

DEFAULT_TIMEOUT_SECONDS = 5


class Configuration(object):

    def __init__(
            self, webhook_url=None,
            webhook_timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
            include_webhook_url=False, base_open_tracking_url=None,
            base_click_tracking_url=None, default_metadata=None,
            include_default_metadata=False, encryption_bytestring_key=None,
            encoding="utf-8", **kwargs):
        """

        :param webhook_url: The webhook to notify when a click or open is
            registered.
        :param webhook_timeout_seconds: Raises a timeout if the webhook does
            not response before the value. Default to None
        :param include_webhook_url: If True, the webhook URL is included in the
            encoded link. Default to False.
        :param base_open_tracking_url: The base URL to prepend to the encoded
            open tracking link.
        :param base_click_tracking_url: The base URL to prepend to the encoded
            click tracking link.
        :param default_metadata: Default metadata to associated with all
            tracking events.
        :param include_default_metadata: If True, the default metadata is
            included in the encoded link. Default to False.
        :param encryption_bytestring_key: The encryption key given by Fernet.
        :param encoding: The encoding to use to encode and decode the tracking
            link. Default to utf-8.
        :param kwargs: Other args
        """
        self.webhook_url = webhook_url
        self.webhook_timeout_seconds = webhook_timeout_seconds
        self.include_webhook_url = include_webhook_url
        self.base_open_tracking_url = base_open_tracking_url
        self.base_click_tracking_url = base_click_tracking_url
        self.default_metadata = default_metadata
        self.include_default_metadata = include_default_metadata
        self.encryption_bytestring_key = encryption_bytestring_key
        self.encoding = encoding
        self.kwargs = kwargs
        self.encryption_key = None

        self.cache_encryption_key()

    def __str__(self):
        return "<pytracking.Configuration> "\
            "Open Tracking URL: {0} "\
            "Click Tracking URL: {1} "\
            "Webhook URL: {2}".format(
                self.base_open_tracking_url, self.base_click_tracking_url,
                self.webhook_url)

    def __deepcopy__(self, memo):
        new_config = Configuration()
        for key, value in self.__dict__.items():
            if key != "encryption_key":
                new_config.__dict__[key] = deepcopy(value)

        return new_config

    def merge_with_kwargs(self, kwargs):
        """

        :param kwargs:
        """
        new_configuration = deepcopy(self)
        for key, value in kwargs.items():
            if hasattr(new_configuration, key):
                setattr(new_configuration, key, value)

        # In case a new encryption key was provided
        new_configuration.cache_encryption_key()

        return new_configuration

    def cache_encryption_key(self):
        """TODO
        """
        if self.encryption_bytestring_key:
            self.encryption_key = Fernet(self.encryption_bytestring_key)
        else:
            self.encryption_key = None

    def get_data_to_embed(self, url_to_track, extra_metadata):
        """TODO

        :param url_to_track:
        :param meta_data:
        """
        data = {}
        if url_to_track:
            data["url"] = url_to_track
        metadata = {}

        if self.include_default_metadata and self.default_metadata:
            metadata.update(self.default_metadata)
        if extra_metadata:
            metadata.update(extra_metadata)

        if metadata:
            data["metadata"] = metadata

        if self.include_webhook_url and self.webhook_url:
            data["webhook"] = self.webhook_url

        return data

    def get_url_encoded_data_str(self, data_to_embed):
        """TODO
        """
        json_byte_str = json.dumps(data_to_embed).encode(self.encoding)

        if self.encryption_key:
            data_str = self.encryption_key.encrypt(
                json_byte_str).decode(self.encoding)
        else:
            data_str = base64.urlsafe_b64encode(
                json_byte_str).decode(self.encoding)

        return data_str

    def get_open_tracking_url_from_data_str(self, data_str):
        """TODO
        """
        return urljoin(self.base_open_tracking_url, data_str)

    def get_click_tracking_url_from_data_str(self, data_str):
        """TODO
        """
        return urljoin(self.base_click_tracking_url, data_str)

    def get_open_tracking_url(self, extra_metadata):
        data_to_embed = self.get_data_to_embed(None, extra_metadata)
        data_str = self.get_url_encoded_data_str(data_to_embed)
        return self.get_open_tracking_url_from_data_str(data_str)

    def get_click_tracking_url(self, url_to_track, extra_metadata):
        """TODO
        """
        data_to_embed = self.get_data_to_embed(url_to_track, extra_metadata)
        data_str = self.get_url_encoded_data_str(data_to_embed)
        return self.get_click_tracking_url_from_data_str(data_str)

    def get_tracking_result(
            self, encoded_url_path, request_data, is_open):
        """TODO
        """
        timestamp = int(time.time())
        if encoded_url_path.startswith("/"):
            encoded_url_path = encoded_url_path[1:]

        if self.encryption_key:
            payload = self.encryption_key.decrypt(
                encoded_url_path.encode(self.encoding)).decode(
                    self.encoding)
        else:
            payload = base64.urlsafe_b64decode(
                encoded_url_path.encode(self.encoding)).decode(
                    self.encoding)
        data = json.loads(payload)

        metadata = {}
        if not self.include_default_metadata and self.default_metadata:
            metadata.update(self.default_metadata)
        metadata.update(data.get("metadata", {}))

        if self.include_webhook_url:
            webhook_url = data.get("webhook")
        else:
            webhook_url = self.webhook_url

        return TrackingResult(
            is_open_tracking=is_open,
            is_click_tracking=not is_open,
            tracked_url=data.get("url"),
            webhook_url=webhook_url,
            metadata=metadata,
            request_data=request_data,
            timestamp=timestamp,
        )

    def get_click_tracking_url_path(self, url):
        """TODO
        """
        return url[len(self.base_click_tracking_url):]

    def get_open_tracking_url_path(self, url):
        """TODO
        """
        return url[len(self.base_open_tracking_url):]


TrackingResultJSON = namedtuple(
    "TrackingResultJSON", [
        "is_open_tracking", "is_click_tracking", "tracked_url", "webhook_url",
        "metadata", "request_data", "timestamp"])


class TrackingResult(object):

    def __init__(self, is_open_tracking=False, is_click_tracking=False,
                 tracked_url=None, webhook_url=None,
                 metadata=None, request_data=None, timestamp=None):
        """
        :param is_open_tracking: If the result is about open tracking.
        :param is_click_tracking: If the result is about click tracking.
        :param tracked_url: The URL to redirect to. Provided only if
            is_click_tracking is True
        :param webhook_url: The webhook URL to send the tracking notification.
        :param metadata: The metadata (dict) associated with a tracking link.
        :param request_data: The request data (dict) associated with the client
            that made the request to the tracking link.
        :param timestamp: Number of seconds since epoch in UTC
        """
        self.is_open_tracking = is_open_tracking
        self.is_click_tracking = is_click_tracking
        self.tracked_url = tracked_url
        self.webhook_url = webhook_url
        self.metadata = metadata
        self.request_data = request_data
        self.timestamp = timestamp

    def to_json_dict(self):
        """Returns a version of the tracking result that can be safely encoded
        and decoded in JSON

        :rtype: TrackingResultJSON
        """
        return TrackingResultJSON(
            self.is_open_tracking, self.is_click_tracking, self.tracked_url,
            self.webhook_url, self.metadata, self.request_data, self.timestamp)

    def __str__(self):
        return "<pytracking.TrackingResult> is_open_tracking: {0} "\
            "is_click_tracking: {1} tracked_url: {2}".format(
                self.is_open_tracking, self.is_click_tracking,
                self.tracked_url)


def get_configuration(configuration, kwargs):
    """Returns a Configuration instance that merges a configuration instance
    and individual parameters given in a dictionary (usually, the **kwargs of
    an API function).

    The kwargs parameters take precendence over the Configuration instance.
    """
    if configuration:
        configuration = configuration.merge_with_kwargs(kwargs)
    else:
        configuration = Configuration().merge_with_kwargs(kwargs)
    return configuration


def get_open_tracking_url(metadata=None, configuration=None, **kwargs):
    """Returns a tracking URL encoding the metadata and other information
    specified in the configuration or kwargs.

    :param metadata: A dict that can be json-encoded and that will be encoded
        in the tracking link.
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)

    return configuration.get_open_tracking_url(metadata)


def get_open_tracking_pixel():
    """Returns a tuple consisting of a binary string (the transparent PNG
    pixel) and the MIME type.
    """
    return (TRACKING_PIXEL, PNG_MIME_TYPE)


def get_click_tracking_url(
        url_to_track, metadata=None, configuration=None, **kwargs):
    """Returns a tracking URL encoding the link to track, the provided
    metadata, and other information specified in the configuration or kwargs.

    :param url_to_track: The URL to track.
    :param metadata: A dict that can be json-encoded and that will be encoded
        in the tracking link.
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)

    return configuration.get_click_tracking_url(url_to_track, metadata)


def get_click_tracking_result(
        encoded_url_path, request_data=None, configuration=None, **kwargs):
    """Get a TrackingResult instance from an encoded click tracking link.

    :param encoded_url_path: The part of the URL that is encoded and contains
        the tracking information or the full URL (base_click_tracking_url must
        be provided)
    :param request_data: The dictionary to attach to the TrackingResult
        representing the information (e.g., user agent) of the client that
        requested the tracking link.
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)
    if configuration.base_click_tracking_url and\
            encoded_url_path.startswith(
                configuration.base_click_tracking_url):
        encoded_url_path = get_click_tracking_url_path(
            encoded_url_path, configuration)
    return configuration.get_tracking_result(
        encoded_url_path, request_data, is_open=False)


def get_click_tracking_url_path(
        url, configuration=None, **kwargs):
    """Get a part of a URL that contains the encoded click tracking
    information. This is the part that needs to be supplied to
    get_click_tracking_result.

    :param url: The full tracking URL
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)
    return configuration.get_click_tracking_url_path(url)


def get_open_tracking_result(
        encoded_url_path, request_data=None, configuration=None, **kwargs):
    """Get a TrackingResult instance from an encoded open tracking link.

    :param encoded_url_path: The part of the URL that is encoded and contains
        the tracking information or the full URL (base_open_tracking_url must
        be provided)
    :param request_data: The dictionary to attach to the TrackingResult
        representing the information (e.g., user agent) of the client that
        requested the tracking link.
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)
    if configuration.base_open_tracking_url and\
            encoded_url_path.startswith(
                configuration.base_open_tracking_url):
        encoded_url_path = get_open_tracking_url_path(
            encoded_url_path, configuration)
    return configuration.get_tracking_result(
        encoded_url_path, request_data, is_open=True)


def get_open_tracking_url_path(
        url, configuration=None, **kwargs):
    """Get a part of a URL that contains the encoded open tracking
    information. This is the part that needs to be supplied to
    get_open_tracking_result.

    :param url: The full tracking URL
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)
    return configuration.get_open_tracking_url_path(url)
