from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'phone_number']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Введите email'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+995 ...'}),
        }