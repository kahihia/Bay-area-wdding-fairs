from bayareaweddingfairs_blogs.models import CommentModel
from django import forms


class CommentFormAdd(forms.ModelForm):
    text = forms.CharField(max_length=120)
    class Meta:
        model = CommentModel
        fields = ['text']