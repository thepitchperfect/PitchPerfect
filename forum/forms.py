from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'post_type', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full rounded border border-[#ffd7aa] px-3 py-2'}),
            'post_type': forms.Select(attrs={'class': 'w-full rounded border border-[#ffd7aa] px-3 py-2'}),
            'content': forms.Textarea(attrs={'class': 'w-full rounded border border-[#ffd7aa] px-3 py-2', 'rows': 6})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if not (user and user.is_staff):
            self.fields['post_type'].choices = [
                ('discussion', 'Discussion')
            ]
            self.fields['post_type'].initial = 'discussion'