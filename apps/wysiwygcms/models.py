# -*- coding: utf-8 -*-
import django.db.models
import django.contrib.auth.models
from django.utils.translation import ugettext_lazy as _
import tagging
import fcdjangoutils.signalautoconnectmodel
import linkableobject.models

class Node(fcdjangoutils.signalautoconnectmodel.SignalAutoConnectModel, linkableobject.models.LinkableModelMixin):
    def get_absolute_url(self, group=None):
        return django.core.urlresolvers.reverse("wysiwygcms.views.view_node", kwargs={"slug": self.slug})

    slug = django.db.models.SlugField(_('slug'))
    latest_version = django.db.models.ForeignKey("NodeVersion", related_name="dummy1", verbose_name="Latest version", blank=True, null=True)

    def __unicode__(self):
        if self.latest_version is not None:
            return "%s last edited @ %s" % (self.slug, self.latest_version.timestamp)
        return "%s is empty" % self.slug

class NodeVersion(fcdjangoutils.signalautoconnectmodel.SignalAutoConnectModel, linkableobject.models.LinkableModelMixin):
    def get_absolute_url(self, group=None):
        return django.core.urlresolvers.reverse("wysiwygcms.views.view_node", kwargs={"slug": self.slug, "version_id": self.id})

    node = django.db.models.ForeignKey(Node, related_name="versions", verbose_name="Node")
    node.verbose_related_name = "Versions"
    node.display_context = ['display']
    node.display_inline = True

    timestamp = django.db.models.DateTimeField(_('timestamp'), auto_now_add = True)
    content = django.db.models.TextField(_('content'))
    owner = django.db.models.ForeignKey(django.contrib.auth.models.User, related_name="node_versions", verbose_name="Owner")
    owner.verbose_related_name = "Node versions"

    tags = django.db.models.ManyToManyField(Node, related_name="tagged", verbose_name="Tags")
    tags.verbose_related_name = "Nodes tagged with this node"
    tags.display_context = ['display']
    tags.related_display_context = ['display']

    @property
    def slug(self):
        return self.node.slug

    @property
    def title(self):
        return self.slug

    @classmethod
    def on_post_save(cls, sender, instance, **kwargs):
        instance.node.latest_version = instance
        instance.node.save()

    def display(self, display_context, context = None):
        if not context: context = django.template.Context()
        context.push()
        try:
            context["obj"] = self
            context["display_context"] = display_context
            template = django.template.Template(self.content)
            context["content"] = template.render(context)
            return self.template_for_display_context("display", display_context).render(context)
        finally:
            context.pop()

    def __unicode__(self):
        return "%s @ %s" % (self.slug, self.timestamp)
