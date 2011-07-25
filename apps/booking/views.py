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

def group_and_bridge(request):
    """
    Given the request we can depend on the GroupMiddleware to provide the
    group and bridge.
    """
    
    # be group aware
    group = getattr(request, "group", None)
    if group:
        bridge = request.bridge
    else:
        bridge = None
    
    return group, bridge

def group_context(group, bridge):
    # @@@ use bridge
    ctx = {
        "group": group,
    }
    if group:
        ctx["group_base"] = bridge.group_base_template()
    return ctx

def group_is_member(request, group):
    if not request.user.is_authenticated():
        return False
    else:
        if group:
            return group.user_is_member(request.user)
        else:
            return True


def event(request, event_id = None):
    group, bridge = group_and_bridge(request)
    is_member = group_is_member(request, group)

    if group:
        events = group.content_objects(booking.models.Event)
    else:
        events = booking.models.Event.objects.all()

    if event_id is not None:
        e = events.get(id = event_id)

        u = request.user

        if request.method == "POST":
            form = booking.forms.EventForm(request.user, group, request.POST, instance=e)
            if form.is_valid():
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
                event_booking = u.event_bookings.get(event__id = event_id)
            except:
                event_booking = booking.models.EventBooking(booker=u, event=e)
            event_booking.save()

            for date in event_booking.dates.all():
                date.delete()

            for date in dates:
                d = e.dates.get(date=date)
                booking.models.EventDateBooking(event_booking = event_booking, date=d).save()

        else:
            form =booking.forms.EventForm(request.user, group, instance=e)

        return django.shortcuts.render_to_response(
            "booking/event.html", 
            {
                "event": e,
                "user": u,
                "group": group,
                "is_member": is_member,
                'static_url': settings.STATIC_URL,
                "form": form,
                },
            context_instance=django.template.RequestContext(request))

            
    else:
        return django.shortcuts.render_to_response("booking/event_list.html", {
            "group": group,
            "events": events,
            "user": request.user,
            "is_member": is_member,
        }, context_instance=django.template.RequestContext(request))

def remove_event_date(request, event_id, date_id):
    group, bridge = group_and_bridge(request)

    is_member = group_is_member(request, group)

    if group:
        events = group.content_objects(booking.models.Event)
    else:
        events = booking.models.Event.objects.all()

    e = events.get(id = event_id)
    u = request.user
    assert e.owner.id == u.id

    for date in e.dates.filter(id = date_id):
        date.delete()
    
    kwarg = {"event_id":e.id}
    if group:
        redirect_to = bridge.reverse("booking_event", group, kwarg)
    else:
        redirect_to = django.core.urlresolvers.reverse("booking_event", kwarg)
            
    return django.http.HttpResponseRedirect(redirect_to)


def add_event(request):
    group, bridge = group_and_bridge(request)
    is_member = group_is_member(request, group)

    if request.method == "POST":
        if request.user.is_authenticated():
            form = booking.forms.EventForm(request.user, group, request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.group = group
                event.owner = request.user
                event.save()
                django.contrib.messages.add_message(request, django.contrib.messages.SUCCESS,
                                                    _("added event '%s'") % event.name
                                                    )
                kwarg = {"event_id":event.id}
                if group:
                    redirect_to = bridge.reverse("booking_event", group, kwarg)
                else:
                    redirect_to = django.core.urlresolvers.reverse("booking_event", kwarg)

                return django.http.HttpResponseRedirect(redirect_to)


    form = booking.forms.EventForm(request.user, group)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "is_member": is_member,
        "form": form,
    })
    
    return django.shortcuts.render_to_response("booking/event_add.html", django.template.RequestContext(request, ctx))


