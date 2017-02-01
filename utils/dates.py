# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2016


import calendar


def get_last_of_month(d):
    day = calendar.monthrange(d.year, d.month)[1]
    return d.replace(day=day)
