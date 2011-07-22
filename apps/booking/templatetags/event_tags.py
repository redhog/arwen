import django.template
import booking.models
import django.template

register = django.template.Library()

@register.filter
def event_get_date(value, date):
     res = list(value.filter(date=date.id))
     if res:
         return res[0]
     return None

@register.filter
def event_get_booking(value, user):
     if not user.is_anonymous():
          bookings = list(user.event_bookings.filter(event__id = value.id))
          if bookings:
               return bookings[0]
     return None
