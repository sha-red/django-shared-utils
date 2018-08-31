# -*- coding: utf-8 -*-
from __future__ import unicode_literals


try:
    from ._version import __version__
except ImportError:
    __version__ = '0.0.0+see-git-tag'


VERSION = __version__.split('+')
VERSION = tuple(list(map(int, VERSION[0].split('.'))) + VERSION[1:])
