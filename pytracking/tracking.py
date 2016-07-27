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
            **kwargs):
        """

        :param webhook_url:
        :param webhook_timeout_seconds:
        :param include_webhook_url:
        :param base_open_tracking_url:
        :param base_click_tracking_url:
        :param default_metadata:
        :param include_default_metadata:
        :param encryption_bytestring_key:
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
        self.kwargs = kwargs
        self.encryption_key = None

        self.cache_encryption_key()

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

    def get_url_encoded_data_str(self, data_to_embed, encoding="utf-8"):
        """TODO
        """
        json_byte_str = json.dumps(data_to_embed).encode(encoding)

        if self.encryption_key:
            data_str = self.encryption_key.encrypt(
                json_byte_str).decode(encoding)
        else:
            data_str = base64.urlsafe_b64encode(
                json_byte_str).decode(encoding)

        return data_str

    def get_click_tracking_url_from_data_str(self, data_str):
        """TODO
        """
        return urljoin(self.base_click_tracking_url, data_str)

    def get_click_tracking_url(
            self, url_to_track, extra_metadata, encoding="utf-8"):
        """TODO
        """
        data_to_embed = self.get_data_to_embed(url_to_track, extra_metadata)
        data_str = self.get_url_encoded_data_str(data_to_embed, encoding)
        return self.get_click_tracking_url_from_data_str(data_str)


class TrackingResult(object):

    def __init__(self, is_open_tracking=False, is_click_tracking=False,
                 tracked_url=None, webhook_url=None,
                 meta_data=None, user_ip=None, user_agent=None):
        """
        :param is_open_tracking:
        :param is_click_tracking:
        :param tracked_url:
        :param webhook_url:
        :param meta_data:
        :param user_ip:
        :param user_agent:
        """
        self.is_open_tracking = is_open_tracking
        self.is_click_tracking = is_click_tracking
        self.tracked_url = tracked_url
        self.webhook_url = webhook_url
        self.meta_data = meta_data
        self.user_ip = user_ip
        self.user_agent = user_agent


def get_click_tracking_url(
        url_to_track, metadata=None, encoding="utf-8", configuration=None,
        **kwargs):
    """TODO
    """
    if configuration:
        configuration = configuration.merge_with_kwargs(kwargs)
    else:
        configuration = Configuration().merge_with_kwargs(kwargs)

    print("MERGED")

    return configuration.get_click_tracking_url(
        url_to_track, metadata, encoding)
