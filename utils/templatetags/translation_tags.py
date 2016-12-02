# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2014-2015

from django import template

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


'''
Unfinished:

from django import template
from django.core.urlresolvers import reverse
from django.core.urlresolvers import resolve
from django.urls.base import translate_url


class TranslatedURL(template.Node):
    # from http://stackoverflow.com/questions/11437454/django-templates-get-current-url-in-another-language

    def __init__(self, language):
        self.language = language

    def render(self, context):
        view = resolve(context['request'].path)
        request_language = translation.get_language()
        translation.activate(self.language)
        url = reverse(view.url_name, args=view.args, kwargs=view.kwargs)
        translation.activate(request_language)
        return url


@register.tag(name='translate_url')
def do_translate_url(parser, token):
    language = token.split_contents()[1]
    return TranslatedURL(language)


@register.simple_tag
def translate_url(language, url=None):
    """
    {% get_language_info_list for LANGUAGES as languages %}
    {% for language in languages %}
        <a href="{% translate_url language.code %}">{{ language.name_local }}</a>
    {% endfor %}
    """

    import ipdb; ipdb.set_trace()
    # if not url:
    #     view = resolve(context['request'].path)
    #     request_language = translation.get_language()
    #     translation.activate(self.language)
    #     url = reverse(view.url_name, args=view.args, kwargs=view.kwargs)

    #     view = resolve(context['request'].path)

    return TranslatedURL(language)
'''
