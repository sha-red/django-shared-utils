#!/usr/bin/env python

from io import open
import os
from setuptools import setup, find_packages


def read(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, encoding='utf-8') as handle:
        return handle.read()


setup(
    name='django-shared-utils',
    version=__import__('utils').__version__,
    description=' Mix of Python and Django utility functions, classed etc.',
    long_description=read('README.md'),
    author='Erik Stein',
    author_email='code@classlibrary.net',
    url='https://projects.c--y.net/erik/django-shared-utils/',
    license='MIT License',
    platforms=['OS Independent'],
    packages=find_packages(
        exclude=['tests', 'testapp'],
    ),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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