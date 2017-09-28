# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2017


from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import normalize_newlines
from django.utils.translation import ugettext_lazy as _

from ..fields import AutoSlugField
from ..functional import firstof


# TODO Use translatable fields by default
@python_2_unicode_compatible
class PageTitlesMixin(models.Model):
    """
    A model mixin containg title and slug field for models serving as website
    pages with an URL.
    """
    short_title = models.CharField(_("Name"), max_length=50)
    slug = AutoSlugField(_("URL-Name"), max_length=200, populate_from='short_title', unique_slug=True)
    title = models.TextField(_("Titel (Langform)"), null=True, blank=True, max_length=300)
    window_title = models.CharField(_("Fenster-/Suchmaschinentitel"), null=True, blank=True, max_length=300)

    class Meta:
        abstract = True

    def __str__(self):
        return self.short_title

    def get_title(self):
        return firstof(
            self.title,
            self.short_title
        )

    def get_window_title(self):
        return firstof(
            self.window_title,
            self.short_title,
            self.get_first_title_line(),
        )

    def get_first_title_line(self):
        """
        First line of title field.
        """
        return normalize_newlines(self.get_title()).partition("\n")[0]

    def get_subtitle_lines(self):
        """
        All but first line of the long title field.
        """
        return normalize_newlines(self.title).partition("\n")[2]


class PageTitleAdminMixin(object):
    search_fields = ['short_title', 'title', 'window_title']
    list_display = ['short_title', 'slug']
    prepopulated_fields = {
        'slug': ('short_title',),
    }
