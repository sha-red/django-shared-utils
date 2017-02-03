# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2016


import calendar
from collections import namedtuple
from dateutil import rrule
from datetime import date, datetime


def force_date(d):
    if type(d) == datetime:
        return d.date()
    else:
        return d


def first_of_month(d):
    return d.replace(day=1)


def get_last_of_month(d):
    """
    >>> get_last_of_month(date(2000, 2, 1))
    datetime.date(2000, 2, 29)
    >>> get_last_of_month(date(2004, 2, 1))
    datetime.date(2004, 2, 29)
    >>> get_last_of_month(date(2004, 12, 1))
    datetime.date(2004, 12, 31)
    """
    day = calendar.monthrange(d.year, d.month)[1]
    return d.replace(day=day)


def as_month(d):
    """
    >>> as_month(datetime(2007, 1, 13, 14, 0))
    datetime.date(2007, 1, 1)
    """
    return force_date(first_of_month(d))


#
# Date Range Calculations


DateRange = namedtuple('Range', ['start', 'end'])


def months_for_daterange(daterange):
    """
    Returns all months for a given date range.
    A month is represented by a datetime.date object of the first day of the month

    >>> daterange = DateRange(date(2015, 3, 5), date(2015, 8, 25))
    >>> months_for_daterange(daterange)
    [datetime.date(2015, 3, 1), datetime.date(2015, 4, 1), datetime.date(2015, 5, 1), datetime.date(2015, 6, 1), datetime.date(2015, 7, 1), datetime.date(2015, 8, 1)]

    """
    return map(
        as_month,
        rrule.rrule(rrule.MONTHLY, dtstart=daterange.start, until=daterange.end)
    )


def months_for_daterange_list(daterange_list):
    """
    >>> range_list = [DateRange(date(2015, 2, 25), date(2015, 2, 25)), DateRange(date(2015, 3, 13), date(2015, 3, 13)), DateRange(date(2015, 5, 3), date(2015, 5, 3)), DateRange(date(2015, 5, 7), date(2015, 7, 7)), DateRange(date(2015, 6, 28), date(2015, 6, 28)), DateRange(date(2015, 7, 5), date(2015, 7, 5)), DateRange(date(2015, 10, 14), date(2015, 10, 14)), DateRange(date(2015, 11, 11), date(2015, 12, 11))]
    >>> months_for_daterange_list(range_list)
    [datetime.date(2015, 2, 1), datetime.date(2015, 3, 1), datetime.date(2015, 5, 1), datetime.date(2015, 6, 1), datetime.date(2015, 7, 1), datetime.date(2015, 10, 1), datetime.date(2015, 11, 1), datetime.date(2015, 12, 1)]
    """
    all_months = set()
    for dr in daterange_list:
        all_months.update(months_for_daterange(dr))
    return sorted(list(all_months))


"""
# >>> from datetime import datetime
# >>> from collections import namedtuple
# >>> Range = namedtuple('Range', ['start', 'end'])
# >>> r1 = Range(start=datetime(2012, 1, 15), end=datetime(2012, 5, 10))
# >>> r2 = Range(start=datetime(2012, 3, 20), end=datetime(2012, 9, 15))
# >>> latest_start = max(r1.start, r2.start)
# >>> earliest_end = min(r1.end, r2.end)
# >>> overlap = (earliest_end - latest_start).days + 1
# >>> overlap
52
"""


if __name__ == "__main__":
    import doctest
    doctest.testmod()
