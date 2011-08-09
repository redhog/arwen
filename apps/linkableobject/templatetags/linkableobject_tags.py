import django.template

register = django.template.Library()

@register.filter
def get_links(obj, display_context):
    return obj.get_links(display_context).iteritems()

@register.filter
def display(obj, display_context):
    return obj.display(display_context)

@register.filter
def display_links(obj, display_context):
    return obj.display_links(display_context)

@register.filter
def display_link(obj, display_context):
    return obj.display_link(display_context)
