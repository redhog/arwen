import django.template
import wysiwygcms.models
import settings
import django.template.loader


class Loader(django.template.loader.BaseLoader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        nodes = wysiwygcms.models.Node.objects.filter(slug = template_name)
        if nodes and nodes[0].latest_version:
            return nodes[0].latest_version.content, "The internets"
        raise django.template.TemplateDoesNotExist(template_name)
