# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2015

import os
from contextlib import contextmanager
from django import http
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, FieldDoesNotExist
from django.core.urlresolvers import translate_url
from django.http import HttpResponseRedirect
from django.template.loader import select_template
from django.utils import translation
from django.utils.http import is_safe_url
from django.utils.six.moves.urllib.parse import urlsplit, urlunsplit
from django.utils.translation import check_for_language, LANGUAGE_SESSION_KEY
from django.views.generic import TemplateView
from django.views.i18n import LANGUAGE_QUERY_PARAMETER


def get_language(language_code=None):
    """
    Calls Django's translation.get_language but makes sure
    that
    """
    if not language_code:
        language_code = translation.get_language()
    if not language_code:
        language_code = settings.LANGUAGE_CODE
    language_code = language_code[:2] or 'de'  # FIXME Fall back to default language

def lang_suffix(language_code=None):
    """
    Returns the suffix appropriate for adding to field names for selecting
    the current language.
    """
    return "_%s" % language_code


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
    language_code = language_code or translation.get_language()[:2]
    try:
        return getattr(obj, relation_name).get(language=language_code)
    except ObjectDoesNotExist:
        try:
            return getattr(obj, relation_name).get(language=(language_code == 'en' and 'de' or 'en'))
        except ObjectDoesNotExist:
            return None


# class FieldTranslationMixin(object):
#     """
#     If the model has a field `attr` or `attr_<language_code>`, return it's
#     value, else raise ValueError.
#     """

#     def __getattr__(self, attr):
#         if attr in self.__dict__:
#             return self.__dict__[attr]
#         for field in self._meta.multilingual:
#             code = None
#             match = re.match(r'^%s_(?P<code>[a-z_]{2,5})$' % field, str(attr))
#             if match:
#                 code = match.groups('code')
#                 code = code[:2] # let's limit it to two letter
#             elif attr in self._meta.multilingual:
#                 code = self._language
#                 field = attr
#             if code is not None:
#                 try:
#                     return self._meta.translation.objects.select_related().get(model=self, language__code=code).__dict__[field]
#                 except ObjectDoesNotExist:
#                     if MULTILINGUAL_FALL_BACK_TO_DEFAULT and MULTILINGUAL_DEFAULT and code != MULTILINGUAL_DEFAULT:
#                         try:
#                             return self._meta.translation.objects.select_related().get(model=self, language__code=MULTILINGUAL_DEFAULT).__dict__[field]
#                         except ObjectDoesNotExist:
#                             pass
#                     if MULTILINGUAL_FAIL_SILENTLY:
#                         return None
#                     raise ValueError, "'%s' has no translation in '%s'"%(self, code)
#         raise AttributeError, "'%s' object has no attribute '%s'"%(self.__class__.__name__, str(attr))


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
    language_code = (language_code or
            translation.get_language() or
            settings.LANGUAGE_CODE)[:2]
    is_default_language = bool(language_code == settings.LANGUAGE_CODE[:2])
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
    modified copy from django.views.i18n (django 1.9.x)
    """
    next = request.POST.get('next', request.GET.get('next'))
    if not is_safe_url(url=next, host=request.get_host()):
        next = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=next, host=request.get_host()):
            next = '/'
    response = http.HttpResponseRedirect(next)
    if request.method == 'GET':
        lang_code = request.GET.get(LANGUAGE_QUERY_PARAMETER, None)
        if lang_code and check_for_language(lang_code):
            next_trans = translate_url(next, lang_code)
            if next_trans != next:
                response = http.HttpResponseRedirect(next_trans)

            if hasattr(request, 'session'):
                request.session[LANGUAGE_SESSION_KEY] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code,
                                    max_age=settings.LANGUAGE_COOKIE_AGE,
                                    path=settings.LANGUAGE_COOKIE_PATH,
                                    domain=settings.LANGUAGE_COOKIE_DOMAIN)
    return response
