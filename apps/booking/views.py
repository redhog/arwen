# -*- coding: utf-8 -*-

import django.shortcuts
import django.contrib.auth.decorators
import django.contrib.auth.models
import django.template
import booking.models
import booking.forms
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
import django.contrib.messages
import django.http
import django.core.urlresolvers
from django.utils.translation import ugettext_lazy as _

_has_openid = pinax.apps.account.utils.has_openid
def has_openid(request):
    if request.user.is_anonymous():
        return False
    return _has_openid(request)
pinax.apps.account.utils.has_openid = has_openid

def event(request, slug):
    events = booking.models.Event.objects.all()

    if slug is not None:
        u = request.user
        es = events.filter(slug = slug)

        if es:
            return edit_event(request, es[0])
        else:
            return add_event(request, slug)
    else:
        return list_events(request, events)

def list_events(request, events):
    return django.shortcuts.render_to_response("booking/event_list.html", {
        "events": events,
        "user": request.user,
    }, context_instance=django.template.RequestContext(request))

def remove_event_date(request, slug, date_id):
    events = booking.models.Event.objects.all()

    e = events.get(slug = slug)
    u = request.user
    assert e.owner.id == u.id

    for date in e.dates.filter(id = date_id):
        date.delete()
    
    redirect_to = django.core.urlresolvers.reverse("booking_event", kwargs = {"slug":e.slug})
            
    return django.http.HttpResponseRedirect(redirect_to)

def edit_event(request, e):
    u = request.user
    if request.method == "POST":
        form = booking.forms.EditEventForm(u, request.POST, instance=e)
        if e.owner.id == u.id and form.is_valid():
            e = form.save()
            if form.cleaned_data['add_date']:
                if not e.dates.filter(date = form.cleaned_data['add_date']).count():
                    booking.models.EventDate(date=form.cleaned_data['add_date'], event=e).save()

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

        try:
            i = u.info
        except u.DoesNotExist:
            i = None
        if i:
            i.phone = phone
            i.save()
        else:
            account.models.UserInfo(user = u, phone = phone).save()

        try:
            event_booking = u.event_bookings.get(event__id = e.id)
        except:
            event_booking = booking.models.EventBooking(booker=u, event=e)
        event_booking.save()

        for date in event_booking.dates.all():
            date.delete()

        for date in dates:
            d = e.dates.get(date=date)
            booking.models.EventDateBooking(event_booking = event_booking, date=d).save()

        return django.http.HttpResponseRedirect(django.core.urlresolvers.reverse("booking_event", kwargs = {"slug":e.slug}))
    else:
        form = booking.forms.EditEventForm(u, instance=e)

    return django.shortcuts.render_to_response(
        "booking/event.html", 
        {
            "event": e,
            "user": u,
            'static_url': settings.STATIC_URL,
            "form": form,
            },
        context_instance=django.template.RequestContext(request))


def add_event(request, slug):
    if request.method == "POST":
        if request.user.is_authenticated():
            form = booking.forms.EventForm(request.user, request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.owner = request.user
                event.save()
                django.contrib.messages.add_message(request, django.contrib.messages.SUCCESS,
                                                    _("added event '%s'") % event.name)
                return django.http.HttpResponseRedirect(django.core.urlresolvers.reverse("booking_event", kwargs = {"slug":event.slug}))
    form = booking.forms.EventForm(request.user)    
    return django.shortcuts.render_to_response("booking/event_add.html", {"form": form}, context_instance=django.template.RequestContext(request))


