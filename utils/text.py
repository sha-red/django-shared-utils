# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2015-2017

from django.utils.text import slugify
from django.utils import six
from django.utils.encoding import force_text, smart_text
from django.utils.functional import allow_lazy
from django.utils.safestring import SafeText

from bs4 import BeautifulStoneSoup
import translitcodec  # provides 'translit/long', used by codecs.encode()
import codecs


def downgrade(value):
    """
    Downgrade unicode to ascii, transliterating accented characters.
    """
    value = force_text(value)
    return codecs.encode(value, 'translit/long')
downgrade = allow_lazy(downgrade, six.text_type, SafeText)


def slugify_long(value):
    return slugify(downgrade(value))
slugify_long = allow_lazy(slugify_long, six.text_type, SafeText)


# Spreading umlauts is included in the translit/long codec.
slugify_german = slugify_long


def html_entities_to_unicode(html):
    text = smart_text(BeautifulStoneSoup(html, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
    return text
html_entities_to_unicode = allow_lazy(html_entities_to_unicode, six.text_type, SafeText)
