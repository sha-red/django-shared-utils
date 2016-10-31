# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2016

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


# from http://stackoverflow.com/questions/877723/inline-form-validation-in-django#877920

class MandatoryInlineFormSet(forms.models.BaseInlineFormSet):
    """
    Make sure at least one inline form is valid.
    """
    mandatory_error_message = _("Bitte mindestens %(min_num)s %(name)s angeben.")

    def is_valid(self):
        return super(MandatoryInlineFormSet, self).is_valid() and \
                     not any([bool(e) for e in self.errors])

    def clean(self):
        # get forms that actually have valid data
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    count += 1
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if count < self.min_num:
            if self.min_num > 1:
                name = self.model._meta.verbose_name_plural
            else:
                name = self.model._meta.verbose_name
            raise forms.ValidationError(
                self.mandatory_error_message % {
                    'min_num': self.min_num,
                    'name': name,
                }
            )


class MandatoryTabularInline(admin.TabularInline):
    formset = MandatoryInlineFormSet


class MandatoryStackedInline(admin.StackedInline):
    formset = MandatoryInlineFormSet
