from django.conf import settings
from django.core import validators
from django.db import models
from django.db.models import fields as django_fields
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from dirtyfields import DirtyFieldsMixin

from ..text import slugify, downgrading_slugify, django_slugify

if six.PY3:
    from functools import reduce


DEFAULT_SLUG = getattr(settings, 'DEFAULT_SLUG', "item")

SLUG_HELP = _("Kurzfassung des Namens für die Adresszeile im Browser. Vorzugsweise englisch, keine Umlaute, nur Bindestrich als Sonderzeichen.")


slug_re = validators._lazy_re_compile(r'^[-a-z0-9]+\Z')
validate_downgraded_slug = validators.RegexValidator(
    slug_re,
    _("Enter a valid 'slug' consisting of lower-case letters, numbers or hyphens."),
    'invalid'
)


class AutoSlugField(django_fields.SlugField):
    """
    SlugField which optionally populates the value and/or makes sure that
    the value is unique. By default as stricter slugify function is used.

    populate_from: Field name
    unique_slug: Boolean, automatically make the field value unique
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 50)
        kwargs.setdefault('help_text', SLUG_HELP)
        if 'populate_from' in kwargs:
            self.populate_from = kwargs.pop('populate_from')
        self.unique_slug = kwargs.pop('unique_slug', False)
        super(AutoSlugField, self).__init__(*args, **kwargs)

    def slugify(self, value):
        return slugify(value)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if not value:
            if hasattr(self, 'populate_from'):
                if callable(self.populate_from):
                    value = self.populate_from(model_instance, self)
                else:
                    # Follow dotted path (e.g. "occupation.corporation.name")
                    value = reduce(lambda obj, attr: getattr(obj, attr),
                        self.populate_from.split("."), model_instance)
                    if callable(value):
                        value = value()
            if not value:
                value = DEFAULT_SLUG
        value = self.slugify(value)
        if self.unique_slug:
            # TODO Move import to top of file once AutoSlugField is removed from shared.utils.fields and we no longer have a circular import
            from ..fields import uniquify_field_value
            return uniquify_field_value(
                model_instance, self.name, value, max_length=self.max_length)
        else:
            return value


class DowngradingSlugField(AutoSlugField):
    """
    SlugField which allows only lowercase ASCII characters and the dash,
    automatically downgrading/replacing the entered content.
    """

    default_validators = [validate_downgraded_slug]

    def __init__(self, *args, **kwargs):
        kwargs['allow_unicode'] = False
        super(DowngradingSlugField, self).__init__(*args, **kwargs)

    def slugify(self, value):
        return downgrading_slugify(value)

    def to_python(self, value):
        # Downgrade immediately so that validators work
        value = super().to_python(value)
        return self.slugify(value)

    def formfield(self, **kwargs):
        # Remove the slug validator from the form field so that we can modify
        # the field value in the model
        field = super().formfield(**kwargs)
        if field.default_validators:
            try:
                field.validators.remove(field.default_validators[0])
            except ValueError:
                pass
        return field


class SlugTreeMixin(DirtyFieldsMixin, models.Model):
    """
    Expects a `slug` and a `has_url` field.
    """
    slug_path = models.CharField(_("URL path"), max_length=2000, editable=False)
    has_url = models.BooleanField(_("has webaddress"), default=True)

    FIELDS_TO_CHECK = ['slug']

    class Meta:
        abstract = True

    def _get_slug_path(self):
        if self.pk:
            ancestors = self.get_ancestors(include_self=False).filter(has_url=True).values_list('slug', flat=True)
            parts = list(ancestors)
        else:
            parts = []
        if self.slug:
            parts += [self.slug]
        return "/".join(parts)

    def _rebuild_descendants_slug_path(self):
        for p in self.get_descendants():
            p.slug_path = p._get_slug_path()
            p.save()


@receiver(pre_save)
def slug_tree_mixin_pre_save(sender, instance, **kwargs):
    if isinstance(instance, SlugTreeMixin):
        # FIXME: find a way to not always call this
        instance.slug = instance._meta.get_field('slug').pre_save(instance, False)
        instance.slug_path = instance._get_slug_path()


@receiver(post_save)
def slug_tree_mixin_post_save(sender, instance, **kwargs):
    if isinstance(instance, SlugTreeMixin):
        if kwargs.get('created'):
            # Always get a new database instance before saving again
            # or MPTTModel.save() will interpret the newly .save as
            # not allowed tree move action
            # FIXME Not clear if this is a proper solution -> get rid of the slug_path stuff altogether
            instance_copy = type(instance).objects.get(pk=instance.pk)
            instance_copy.slug_path = instance_copy._get_slug_path()
            if 'slug_path' in instance_copy.get_dirty_fields().keys():
                instance_copy.save()
        elif instance.get_dirty_fields().keys() & {'slug_path'}:
            instance._rebuild_descendants_slug_path()
