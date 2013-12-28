from django import forms
from django.contrib.auth.models import User
from apps.manager.models import Translator, App, Language, String


class RegistrationForm(forms.ModelForm):

    first_name = forms.CharField(label=(u'First name'))
    last_name = forms.CharField(label=(u'Last name'))
    username = forms.CharField(label=(u'User name'))
    email = forms.EmailField(label=(u'Email address'))
    password = forms.CharField(label=(u'Password'),
                               widget=forms.PasswordInput(render_value=False))
    password_ver = forms.CharField(label=(u'Verify password'),
                                   widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = Translator
        exclude = ('user', 'words_translated')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('That username is already taken.')

    def clean(self):
        password = self.cleaned_data.get('password', None)
        password_ver = self.cleaned_data.get('password_ver', None)
        if password and password_ver and password != password_ver:
            raise forms.ValidationError('The passwords did not match.')
        return self.cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(label=(u'User name'), widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label=(u'Password'),
                               widget=forms.PasswordInput(render_value=False, attrs={'class': 'form-control'}))


class GenerateForm(forms.Form):
    app = forms.ModelChoiceField(queryset=App.objects.all())
    language = forms.ModelMultipleChoiceField(queryset=Language.objects.all(),
                                         widget=forms.CheckboxSelectMultiple())


class ModifyForm(forms.ModelForm):
    text = forms.CharField(label=(u'Translation'),
                           widget=forms.Textarea(attrs={'class': 'expand',
                                                        'rows': '1'}))

    class Meta:
        model = String
        fields = ('text',)


class TranslateForm(forms.ModelForm):
    translation = forms.CharField(label=(u'Translation'),
                                  widget=forms.Textarea(attrs={'class': 'expand',
                                                               'rows': '1'}),
                                  required=False)

    class Meta:
        model = String
        fields = ()
