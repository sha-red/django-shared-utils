# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2015

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter()
def conditional_punctuation(value, punctuation=",", space=" "):
    """
    Appends punctuation if the (stripped) value is not empty
    and the value does not already end in a punctuation mark (.,:;!?).
    """
    value = value.strip()
    if value:
        if value[-1] not in ".,:;!?":
            value += conditional_escape(punctuation)
        value += conditional_escape(space)  # Append previously stripped space
    return value
conditional_punctuation.is_safe = True
