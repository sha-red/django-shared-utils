import logging

from django.template import TemplateDoesNotExist
from django.template.loader import select_template


logger = logging.getLogger(__name__)


def log_select_template(template_names):
    logger.info("\nPossible template names:")
    logger.info("\n".join(template_names))
    try:
        logger.info("Chosen: %s" % select_template(template_names).template.name)
    except TemplateDoesNotExist:
        logger.warn("   Could not find a matching template file.")
