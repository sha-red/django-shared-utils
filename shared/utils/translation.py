# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import copy
import os
from collections import OrderedDict
from contextlib import contextmanager
from django import http
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, FieldDoesNotExist
from django.urls.base import translate_url
from django.http import HttpResponseRedirect
from django.template.loader import select_template
from django.utils import translation
from django.utils.http import is_safe_url
from django.utils.six.moves.urllib.parse import urlsplit, urlunsplit
from django.utils.translation import check_for_language, LANGUAGE_SESSION_KEY
from django.views.generic import TemplateView
from django.views.i18n import LANGUAGE_QUERY_PARAMETER, set_language


FALLBACK_LANGUAGE_CODE = getattr(settings, 'FALLBACK_LANGUAGE_CODE', 'en')


def _normalize_language_code(language_code):
    """
    Makes sure the language code is not an empty string.
    """
    return (
        language_code or
        translation.get_language() or
        settings.LANGUAGE_CODE or
        FALLBACK_LANGUAGE_CODE
    )


def get_language(language_code=None):
    return _normalize_language_code(language_code).split("-")[0]


def get_language_order(languages=None):
    """
    Returns a copy of settings.LANGUAGES with the active language at the first position.
    """
    languages = languages or list(OrderedDict(settings.LANGUAGES).keys())
    languages.insert(0, languages.pop(languages.index(get_language())))
    return languages


# TODO Deprecated 'fieldname' parameter, use 'field_name'
def lang_suffix(language_code=None, field_name=None, fieldname=None):
    """
    Returns the suffix appropriate for adding to field names for selecting
    the current language.

    If fieldname is given, returns the suffixed fieldname.
    """
    language_code = _normalize_language_code(language_code or get_language()).split("-")[0]
    return "{}_{}".format(field_name or fieldname or "", language_code)


class DirectTemplateView(TemplateView):
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super(DirectTemplateView, self).get_context_data(**kwargs)
        if self.extra_context is not None:
            for key, value in self.extra_context.items():
                if callable(value):
                    context[key] = value()
                else:
                    context[key] = value
        return context


class I18nDirectTemplateView(DirectTemplateView):
    def get_template_names(self):
        t_name, t_ext = os.path.splitext(self.template_name)
        lang = translation.get_language()
        template_name = select_template((
            "%s.%s%s" % (t_name, lang, t_ext),
            self.template_name
        )).name
        return [template_name]


def i18n_direct_to_template(request, *args, **kwargs):
    return I18nDirectTemplateView(*args, **kwargs).as_view()


def get_translation(obj, relation_name='translations', language_code=None):
    language_code = _normalize_language_code(language_code).split("-")[0]
    try:
        return getattr(obj, relation_name).get(language=language_code)
    except ObjectDoesNotExist:
        # FIXME Fetch best possible language from settings.LANGUAGES
        try:
            return getattr(obj, relation_name).get(language=(language_code == 'en' and 'de' or 'en'))
        except ObjectDoesNotExist:
            return None


def get_translated_field(obj, field_name, language_code=None):
    """
    Tries to get the model attribute corresponding to the current
    selected language by appending "_<language_code>" to the attribute
    name and returning the value.

    On AttributeError try to return the other language or the attribute
    without the language suffix.

    If the attribute is empty or null, try to return the value of
    the other language's attribute.

    If there is an attribute with the name without any language code
    extension, return the value of this.

    Best return value:
        field_name + lang_suffix for current language

    If empty or field does not exist:
        if default language and field_name
            field_name
        else
            field_name + lang_suffix other language
    """
    # TODO Implement multiple languages
    language_code = _normalize_language_code(language_code).split("-")[0]
    is_default_language = bool(language_code == settings.LANGUAGE_CODE.split("-")[0])
    if language_code == 'de':
        other_language_code = 'en'
    else:
        other_language_code = 'de'

    def has_db_field(field_name):
        try:
            # Only try to access database fields to avoid recursion
            obj._meta.get_field(field_name)
            return True
        except FieldDoesNotExist:
            return False

    translated_field_name = '%s_%s' % (field_name, language_code)
    other_translated_field_name = '%s_%s' % (field_name, other_language_code)
    rv = ""
    if hasattr(obj, translated_field_name):
        rv = getattr(obj, translated_field_name)
    if not rv:
        if is_default_language and has_db_field(field_name):
            rv = getattr(obj, field_name)
        elif hasattr(obj, other_translated_field_name):
            rv = getattr(obj, other_translated_field_name)
    if not rv and has_db_field(field_name):
        rv = getattr(obj, field_name)
    # FIXME Raise error if neither field exists
    return rv


@contextmanager
def active_language(lang='de'):
    translation.activate(lang)
    yield
    translation.deactivate()


def set_language_get(request):
    """
    set_language per GET request,
    """
    request = copy(request)
    request.POST = request.GET
    request.method = 'POST'
    return set_language(request)


class I18nUrlMixin(object):
    """
    View Mixin.
    Makes the url pattern name available in the template context.

    Usage:
        class ViewClass(I18nUrlMixin, TemplateView):
            ...

        url(r'<your_pattern>', ViewClass.as_view(view_name='my-wonderful-view', name='my-wonderful-view'),
    """
    view_name = None

    def get_context_data(self, **kwargs):
        if 'view_name' not in kwargs and self.view_name:
            kwargs['view_name'] = self.view_name
        context = super().get_context_data(**kwargs)
        return context
