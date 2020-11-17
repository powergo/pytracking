Changelog - pytracking
======================

0.2.2 - November 17th 2020
--------------------------

- Updated django-ipware to >=2.0.
- Updated tests structure and added Github Actions for running tests
- Updated supported Python versions to 3.6, 3.7, 3.8, 3.9

0.2.1 - October 28th 2020
-------------------------

- Added append_slash configuration parameter to append a slash to click and
  open tracking URLs
- Updated dependencies to prevent breaking changes in django-ipware
- Updated supported Python version to 3.6
- Updated README file
- Removed CircleCI integration

0.2.0 - June 6th 2017
---------------------

- Added request parameter to notify_decoding_error callback in
  ``pytracking.django.TrackingView``
- Added a reference to professional services in README.rst


0.1.0 - August 10th 2016
------------------------

- First release!
- Support encoding and decoding of open/click tracking links.
- Basic Django Views.
- Can send webhook POST requests with tracking data.
- Can encrypt tracking data instead of relying on base64.
- Can modify HTML content to replace links and add tracking pixel.
