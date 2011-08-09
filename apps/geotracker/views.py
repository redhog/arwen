# -*- coding: utf-8 -*-

import django.shortcuts
import django.contrib.auth.decorators
import django.contrib.auth.models
import django.template
import geotracker.models
import settings
import datetime
import django.template.loader
import django.utils.http
import django.contrib.messages
import django.http
import django.core.urlresolvers
from django.utils.translation import ugettext_lazy as _

@django.contrib.auth.decorators.login_required
def view_journey(request, journey_id):
    j = django.shortcuts.get_object_or_404(geotracker.models.Journey, id=journey_id)

    return django.shortcuts.render_to_response(
        "geotracker/view_journey.html",
        {
            "journey": j
            },
        django.template.RequestContext(request))


@django.contrib.auth.decorators.login_required
def export_journey(request, journey_id, format):
    j = django.shortcuts.get_object_or_404(geotracker.models.Journey, id=journey_id)

    if format == "geojson":
        return django.http.HttpResponse(j.as_geoscollection.json, mimetype="text/json")

    return django.http.HttpResponse("Unknown format", status=400, mimetype="text/plain")
