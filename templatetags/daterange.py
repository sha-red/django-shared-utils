# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2016
#            improved from https://djangosnippets.org/snippets/1405/


from django import template
from ..dateformat import date_format, get_format


"""
# TODO Describe custom formats
"""


register = template.Library()


@register.simple_tag
def format_date_range(from_date, to_date, variant='short'):
    """
    >>> import datetime
    >>> format_date_range(datetime.date(2009,1,15), datetime.date(2009,1,20))
    '15. - 20.01.2009.'
    >>> format_date_range(datetime.date(2009,1,15), datetime.date(2009,2,20))
    '15.01. - 20.02.2009.'
    >>> format_date_range(datetime.date(2009,1,15), datetime.date(2010,2,20))
    '15.01.2009. - 20.02.2010.'
    >>> format_date_range(datetime.date(2009,1,15), datetime.date(2010,1,20))
    '15.01.2009. - 20.01.2010.'

    Use in django templates:

    {% load date_range %}
    {% format_date_range exhibition.start_on exhibition.end_on %}
    """
    if variant.lower() not in ('short', 'long', ''):
        variant = 'short'
    if variant.endswith("_"):
        variant = variant + "_"

    from_format = to_format = get_format(variant.upper() + 'DATE_FORMAT')

    if from_date == to_date:
        return date_format(to_date, get_format(to_format))

    if (from_date.year == to_date.year):
        from_format = get_format(variant.upper() + 'DAYMONTH_FORMAT') or 'd/m/'
        if (from_date.month == to_date.month):
            from_format = get_format(variant.upper() + 'DAYONLY_FORMAT') or 'd'
    separator = get_format('DATE_RANGE_SEPARATOR') or "–"
    # import ipdb; ipdb.set_trace()

    print from_format, to_format

    f = date_format(from_date, get_format(from_format))
    t = date_format(to_date, get_format(to_format))

    return variant.upper() + " " + separator.join((f, t))


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()