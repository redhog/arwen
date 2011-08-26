import django.forms
import booking.models
import datetime

class EventForm(django.forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EventForm, self).__init__(*args, **kwargs)

    class Meta:
        model = booking.models.Event
        exclude = ["owner"]
    
    def clean(self):
        return self.cleaned_data

class EditEventForm(EventForm):
    add_date = django.forms.DateField(required=False)
