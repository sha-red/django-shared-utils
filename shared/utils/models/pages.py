# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.text import normalize_newlines
from django.utils.translation import ugettext_lazy as _

from shared.multilingual.utils import i18n_fields_list
from ..functional import firstof
from ..text import slimdown
from .slugs import DowngradingSlugField


from ..conf import USE_TRANSLATABLE_FIELDS


if USE_TRANSLATABLE_FIELDS:
    from shared.multilingual.utils.fields import (
        TranslatableCharField,
        TranslatableTextField
    )
    # TODO populate_from might use settings.LANGUAGE_CODE
    SLUG_POPULATE_FORM = getattr(settings, 'SLUG_POPULATE_FORM', 'name_en')

else:
    TranslatableCharField = models.CharField
    TranslatableTextField = models.TextField
    SLUG_POPULATE_FORM = 'name'


# TODO Make slimdown optional through settings
# TODO Leave window_title alone, do not slimdown


class PageTitlesFunctionMixin(object):
    def __str__(self):
        return strip_tags(slimdown(self.get_short_title()))

    def get_title(self):
        return slimdown(firstof(
            self.title,
            self.get_short_title(),
            ''
        ))

    def get_short_title(self):
        return self.name

    def get_window_title(self):
        return strip_tags(slimdown(
            firstof(
                getattr(self, 'window_title', None),
                self.get_short_title(),
                self.get_first_title_line(),
                ''
            )
        ))

    def get_first_title_line(self):
        """
        First line of title field.
        """
        return slimdown(
            normalize_newlines(self.get_title()).partition("\n")[0]
        )

    def get_subtitle_lines(self):
        """
        All but first line of the long title field.
        """
        return slimdown(
            normalize_newlines(self.title).partition("\n")[2]
        )


# TODO Use translatable fields by default
@python_2_unicode_compatible
class PageTitlesMixin(models.Model, PageTitlesFunctionMixin):
    """
    A model mixin containg title and slug field for models serving as website
    pages with an URL.
    """
    name = TranslatableCharField(_("Name"),
        max_length=250)
    short_name = TranslatableCharField(_("Short Name"),
        max_length=25, null=True, blank=True,
        help_text=_("Optional, used for menus etc."))
    title = TranslatableTextField(_("title/subtitle"),
        null=True, blank=True, max_length=500)
    window_title = TranslatableCharField(_("window title"),
        null=True, blank=True, max_length=300)
    slug = DowngradingSlugField(_("URL-Name"), max_length=200,
        populate_from=SLUG_POPULATE_FORM, unique_slug=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    # FIXME short_title is deprecated
    @property
    def short_title(self):
        return self.name

    @short_title.setter
    def short_title(self, value):
        self.name = value


class PageTitleAdminMixin(object):
    list_display = ['name', 'slug']
    search_fields = ['name', 'title', 'window_title']
    if USE_TRANSLATABLE_FIELDS:
        search_fields = i18n_fields_list(search_fields)
    prepopulated_fields = {
        'slug': [SLUG_POPULATE_FORM]
    }
