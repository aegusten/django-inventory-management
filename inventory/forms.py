# inventory/forms.py

from django import forms
from .models import (
    Product, Inbound, Outbound,
    User, ScheduledOutbound, Customer
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        return quantity

class InboundForm(forms.ModelForm):
    new_product_sku = forms.CharField(required=False)
    new_product_name = forms.CharField(required=False)
    new_category = forms.CharField(required=False)
    new_supplier = forms.CharField(required=False)
    new_location = forms.CharField(required=False)
    new_tags = forms.CharField(required=False)

    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Inbound
        fields = ['reference', 'date_received', 'product', 'quantity', 'remarks']
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'date_received': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        new_product_sku = cleaned_data.get('new_product_sku')
        new_product_name = cleaned_data.get('new_product_name')
        new_category = cleaned_data.get('new_category')
        new_supplier = cleaned_data.get('new_supplier')
        new_location = cleaned_data.get('new_location')

        if not product and not new_product_sku:
            raise forms.ValidationError('Either select an existing product or provide details for a new product.')

        if new_product_sku:
            required_fields = [new_product_name, new_category, new_supplier, new_location]
            if not all(required_fields):
                raise forms.ValidationError('For a new product, "Product Name", "Category", "Supplier", and "Location" are required fields.')

        return cleaned_data


class OutboundForm(forms.ModelForm):
    date_shipped = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Outbound
        fields = ['reference', 'date_shipped', 'product', 'quantity', 'destination', 'customer_name', 'category', 'remarks']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        product = self.cleaned_data.get('product')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        if product and quantity > product.available_quantity:
            raise forms.ValidationError(f"Not enough available stock. Available: {product.available_quantity}")
        return quantity
    
    
class ScheduledOutboundForm(forms.ModelForm):
    scheduled_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = ScheduledOutbound
        fields = ['customer', 'product', 'quantity', 'destination', 'scheduled_date', 'remarks']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role and self.request.user.role == 'Admin':
            raise forms.ValidationError("Role must be set by an Admin.")
        return role

    def __init__(self, *args, **kwargs):
        self.role = kwargs.pop('role', None)
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        if self.role:
            user.role = self.role
        if commit:
            user.save()
        return user
    
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'address', 'contact_person', 'contact_email', 'contact_phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        

class UserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']