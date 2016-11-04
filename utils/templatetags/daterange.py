# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2016
#            Initially based on https://djangosnippets.org/snippets/1405/

from django import template
from .. import dateformat


# TODO Get DEFAULT_VARIANT from settings
DEFAULT_VARIANT = 'SHORT'


register = template.Library()


@register.simple_tag
def format_date_range(from_date, to_date, variant=DEFAULT_VARIANT):
    """
    Use in django templates:

    {% load date_range %}
    {% format_date_range start_date end_date %}
    """
    return dateformat.format_date_range(from_date, to_date, variant)


@register.simple_tag
def format_time_range(from_time, to_time, variant=DEFAULT_VARIANT):
    """
    Knows how to deal with left out from_time/to_time values.

    Use in django templates:

    {% load date_range %}
    {% format_time_range start_time end_time %}
    """
    return dateformat.format_time_range(from_time, to_time, variant)


def format_timespan_range(timespan_object, force_wholeday=False, variant=DEFAULT_VARIANT):
    return dateformat.format_timespan_range(timespan_object, force_wholeday, variant)
