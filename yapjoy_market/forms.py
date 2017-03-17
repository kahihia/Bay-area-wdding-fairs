__author__ = 'Adeel'
from django import forms
from.models import *

class ProductForm(forms.ModelForm):
    amount = forms.IntegerField(required=True)
    class Meta:
        model = Product
        fields = ['title','description','end_date','category']
        widgets = {
                   'end_date': forms.DateInput(attrs={'class':'form-control endpicker', 'placeholder':'End Date'}),
                   'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Title'}),
                   'description': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Description', 'rows':3}),

               }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['category'].required = True

class PledgeForm(forms.ModelForm):
    amount = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Amount'}))
    class Meta:
        model = Pledge
        fields = ['message']
        widgets = {

                   'message': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Message', 'rows':5}),

               }

    def clean_amount(self):
        cleaned_data = super(PledgeForm, self).clean()
        amount = self.cleaned_data.get('amount')
        try:
            amount = int(amount)
        except:
            raise forms.ValidationError('Amount can only be integers.')
        return amount


class ProductBudgetForm(forms.ModelForm):
    class Meta:
        model = ProductBudget
        fields = ['title', 'budget']
        widgets = {
                   'title': forms.Textarea(attrs={'class':'form-control', 'placeholder':'title', 'rows':1}),
                   'budget': forms.Textarea(attrs={'class':'form-control', 'placeholder':'$0', 'rows':1}),
               }

class dreamImageForm(forms.Form):
    # picture = forms.URLField(widget=S3DirectWidget(dest='imgs'))
    image = forms.ImageField()
    # description = forms.Textarea()