# Introduction 

[![Pypi](https://img.shields.io/pypi/v/hikvision.svg)](https://pypi.python.org/pypi/hikvision) [![Build Status](https://travis-ci.org/fbradyirl/hikvision.svg?branch=master)](https://travis-ci.org/fbradyirl/hikvision) [![Coverage Status](https://coveralls.io/repos/fbradyirl/hikvision/badge.svg?branch=master)](https://coveralls.io/r/fbradyirl/hikvision?branch=master)

This is a very basic python module providing a basic python
interface to interact with a Hikvision IP Camera

This is licensed under the MIT license.

## Getting started

This module is tested against firmware 5.2.0.
It may work on older versions, but that has not been tested.

For further info on  the camera API's see:
CGI API Guide:
http://bit.ly/1RuyUuF


## Development

hikvision is hosted by Github at https://github.com/fbradyirl/hikvision

CI run after commit:

```python
tox
```

## Install
-------
```python
git clone --recursive git@github.com:fbradyirl/hikvision.git
cd hikvision
# NOTE: You might need administrator privileges to install python modules.
pip install -r requirements.txt
pip install -e .
```

# Usage

Variables:

```python
import hikvision.api

# This will use http by default (not https)
# pass False to the digest_auth parameter of CreateDevice to fallback to basic auth
# (note that basic auth and http without ssl are inherently insecure)
# more recent hikvision firmwares default to turning basic auth off
# (and that's a good idea for security)
hik_camera = hikvision.api.CreateDevice('192.168.2.5', username='admin', password='12345')
hik_camera.enable_motion_detection()
hik_camera.disable_motion_detection()
hik_camera.is_motion_detection_enabled()
```

* `host` (*Required) : This is the IP address of your Hikvision camera. Example: 192.168.1.32

* `username` (*Required) : Your Hikvision camera username

* `password` (*Required) : Your Hikvision camera username


# History


2.0.3 (07-09-2020)
------------------

* Updated to use travis, tox, and some other cosmetic improvements.


