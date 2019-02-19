"""

Django and Timezones
--------------------

https://github.com/ixc/django-timezone/
Helper functions for working with datetime objects without caring if they are timezone aware or not.

https://github.com/michaeljohnbarr/django-timezone-utils/
Time zone utilities for Django models.

https://github.com/counsyl/django-postgres-timezones
A sample Django application illustrating some time zone traps for the unwary.

"""

import datetime
from django.conf import settings
from django.utils import timezone


def smart_default_tz(datetime_value):
    """
    Returns the give datetime with the default timezone applied.
    """
    if timezone.is_naive(datetime_value):
        datetime_value = timezone.make_aware(datetime_value, timezone=timezone.get_default_timezone())
    return timezone.localtime(datetime_value, timezone.get_default_timezone())


def timezone_today():
    """
    Return the current date in the current time zone.
    """
    if settings.USE_TZ:
        return timezone.localdate()
    else:
        return datetime.date.today()
