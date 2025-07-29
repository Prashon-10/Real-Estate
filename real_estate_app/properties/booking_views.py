import base64
import hashlib
import hmac
import json
import time
import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView

from .models import Property, PropertyBooking, BookingFee
from .booking_forms import PropertyBookingForm, BookingVerificationForm
from accounts.models import User


@login_required
def property_booking_view(request, property_id):
    """Handle property booking form and payment initiation"""
    property_obj = get_object_or_404(Property, id=property_id, status='available')
    
    # Get booking type from URL parameter
    booking_type = request.GET.get('type', 'booking')  # 'booking' or 'visit'
    
    if request.method == 'POST':
        form = PropertyBookingForm(request.POST, user=request.user, initial_booking_type=booking_type, current_property=property_obj)
        
        if form.is_valid():
            # Calculate payment amount
            payment_amount = form.get_payment_amount()
            
            # Store booking data in session
            booking_data = {
                'property_id': property_obj.id,
                'customer_name': form.cleaned_data['customer_name'],
                'customer_email': form.cleaned_data['customer_email'],
                'customer_phone': form.cleaned_data['customer_phone'],
                'booking_type': form.cleaned_data['booking_type'],
                'preferred_date': form.cleaned_data.get('preferred_date').isoformat() if form.cleaned_data.get('preferred_date') else None,
                'message': form.cleaned_data.get('message', ''),
                'payment_method': form.cleaned_data['payment_method'],
                'payment_amount': payment_amount,
            }
            
            request.session['booking_data'] = booking_data
            
            # Redirect to payment based on method
            if form.cleaned_data['payment_method'] == 'stripe':
                return redirect('properties:stripe_payment')
            else:
                return redirect('properties:esewa_payment')
    else:
        form = PropertyBookingForm(user=request.user, initial_booking_type=booking_type, current_property=property_obj)
    
    # Get current fees for display
    fees = BookingFee.get_current_fees()
    
    # Get blocked visit dates for this property (dates already taken by other users)
    blocked_dates = list(
        PropertyBooking.objects.filter(
            property_ref=property_obj,
            booking_type='visit',
            status__in=['pending', 'confirmed'],
            preferred_date__isnull=False
        ).values_list('preferred_date', flat=True)
    )
    
    # Convert datetime objects to date strings for JavaScript
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    blocked_dates_json = json.dumps(
        [date.strftime('%Y-%m-%d') for date in blocked_dates if date],
        cls=DjangoJSONEncoder
    )
    
    # Get user's existing visit dates across ALL properties for conflict checking
    user_visit_dates = []
    if request.user.is_authenticated:
        user_visits = PropertyBooking.objects.filter(
            customer=request.user,
            booking_type='visit',
            status__in=['pending', 'confirmed'],
            preferred_date__isnull=False
        ).exclude(property_ref=property_obj)  # Exclude current property
        
        user_visit_dates = [
            {
                'date': visit.preferred_date.strftime('%Y-%m-%d'),
                'time': visit.preferred_date.strftime('%I:%M %p'),
                'property': visit.property_ref.title
            }
            for visit in user_visits
        ]
    
    user_visit_dates_json = json.dumps(user_visit_dates, cls=DjangoJSONEncoder)
    
    context = {
        'form': form,
        'property': property_obj,
        'fees': fees,
        'booking_type': booking_type,
        'blocked_visit_dates': blocked_dates_json,
        'user_visit_dates': user_visit_dates_json,
    }
    return render(request, 'properties/booking_form.html', context)


@login_required
def stripe_payment_view(request):
    """Handle Stripe payment processing"""
    booking_data = request.session.get('booking_data')
    if not booking_data:
        messages.error(request, 'No booking data found. Please start the booking process again.')
        return redirect('properties:property_list')
    
    property_obj = get_object_or_404(Property, id=booking_data['property_id'])
    
    if request.method == 'POST':
        # Demo mode - simulate successful payment
        if getattr(settings, 'PAYMENT_DEMO_MODE', False):
            # Create booking with demo payment
            transaction_id = f"stripe_demo_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            booking = create_demo_booking(
                request.user, 
                booking_data, 
                'stripe', 
                transaction_id
            )
            
            # Clear session data
            del request.session['booking_data']
            
            messages.success(request, 'Stripe payment successful! Your booking is now pending verification.')
            return redirect('properties:booking_detail', booking_id=booking.id)
        else:
            # Real Stripe payment processing would go here
            try:
                # This would integrate with actual Stripe API
                payment_intent_data = {
                    'amount': int(float(booking_data['payment_amount']) * 100),  # Convert to cents
                    'currency': 'npr',
                    'metadata': {
                        'property_id': booking_data['property_id'],
                        'customer_email': booking_data['customer_email'],
                        'booking_type': booking_data['booking_type']
                    }
                }
                
                return JsonResponse({
                    'client_secret': 'demo_client_secret',
                    'public_key': settings.STRIPE_PUBLISHABLE_KEY
                })
                
            except Exception as e:
                return JsonResponse({
                    'error': f'Payment processing failed: {str(e)}'
                }, status=400)
    
    context = {
        'booking_data': booking_data,
        'property': property_obj,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''),
        'demo_mode': getattr(settings, 'PAYMENT_DEMO_MODE', False),
    }
    return render(request, 'properties/stripe_payment.html', context)


@login_required  
def esewa_payment_view(request):
    """Handle eSewa payment processing"""
    booking_data = request.session.get('booking_data')
    if not booking_data:
        messages.error(request, 'No booking data found. Please start the booking process again.')
        return redirect('properties:property_list')
    
    property_obj = get_object_or_404(Property, id=booking_data['property_id'])
    
    if request.method == 'POST':
        # Demo mode - simulate successful payment
        if getattr(settings, 'PAYMENT_DEMO_MODE', False):
            # Create booking with demo payment
            transaction_id = f"esewa_demo_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            booking = create_demo_booking(
                request.user, 
                booking_data, 
                'esewa', 
                transaction_id
            )
            
            # Clear session data
            del request.session['booking_data']
            
            messages.success(request, 'eSewa payment successful! Your booking is now pending verification.')
            return redirect('properties:booking_detail', booking_id=booking.id)
    
    # Generate eSewa payment parameters
    transaction_uuid = str(uuid.uuid4())
    amount = booking_data['payment_amount']
    
    # Create signature for eSewa
    message = f"total_amount={amount},transaction_uuid={transaction_uuid},product_code={settings.ESEWA_MERCHANT_ID}"
    signature = base64.b64encode(
        hmac.new(
            settings.ESEWA_SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
    ).decode()
    
    context = {
        'booking_data': booking_data,
        'property': property_obj,
        'amount': amount,
        'transaction_uuid': transaction_uuid,
        'merchant_id': settings.ESEWA_MERCHANT_ID,
        'signature': signature,
        'success_url': settings.ESEWA_SUCCESS_URL,
        'failure_url': settings.ESEWA_FAILURE_URL,
        'demo_mode': getattr(settings, 'PAYMENT_DEMO_MODE', False),
    }
    return render(request, 'properties/esewa_payment.html', context)


def create_demo_booking(user, booking_data, payment_method, transaction_id):
    """Create a booking with demo payment data"""
    property_obj = get_object_or_404(Property, id=booking_data['property_id'])
    
    booking = PropertyBooking(
        property_ref=property_obj,
        customer=user,
        customer_name=booking_data['customer_name'],
        customer_email=booking_data['customer_email'],
        customer_phone=booking_data['customer_phone'],
        booking_type=booking_data['booking_type'],
        message=booking_data.get('message', ''),
        payment_method=payment_method,
        transaction_id=transaction_id,
        payment_amount=Decimal(str(booking_data['payment_amount'])),
        payment_status='completed',
        payment_data={'demo': True, 'payment_method': payment_method}
    )
    
    # Set preferred date if it exists
    if booking_data.get('preferred_date'):
        from django.utils.dateparse import parse_datetime
        booking.preferred_date = parse_datetime(booking_data['preferred_date'])
    
    booking.save()
    return booking


@login_required
def esewa_success_view(request):
    """Handle eSewa payment success callback"""
    transaction_id = request.GET.get('oid')
    amount = request.GET.get('amt')
    ref_id = request.GET.get('refId')
    
    if transaction_id:
        try:
            booking = PropertyBooking.objects.get(transaction_id=transaction_id)
            booking.payment_status = 'completed'
            booking.payment_data = {
                'esewa_ref_id': ref_id,
                'amount': amount,
                'success': True
            }
            booking.save()
            
            messages.success(request, 'Payment successful! Your booking is now pending verification.')
            return redirect('properties:booking_detail', booking_id=booking.id)
        except PropertyBooking.DoesNotExist:
            messages.error(request, 'Booking not found.')
    else:
        messages.error(request, 'Invalid payment response.')
    
    return redirect('properties:property_list')


@login_required
def esewa_failure_view(request):
    """Handle eSewa payment failure callback"""
    messages.error(request, 'Payment failed or was cancelled. Please try again.')
    return redirect('properties:property_list')


class MyBookingsView(LoginRequiredMixin, ListView):
    model = PropertyBooking
    template_name = 'properties/my_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        return PropertyBooking.objects.filter(
            customer=self.request.user
        ).select_related('property_ref').order_by('-created_at')


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = PropertyBooking
    template_name = 'properties/booking_detail.html'
    context_object_name = 'booking'
    pk_url_kwarg = 'booking_id'
    
    def get_object(self, queryset=None):
        booking = super().get_object(queryset)
        # Ensure user can only view their own bookings (unless staff)
        if not self.request.user.is_staff and booking.customer != self.request.user:
            raise PermissionDenied
        return booking


class AgentBookingsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Agent view to manage bookings for their properties"""
    model = PropertyBooking
    template_name = 'properties/agent_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_agent
    
    def get_queryset(self):
        # Get bookings only for properties owned by this agent
        queryset = PropertyBooking.objects.filter(
            property_ref__agent=self.request.user
        ).select_related(
            'property_ref', 'customer', 'verified_by'
        ).order_by('-created_at')
        
        # Filter by status if provided
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by booking type if provided
        type_filter = self.request.GET.get('booking_type')
        if type_filter:
            queryset = queryset.filter(booking_type=type_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add statistics for agent's properties
        agent_bookings = PropertyBooking.objects.filter(property_ref__agent=self.request.user)
        context['stats'] = {
            'total_bookings': agent_bookings.count(),
            'pending_bookings': agent_bookings.filter(status='pending').count(),
            'confirmed_bookings': agent_bookings.filter(status='confirmed').count(),
            'rejected_bookings': agent_bookings.filter(status='rejected').count(),
        }
        
        # Add filters
        context['current_status'] = self.request.GET.get('status', '')
        context['current_booking_type'] = self.request.GET.get('booking_type', '')
        
        return context


class AdminBookingsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = PropertyBooking
    template_name = 'properties/admin_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = PropertyBooking.objects.select_related(
            'property_ref', 'customer', 'verified_by'
        ).order_by('-created_at')
        
        # Filter by status if provided
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by payment method if provided
        payment_filter = self.request.GET.get('payment_method')
        if payment_filter:
            queryset = queryset.filter(payment_method=payment_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add statistics
        context['stats'] = {
            'total_bookings': PropertyBooking.objects.count(),
            'pending_bookings': PropertyBooking.objects.filter(status='pending').count(),
            'confirmed_bookings': PropertyBooking.objects.filter(status='confirmed').count(),
            'rejected_bookings': PropertyBooking.objects.filter(status='rejected').count(),
        }
        
        # Add filters
        context['current_status'] = self.request.GET.get('status', '')
        context['current_payment_method'] = self.request.GET.get('payment_method', '')
        
        return context


class VerifyBookingView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = PropertyBooking
    template_name = 'properties/verify_booking.html'
    context_object_name = 'booking'
    pk_url_kwarg = 'booking_id'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def post(self, request, *args, **kwargs):
        booking = self.get_object()
        form = BookingVerificationForm(request.POST, instance=booking)
        
        if form.is_valid():
            booking = form.save(commit=False)
            booking.verified_by = request.user
            
            if booking.status in ['confirmed', 'rejected']:
                from django.utils import timezone
                booking.verified_at = timezone.now()
            
            booking.save()
            
            action = 'confirmed' if booking.status == 'confirmed' else 'rejected'
            messages.success(request, f'Booking has been {action} successfully.')
            
            return redirect('properties:admin_bookings')
        
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BookingVerificationForm(instance=self.get_object())
        return context


@login_required
def update_booking_status(request, booking_id):
    """Update booking status - accessible by both Admin and Agent"""
    booking = get_object_or_404(PropertyBooking, id=booking_id)
    
    # Permission check: Admin can update any booking, Agent can only update their property bookings
    if not request.user.is_staff and booking.property_ref.agent != request.user:
        raise PermissionDenied("You don't have permission to update this booking.")
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        
        if new_status in dict(PropertyBooking.STATUS_CHOICES):
            old_status = booking.status
            booking.status = new_status
            booking.admin_notes = admin_notes
            booking.verified_by = request.user
            
            if new_status in ['confirmed', 'rejected']:
                from django.utils import timezone
                booking.verified_at = timezone.now()
            
            booking.save()
            
            # Return JSON response for AJAX calls
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Booking status updated from {old_status} to {new_status}',
                    'new_status': new_status,
                    'new_status_display': booking.get_status_display(),
                    'verified_by': request.user.get_full_name() or request.user.email,
                    'verified_at': booking.verified_at.strftime('%Y-%m-%d %H:%M:%S') if booking.verified_at else None
                })
            else:
                messages.success(request, f'Booking status updated to {booking.get_status_display()}')
                
                # Redirect based on user type
                if request.user.is_staff:
                    return redirect('properties:admin_bookings')
                else:
                    return redirect('properties:agent_bookings')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Invalid status'})
            else:
                messages.error(request, 'Invalid status provided')
    
    # For GET requests or invalid POST, redirect back
    if request.user.is_staff:
        return redirect('properties:admin_bookings')
    else:
        return redirect('properties:agent_bookings')


@csrf_exempt
@require_POST
def stripe_webhook_view(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        # In a real implementation, you would verify the webhook signature
        # and process the event data
        
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=400)
