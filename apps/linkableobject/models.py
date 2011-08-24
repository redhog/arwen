# -*- coding: utf-8 -*-
import django.db.models.base

def prefixes(lst):
    yield lst
    while lst:
        lst = lst[:-1]
        yield lst

def is_prefix(prefix, value):
    prefix = tuple(prefix)
    value = tuple(value)
    value_len = len(value)
    prefix_len = len(prefix)
    if value_len < prefix_len: return False
    return prefix == value[:prefix_len]

class LinkableObjectMixin(object):
    @classmethod
    def get_class_context(cls):
        if hasattr(cls, "class_context"):
            return cls.class_context
        return cls.__module__.lower().split('.') + [cls.__name__.lower()]

    _template_for_display_context_cache = {}
    @classmethod
    def template_for_display_context(cls, use, display_context):
        class_context = cls.get_class_context()
        key = (use, tuple(class_context), tuple(display_context))
        if key not in cls._template_for_display_context_cache:
            templates = []
            for class_prefix in prefixes(class_context):
                for prefix in prefixes(display_context):
                    templates.append("linkableobject/%s__%s__%s.html" % (use, '_'.join(class_prefix), '_'.join(prefix)))
            cls._template_for_display_context_cache[key] = django.template.loader.select_template(templates)
        return cls._template_for_display_context_cache[key]

    @classmethod
    def get_link_fields(cls, display_context):
        return {}

    def get_links(self, display_context):
        return {}

    def display(self, display_context, context = None):
        if not context: context = django.template.Context()
        context.push()
        try:
            context["obj"] = self
            context["display_context"] = display_context
            return self.template_for_display_context("display", display_context).render(context)
        finally:
            context.pop()

    def display_links(self, display_context, context = None):
        if not context: context = django.template.Context()
        context.push()
        try:
            context["obj"] = self
            context["display_context"] = display_context
            return self.template_for_display_context("display_links", display_context).render(context)
        finally:
            context.pop()

    def display_link(self, display_context, context = None):
        if not context: context = django.template.Context()
        context.push()
        try:
            context["obj"] = self
            context["display_context"] = display_context
            return self.template_for_display_context("display_link", display_context).render(context)
        finally:
            context.pop()

class LinkableModelMixin(LinkableObjectMixin):
    @classmethod
    def get_link_fields(cls, display_context):
        res = {}
        for name in dir(cls):
            #if name.endswith("__display_context"): continue
            field = getattr(cls, name, None)
            if not isinstance(field, (django.db.models.fields.related.ForeignRelatedObjectsDescriptor,
                                      django.db.models.fields.related.ReverseSingleRelatedObjectDescriptor,
                                      django.db.models.fields.related.SingleRelatedObjectDescriptor)): continue
            field_descriptor = getattr(field, "field", None)

            field_display_context = getattr(field_descriptor, "display_context", name.split('_'))
            if not is_prefix(display_context, field_display_context): continue

            if getattr(field_descriptor, "display_inline", False):
                if isinstance(field, django.db.models.fields.related.ForeignRelatedObjectsDescriptor):
                    import pdb
                    pdb.set_trace()
                elif isinstance(field, django.db.models.fields.related.ReverseSingleRelatedObjectDescriptor) and not issubclass(cls, field.field.rel.to):
                    res.update(field.field.related.parent_model.get_link_fields(display_context))
                elif isinstance(field, django.db.models.fields.related.SingleRelatedObjectDescriptor) and not issubclass(field.related.model, cls):
                    import pdb
                    pdb.set_trace()
            else:
                if isinstance(field, django.db.models.fields.related.ForeignRelatedObjectsDescriptor):
                    if hasattr(field.related.field, 'verbose_related_name'):
                        res[name] = field.related.field.verbose_related_name
                    elif hasattr(field.related.field, 'verbose_name'):
                        res[name] = "reverse for " + field.related.field.verbose_name
                    else:
                        res[name] = "reverse for " + field.related.field.name
                elif isinstance(field, django.db.models.fields.related.ReverseSingleRelatedObjectDescriptor) and not issubclass(cls, field.field.rel.to):
                    res[name] = field.field.verbose_name
                elif isinstance(field, django.db.models.fields.related.SingleRelatedObjectDescriptor) and not issubclass(field.related.model, cls):
                    import pdb
                    pdb.set_trace()

        return res

    def get_links(self, display_context):
        res = self.get_link_fields(display_context)
        for name, description in res.iteritems():
            value = getattr(self, name, None)
            t = type(value)
            res[name] = {'description': description}
            if t.__name__ == "RelatedManager":
                res[name]['values'] = value.all()
            else:
                res[name]['values'] = [value]
        return res
