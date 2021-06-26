from django import forms
from django.forms import ModelForm

from .models import Comment


class CommentForm(ModelForm):
    parent_comment_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ['content', 'username', 'qq']
        widgets = {
            'content': forms.Textarea(attrs={'rows': "4",  'tabindex': '1',  'id': 'comment'}),
            'username': forms.TextInput(attrs={'tabindex': '2', 'id': 'author', 'class': 'commenttext'}),
            'qq': forms.TextInput(attrs={'tabindex': '3', 'id': 'qq', 'class': 'commenttext'})
        }
