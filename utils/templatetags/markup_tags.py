# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2015

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from .. import markdown_utils


register = template.Library()


@register.filter(needs_autoescape=True)
@stringfilter
def inline_markdown(text, autoescape=None, **kwargs):
    """ Doesn't wrap the markup in a HTML paragraph. """
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    return mark_safe(markdown_utils.inline_markdown_processor.convert(esc(text), **kwargs))


@register.filter(needs_autoescape=True)
@stringfilter
def markdown(text, autoescape=None, **kwargs):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    return mark_safe(markdown_utils.markdown_processor.convert(esc(text), **kwargs))
