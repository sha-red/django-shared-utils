# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2016
"""
Extends django.utils.dateformat
Adds date and time range functions

# TODO Describe custom formats
"""


import datetime
import re
from django.conf import settings
from django.utils.dateformat import DateFormat, re_escaped
from django.utils.formats import get_format
from django.utils.encoding import force_text
from django.utils.translation import get_language, ugettext_lazy as _


DEFAULT_VARIANT = getattr(settings, 'DEFAULT_DATE_VARIANT', 'SHORT')


# Adding "q"
re_formatchars = re.compile(r'(?<!\\)([aAbBcdDeEfFgGhHiIjlLmMnNoOPqrsStTUuwWyYzZ])')


class ExtendedFormat(DateFormat):
    def q(self):
        """
        Time, in 24-hour hours and minutes, with minutes left off if they're
        zero.
        Examples: '1', '1:30', '13:05', '14'
        Proprietary extension.
        """
        if self.data.minute == 0:
            return self.G()
        return '%s:%s' % (self.G(), self.i())

    def format(self, formatstr):
        pieces = []
        for i, piece in enumerate(re_formatchars.split(force_text(formatstr))):
            if i % 2:
                pieces.append(force_text(getattr(self, piece)()))
            elif piece:
                pieces.append(re_escaped.sub(r'\1', piece))
        return ''.join(pieces)


def format(value, format):
    # Copy of django.utils.dateformat.format, using our extended formatter
    df = ExtendedFormat(value)
    return df.format(format)


def time_format(value, format=None, use_l10n=None):
    # Copy of django.utils.dateformat.time_format, using our extended formatter
    tf = ExtendedFormat(value)
    return tf.format(get_format(format or 'DATE_FORMAT', use_l10n=use_l10n))


def date_format(value, format=None, use_l10n=None):
    df = ExtendedFormat(value)
    return df.format(get_format(format or 'DATE_FORMAT', use_l10n=use_l10n))


def _normalize_variant(variant):
    if variant.lower() not in ('short', 'long', ''):
        variant = DEFAULT_VARIANT
    if variant and not variant.endswith("_"):
        variant = variant + "_"
    return variant.upper()


def format_date_range(from_date, to_date, variant=DEFAULT_VARIANT):
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
    """
    if not (from_date or to_date):
        return ""

    variant = _normalize_variant(variant)

    # Only deal with dates, ignoring time
    def datetime_to_date(dt):
        try:
            return dt.date()
        except AttributeError:
            return dt
    from_date = datetime_to_date(from_date)
    to_date = datetime_to_date(to_date)

    from_format = to_format = get_format(variant + 'DATE_FORMAT')
    if from_date == to_date or not to_date:
        return date_format(from_date, from_format)
    else:
        if (from_date.year == to_date.year):
            from_format = get_format(variant + 'DAYMONTH_FORMAT') or 'd/m/'
            if (from_date.month == to_date.month):
                from_format = get_format(variant + 'DAYONLY_FORMAT') or 'd'

        f = t = ""
        if from_date:
            f = date_format(from_date, get_format(from_format))
        if to_date:
            t = date_format(to_date, get_format(to_format))

        separator = get_format('DATE_RANGE_SEPARATOR') or " - "
        return separator.join((f, t))


def format_time_range(from_time, to_time, variant=DEFAULT_VARIANT):
    """
    Knows how to deal with left out from_time/to_time values.
    """
    if not (from_time or to_time):
        return ""

    variant = _normalize_variant(variant)

    from_format = to_format = "q"  # get_format(variant + 'TIME_FORMAT')

    if from_time == to_time or not to_time:
        return time_format(from_time, get_format(from_format))
    else:
        f = t = ""
        if from_time:
            f = time_format(from_time, get_format(from_format))
        if to_time:
            t = time_format(to_time, get_format(to_format))

        separator = get_format('DATE_RANGE_SEPARATOR') or "–"
        return separator.join((f, t))


def format_timespan_range(timespan_object, force_wholeday=False, variant=DEFAULT_VARIANT):
    """
    For Timespan-objects, i.e. object with start_date, end_date, start_time and end_time properties.

    Multiday or force_wholeday:
    "10.07.2016-11.07.2016"

    Single days:
    "10.07.2016 11 Uhr"
    "10.07.2016 11-14 Uhr"

    >>> import datetime
    >>> sd, ed = datetime.date(2009,1,15), datetime.date(2009,1,20)
    >>> st, et = datetime.date(2009,1,15), datetime.date(2009,1,20)
    >>> class TestObject(object):
    >>>     start_date = None
    >>>     end_date = None
    >>>     start_time = None
    >>>     end_time = None
    >>> obj = TestObject()
    >>> obj.start_date = obj.end_date = sd
    >>> format_timespan_range(obj)
    '15.01.–20.01.2009'

    """
    variant = _normalize_variant(variant)

    rv = format_date_range(timespan_object.start_date, timespan_object.end_date, variant)

    if (timespan_object.is_multiday() or
       not timespan_object.start_time or
       force_wholeday):
        # Don't show timespan
        return rv
    else:
        rv = _("%(daterange)s %(timespan)s Uhr") % {
            'daterange': rv,
            'timespan': format_time_range(timespan_object.start_time, timespan_object.end_time, variant)
        }
    return rv


def format_partial_date(year=None, month=None, day=None, variant=DEFAULT_VARIANT):
    if year and month and day:
        format_name = 'DATE_FORMAT'
    elif year and month:
        format_name = 'YEARMONTH_FORMAT'
    elif month and day:
        format_name = 'DAYMONTH_FORMAT'
    elif year:
        format_name = 'YEAR_FORMAT'
    elif month:
        format_name = 'MONTH_FORMAT'
    elif day:
        format_name = 'DAYONLY_FORMAT'

    name = _normalize_variant(variant) + format_name
    # TODO Django bug or what? Sometimes get_language returns None, therefore force a language here
    partial_date_format = get_format(name, lang=get_language() or settings.LANGUAGE_CODE)
    return date_format(datetime.date(year or 2000, month or 1, day or 1), partial_date_format)


# TODO Add format_partial_date_range function


def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()
