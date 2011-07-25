# -*- coding: utf-8 -*-

import django.conf.urls.defaults
import groups.bridge
import pinax.apps.tribes.models

urlpatterns = django.conf.urls.defaults.patterns('')

bridge = groups.bridge.ContentBridge(pinax.apps.tribes.models.Tribe)
urlpatterns += bridge.include_urls("booking.urls", r"^tribes/tribe/(?P<tribe_slug>[-\w]+)/")
