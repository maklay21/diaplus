from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Product


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя пользователя',
            'autofocus': True
        })
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'manufacturer', 'product_type', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.Select(attrs={'class': 'form-select', 'style': 'flex: 1;'}),
            'product_type': forms.Select(attrs={'class': 'form-select', 'style': 'flex: 1;'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg, image/png'})
        }
        labels = {
            'name': 'Наименование товара',
            'manufacturer': 'Производитель',
            'product_type': 'Вид товара',
            'description': 'Описание товара',
            'image': 'Фото товара'
        }