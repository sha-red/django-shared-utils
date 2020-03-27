# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import string

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


@register.filter(needs_autoescape=False)
def slimdown(text):
    return mark_safe(text_utils.slimdown(text))


@register.filter(needs_autoescape=False)
def strip_links(text):
    return mark_safe(text_utils.strip_links(text))


@register.filter(is_safe=True)
@stringfilter
def html_lines_to_list(value):
    """
    Replaces all <br> tags with ", "
    """
    rv = []
    lines = value.split("<br>")
    for i in range(0, len(lines)):
        line = lines[i].strip()
        rv.append(line)
        if i < len(lines) - 1:
            if line[-1] not in ";:,.-–—":
                rv.append(", ")
            else:
                rv.append(" ")
    return "".join(rv)
    return ", ".join([l.strip() for l in value.split("<br>")])


def remove_punctuation(s):
    # http://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
    # return s.translate(s.maketrans("",""), string.punctuation)
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    return regex.sub('', s)


def splitn(s, n):
    """split string s into chunks no more than n characters long"""
    parts = re.split("(.{%d,%d})" % (n, n), s)
    map(parts.remove, [""] * parts.count(""))
    return parts


def clean_value(value):
    # Convert all whitespace including non-breaking space to a single space
    if value:
        return re.sub(u"([\s\u00A0]+)", u" ", force_text(value.strip()))
    else:
        return value


@register.filter()
@stringfilter
def append(value, text):
    """
    Appends text if value is not None.
    """
    if value is not None:
        value = str(value).strip()
        if value:
            return "{}{}".format(value, text)
    return ""


@register.filter()
@stringfilter
def prepend(value, text):
    """
    Prepends text if value is not None.
    """
    if value is not None:
        value = str(value).strip()
        if value:
            return "{}{}".format(text, value)
    return ""


@register.filter
@stringfilter
def first_line(s):
    """
    Strips whitespace, then returns the first line of text.
    """
    return s.strip().splitlines(False)[0]
