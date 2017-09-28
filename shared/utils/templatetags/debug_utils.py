# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2009-2017

try:
    import ipdb
    from django import template


    register = template.Library()


    @register.filter
    def ipdb_inspect(value):
        ipdb.set_trace()
        return value


    @register.simple_tag
    def ipdb_set_breakpoint():
        ipdb.set_trace()

except:
    pass