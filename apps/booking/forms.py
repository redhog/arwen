import django.forms
import booking.models
import datetime

class EventForm(django.forms.ModelForm):
    def __init__(self, user, group, *args, **kwargs):
        self.user = user
        self.group = group
        
        super(EventForm, self).__init__(*args, **kwargs)

    add_date = django.forms.DateField(initial=datetime.date.today)
    
    class Meta:
        model = booking.models.Event
        fields = ["name", "description", "min_bookings", "ideal_bookings", "max_bookings", "add_date"]
    
    def clean(self):
        self.check_group_membership()
        return self.cleaned_data
    
    def check_group_membership(self):
        group = self.group
        if group and not self.group.user_is_member(self.user):
            raise django.forms.ValidationError("You must be a member to create events")

class EditEventForm(EventForm):
    add_date = django.forms.DateField()
    
    class Meta(EventForm.Meta):
        fields = EventForm.Meta.fields + ["add_date"]
