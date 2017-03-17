from django import forms
from functools import partial


class TasksForm(forms.Form):
    subject = forms.CharField(max_length=225, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Create your custom task'}),
                              required=True, error_messages={'required': 'Subject is required.'})

    due = forms.DateField(required=True, error_messages={'required': 'Due Date is required.','class': 'form-control','placeholder':'Due Date'})

    notes = forms.CharField(max_length=255, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Notes','rows':3}),
                                   required=False, error_messages={'required': 'Please leave task notes.'}, )

    complete = forms.BooleanField(required=False, error_messages={'required': 'Please select Complete or not'})

    #assignee = forms.ModelMultipleChoiceField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=True, error_messages={'required': 'Please choose assignees.'})