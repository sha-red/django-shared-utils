# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from shared.utils.dateformat import format_partial_date, format_date_range


USE_TRANSLATABLE_FIELDS = getattr(settings, 'CONTENT_USE_TRANSLATABLE_FIELDS', False)
# TODO Implement translatable AutoSlugField: USE_TRANSLATABLE_SLUG_FIELDS = getattr(settings, 'CONTENT_USE_TRANSLATABLE_SLUG_FIELDS', True)

if USE_TRANSLATABLE_FIELDS:
    from shared.multilingual.utils.fields import TranslatableCharField
else:
    TranslatableCharField = models.CharField


# FIXME Currently Python cannot handle BC dates
#       Possibly solution: https://github.com/okfn/datautil/blob/master/datautil/date.py
MIN_DATE = datetime.date.min
MAX_DATE = datetime.date.max


class RuntimeMixin(models.Model):
    """Allows a model to have partially defined from-/to-dates;
    at least one year value must be entered.
    """
    from_year_value = models.PositiveIntegerField(_("starting year"), null=True, blank=True)
    from_month_value = models.PositiveIntegerField(_("starting month"), null=True, blank=True)
    from_day_value = models.PositiveIntegerField(_("starting day"), null=True, blank=True)
    _from_sort_date = models.DateField(_("from"), editable=False)
    until_year_value = models.PositiveIntegerField(_("ending year"), null=True, blank=True)
    until_month_value = models.PositiveIntegerField(_("ending month"), null=True, blank=True)
    until_day_value = models.PositiveIntegerField(_("ending day"), null=True, blank=True)
    _until_sort_date = models.DateField(_("until"), editable=False)

    runtime_text = TranslatableCharField(_("Zeitangabe Textform"),
        max_length=200, null=True, blank=True,
        help_text=_("Alternativer Text für die Laufzeitangabe"))

    class Meta:
        abstract = True

    def clean(self):
        if not (self.from_year_value or self.until_year_value):
            raise ValidationError(_('Please enter either a from or an until date year.'))

        # Update from/sort date fields
        if self.from_year_value:
            self._from_sort_date = datetime.date(
                self.from_year_value, self.from_month_value or 1, self.from_day_value or 1)
        else:
            self._from_sort_date = MIN_DATE

        if self.until_year_value:
            self._until_sort_date = datetime.date(
                self.until_year_value, self.until_month_value or 12, self.until_day_value or 31)
        else:
            self._until_sort_date = MAX_DATE

    def save(self, *args, **kwargs):
        self.full_clean()
        super(RuntimeMixin, self).save(*args, **kwargs)

    @property
    def from_date(self):
        return self._from_sort_date

    @property
    def until_date(self):
        return self._until_sort_date

    # TODO Implement @fron_date.setter, @until_date.setter

    def get_from_display(self):
        return self.runtime_text or format_partial_date(
            self.from_year_value,
            self.from_month_value,
            self.from_day_value)
    get_from_display.admin_order_field = '_from_sort_date'
    get_from_display.short_description = _("from")

    def get_until_display(self):
        if self.runtime_text:
            return ""
        else:
            return format_partial_date(
                self.until_year_value,
                self.until_month_value,
                self.until_day_value)
    get_until_display.admin_order_field = '_until_sort_date'
    get_until_display.short_description = _("until")

    def get_runtime_display(self):
        # TODO Improve
        if not self.runtime_text and \
           self.from_day_value and self.from_month_value:
            return format_date_range(self._from_sort_date, self._until_sort_date)
        else:
            f = self.get_from_display()
            # Single point
            if self._from_sort_date == self._until_sort_date:
                return f

            u = self.get_until_display()
            if f and u:
                return "{}–{}".format(f, u)
            else:
                return f or u
