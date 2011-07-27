# -*- coding: utf-8 -*-
import django.contrib.gis.admin
import geotracker.models

django.contrib.gis.admin.site.register(geotracker.models.Vehicle, django.contrib.gis.admin.GeoModelAdmin)
django.contrib.gis.admin.site.register(geotracker.models.TimePoint, django.contrib.gis.admin.GeoModelAdmin)
django.contrib.gis.admin.site.register(geotracker.models.Path, django.contrib.gis.admin.GeoModelAdmin)
django.contrib.gis.admin.site.register(geotracker.models.PathPoint, django.contrib.gis.admin.GeoModelAdmin)
django.contrib.gis.admin.site.register(geotracker.models.Journey, django.contrib.gis.admin.GeoModelAdmin)
django.contrib.gis.admin.site.register(geotracker.models.JourneyPath, django.contrib.gis.admin.GeoModelAdmin)
