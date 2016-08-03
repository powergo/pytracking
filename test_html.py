import pytest

from test_pytracking import (
    DEFAULT_BASE_OPEN_TRACKING_URL, DEFAULT_BASE_CLICK_TRACKING_URL,
    DEFAULT_METADATA, DEFAULT_WEBHOOK_URL, DEFAULT_DEFAULT_METADATA,
    )

TEST_HTML_EMAIL = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"></meta>
<head>
</head>
<body>
<h1>Hello World</h1>
<p>
<a href="http://www.example.com">This is an inline link</a> with some text.
</p>
<p>
<a href="mailto:bob@bob.com">Mail to Bob!</a>
</p>
<ul>
<li><a href="http://www.domain2.com">
<img src="http://www.test.com/test.jpg"></a></li>
</ul>
</body>
</html>
"""


DEFAULT_SETTINGS = {
    "webhook_url": DEFAULT_WEBHOOK_URL,
    "base_open_tracking_url": DEFAULT_BASE_OPEN_TRACKING_URL,
    "base_click_tracking_url": DEFAULT_BASE_CLICK_TRACKING_URL,
    "default_metadata": DEFAULT_DEFAULT_METADATA
}

try:
    from lxml import html  # noqa

    import pytracking.html as tracking_html

    support_html = True
except ImportError:
    support_html = False


pytestmark = pytest.mark.skipif(
    not support_html, reason="HTML-support lib not installed")


def test_adapt_html_full():
    new_html = tracking_html.adapt_html(
        TEST_HTML_EMAIL, DEFAULT_METADATA, **DEFAULT_SETTINGS)

    tree = html.fromstring(new_html)

    pixel_img = tree.xpath("//body/img")[-1]

    assert pixel_img is not None
