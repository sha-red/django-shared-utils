# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2015-2017

from django.utils import six
if six.PY3:
    import html

import re

from django.utils.encoding import force_text, smart_text
from django.utils.functional import keep_lazy, keep_lazy_text
from django.utils.safestring import SafeText
from django.utils.html import mark_safe
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy

# from bs4 import BeautifulStoneSoup
import translitcodec  # provides 'translit/long', used by codecs.encode()
import codecs


def downgrade(value):
    """
    Downgrade unicode to ascii, transliterating accented characters.
    """
    value = force_text(value)
    return codecs.encode(value, 'translit/long')
# downgrade = allow_lazy(downgrade, six.text_type, SafeText)


def slugify_long(value):
    return slugify(downgrade(value))
# slugify_long = allow_lazy(slugify_long, six.text_type, SafeText)


# Spreading umlauts is included in the translit/long codec.
slugify_german = slugify_long


if six.PY2:
    import bs4

    def html_entities_to_unicode(html):
        # An incoming HTML or XML entity is always converted into the corresponding Unicode character in bs4
        return smart_text(bs4.BeautifulSoup(html), 'lxml')

else:
    # Works only with Python >= 3.4
    def html_entities_to_unicode(html_str):
        return html.unescape(html_str)
    # html_entities_to_unicode = allow_lazy(html_entities_to_unicode, six.text_type, SafeText)


# Translators: This string is used as a separator between list elements
DEFAULT_SEPARATOR = ugettext_lazy(", ")


@keep_lazy_text
def get_text_joined(list_, separator=DEFAULT_SEPARATOR, last_word=ugettext_lazy(' and ')):
    list_ = list(list_)
    if len(list_) == 0:
        return ''
    if len(list_) == 1:
        return force_text(list_[0])
    return '%s%s%s' % (
        separator.join(force_text(i) for i in list_[:-1]),
        force_text(last_word), force_text(list_[-1]))


def slimdown(text):
    """
    Converts simplified markdown (**, *, _) to <b>, <i> und <u> tags.
    """
    b_pattern = re.compile(r"(\*\*)(.*?)\1")
    i_pattern = re.compile(r"(\*)(.*?)\1")
    u_pattern = re.compile(r"(__)(.*?)\1")

    text, n = re.subn(b_pattern, "<b>\\2</b>", text)
    text, n = re.subn(i_pattern, "<i>\\2</i>", text)
    text, n = re.subn(u_pattern, "<u>\\2</u>", text)
    return mark_safe(text)

