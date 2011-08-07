# -*- coding: utf-8 -*-

import django.conf.urls.defaults

urlpatterns = django.conf.urls.defaults.patterns(
    '',
    django.conf.urls.defaults.url(r'^journey/(?P<journey_id>\d+)/?$', 'geotracker.views.view_journey', name="geotracker_view_journey"),
    django.conf.urls.defaults.url(r'^journey/(?P<journey_id>\d+)/export/(?P<format>\w+)?$', 'geotracker.views.export_journey', name="geotracker_export_journey"),
)
