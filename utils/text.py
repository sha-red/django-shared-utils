# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2015

from django.utils.text import slugify
from django.utils import six
from django.utils.encoding import force_text
from django.utils.functional import allow_lazy
from django.utils.safestring import SafeText

# import unicodedata
import translitcodec
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


def slugify_german(value):
    """
    Transliterates Umlaute before calling django's slugify function.
    """
    umlaute = {
        'Ä': 'Ae',
        'Ö': 'Oe',
        'Ü': 'Ue',
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'ß': 'ss',
    }

    value = force_text(value)
    umap = {ord(key): unicode(val) for key, val in umlaute.items()}
    return slugify(value.translate(umap))
slugify_german = allow_lazy(slugify_german, six.text_type, SafeText)
