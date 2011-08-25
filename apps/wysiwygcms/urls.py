# -*- coding: utf-8 -*-

import django.conf.urls.defaults

urlpatterns = django.conf.urls.defaults.patterns(
    '',
    django.conf.urls.defaults.url(r'^wysiwygcms/(?P<slug>\w+)/?$', 'wysiwygcms.views.view_node', name="wysiwygcms_node"),
    django.conf.urls.defaults.url(r'^wysiwygcms/(?P<slug>\w+)/(?P<version_id>\d+)/?$', 'wysiwygcms.views.view_node', name="wysiwygcms_node"),
    django.conf.urls.defaults.url(r'^wysiwygcms/(?P<slug>\w+)/edit/?$', 'wysiwygcms.views.edit_node', name="wysiwygcms_node"),
)
