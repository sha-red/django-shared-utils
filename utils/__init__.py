# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2007-2016

from django.utils.translation import ugettext_lazy as _


VERSION = (0, 1, 0)
__version__ = '.'.join(map(str, VERSION))


SLUG_HELP = _("Kurzfassung des Namens für die Adresszeile im Browser. Vorzugsweise englisch, keine Umlaute, nur Bindestrich als Sonderzeichen.")
