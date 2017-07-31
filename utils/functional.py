# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2017


def firstof(*args, default=None):
    """
    Returns the first value which is neither empty nor None.

    """
    if len(args) == 1:
        iterable = args[0]
    else:
        iterable = args

    for value in iterable:
        if value:
            return value
    return default
