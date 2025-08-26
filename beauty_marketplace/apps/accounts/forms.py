from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile, UserKYC


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "phone", "user_type", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        user.user_type = self.cleaned_data["user_type"]
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['display_name', 'bio']


class KYCForm(forms.ModelForm):
    class Meta:
        model = UserKYC
        fields = ['id_document_url', 'selfie_url']
        widgets = {
            'id_document_url': forms.URLInput(attrs={'class': 'form-control'}),
            'selfie_url': forms.URLInput(attrs={'class': 'form-control'}),
        }


class AgeVerificationForm(forms.Form):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Please enter your date of birth to verify your age."
    )
