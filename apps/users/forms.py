from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationForm(UserCreationForm):
    """Extends Django's built-in UserCreationForm with a required email field."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()  # UserProfile is created automatically via signal.
        return user


class ProfileEditForm(forms.ModelForm):
    """Lets a user edit their own profile fields."""

    class Meta:
        model = User
        fields = ['bio', 'avatar', 'location']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell your story...'}),
            'location': forms.TextInput(attrs={'placeholder': 'City, Country'}),
        }
