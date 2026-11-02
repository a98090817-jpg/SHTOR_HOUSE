from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from PIL import Image

from .image_processing import normalize_product_image
from .models import Product, QuoteRequest


class EmailOrUsernameLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Email or username',
        widget=forms.TextInput(attrs={
            'placeholder': 'Email or username',
            'autocomplete': 'username',
            'autofocus': True,
        }),
    )

    def clean(self):
        identifier = self.cleaned_data.get('username')
        if identifier and '@' in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
            if user:
                self.cleaned_data['username'] = user.get_username()
        elif identifier:
            user = User.objects.filter(username__iexact=identifier).first()
            if user:
                self.cleaned_data['username'] = user.get_username()
        return super().clean()


class ProductForm(forms.ModelForm):
    image = forms.ImageField(
        required=True,
        label='Product image (file)',
        widget=forms.ClearableFileInput(attrs={
            'accept': '.jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp',
        }),
    )

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'color', 'material', 'length_meters', 'origin', 'price', 'description',
            'image', 'is_featured', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Luxury Curtain Name'}),
            'color': forms.TextInput(attrs={'placeholder': 'Ivory, Sand, Beige'}),
            'material': forms.TextInput(attrs={'placeholder': 'Silk, Linen, Cotton'}),
            'length_meters': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'placeholder': 'For example: 3.50'}),
            'origin': forms.TextInput(attrs={'placeholder': 'For example: Turkey, Uzbekistan'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe the product and benefits'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://example.com/image.jpg'}),
        }

    def clean_image(self):
        uploaded_image = self.cleaned_data.get('image')
        if not uploaded_image:
            return uploaded_image

        try:
            return normalize_product_image(uploaded_image)
        except (Image.DecompressionBombError, Image.UnidentifiedImageError, OSError, ValueError):
            raise ValidationError(
                'Upload a valid JPG, PNG, or WEBP image.',
                code='invalid_image',
            ) from None


class QuoteRequestForm(forms.ModelForm):
    phone = forms.CharField(
        validators=[RegexValidator(
            regex=r'^[0-9+()\-\s]+$',
            message='Please enter a valid phone number using digits only.',
        )],
        widget=forms.TextInput(attrs={
            'type': 'tel',
            'inputmode': 'numeric',
            'pattern': r'[0-9+()\-\s]+',
            'autocomplete': 'tel',
            'placeholder': '+998 90 123 45 67',
        }),
    )

    class Meta:
        model = QuoteRequest
        fields = ['full_name', 'phone', 'email', 'product', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about your room and preferred style'}),
        }


class CustomUserCreationForm(DjangoUserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
