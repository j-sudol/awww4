from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
        }
        help_texts = {
            'username': None,  # Remove the default help text for the username field
        }

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match")
        return password_confirm
    
class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if not username or not password:
            raise forms.ValidationError("Both fields are required")
        return self.cleaned_data


