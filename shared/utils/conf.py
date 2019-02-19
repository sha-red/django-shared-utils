from django.conf import settings

USE_TRANSLATABLE_FIELDS = (
    getattr(settings, 'CONTENT_PLUGINS_USE_TRANSLATABLE_FIELDS', False) or
    getattr(settings, 'USE_TRANSLATABLE_FIELDS', False)
)


USE_PREVIEW_DATETIME = getattr(settings, 'USE_PREVIEW_DATETIME', False)
# You also have to set PREVIEW_DATETIME = datetime(...)
