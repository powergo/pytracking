pytracking - Email Open and Click Tracking Library
==================================================

:Authors:
  Resulto Developpement Web Inc.
:Version: 0.1.0

This library provides a set of functions to provide open and click tracking
and to send webhook requests when a tracking pixel or tracking link is
requested.

The library only provides building blocks and does not handle the actual
sending of email or the serving of tracking pixel and links.


.. contents:: Summary
   :backlinks: entry
   :local:



Requirements
------------

pytracking works with Python 3.4+. It doesn't require any external library, but
there are many optional features that have dependencies.


Installation
------------

You can install pytracking using pip:

::

    pip install pytracking

You can install specific features with extras:

::

    pip install pytracking[django,crypto]

You can also install all features:

::

    pip install pytracking[all]



Basic Library Usage
-------------------

You can generate two kinds of tracking links with pytracking: a link to a
transparent tracking pixel and a link that redirects to another link.

Encoding
~~~~~~~~

You can encode metadata in both kinds of links. For example, you can associate
a customer id with a click tracking link so when the customer click on the
link, you'll know exactly which customer clicked on it.

pylinktracking implements a stateless tracking strategy: all necessary
information can be encoded in the tracking links. You can optionally keep
common settings (e.g., default metadata to associate with all links, webhook
URL) in a separate configuration.

The information is encoded using url-safe base64 so anyone intercepting your
links, including your customers, could potentially decode the information. You
can optionally encrypt the tracking information (see below).

Most functions take as a parameter a ``pytracking.Configuration``
instance that tells how to generate the links. You can also pass the
configuration parameters as ``**kwargs`` argument or can mix both: the kwargs
will override the configuration parameters.

Decoding
~~~~~~~~

Once you get a request from a tracking link, you can use pytracking to decode
the link and get a ``pytracking.TrackingResult`` instance, which contains
information such as the link to redirect to (if it's a click tracking link),
the associated metadata, the webhook URL to notify, etc.

Basic Library Examples
----------------------

Get Open Tracking Link
~~~~~~~~~~~~~~~~~~~~~~

::

    import pytracking

    open_tracking_url = pytracking.get_open_tracking_url(
        {"customer_id": 1}, base_open_tracking_url="https://trackingdomain.com/path/",
        webhook_url="http://requestb.in/123", include_webhook_url=True)

    # This will produce a URL such as:
    # https://trackingdomain.com/path/e30203jhd9239754jh21387293jhf989sda=


Get Open Tracking Link with Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    import pytracking

    configuration = pytracking.Configuration(
        base_open_tracking_url="https://trackingdomain.com/path/",
        webhook_url="http://requestb.in/123",
        include_webhook_url=False)

    open_tracking_url = pytracking.get_open_tracking_url(
        {"customer_id": 1}, configuration=configuration)

    # This will produce a URL such as:
    # https://trackingdomain.com/path/e30203jhd9239754jh21387293jhf989sda=


Get Click Tracking Link
~~~~~~~~~~~~~~~~~~~~~~~

::

    import pytracking

    click_tracking_url = pytracking.get_click_tracking_url(
        "http://www.example.com/?query=value", {"customer_id": 1},
        base_click_tracking_url="https://trackingdomain.com/path/",
        webhook_url="http://requestb.in/123", include_webhook_url=True)

    # This will produce a URL such as:
    # https://trackingdomain.com/path/e30203jhd9239754jh21387293jhf989sda=


Get Open Tracking Data from URL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    import pytracking

    full_url = "https://trackingdomain.com/path/e30203jhd9239754jh21387293jhf989sda="
    tracking_result = pytracking.get_open_tracking_result(
        full_url, base_open_tracking_url="https://trackingdomain.com/path/")

    # Metadata is in tracking_result.metadata
    # Webhook URL is in tracking_result.webhook_url


Get Click Tracking Data from URL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    import pytracking

    full_url = "https://trackingdomain.com/path/e30203jhd9239754jh21387293jhf989sda="
    tracking_result = pytracking.get_open_tracking_result(
        full_url, base_click_tracking_url="https://trackingdomain.com/path/")

    # Metadata is in tracking_result.metadata
    # Webhook URL is in tracking_result.webhook_url
    # Tracked URL to redirect to is in tracking_result.tracked_url


Get a 1x1 transparent PNG pixel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    import pytracking

    (pixel_byte_string, mime_type) = pytracking.get_open_tracking_pixel()



Encrypting Data
---------------

You can encrypt your encoded data to prevent third parties from accessing the
tracking data encoded in your link.

To use the encryption feature, you must install pytracking with
``pytracking[crypto]``, which uses the `cryptography Python library
<https://cryptography.io/en/latest/>`_.

Encrypting your data slightly increases the length of the generated URL.

::

    import pytracking
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()

    # Encode
    click_tracking_url = pytracking.get_click_tracking_url(
        "http://www.example.com/?query=value", {"customer_id": 1},
        base_click_tracking_url="https://trackingdomain.com/path/",
        webhook_url="http://requestb.in/123", include_webhook_url=True,
        encryption_bytestring_key=key)

    # Decode
    tracking_result = pytracking.get_open_tracking_result(
        full_url, base_click_tracking_url="https://trackingdomain.com/path/",
        encryption_bytestring_key=key)


Using pytracking with Django
----------------------------

pytracking comes with View classes that you can extend and that handle open and
click tracking link request.

For example, the ``pytracking.django.OpenTrackingView`` will return a 1x1
transparent PNG pixel for GET requests.

The ``pytracking.django.ClickTrackingView`` will return a 302 redirect response
to the tracked URL.

Both views will return a 404 response if the tracking URL is invalid.

Both views will capture the user agent and the user ip of the request. This
information will be available in TrackingResult.request_data.

You can extend both views to determine what to do with the tracking result
(e.g., call a webhook or submit a task to a celery queue).

Finally, you can encode your configuration parameters in your Django settings
or you can compute them in your view.

To use the django feature, you must install pytracking with
``pytracking[django]``.

Configuration parameters in Django settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can provide default configuration parameters in your Django settings by
adding this key in your settings file:

::

    PYTRACKING_CONFIGURATION = {
        "webhook_url": "http://requestb.in/123",
        "base_open_tracking_url": "http://tracking.domain.com/open/",
        "base_click_tracking_url": "http://tracking.domain.com/click/",
        "default_metadata": {"analytics_key": "123456"}
    }


Extending default views
~~~~~~~~~~~~~~~~~~~~~~~

::

    from pytracking import Configuration
    from pytracking.django import OpenTrackingView, ClickTrackingView

    class MyOpenTrackingView(OpenTrackingView):

        def notify_tracking_event(self, tracking_result):
            # Override this method to do something with the tracking result.
            # tracking_result.request_data["user_agent"] and
            # tracking_result.request_data["user_ip"] contains the user agent
            # and ip of the client.
            send_tracking_result_to_queue(tracking_result)

        def notify_decoding_error(self, exception):
            # Called when the tracking link cannot be decoded
            # Override this to, for example, log the exception
            logger.log(exception)

        def get_configuration(self):
            # By defaut, fetchs the configuration parameters from the Django
            # settings. You can return your own Configuration object here if
            # you do not want to use Django settings.
            return Configuration()


    class MyClickTrackingView(ClickTrackingView):

        def notify_tracking_event(self, tracking_result):
            # Override this method to do something with the tracking result.
            # tracking_result.request_data["user_agent"] and
            # tracking_result.request_data["user_ip"] contains the user agent
            # and ip of the client.
            send_tracking_result_to_queue(tracking_result)

        def notify_decoding_error(self, exception):
            # Called when the tracking link cannot be decoded
            # Override this to, for example, log the exception
            logger.log(exception)

        def get_configuration(self):
            # By defaut, fetchs the configuration parameters from the Django
            # settings. You can return your own Configuration object here if
            # you do not want to use Django settings.
            return Configuration()

URLs configuration
~~~~~~~~~~~~~~~~~~

Add this to your urls.py file:

::

    urlpatterns = [
        url(
            "^open/(?P<path>[\w=-]+)/$", MyOpenTrackingView.as_view(),
            name="open_tracking"),
        url(
            "^click/(?P<path>[\w=-]+)/$", MyClickTrackingView.as_view(),
            name="click_tracking"),
    ]


Notifying Webhooks
------------------

You can send a POST request to a webhook with the tracking result. The webhook
feature just package the tracking result as a json string in the POST body. It
also sets the content encoding to ``application/json``.

To use the webhook feature, you must install pytracking with
``pytracking[webhook]``.


::

    import pytracking
    from pytracking.webhook import send_webhook

    # Assumes that the webhook url is encoded in the url.
    full_url = "https://trackingdomain.com/path/e30203jhd9239754jh21387293jhf989sda="
    tracking_result = pytracking.get_open_tracking_result(
        url_path, base_click_tracking_url="https://trackingdomain.com/path/")

    # Will send a POST request with the following json str body:
    #  {
    #    "is_click_tracking": True,
    #    "metadata": {...},
    #    "request_data": None,
    #    "tracked_url": "http://...",
    #    "timestamp": 1389177318
    #  }
    send_webhook(tracking_result)



Modifying HTML emails to add tracking links
-------------------------------------------

If you have an HTML email, pytracking can update all links with tracking links
and it can also add a transparent tracking pixel at the end of your email.

To use the HTML feature, you must install pytracking with ``pytracking[html]``,
which uses the `lxml library <http://lxml.de/>`_.

::

    import pytracking
    from pytracking.html import adapt_html

    html_email_text = "..."
    new_html_email_text = adapt_html(
        html_email_text, extra_metadata={"customer_id": 1},
        click_tracking=True, open_tracking=True)


Testing pytracking
------------------

pytracking uses `tox <https://tox.readthedocs.io/en/latest/>`_ and `py.test
<http://docs.pytest.org/en/latest/>`_. If you have tox installed, just run
``tox`` and all possible configurations of pytracking will be tested on Python
3.4.


TODO
----

1. Add various checks to ensure that the input data is sane and does not bust
   any known limits (e.g., URL length).

2. Add more examples.

3. Allow mulitple webhooks and webhooks per tracking method.

4. Transform Django views into view mixins.

5. Add option to encode the webhook timeout in the tracking URL.

6. Document caveats of using pytracking.html (example: long emails are often
   cut off by the email clients and the tracking pixel is thus not loaded).

7. Add some form of API documentation (at least Configuration and
   TrackingResult), maybe as a separate document.

License
-------

This software is licensed under the `New BSD License`. See the `LICENSE` file
in the repository for the full license text.
