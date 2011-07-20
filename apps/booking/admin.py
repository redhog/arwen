# -*- coding: utf-8 -*-
import django.contrib.admin
import booking.models

django.contrib.admin.site.register(booking.models.Event)
django.contrib.admin.site.register(booking.models.EventDate)
django.contrib.admin.site.register(booking.models.EventBooking)
django.contrib.admin.site.register(booking.models.EventDateBooking)
