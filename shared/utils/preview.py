from django.conf import settings
from django.utils import timezone

from .conf import USE_PREVIEW_DATETIME
from .timezone import smart_default_tz


class datetime(timezone.datetime):
    @classmethod
    def now(klass):
        if USE_PREVIEW_DATETIME:
            if settings.DEBUG_PREVIEW_DATETIME:
                now = timezone.datetime(*settings.DEBUG_PREVIEW_DATETIME)
            else:
                # TODO Get preview datetime from request user
                now = timezone.now()
            if settings.USE_TZ:
                now = smart_default_tz(now)
        else:
            now = timezone.now()
        return now

    @classmethod
    def today(klass):
        return klass.now().date()
