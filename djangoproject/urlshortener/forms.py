from django.forms import ModelForm, URLField, HiddenInput, TextInput, URLInput
from urlshortener.models import URLs

class URLsFormPartial(ModelForm):
    class Meta:
        model = URLs
        fields = ['long_url', 'short_url']
        widgets = {'short_url': HiddenInput(), 'long_url':URLInput(attrs={'placeholder':'Paste URL you would like to shorten', 'autofocus':'autofocus'})}



class URLsForm(ModelForm):
    class Meta:
        model = URLs
        fields = ['long_url', 'short_url']
        widgets = {'short_url': TextInput(attrs={'readonly':'readonly'}),'long_url': TextInput(attrs={'readonly':'readonly'})}
