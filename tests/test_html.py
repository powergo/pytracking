from pytracking import (
    get_click_tracking_url_path, get_open_tracking_url_path,
    get_open_tracking_result, get_click_tracking_result)

from .test_pytracking import (
    DEFAULT_BASE_OPEN_TRACKING_URL, DEFAULT_BASE_CLICK_TRACKING_URL,
    DEFAULT_METADATA, DEFAULT_WEBHOOK_URL, DEFAULT_DEFAULT_METADATA,
    EXPECTED_METADATA)

from lxml import html
import pytracking.html as tracking_html

TEST_HTML_EMAIL = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"></meta>
<head>
</head>
<body>
<h1>Hello World Some éàù and &eacute; entities.</h1>
<p>
<a href="http://www.example.com/foo/?question=response">This is an inline link
</a> with some text.
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


def test_adapt_html_full():
    new_html = tracking_html.adapt_html(
        TEST_HTML_EMAIL, DEFAULT_METADATA, **DEFAULT_SETTINGS)

    tree = html.fromstring(new_html)

    _test_open_tracking(tree)
    _test_click_tracking(tree)


def test_adapt_html_click_only():
    new_html = tracking_html.adapt_html(
        TEST_HTML_EMAIL, DEFAULT_METADATA, open_tracking=False,
        **DEFAULT_SETTINGS)

    tree = html.fromstring(new_html)
    assert len(tree.xpath("//img")) == 1

    _test_click_tracking(tree)


def test_adapt_html_open_only():
    new_html = tracking_html.adapt_html(
        TEST_HTML_EMAIL, DEFAULT_METADATA, click_tracking=False,
        **DEFAULT_SETTINGS)

    tree = html.fromstring(new_html)

    _test_open_tracking(tree)

    links = tree.xpath("//a")

    assert links[0].attrib["href"] ==\
        "http://www.example.com/foo/?question=response"
    assert links[1].attrib["href"] == "mailto:bob@bob.com"
    assert links[2].attrib["href"] == "http://www.domain2.com"


def _test_click_tracking(tree):
    links = tree.xpath("//a")
    first_link_url_path = get_click_tracking_url_path(
        links[0].attrib["href"], **DEFAULT_SETTINGS)
    click_result = get_click_tracking_result(
        first_link_url_path, **DEFAULT_SETTINGS)
    assert click_result.metadata == EXPECTED_METADATA
    assert click_result.tracked_url ==\
        "http://www.example.com/foo/?question=response"

    assert links[1].attrib["href"] == "mailto:bob@bob.com"

    second_link_url_path = get_click_tracking_url_path(
        links[2].attrib["href"], **DEFAULT_SETTINGS)
    click_result = get_click_tracking_result(
        second_link_url_path, **DEFAULT_SETTINGS)
    assert click_result.metadata == EXPECTED_METADATA
    assert click_result.tracked_url == "http://www.domain2.com"


def _test_open_tracking(tree):
    pixel_img = tree.xpath("//img")[-1]
    open_url_path = get_open_tracking_url_path(
        pixel_img.attrib["src"], **DEFAULT_SETTINGS)
    open_result = get_open_tracking_result(
        open_url_path, **DEFAULT_SETTINGS)

    assert open_result.metadata == EXPECTED_METADATA
