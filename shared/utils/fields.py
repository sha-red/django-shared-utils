# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from .text import slugify


# TODO Remove deprecated location
from .models.slugs import AutoSlugField


def uniquify_field_value(instance, field_name, value, max_length=None, queryset=None):
    """
    Makes a char field value unique by appending an index, taking care of the
    field's max length.

    FIXME Doesn't work with model inheritance, where the field is part of the parent class.
    """
    def get_similar_values(value):
        return queryset.exclude(pk=instance.pk) \
            .filter(**{"%s__istartswith" % field_name: value}).values_list(field_name, flat=True)

    if not value:
        raise ValueError("Cannot uniquify empty value")
        # TODO Instead get value from instance.field, or use a default value?
    if not max_length:
        max_length = instance._meta.get_field(field_name).max_length
    if not queryset:
        queryset = instance._meta.default_manager.get_queryset()

    # Find already existing counter
    m = re.match(r'(.+)(-\d+)$', value)
    if m:
        base_value, counter = m.groups()
        index = int(counter.strip("-")) + 1
    else:
        base_value = value
        index = 2  # Begin appending "-2"

    similar_values = get_similar_values(value)
    while value in similar_values or len(value) > max_length:
        value = "%s-%i" % (base_value, index)
        if len(value) > max_length:
            base_value = base_value[:-(len(value) - max_length)]
            value = "%s-%i" % (base_value, index)
            similar_values = get_similar_values(base_value)
        index += 1
    return value


# TODO Remove alias
def unique_slug(instance, slug_field, slug_value, max_length=50, queryset=None):
    slug_value = slugify(slug_value)
    return uniquify_field_value(instance, slug_field, slug_value, max_length=50, queryset=None)
