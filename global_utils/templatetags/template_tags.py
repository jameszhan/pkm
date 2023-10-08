from django import template
from global_utils.functions import human_readable_size

register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()


@register.filter(name="zfill")
def get_item(num, n):
    return str(num).zfill(n)


@register.filter(name="humanize")
def humanize(num):
    return human_readable_size(num)

