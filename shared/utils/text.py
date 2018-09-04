# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
import translitcodec  # provides 'translit/long', used by codecs.encode()
import re

from django.conf import settings
from django.utils.encoding import force_text, smart_text
from django.utils.functional import keep_lazy_text
from django.utils.html import mark_safe
from django.utils import six
from django.utils.text import slugify as django_slugify
from django.utils.translation import ugettext_lazy


@keep_lazy_text
def downgrade(value):
    """
    Downgrade unicode to ascii, transliterating accented characters.
    """
    value = force_text(value)
    return codecs.encode(value, 'translit/long')


@keep_lazy_text
def slugify_long(value):
    return django_slugify(downgrade(value))


# Spreading umlauts is included in the translit/long codec.
slugify_german = slugify_long


@keep_lazy_text
def downgrading_slugify(value):
    # Slugfiy only allowing hyphens, numbers and ASCII characters
    # FIXME django_slugify might return an empty string; take care that we always return something
    return re.sub("[ _]+", "-", django_slugify(downgrade(value)))


SLUGIFY_FUNCTION = getattr(settings, 'SLUGIFY_FUNCTION', downgrading_slugify)
slugify = SLUGIFY_FUNCTION


if six.PY2:
    import bs4

    def html_entities_to_unicode(html):
        # An incoming HTML or XML entity is always converted into the corresponding Unicode character in bs4
        return smart_text(bs4.BeautifulSoup(html), 'lxml')

else:
    import html

    # Works only with Python >= 3.4
    def html_entities_to_unicode(html_str):
        return html.unescape(html_str)
    # html_entities_to_unicode = allow_lazy(html_entities_to_unicode, six.text_type, SafeText)


# Translators: Separator between list elements
DEFAULT_SEPARATOR = ugettext_lazy(", ")

# Translators: Last separator of list elements
LAST_WORD_SEPARATOR = ugettext_lazy(" and ")


@keep_lazy_text
def get_text_joined(list_, separator=DEFAULT_SEPARATOR, last_word=LAST_WORD_SEPARATOR):
    list_ = list(list_)
    if len(list_) == 0:
        return ''
    if len(list_) == 1:
        return force_text(list_[0])
    return '%s%s%s' % (
        separator.join(force_text(i) for i in list_[:-1]),
        force_text(last_word), force_text(list_[-1]))


@keep_lazy_text
def slimdown(text):
    """
    Converts simplified markdown (`**`, `*`, `__`) to <b>, <i> und <u> tags.
    """
    b_pattern = re.compile(r"(\*\*)(.*?)\1")
    i_pattern = re.compile(r"(\*)(.*?)\1")
    u_pattern = re.compile(r"(__)(.*?)\1")

    text, n = re.subn(b_pattern, "<b>\\2</b>", text)
    text, n = re.subn(i_pattern, "<i>\\2</i>", text)
    text, n = re.subn(u_pattern, "<u>\\2</u>", text)
    return mark_safe(text)
