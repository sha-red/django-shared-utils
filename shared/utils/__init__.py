# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2007-2016

VERSION = (0, 2, 1)
__version__ = '.'.join(map(str, VERSION))


try:
    from django.utils.translation import ugettext_lazy as _

    SLUG_HELP = _("Kurzfassung des Namens für die Adresszeile im Browser. Vorzugsweise englisch, keine Umlaute, nur Bindestrich als Sonderzeichen.")
except ImportError:
    pass
