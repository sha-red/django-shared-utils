# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Erik Stein <code@classlibrary.net>, 2007-2016

__version__ = '0.2.1'

try:
    from ._version import __version__
except ImportError:
    pass

VERSION = __version__.split('+')
VERSION = tuple(list(map(int, VERSION[0].split('.'))) + VERSION[1:])

try:
    from django.utils.translation import ugettext_lazy as _

    SLUG_HELP = _("Kurzfassung des Namens für die Adresszeile im Browser. Vorzugsweise englisch, keine Umlaute, nur Bindestrich als Sonderzeichen.")
except ImportError:
    pass
