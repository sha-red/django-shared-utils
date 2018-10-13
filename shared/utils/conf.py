from django.conf import settings

USE_TRANSLATABLE_FIELDS = getattr(settings, 'USE_TRANSLATABLE_FIELDS', False)
