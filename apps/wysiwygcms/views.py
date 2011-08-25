# -*- coding: utf-8 -*-

import django.shortcuts
import django.contrib.auth.decorators
import django.contrib.auth.models
import django.template
import wysiwygcms.models
import django.contrib.sites.models
import django.template.loader
import django.utils.http
import pinax.core.utils
import django.contrib.messages
import django.http
import django.core.urlresolvers
from django.utils.translation import ugettext_lazy as _


def view_node(request, slug, version_id = None):
    node_version = None
    nodes = wysiwygcms.models.Node.objects.filter(slug=slug)
    if nodes:
        node_version = nodes[0].latest_version
        if version_id is not None:
            node_versions = nodes[0].versions.filter(id = version_id)
            if node_versions:
                node_version = node_versions[0]
    if not node_version:
        return django.shortcuts.redirect("wysiwygcms.views.edit_node", slug=slug)

    return django.shortcuts.render_to_response(
        "wysiwygcms/view_node.html",
        {"node_version": node_version},
        django.template.RequestContext(request))

def edit_node(request, slug):
    nodes = wysiwygcms.models.Node.objects.filter(slug=slug)
    node = nodes and nodes[0] or None
    node_version = None
    if node:
        node_version = node.latest_version

    if request.method == "POST":
        if not node:
            node = wysiwygcms.models.Node(slug = slug)
            node.save()
        wysiwygcms.models.NodeVersion(node = node, content = request.POST['content'], owner = request.user).save()
        return django.shortcuts.redirect(node)

    return django.shortcuts.render_to_response(
        "wysiwygcms/edit_node.html",
        {"node_version": node_version},
        django.template.RequestContext(request))
