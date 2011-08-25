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
            clsfield = getattr(cls, name, None)
            if hasattr(clsfield, 'field'):
                field = clsfield.field
                othercls = field.related.parent_model
                reverse = False
            elif hasattr(clsfield, 'related'):
                field = clsfield.related.field
                othercls = clsfield.related.parent_model
                reverse = True
            else:
                continue
            revprefix = ['', 'related_'][reverse]
            namepattern = ['%s', 'reverse of %s'][reverse]

            field_display_context = getattr(field, revprefix + "display_context", name.split('_'))
            if not is_prefix(display_context, field_display_context): continue

            res[name] = {'description': getattr(field, "verbose_%sname" % (revprefix,),
                                                getattr(field, "%sname" % (revprefix,),
                                                        namepattern % getattr(field, "verbose_name", field.name)))}
            if getattr(field, revprefix + "display_inline", False):
                res[name]['fields'] = othercls.get_link_fields(display_context)
        return res

    def get_links(self, display_context, flatten = True):
        def merge_values(data1, data2):
            for name, item_data in data2.iteritems():
                if name not in data1: 
                    data1[name] = dict(item_data)
                    data1[name]['values'] = []
                data1[name]['values'].extend(item_data['values'])
        def get_values(model, data):
            for name, item_data in data.items():
                value = getattr(model, name, None)
                t = type(value)
                if t.__name__ in ("RelatedManager", "ManyRelatedManager"):
                    item_data['values'] = [{'model': submodel} for submodel in value.all()]
                else:
                    item_data['values'] = [{'model': value}]
                if 'fields' in item_data: # display inline
                    for value in item_data['values']:
                        value['fields'] = dict(item_data['fields'])
                        get_values(value['model'], value['fields'])
                    if flatten:
                        del data[name]
                        for value in item_data['values']:
                            merge_values(data, value['fields'])

        data = self.get_link_fields(display_context)
        get_values(self, data)

        return data
