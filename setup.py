# Copyright (c) 2015, 2019 Finbarr Brady <https://github.com/fbradyirl>
# Licensed under the MIT license.

# Used this guide to create module
# http://peterdowns.com/posts/first-time-with-pypi.html

# git tag 0.1 -m "0.1 release"
# git push --tags origin master
#
# Upload to PyPI Live
# python setup.py register -r pypi ; python setup.py sdist upload -r pypi
#

from distutils.core import setup

setup(
    name='hikvision',
    version='1.3',
    description='Provides a python interface to interact with a hikvision camera',
    author='Finbarr Brady',
    author_email='fbradyirl@users.noreply.github.com',
    url='https://github.com/fbradyirl/hikvision',
    download_url = 'https://github.com/fbradyirl/hikvision/tarball/1.2',
    license='MIT',
    keywords='hikvision camera python cgi interface',
    packages=['hikvision'],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet'
        ],
    )
