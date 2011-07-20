# -*- coding: utf-8 -*-

import django.shortcuts
import django.contrib.auth.decorators
import django.contrib.auth.models
import django.template
import booking.models
import settings
import datetime

@django.contrib.auth.decorators.login_required
def event(request, event_id = None):
    if event_id is None:
        ee = booking.models.Event.objects.all()
        u = request.user

        return django.shortcuts.render_to_response(
            "booking/events.html", 
            {
                "events": ee,
                "user": u,
                'static_url': settings.STATIC_URL,
                },
            context_instance=django.template.RequestContext(request))
    else:
        e = django.shortcuts.get_object_or_404(booking.models.Event, id=event_id)
        u = request.user

        if request.method == "POST":
            email = request.POST['email'].lower()
            phone = request.POST['phone']
            dates = [datetime.datetime(*[int(x) for x in day.split("-")]) for day in request.POST.getlist("days")]

            try:
                u = django.contrib.auth.models.User.objects.get(email=email)
            except:
                u = django.contrib.auth.models.User(username=email.replace("@", "_"), email=email)
            
            u.phone = phone
            u.save()

            try:
                event_booking = u.event_bookings.get(event__id = event_id)
            except:
                event_booking = booking.models.EventBooking(booker=u, event=e)
            event_booking.save()

            for date in event_booking.dates.all():
                date.delete()

            for date in dates:
                d = e.dates.get(date=date)
                booking.models.EventDateBooking(event_booking = event_booking, date=d).save()

        return django.shortcuts.render_to_response(
            "booking/event.html", 
            {
                "event": e,
                "user": u,
                'static_url': settings.STATIC_URL,
                },
            context_instance=django.template.RequestContext(request))
