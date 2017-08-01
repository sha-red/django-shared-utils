# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2008-2015

import re
from django.db.models import fields
from django.utils import six
from django.utils.translation import ugettext_lazy as _
if six.PY3:
    from functools import reduce

from .text import slugify_long as slugify
from . import SLUG_HELP


DEFAULT_SLUG = _("item")


def unique_slug(instance, slug_field, slug_value, max_length=50, queryset=None):
    """
    TODO Doesn't work with model inheritance, where the slug field is part of the parent class.
    """
    if not slug_value:
        raise ValueError("Cannot uniquify empty slug")
    orig_slug = slug = slugify(slug_value)
    index = 0
    if not queryset:
        queryset = instance.__class__._default_manager.get_queryset()

    def get_similar_slugs(slug):
        return queryset.exclude(pk=instance.pk) \
            .filter(**{"%s__istartswith" % slug_field: slug}).values_list(slug_field, flat=True)

    similar_slugs = get_similar_slugs(slug)
    while slug in similar_slugs or len(slug) > max_length:
        index += 1
        slug = "%s-%i" % (orig_slug, index)
        if len(slug) > max_length:
            orig_slug = orig_slug[:-(len(slug) - max_length)]
            slug = "%s-%i" % (orig_slug, index)
            similar_slugs = get_similar_slugs(orig_slug)
    return slug


def unique_slug2(instance, slug_source, slug_field):
    slug = slugify(slug_source)
    all_slugs = [sl.values()[0] for sl in instance.__class__._default_manager.values(slug_field)]
    if slug in all_slugs:
        counter_finder = re.compile(r'-\d+$')
        counter = 2
        slug = "%s-%i" % (slug, counter)
        while slug in all_slugs:
            slug = re.sub(counter_finder, "-%i" % counter, slug)
            counter += 1
    return slug


class AutoSlugField(fields.SlugField):
    # AutoSlugField based on http://www.djangosnippets.org/snippets/728/

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 50)
        kwargs.setdefault('help_text', SLUG_HELP)
        if 'populate_from' in kwargs:
            self.populate_from = kwargs.pop('populate_from')
        self.unique_slug = kwargs.pop('unique_slug', False)
        super(AutoSlugField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if not value:
            if hasattr(self, 'populate_from'):
                # Follow dotted path (e.g. "occupation.corporation.name")
                value = reduce(lambda obj, attr: getattr(obj, attr), self.populate_from.split("."), model_instance)
                if callable(value):
                    value = value()
            if not value:
                value = DEFAULT_SLUG
        if self.unique_slug:
            return unique_slug(model_instance, self.name, value, max_length=self.max_length)
        else:
            return slugify(value)

