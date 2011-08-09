import django.template

register = django.template.Library()

@register.filter
def get_links(obj, display_context = []):
    return obj.get_links(display_context).iteritems()

@register.filter
def display(obj, display_context = []):
    if not hasattr(obj, "display"):
        return unicode(obj)
    return obj.display(display_context)

@register.filter
def display_links(obj, display_context = []):
    if not hasattr(obj, "display"):
        return ''
    return obj.display_links(display_context)

@register.filter
def display_link(obj, display_context = []):
    if not hasattr(obj, "display_link"):
        return unicode(obj)
    return obj.display_link(display_context)
