from lxml import html

from pytracking.tracking import (
    get_configuration, get_open_tracking_url, get_click_tracking_url)


DEFAULT_ATTRIBUTES = {
    "border": "0",
    "width": "0",
    "height": "0",
    "alt": ""
}


def adapt_html(
        html_text, extra_metadata, click_tracking=True, open_tracking=True,
        configuration=None, **kwargs):
    """Changes an HTML string by replacing links (<a href...>) with tracking
    links and by adding a 1x1 transparent pixel just before the closing body
    tag.

    :param html_text: The HTML to change (unicode or bytestring).
    :param extra_metadata: A dict that can be json-encoded and that will
        be encoded in the tracking link.
    :param click_tracking: If links (<a href...>) must be changed.
    :param open_tracking: If a transparent pixel must be added before the
        closing body tag.
    :param configuration: An optional Configuration instance.
    :param kwargs: Optional configuration parameters. If provided with a
        Configuration instance, the kwargs parameters will override the
        Configuration parameters.
    """
    configuration = get_configuration(configuration, kwargs)

    tree = html.fromstring(html_text)

    if click_tracking:
        _replace_links(tree, extra_metadata, configuration)

    if open_tracking:
        _add_tracking_pixel(tree, extra_metadata, configuration)

    new_html_text = html.tostring(tree)

    return new_html_text.decode("utf-8")


def _replace_links(tree, extra_metadata, configuration):
    for (element, attribute, link, pos) in tree.iterlinks():
        if element.tag == "a" and attribute == "href" and _valid_link(link):
            new_link = get_click_tracking_url(
                link, extra_metadata, configuration)
            element.attrib["href"] = new_link


def _add_tracking_pixel(tree, extra_metadata, configuration):
    url = get_open_tracking_url(extra_metadata, configuration)
    pixel = html.Element("img", {"src": url})
    tree.body.append(pixel)


def _valid_link(link):
    return link.startswith("http://") or link.startswith("https://") or\
        link.startswith("//")
