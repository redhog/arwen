import django.template
import fcdjangoutils.templatetaghelpers

register = django.template.Library()

@register.filter
def get_links(obj, display_context = []):
    return obj.get_links(display_context).iteritems()

@register.tag
@fcdjangoutils.templatetaghelpers.simple_tag
def display(context, obj, display_context = []):
    if isinstance(display_context, (str, unicode)):
        display_context = display_context and display_context.split(".") or []
    if not hasattr(obj, "display"):
        return unicode(obj)
    return obj.display(display_context, context)

@register.tag
@fcdjangoutils.templatetaghelpers.simple_tag
def display_links(context, obj, display_context = []):
    if isinstance(display_context, (str, unicode)):
        display_context = display_context and display_context.split(".") or []
    if not hasattr(obj, "display_links"):
        return ''
    return obj.display_links(display_context, context)

@register.tag
@fcdjangoutils.templatetaghelpers.simple_tag
def display_link(context, obj, display_context = []):
    if isinstance(display_context, (str, unicode)):
        display_context = display_context and display_context.split(".") or []
    if not hasattr(obj, "display_link"):
        return unicode(obj)
    return obj.display_link(display_context, context)

