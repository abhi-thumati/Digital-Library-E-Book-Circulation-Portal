from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'role', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control bg-dark text-white border-secondary'
            if field_name == 'role':
                field.widget.attrs['class'] = 'form-select bg-dark text-white border-secondary'


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'first_name', 'last_name', 'phone', 'address', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control bg-dark text-white border-secondary'
            if field_name == 'role':
                field.widget.attrs['class'] = 'form-select bg-dark text-white border-secondary'


class CustomUserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, help_text="Required.")
    last_name = forms.CharField(max_length=150, required=True, help_text="Required.")
    email = forms.EmailField(required=True, help_text="Required.")
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'phone', 'address', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply styling to all fields
        for field_name, field in self.fields.items():
            if field_name == 'profile_picture':
                field.widget.attrs['class'] = 'form-control bg-dark text-white border-secondary'
            elif field_name == 'address':
                field.widget.attrs['class'] = 'form-control bg-dark text-white border-secondary'
                field.widget.attrs['rows'] = '3'
            elif field_name in ('password1', 'password2'):
                field.widget.attrs['class'] = 'form-control bg-dark text-white border-secondary'
            else:
                field.widget.attrs['class'] = 'form-control bg-dark text-white border-secondary'


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'address', 'profile_picture')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'profile_picture':
                field.widget.attrs['class'] = 'form-control bg-dark text-white border-secondary'
            else:
                field.widget.attrs['class'] = 'form-control bg-dark text-white border-secondary'
