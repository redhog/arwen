import django.template
import wysiwygcms.models

register = django.template.Library()

@register.filter
def get_node(slug):
    nodes = wysiwygcms.models.Node.objects.filter(slug=slug)
    if nodes and nodes[0].latest_version:
        return nodes[0].latest_version
    return None
