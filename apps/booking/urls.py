# -*- coding: utf-8 -*-

import django.conf.urls.defaults

urlpatterns = django.conf.urls.defaults.patterns(
    '',
    django.conf.urls.defaults.url(r'^booking/?$', 'booking.views.event', name="booking_event_list"),
    django.conf.urls.defaults.url(r'^booking/(?P<event_id>\d+)/?$', 'booking.views.event', name="booking_event"),
    django.conf.urls.defaults.url(r'^booking/add/?$', 'booking.views.add_event', name="booking_event_add"),
)
