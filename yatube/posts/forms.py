from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    '''Форма для создания поста.'''
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Введите текст поста',
            })
        }


class CommentForm(forms.ModelForm):
    '''Форма для создания комментария.'''
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Введите текст комментария',
                'rows': 3,
            })
        }
