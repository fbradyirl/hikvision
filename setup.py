#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'requests>=2.21.0']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Finbarr Brady",
    author_email='fbradyirl@github.io',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
    description='Provides a python interface to interact with a hikvision camera',
    install_requires=requirements,
    license='MIT',
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='hikvision camera python cgi interface',
    name='hikvision',
    packages=['hikvision'],
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/fbradyirl/hikvision',
    version='2.0.1',
    zip_safe=False,
)
