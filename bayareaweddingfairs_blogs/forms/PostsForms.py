from django import forms
from django.contrib.auth.models import User
from bayareaweddingfairs_blogs.models import PostModel


class PostCreateForm(forms.ModelForm):

    class Meta:
        model = PostModel
        fields = ('title', 'text')
