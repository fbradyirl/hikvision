# Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
# Licensed under the MIT license.

# Used this guide to create module
# http://peterdowns.com/posts/first-time-with-pypi.html

from distutils.core import setup

setup(
    name='hikvision',
    version='0.4',
    description='Provides a python interface to interact with a hikvision camera',
    author='Finbarr Brady',
    author_email='fbradyirl@users.noreply.github.com',
    url='https://github.com/fbradyirl/hikvision',
    download_url = 'https://github.com/fbradyirl/hikvision/tarball/0.4',
    keywords='hikvision camera python cgi interface',
    packages=['hikvision'],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet'
        ],
    )
