# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2014-2015

from django import template
from django.db import models

from ..translation import get_translation, get_translated_field


register = template.Library()


@register.filter
def translation(obj):
    return get_translation(obj)


@register.filter
def translate(obj, field_name):
    return get_translated_field(obj, field_name)

# Alias
translated_field = translate
