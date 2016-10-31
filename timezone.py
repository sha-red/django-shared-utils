# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2015

from django.utils import timezone


def smart_default_tz(datetime_value):
    """
    Returns the give datetime with the default timezone applied.
    """
    if timezone.is_naive(datetime_value):
        datetime_value = timezone.make_aware(datetime_value, timezone=timezone.get_default_timezone())
    return timezone.localtime(datetime_value, timezone.get_default_timezone())

