from django import forms
from .models import Comment, Product


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment_content',)


class SearchForm(forms.ModelForm):
    query = forms.CharField(max_length=100)

    class Meta:
        model = Product
        fields = '__all__'


# kbr:Form olusturuldu
class ContactForm(forms.Form):
    username = forms.CharField(required=True)
    from_email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
