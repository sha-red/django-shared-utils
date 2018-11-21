from urllib.parse import urlencode

from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)


@register.filter
def paginator_context(page_range, current):
    before = [p for p in page_range if p < current]
    after = [p for p in page_range if p > current]
    if len(before) > 3:
        before = before[:2] + [''] + before[-1:]
    if len(after) > 3:
        after = after[:1] + [''] + after[-2:]
    return before + [current] + after
