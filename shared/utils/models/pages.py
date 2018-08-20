# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.text import normalize_newlines
from django.utils.translation import ugettext_lazy as _

from shared.multilingual.utils import i18n_fields_list
from ..fields import AutoSlugField
from ..functional import firstof
from ..text import slimdown


USE_TRANSLATABLE_FIELDS = getattr(settings, 'CONTENT_USE_TRANSLATABLE_FIELDS', False)
# TODO Implement translatable AutoSlugField: USE_TRANSLATABLE_SLUG_FIELDS = getattr(settings, 'CONTENT_USE_TRANSLATABLE_SLUG_FIELDS', True)


if USE_TRANSLATABLE_FIELDS:
    from shared.multilingual.utils.fields import TranslatableCharField, TranslatableTextField

# TODO Make slimdown optional through settings
# TODO Leave window_title alone, do not slimdown


class PageTitlesFunctionMixin(object):
    def __str__(self):
        return strip_tags(slimdown(self.get_short_title()))

    def get_title(self):
        return slimdown(firstof(
            self.title,
            self.get_short_title()
        ))

    def get_short_title(self):
        return self.short_title

    def get_window_title(self):
        return strip_tags(slimdown(
            firstof(
                self.window_title,
                self.get_short_title(),
                self.get_first_title_line(),
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
    # FIXME signals are not sent from abstract models, therefore AutoSlugField doesn't work
    if USE_TRANSLATABLE_FIELDS:
        short_title = TranslatableCharField(_("Name"), max_length=50)
        title = TranslatableTextField(_("Titel (Langform)"), null=True, blank=True, max_length=300)
        window_title = TranslatableCharField(_("Fenster-/Suchmaschinentitel"), null=True, blank=True, max_length=300)
        # FIXME populate_from should use settings.LANGUAGE
        slug = AutoSlugField(_("URL-Name"), max_length=200, populate_from='short_title_de', unique_slug=True, blank=True)

    else:
        short_title = models.CharField(_("Name"), max_length=50)
        title = models.TextField(_("Titel (Langform)"), null=True, blank=True, max_length=300)
        window_title = models.CharField(_("Fenster-/Suchmaschinentitel"), null=True, blank=True, max_length=300)
        slug = AutoSlugField(_("URL-Name"), max_length=200, populate_from='short_title', unique_slug=True, blank=True)

    class Meta:
        abstract = True


class PageTitleAdminMixin(object):
    search_fields = ['short_title', 'title', 'window_title']
    list_display = ['short_title', 'slug']
    if USE_TRANSLATABLE_FIELDS:
        search_fields = i18n_fields_list(search_fields)
        prepopulated_fields = {
            'slug': ('short_title_en',),  # FIXME Language suffix
        }
    else:
        prepopulated_fields = {
            'slug': ('short_title',),  # FIXME Language suffix
        }
