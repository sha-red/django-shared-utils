#!/usr/bin/env python

from io import open
import os
from setuptools import setup, find_packages


def get_version(prefix):
    import re
    with open(os.path.join(prefix, '__init__.py')) as fd:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fd.read()))
    return metadata['version']


def read(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, encoding='utf-8') as handle:
        return handle.read()


setup(
    name='django-shared-utils',
    version=get_version('shared/utils'),
    description=' Mix of Python and Django utility functions, classed etc.',
    long_description=read('README.md'),
    author='Erik Stein',
    author_email='erik@classlibrary.net',
    url='https://projects.c--y.net/erik/django-shared-utils/',
    license='MIT License',
    platforms=['OS Independent'],
    packages=find_packages(
        exclude=['tests', 'testapp'],
    ),
    namespace_packages=['shared'],
    include_package_data=True,
    install_requires=[
        # 'django<2', commented out to make `pip install -U` easier
        'python-dateutil',
        'beautifulsoup4',
        'translitcodec',
    ],
    classifiers=[
        # 'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        'Topic :: Utilities',
    ],
    zip_safe=False,
    tests_require=[
        'Django',
        # 'coverage',
        # 'django-mptt',
        # 'pytz',
    ],
    # test_suite='testapp.runtests.runtests',
)
