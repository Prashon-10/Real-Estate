from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import PropertyBooking, BookingFee


class PropertyBookingForm(forms.ModelForm):
    """Form for property booking with payment integration"""
    
    customer_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    
    customer_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    customer_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    
    booking_type = forms.ChoiceField(
        choices=PropertyBooking.BOOKING_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    preferred_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
        }),
        help_text="Select your preferred date and time for property visit (required for visit requests)"
    )
    
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Any specific requirements or message...'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=PropertyBooking.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial='stripe'
    )
    
    class Meta:
        model = PropertyBooking
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'booking_type', 'preferred_date', 'message', 'payment_method'
        ]
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.current_property = kwargs.pop('current_property', None)
        initial_booking_type = kwargs.pop('initial_booking_type', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill user data if authenticated
        if self.user and self.user.is_authenticated:
            if not self.initial.get('customer_name'):
                self.initial['customer_name'] = self.user.get_full_name() or self.user.username
            if not self.initial.get('customer_email'):
                self.initial['customer_email'] = self.user.email
        
        # Set initial booking type if provided
        if initial_booking_type and initial_booking_type in ['booking', 'visit']:
            self.initial['booking_type'] = initial_booking_type
                
        # Set minimum date for preferred_date
        min_date = (timezone.now() + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M')
        self.fields['preferred_date'].widget.attrs['min'] = min_date
    
    def clean_preferred_date(self):
        preferred_date = self.cleaned_data.get('preferred_date')
        booking_type = self.cleaned_data.get('booking_type')
        
        if booking_type == 'visit' and not preferred_date:
            raise forms.ValidationError("Preferred date is required for visit requests.")
        
        if preferred_date and preferred_date <= timezone.now():
            raise forms.ValidationError("Please select a future date and time.")
        
        # Check if the date is too far in future (e.g., 6 months)
        if preferred_date and preferred_date > timezone.now() + timedelta(days=180):
            raise forms.ValidationError("Please select a date within the next 6 months.")
        
        # Check for conflicts with user's existing visit requests on the same date
        if preferred_date and booking_type == 'visit' and hasattr(self, 'user') and self.user:
            # Check if user has already booked a visit on the same date for ANY property
            existing_visit_on_same_date = PropertyBooking.objects.filter(
                customer=self.user,
                booking_type='visit',
                status__in=['pending', 'confirmed'],
                preferred_date__date=preferred_date.date()  # Same date (ignoring time)
            ).exclude(
                property_ref=self.current_property  # Exclude current property
            ).first()
            
            if existing_visit_on_same_date:
                property_title = existing_visit_on_same_date.property_ref.title
                existing_time = existing_visit_on_same_date.preferred_date.strftime('%I:%M %p')
                raise forms.ValidationError(
                    f"You already have a visit scheduled for '{property_title}' on {preferred_date.strftime('%B %d, %Y')} at {existing_time}. "
                    f"Please select a different date as you cannot visit multiple properties on the same day."
                )
        
        return preferred_date
    
    def clean_customer_phone(self):
        phone = self.cleaned_data.get('customer_phone')
        # Basic phone validation - remove spaces and check length
        phone = phone.replace(' ', '').replace('-', '')
        if len(phone) < 10:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        booking_type = cleaned_data.get('booking_type')
        preferred_date = cleaned_data.get('preferred_date')
        
        # Additional validation for visit requests
        if booking_type == 'visit' and not preferred_date:
            raise forms.ValidationError("Preferred date and time is required for property visit requests.")
        
        return cleaned_data
    
    def get_payment_amount(self):
        """Calculate payment amount based on booking type"""
        booking_type = self.cleaned_data.get('booking_type', 'booking')
        fees = BookingFee.get_current_fees()
        
        if booking_type == 'visit':
            return float(fees['visit_fee'])
        else:
            return float(fees['booking_fee'])


class BookingVerificationForm(forms.ModelForm):
    """Form for admin to verify bookings"""
    
    status = forms.ChoiceField(
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirm Booking'),
            ('rejected', 'Reject Booking'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    admin_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add verification notes or rejection reason...'
        })
    )
    
    class Meta:
        model = PropertyBooking
        fields = ['status', 'admin_notes']


class BookingFeeForm(forms.ModelForm):
    """Form for managing booking fees"""
    
    booking_fee = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        help_text="Booking fee amount in NPR"
    )
    
    visit_fee = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        help_text="Visit request fee amount in NPR"
    )
    
    class Meta:
        model = BookingFee
        fields = ['booking_fee', 'visit_fee', 'is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
