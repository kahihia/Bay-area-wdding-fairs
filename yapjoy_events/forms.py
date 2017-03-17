from django import forms


class EventsForm(forms.Form):
    subject = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control', }),
                              required=True, error_messages={'required': 'Name is required.'})

    start = forms.DateTimeField(required=True,widget=forms.TextInput(attrs={'class': 'form-control hasDatepicker',}), error_messages={'required': 'Start time is required.'})

    end = forms.DateTimeField(required=True,widget=forms.TextInput(attrs={'class': 'form-control hasDatepicker', }), error_messages={'required': 'End time is required.'})

    all_day = forms.BooleanField(required=False)

    #include_friends = forms.ModelMultipleChoiceField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)