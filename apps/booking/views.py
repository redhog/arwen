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
import pinax.apps.account.utils
import account.models

_has_openid = pinax.apps.account.utils.has_openid
def has_openid(request):
    if request.user.is_anonymous():
        return False
    return _has_openid(request)
pinax.apps.account.utils.has_openid = has_openid

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
            username = request.POST['username'].lower()
            email = request.POST['email'].lower()
            phone = request.POST['phone']
            dates = [datetime.datetime(*[int(x) for x in day.split("-")]) for day in request.POST.getlist("days")]

            if u.is_anonymous():
                u = django.contrib.auth.models.User(username=username, email=email)
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

            u.email = email
            u.username = username

            u.save()

            i = u.info
            if i:
                i.phone = phone
                i.save()
            else:
                account.models.UserInfo(user = u, phone = phone).save()

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
