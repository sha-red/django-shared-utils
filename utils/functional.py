# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2017


def firstof(iterable, default=None):
    """
    Returns the first value which is neither empty nor None.

    """
    for value in iterable:
        if value:
            return value
    return default
