# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse


try:
    import ipdb

    register = template.Library()

    @register.filter
    def ipdb_inspect(value):
        ipdb.set_trace()
        return value

    @register.simple_tag
    def ipdb_set_breakpoint():
        ipdb.set_trace()

except:  # TODO ImportError
    pass


@register.filter
def get_admin_url(obj):
    content_type = ContentType.objects.get_for_model(obj.__class__)
    return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(obj.id,))


