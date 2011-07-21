# -*- coding: utf-8 -*-

import django.shortcuts
import django.contrib.auth.decorators
import django.contrib.auth.models
import django.template
import booking.models
import settings
import datetime
import django.contrib.auth.tokens
import pinax.apps.account.models
import django.contrib.sites.models
import django.template.loader
import django.utils.http
import pinax.core.utils
send_mail = pinax.core.utils.get_send_mail()

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
        eb = None
        if not u.is_anonymous():
            ebs = list(u.event_bookings.filter(event__id = event_id))
            if ebs:
                eb = ebs[0]

        if request.method == "POST":
            email = request.POST['email'].lower()
            phone = request.POST['phone']
            dates = [datetime.datetime(*[int(x) for x in day.split("-")]) for day in request.POST.getlist("days")]

            if not u.is_anonymous():
                u.email = email
            else:
                u = django.contrib.auth.models.User(username=email.replace("@", "_"), email=email)
                u.set_unusable_password()
                u.save()

                temp_key = django.contrib.auth.tokens.default_token_generator.make_token(u)
                password_reset = pinax.apps.account.models.PasswordReset(user=u, temp_key=temp_key)
                password_reset.save()

                # send the password reset email
                message =  django.template.loader.render_to_string("booking/new_account_message.txt", {
                    "user": u,
                    "uid": django.utils.http.int_to_base36(u.id),
                    "temp_key": temp_key,
                    "domain": unicode(django.contrib.sites.models.Site.objects.get_current().domain),
                })
                subject, message = message.split("\n\n", 1)

                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [u.email], priority="high")

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

        ed = []
        last_year = {'year': None, 'nr_dates':0}
        last_month = {'month': None, 'nr_dates':0}
        for date in e.sorted_dates:
            date = date.date
            if date.year != last_year['year']:
                last_month = {'month':date.month, 'dates':[date], 'nr_dates':1}
                last_year = {'year':date.year, 'months':[last_month], 'nr_dates':1}
                ed.append(last_year)
            elif date.month != last_month['month']:
                last_month = {'month':date.month, 'dates':[date], 'nr_dates':1}
                last_year['months'].append(last_month)
                last_year['nr_dates'] += 1
            else:
                last_month['dates'].append(date)
                last_month['nr_dates'] += 1
                last_year['nr_dates'] += 1

        return django.shortcuts.render_to_response(
            "booking/event.html", 
            {
                "event": e,
                "event_dates": ed,
                "event_booking": eb,
                "user": u,
                'static_url': settings.STATIC_URL,
                },
            context_instance=django.template.RequestContext(request))
