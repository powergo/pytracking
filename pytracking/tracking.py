import base64
from copy import deepcopy
import json
from urllib.parse import urljoin

try:
    # Optional Import
    from cryptography.fernet import Fernet
except ImportError:
    pass


class Configuration(object):

    def __init__(
            self, webhook_url=None, webhook_timeout_seconds=5,
            include_webhook_url=False, base_open_tracking_url=None,
            base_click_tracking_url=None, default_metadata=None,
            include_default_metadata=False, encryption_bytestring_key=None,
            encoding="utf-8", **kwargs):
        """

        :param webhook_url:
        :param webhook_timeout_seconds:
        :param include_webhook_url:
        :param base_open_tracking_url:
        :param base_click_tracking_url:
        :param default_metadata:
        :param include_default_metadata:
        :param encryption_bytestring_key:
        :param encoding:
        :param kwargs:
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
        data = {"url": url_to_track}
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

    def get_click_tracking_url_from_data_str(self, data_str):
        """TODO
        """
        return urljoin(self.base_click_tracking_url, data_str)

    def get_click_tracking_url(self, url_to_track, extra_metadata):
        """TODO
        """
        data_to_embed = self.get_data_to_embed(url_to_track, extra_metadata)
        data_str = self.get_url_encoded_data_str(data_to_embed)
        return self.get_click_tracking_url_from_data_str(data_str)

    def get_click_tracking_result(self, encoded_url_path, request_data):
        """TODO
        """
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
            is_click_tracking=True,
            tracked_url=data["url"],
            webhook_url=webhook_url,
            metadata=metadata,
            request_data=request_data,
        )

    def get_tracking_url_path(self, url):
        """TODO
        """
        return url[len(self.base_click_tracking_url):]


class TrackingResult(object):

    def __init__(self, is_open_tracking=False, is_click_tracking=False,
                 tracked_url=None, webhook_url=None,
                 metadata=None, request_data=None):
        """
        :param is_open_tracking:
        :param is_click_tracking:
        :param tracked_url:
        :param webhook_url:
        :param metadata:
        :param request_data:
        """
        self.is_open_tracking = is_open_tracking
        self.is_click_tracking = is_click_tracking
        self.tracked_url = tracked_url
        self.webhook_url = webhook_url
        self.metadata = metadata
        self.request_data = request_data

    def __str__(self):
        return "<pytracking.TrackingResult> is_open_tracking: {0} "\
            "is_click_tracking: {1} tracked_url: {2}".format(
                self.is_open_tracking, self.is_click_tracking,
                self.tracked_url)


def get_configuration(configuration, kwargs):
    """TODO
    """
    if configuration:
        configuration = configuration.merge_with_kwargs(kwargs)
    else:
        configuration = Configuration().merge_with_kwargs(kwargs)
    return configuration


def get_click_tracking_url(
        url_to_track, metadata=None, configuration=None, **kwargs):
    """TODO
    """
    configuration = get_configuration(configuration, kwargs)

    return configuration.get_click_tracking_url(url_to_track, metadata)


def get_click_tracking_result(
        encoded_url_path, request_data=None, configuration=None, **kwargs):
    """TODO
    """
    configuration = get_configuration(configuration, kwargs)
    return configuration.get_click_tracking_result(
        encoded_url_path, request_data)


def get_tracking_url_path(
        url, configuration=None, **kwargs):
    """
    """
    configuration = get_configuration(configuration, kwargs)
    return configuration.get_tracking_url_path(url)
