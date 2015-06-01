# Hikvision [![Build Status](https://travis-ci.org/fbradyirl/hikvision.svg?branch=master)](https://travis-ci.org/fbradyirl/hikvision) [![Coverage Status](https://img.shields.io/coveralls/fbradyirl/hikvision.svg)](https://coveralls.io/r/fbradyirl/hikvision?branch=master)

Introduction
============
This is a python module providing a basic python 
interface to interact with a Hikvision IP Camera

This is licensed under the MIT license.

Getting started
===============

This module is tested against firmware 5.2.0. 
It may work on older versions, but that has not been tested.

For further info on  the camera API's see:
CGI API Guide:
http://bit.ly/1RuyUuF

Requirements
------------

module requires:
 * requests>=2.0


Install
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

hik_camera = hikvision.api.CreateDevice('192.168.2.5', username='admin', password='12345')
hik_camera.enable_motion_detection()
hik_camera.disable_motion_detection()
hik_camera.is_motion_detection_enabled()
```

host
*Required
This is the IP address of your Hikvision camera. Example: 192.168.1.32

username
*Required
Your Hikvision camera username

password
*Required
Your Hikvision camera username



TODO
------------
Add more functions

Developer
=========

hikvision is hosted by Github at https://github.com/fbradyirl/hikvision

CI run after commit:

```python
flake8 hikvision
pylint hikvision
coverage run -m unittest discover tests
```

Copyright (c) 2015 Finbarr Brady.
