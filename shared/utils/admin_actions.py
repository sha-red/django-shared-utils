
from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render


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
