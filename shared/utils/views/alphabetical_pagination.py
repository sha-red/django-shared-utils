# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import F, Func, Value


class AlphabeticalPaginationMixin(object):
    alphabetical_pagination_field = 'name'

    def get_alphabetical_pagination_field(self):
        return self.alphabetical_pagination_field

    def get_selected_letter(self):
        return self.request.GET.get('letter', 'a')

    def get_base_queryset(self):
        """
        Queryset before applying pagination filters.
        """
        qs = super(AlphabeticalPaginationMixin, self).get_queryset().exclude(
            **{self.get_alphabetical_pagination_field(): ''}
        )
        return qs

    def get_queryset(self):
        qs = self.get_base_queryset()
        # FIXME Select Umlauts (using downgrade and also downgrade sort_name field?)
        # FIXME Select on TRIM/LEFT as in get_letter_choices
        filter = {
            "{}__istartswith".format(self.get_alphabetical_pagination_field()):
            self.get_selected_letter()}
        return qs.filter(**filter)

    def get_letter_choices(self):
        return self.get_base_queryset().annotate(name_lower=Func(
            Func(
                Func(
                    F(self.get_alphabetical_pagination_field()), function='LOWER'),
                function='TRIM'),
            Value("1"), function='LEFT')).order_by(
                'name_lower').distinct('name_lower').values_list('name_lower', flat=True)

    def get_context_data(self, **kwargs):
        context = super(AlphabeticalPaginationMixin, self).get_context_data(**kwargs)
        context['selected_letter'] = self.get_selected_letter()
        context['alphabet'] = self.get_letter_choices()
        return context

