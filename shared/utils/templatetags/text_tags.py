# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2015

import re

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from .. import text as text_utils


register = template.Library()


@register.filter()
def conditional_punctuation(value, punctuation=",", space=" "):
    """
    Appends punctuation if the (stripped) value is not empty
    and the value does not already end in a punctuation mark (.,:;!?).
    """
    value = force_text(value or "").strip()
    if value:
        if value[-1] not in ".,:;!?":
            value += conditional_escape(punctuation)
        value += conditional_escape(space)  # Append previously stripped space
    return value
conditional_punctuation.is_safe = True


WHITESPACE = re.compile('\s+')


@register.filter(needs_autoescape=True)
@stringfilter
def nbsp(text, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    return mark_safe(WHITESPACE.sub('&nbsp;', esc(text.strip())))


@register.filter(needs_autoescape=False)
@stringfilter
def html_entities_to_unicode(text):
    return mark_safe(text_utils.html_entities_to_unicode(text))