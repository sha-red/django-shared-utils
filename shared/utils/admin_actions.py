from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ngettext, gettext_lazy as _


class AdminActionBase:
    action_name = None
    options_template_name = 'admin/action_forms/admin_action_base.html'
    title = None
    queryset_action_label = None
    action_button_label = None

    def apply(self, queryset, form):
        raise NotImplementedError

    def get_message(self, count):
        raise NotImplementedError

    def get_failure_message(self, count, failure_count):
        raise NotImplementedError

    class BaseForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

    def get_form_class(self, modeladmin, request, queryset):
        """
        Example:

        class CustomForm(BaseForm)
            chosen_target = forms.ModelChoiceField(
                label=_("Choose target itembundle"),
                queryset=ItemBundle.objects.exclude(pk__in=queryset),
                widget=ForeignKeyRawIdWidget(modeladmin.model._meta.get_field('parent').rel, modeladmin.admin_site),
                empty_label=_("Root level"), required=False)
        return CustomForm
        """
        raise NotImplementedError

    def __call__(self, modeladmin, request, queryset):
        form_class = self.get_form_class(modeladmin, request, queryset)

        form = None
        if 'apply' in request.POST:
            form = form_class(request.POST)
            if form.is_valid():
                queryset_count = queryset.count()
                count = self.apply(queryset, form)
                failure_count = queryset_count - count
                if failure_count > 0:
                    message = self.get_failure_message(form, count, failure_count)
                else:
                    message = self.get_message(form, count)
                modeladmin.message_user(request, message)
                return HttpResponseRedirect(request.get_full_path())

        if 'cancel' in request.POST:
            return HttpResponseRedirect(request.get_full_path())

        if not form:
            form = form_class(initial={
                '_selected_action': request.POST.getlist(
                    admin.ACTION_CHECKBOX_NAME),
            })

        return render(request, self.options_template_name, context={
            'action_name': self.action_name,
            'title': self.title,
            'queryset_action_label': self.queryset_action_label,
            'action_button_label': self.action_button_label,
            'queryset': queryset,
            'action_form': form,
            'opts': modeladmin.model._meta,
        })


class TargetActionBase(AdminActionBase):
    target_model = None
    related_field_name = None

    def get_form_class(self, modeladmin, request, queryset):
        class ChooseTargetForm(AdminActionBase.BaseForm):
            chosen_target = forms.ModelChoiceField(
                label=_("Choose {}".format(self.target_model._meta.verbose_name)),
                queryset=self.target_model.objects.exclude(pk__in=queryset),
                widget=ForeignKeyRawIdWidget(
                    modeladmin.model._meta.get_field(self.related_field_name).rel,
                    modeladmin.admin_site
                ),
            )
        return ChooseTargetForm

    def get_message(self, form, count):
        chosen_target = form.cleaned_data['chosen_target']
        target_name = chosen_target.name
        return ngettext(
            'Successfully added %(count)d %(verbose_name)s to %(target)s.',
            'Successfully added %(count)d %(verbose_name_plural)s to %(target)s.',
            count) % {
                'count': count,
                'verbose_name': self.target_model._meta.verbose_name,
                'verbose_name_plural': self.target_model._meta.verbose_name_plural,
                'target': target_name}

    def get_failure_message(self, form, count, failure_count):
        chosen_target = form.cleaned_data['chosen_target']
        target_name = chosen_target.name
        return ngettext(
            'Adding %(count)d %(verbose_name)s to %(target)s, %(failure_count)s failed or skipped.',
            'Adding %(count)d %(verbose_name_plural)s to %(target)s, %(failure_count)s failed or skipped.',
            count) % {
                'count': count,
                'verbose_name': self.target_model._meta.verbose_name,
                'verbose_name_plural': self.target_model._meta.verbose_name_plural,
                'target': target_name,
                'failure_count': failure_count}

