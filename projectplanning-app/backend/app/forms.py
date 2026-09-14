from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    """Form de registro limitado a username (email), first_name y password."""
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    first_name = forms.CharField(label='Nombre', required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        # Guardamos el email también en user.email (username contiene el email)
        user.email = self.cleaned_data.get('username')
        user.first_name = self.cleaned_data.get('first_name', '')
        if commit:
            user.save()
        return user
