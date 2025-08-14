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
    
    additional_properties = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        help_text="Comma-separated list of additional property IDs for multi-property visits (no additional fees)"
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="You must accept the terms and conditions to proceed"
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
        
        # Check if user has already booked this exact property
        if preferred_date and hasattr(self, 'user') and self.user and hasattr(self, 'current_property'):
            from .models import PropertyBooking
            
            existing_booking = PropertyBooking.objects.filter(
                customer=self.user,
                property_ref=self.current_property,
                status__in=['pending', 'confirmed', 'cancelled']  # Include all non-rejected bookings
            ).first()
            
            if existing_booking:
                if existing_booking.status == 'cancelled':
                    raise forms.ValidationError(
                        f"You previously cancelled a booking for this property on {existing_booking.preferred_date.strftime('%Y-%m-%d at %H:%M')}. "
                        f"Please contact support if you want to rebook this property."
                    )
                else:
                    raise forms.ValidationError(
                        f"You have already booked this property on {existing_booking.preferred_date.strftime('%Y-%m-%d at %H:%M')} (Status: {existing_booking.get_status_display()}). "
                        f"You cannot book the same property multiple times."
                    )
        
        # Check for conflicts with user's existing bookings on the same date
        # Allow same-date bookings only if properties are within 5km of each other
        if preferred_date and hasattr(self, 'user') and self.user and hasattr(self, 'current_property'):
            from .utils import check_booking_distance_compatibility
            
            is_compatible, error_message, conflicting_bookings = check_booking_distance_compatibility(
                self.user, 
                self.current_property, 
                preferred_date
            )
            
            if not is_compatible:
                raise forms.ValidationError(error_message)
        
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
        """Calculate payment amount based on booking type and user's previous bookings with the same agent"""
        booking_type = self.cleaned_data.get('booking_type', 'booking')
        preferred_date = self.cleaned_data.get('preferred_date')
        
        return self._calculate_payment_amount(booking_type, preferred_date)
    
    def get_initial_payment_amount(self, booking_type='visit'):
        """Calculate payment amount for initial display (before form submission)"""
        return self._calculate_payment_amount(booking_type, None)
    
    def _calculate_payment_amount(self, booking_type='visit', preferred_date=None):
        """Internal method to calculate payment amount"""
        # Base amount is Rs. 500 for first-time bookings
        base_amount = 500.00
        
        # Check if user has previous bookings with this agent on different dates
        if (hasattr(self, 'user') and self.user and self.user.is_authenticated and 
            hasattr(self, 'current_property') and self.current_property):
            
            from .models import PropertyBooking
            from django.db.models import Q
            
            # Get previous bookings with the same agent
            query = PropertyBooking.objects.filter(
                customer=self.user,
                property_ref__agent=self.current_property.agent,
                status__in=['pending', 'confirmed'],
                preferred_date__isnull=False
            )
            
            # If we have a preferred_date, exclude same-date bookings
            if preferred_date:
                query = query.exclude(preferred_date__date=preferred_date.date())
            
            previous_bookings = query
            
            # If user has previous bookings with this agent on different dates, charge Rs. 250
            if previous_bookings.exists():
                base_amount = 250.00
        
        # No additional fees for multiple properties on the same date
        return base_amount
    
    def get_additional_property_objects(self):
        """Get Property objects for additional properties"""
        from .models import Property
        
        additional_properties = self.cleaned_data.get('additional_properties', '')
        if not additional_properties:
            return []
        
        property_ids = [int(pid.strip()) for pid in additional_properties.split(',') if pid.strip().isdigit()]
        return Property.objects.filter(id__in=property_ids)
    
    def clean_additional_properties(self):
        """Validate additional properties for existing bookings"""
        additional_properties = self.cleaned_data.get('additional_properties', '')
        
        if not additional_properties or not hasattr(self, 'user') or not self.user:
            return additional_properties
        
        property_ids = [int(pid.strip()) for pid in additional_properties.split(',') if pid.strip().isdigit()]
        
        if property_ids:
            from .models import Property, PropertyBooking
            
            # Check each additional property for existing bookings
            for property_id in property_ids:
                try:
                    property_obj = Property.objects.get(id=property_id)
                    
                    # Check if user has already booked this property
                    existing_booking = PropertyBooking.objects.filter(
                        customer=self.user,
                        property_ref=property_obj,
                        status__in=['pending', 'confirmed']
                    ).first()
                    
                    if existing_booking:
                        raise forms.ValidationError(
                            f"You have already booked '{property_obj.title}' on {existing_booking.preferred_date.strftime('%Y-%m-%d at %H:%M')} "
                            f"(Status: {existing_booking.get_status_display()}). "
                            f"Please remove this property from your selection as you cannot book the same property multiple times."
                        )
                        
                except Property.DoesNotExist:
                    continue  # Skip invalid property IDs
        
        return additional_properties


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
