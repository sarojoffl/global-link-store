import os

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Address, UserProfile


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username':   forms.TextInput(attrs={'placeholder': 'Username'}),
            'email':      forms.EmailInput(attrs={'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name':  forms.TextInput(attrs={'placeholder': 'Last Name'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")

        if p1:
            try:
                validate_password(p1)
            except ValidationError as e:
                self.add_error('password1', e)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name  = forms.CharField(max_length=150, required=False)
    email      = forms.EmailField(required=True)
    phone      = forms.CharField(max_length=20, required=False, label="Phone number")
    photo      = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={"accept": "image/*"}))

    class Meta:
        model  = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, instance=user, **kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        self.fields["phone"].initial = profile.phone
        self.fields["photo"].initial = profile.photo
        self._profile = profile
        for name in ("first_name", "last_name", "email", "phone"):
            if name in self.fields:
                self.fields[name].widget.attrs.setdefault("class", "shop-input")

    def save(self, commit=True):
        user = super().save(commit=commit)
        self._profile.phone = self.cleaned_data.get("phone", "")

        # Handle photo upload / clear
        photo = self.cleaned_data.get("photo")
        clear = self.data.get("photo-clear")
        if clear:
            if self._profile.photo and os.path.isfile(self._profile.photo.path):
                os.remove(self._profile.photo.path)
            self._profile.photo = None
        elif photo:
            self._profile.photo = photo

        self._profile.save()
        return user


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "label",
            "full_name",
            "phone",
            "street",
            "city",
            "province",
            "postal_code",
            "is_default",
        ]
        widgets = {
            "label": forms.TextInput(attrs={"placeholder": "Home, Office, etc."}),
            "full_name": forms.TextInput(attrs={"placeholder": "Full name"}),
            "phone": forms.TextInput(attrs={"placeholder": "+977-98XXXXXXXX"}),
            "street": forms.TextInput(attrs={"placeholder": "Street address"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "province": forms.TextInput(attrs={"placeholder": "Province / State"}),
            "postal_code": forms.TextInput(attrs={"placeholder": "Postal code"}),
        }
