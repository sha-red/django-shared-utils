import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..conf import USE_TRANSLATABLE_FIELDS
from ..dateformat import format_partial_date, format_date_range


if USE_TRANSLATABLE_FIELDS:
    from shared.multilingual.utils.fields import TranslatableCharField
else:
    TranslatableCharField = models.CharField


# FIXME Currently Python cannot handle BC dates
#       Possible solution: https://github.com/okfn/datautil/blob/master/datautil/date.py
MIN_DATE = datetime.date.min
MAX_DATE = datetime.date.max


class RuntimeBehaviour:
    """
    Allows a model to have partially defined from-/to-dates;
    at least one year value must be entered.
    """

    start_date_field_name = '_from_sort_date'
    end_date_field_name = '_until_sort_date'
    allow_empty_runtime = False

    def clean(self):
        if not self.allow_empty_runtime and not (self.from_year_value or self.until_year_value):
            raise ValidationError(_('Please enter either a from or an until date year.'))

        # Update from/sort date fields
        if self.from_year_value:
            setattr(self, self.start_date_field_name, datetime.date(
                self.from_year_value, self.from_month_value or 1, self.from_day_value or 1))
        else:
            setattr(self, self.start_date_field_name, MIN_DATE)

        if self.until_year_value:
            setattr(self, self.end_date_field_name, datetime.date(
                self.until_year_value, self.until_month_value or 12, self.until_day_value or 31))
        else:
            setattr(self, self.end_date_field_name, MAX_DATE)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(RuntimeBehaviour, self).save(*args, **kwargs)

    @property
    def from_date(self):
        return getattr(self, self.start_date_field_name)

    @property
    def until_date(self):
        return getattr(self, self.end_date_field_name)

    # TODO ? Implement @from_date.setter, @until_date.setter

    def get_from_display(self):
        return self.runtime_text or format_partial_date(
            self.from_year_value,
            self.from_month_value,
            self.from_day_value)
    get_from_display.admin_order_field = start_date_field_name
    get_from_display.short_description = _("from")

    def get_until_display(self):
        if self.runtime_text:
            return ""
        else:
            return format_partial_date(
                self.until_year_value,
                self.until_month_value,
                self.until_day_value)
    get_until_display.admin_order_field = end_date_field_name
    get_until_display.short_description = _("until")

    def get_runtime_display(self):
        # TODO Improve
        if self.runtime_text:
            return self.runtime_text
        elif self.from_day_value and self.from_month_value:
            return format_date_range(self.from_date, self.until_date)
        else:
            f = self.get_from_display()
            # Single point
            if self.from_date == self.until_date:
                return f

            u = self.get_until_display()
            if f and u and not f == u:
                return "{}–{}".format(f, u)
            else:
                return f or u


class RuntimeMixin(RuntimeBehaviour, models.Model):
    from_year_value = models.PositiveIntegerField(_("starting year"), null=True, blank=True)
    from_month_value = models.PositiveIntegerField(_("starting month"), null=True, blank=True)
    from_day_value = models.PositiveIntegerField(_("starting day"), null=True, blank=True)
    until_year_value = models.PositiveIntegerField(_("ending year"), null=True, blank=True)
    until_month_value = models.PositiveIntegerField(_("ending month"), null=True, blank=True)
    until_day_value = models.PositiveIntegerField(_("ending day"), null=True, blank=True)
    _from_sort_date = models.DateField(_("from"), editable=False)
    _until_sort_date = models.DateField(_("until"), editable=False)

    runtime_text = TranslatableCharField(_("Zeitangabe Textform"),
        max_length=200, null=True, blank=True,
        help_text=_("Alternativer Text für die Laufzeitangabe"))

    start_date_field_name = '_from_sort_date'
    end_date_field_name = '_until_sort_date'
    allow_empty_runtime = False

    class Meta:
        abstract = True
