from django.utils import timezone


def midnight(dt=None):
    """
    Returns upcoming midnight.
    """
    if not dt:
        dt = timezone.now()

    return dt.replace(hour=0, minute=0, second=0, microsecond=0) + \
        timezone.timedelta(days=1)
