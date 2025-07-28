from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from .models import User
from .utils import validate_email_domain

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Please use a valid email address from a recognized provider (Gmail, Yahoo, Outlook, etc.). You can login immediately after registration."
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'profile_image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all fields have proper styling
        for field_name, field in self.fields.items():
            if field_name != 'profile_image':
                field.widget.attrs.update({'class': 'form-control'})
        
        # Make email and names required
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Validate domain
            validate_email_domain(email)
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                raise ValidationError("An account with this email address already exists.")
        
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'customer'
        user.email = self.cleaned_data['email']
        user.is_active = True  # Account active immediately with valid email domain
        
        if commit:
            user.save()
        return user

class AgentRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Please use a valid email address from a recognized provider (Gmail, Yahoo, Outlook, etc.). You can login immediately after registration."
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'phone_number', 'bio', 'profile_image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all fields have proper styling
        for field_name, field in self.fields.items():
            if field_name != 'profile_image':
                field.widget.attrs.update({'class': 'form-control'})
        
        # Make required fields
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['phone_number'].required = True
        self.fields['bio'].required = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Validate domain
            validate_email_domain(email)
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                raise ValidationError("An account with this email address already exists.")
        
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'agent'
        user.email = self.cleaned_data['email']
        user.is_active = True  # Account active immediately with valid email domain
        
        if commit:
            user.save()
        return user

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class KeyBasedPasswordResetForm(forms.Form):
    unique_key = forms.CharField(max_length=9, required=True)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'bio', 'profile_image']