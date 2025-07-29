import json
import uuid
import hashlib
import hmac
import base64
from decimal import Decimal
from datetime import datetime

import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Property, PropertyBooking, BookingFee
from .booking_forms import PropertyBookingForm, BookingVerificationForm

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def property_booking_view(request, property_id):
    """Display booking form for a property"""
    property_obj = get_object_or_404(Property, id=property_id, status='available')
    
    # Check if user already has a pending booking for this property
    existing_booking = PropertyBooking.objects.filter(
        property_ref=property_obj,
        customer=request.user,
        status='pending'
    ).first()
    
    if existing_booking:
        messages.warning(request, 'You already have a pending booking for this property.')
        return redirect('properties:booking_detail', booking_id=existing_booking.id)
    
    if request.method == 'POST':
        form = PropertyBookingForm(request.POST, property=property_obj, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.property_ref = property_obj
            booking.customer = request.user
            booking.payment_amount = form.get_payment_amount()
            
            # Generate unique transaction ID
            booking.transaction_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
            
            # Don't save yet - redirect to payment
            request.session['booking_data'] = {
                'property_id': property_obj.id,
                'customer_name': booking.customer_name,
                'customer_email': booking.customer_email,
                'customer_phone': booking.customer_phone,
                'booking_type': booking.booking_type,
                'preferred_date': booking.preferred_date.isoformat() if booking.preferred_date else None,
                'message': booking.message,
                'payment_method': booking.payment_method,
                'payment_amount': float(booking.payment_amount),
                'transaction_id': booking.transaction_id,
            }
            
            # Redirect to payment processing
            if booking.payment_method == 'stripe':
                return redirect('properties:stripe_payment')
            else:
                return redirect('properties:esewa_payment')
    else:
        form = PropertyBookingForm(property=property_obj, user=request.user)
    
    # Get current fees
    fees = BookingFee.get_current_fees()
    
    context = {
        'property': property_obj,
        'form': form,
        'fees': fees,
    }
    return render(request, 'properties/booking_form.html', context)


@login_required
def stripe_payment_view(request):
    """Handle Stripe payment processing"""
    booking_data = request.session.get('booking_data')
    if not booking_data:
        messages.error(request, 'Invalid booking session. Please try again.')
        return redirect('properties:property_list')
    
    property_obj = get_object_or_404(Property, id=booking_data['property_id'])
    
    if request.method == 'POST':
        try:
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(booking_data['payment_amount'] * 100),  # Stripe expects amount in cents
                currency='npr',
                metadata={
                    'property_id': property_obj.id,
                    'customer_id': request.user.id,
                    'booking_type': booking_data['booking_type'],
                    'transaction_id': booking_data['transaction_id'],
                }
            )
            
            return JsonResponse({
                'client_secret': intent.client_secret,
                'success': True
            })
            
        except stripe.error.StripeError as e:
            return JsonResponse({
                'error': str(e),
                'success': False
            })
    
    context = {
        'property': property_obj,
        'booking_data': booking_data,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'properties/stripe_payment.html', context)


@login_required
def esewa_payment_view(request):
    """Handle eSewa payment processing"""
    booking_data = request.session.get('booking_data')
    if not booking_data:
        messages.error(request, 'Invalid booking session. Please try again.')
        return redirect('properties:property_list')
    
    property_obj = get_object_or_404(Property, id=booking_data['property_id'])
    
    # eSewa payment parameters
    esewa_params = {
        'amt': booking_data['payment_amount'],
        'pcd': 'EPAYTEST',  # eSewa test merchant code
        'psc': '0',
        'txAmt': '0',
        'tAmt': booking_data['payment_amount'],
        'pid': booking_data['transaction_id'],
        'scd': settings.ESEWA_MERCHANT_ID,
        'su': settings.ESEWA_SUCCESS_URL,
        'fu': settings.ESEWA_FAILURE_URL,
    }
    
    context = {
        'property': property_obj,
        'booking_data': booking_data,
        'esewa_params': esewa_params,
        'esewa_url': 'https://uat.esewa.com.np/epay/main',  # Sandbox URL
    }
    return render(request, 'properties/esewa_payment.html', context)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET if hasattr(settings, 'STRIPE_WEBHOOK_SECRET') else None
    
    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        else:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
        # Save the booking
        try:
            create_booking_from_payment(payment_intent, 'stripe')
        except Exception as e:
            print(f"Error creating booking: {e}")
    
    return HttpResponse(status=200)


@login_required
def stripe_success(request):
    """Handle successful Stripe payment"""
    payment_intent_id = request.GET.get('payment_intent')
    
    if payment_intent_id:
        try:
            # Retrieve payment intent from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if payment_intent.status == 'succeeded':
                # Create booking
                booking = create_booking_from_payment(payment_intent, 'stripe')
                
                # Clear session data
                if 'booking_data' in request.session:
                    del request.session['booking_data']
                
                messages.success(request, 'Payment successful! Your booking is pending admin verification.')
                return redirect('properties:booking_detail', booking_id=booking.id)
        
        except stripe.error.StripeError as e:
            messages.error(request, f'Payment verification failed: {str(e)}')
    
    messages.error(request, 'Payment verification failed.')
    return redirect('properties:property_list')


@login_required
def esewa_success(request):
    """Handle successful eSewa payment"""
    # eSewa returns these parameters on success
    amt = request.GET.get('amt')
    rid = request.GET.get('rid')  # eSewa reference ID
    pid = request.GET.get('pid')  # Our transaction ID
    
    if pid and amt:
        booking_data = request.session.get('booking_data')
        if booking_data and booking_data['transaction_id'] == pid:
            # Create booking
            booking = create_booking_from_esewa_success(request.user, booking_data, rid)
            
            # Clear session data
            if 'booking_data' in request.session:
                del request.session['booking_data']
            
            messages.success(request, 'Payment successful! Your booking is pending admin verification.')
            return redirect('properties:booking_detail', booking_id=booking.id)
    
    messages.error(request, 'Payment verification failed.')
    return redirect('properties:property_list')


@login_required
def esewa_failure(request):
    """Handle failed eSewa payment"""
    messages.error(request, 'Payment was cancelled or failed. Please try again.')
    return redirect('properties:property_list')


def create_booking_from_payment(payment_intent, payment_method):
    """Create booking from successful payment"""
    metadata = payment_intent.metadata
    property_obj = get_object_or_404(Property, id=metadata['property_id'])
    customer = get_object_or_404(settings.AUTH_USER_MODEL, id=metadata['customer_id'])
    
    # Get booking data from session or recreate from metadata
    booking = PropertyBooking(
        property_ref=property_obj,
        customer=customer,
        customer_name=customer.get_full_name() or customer.username,
        customer_email=customer.email,
        customer_phone=getattr(customer, 'phone_number', ''),
        booking_type=metadata['booking_type'],
        payment_method=payment_method,
        payment_amount=Decimal(payment_intent.amount) / 100,  # Convert from cents
        transaction_id=metadata['transaction_id'],
        payment_status='completed',
        payment_data={
            'payment_intent_id': payment_intent.id,
            'amount_received': payment_intent.amount_received,
            'currency': payment_intent.currency,
        }
    )
    booking.save()
    return booking


def create_booking_from_esewa_success(user, booking_data, esewa_ref_id):
    """Create booking from successful eSewa payment"""
    property_obj = get_object_or_404(Property, id=booking_data['property_id'])
    
    booking = PropertyBooking(
        property_ref=property_obj,
        customer=user,
        customer_name=booking_data['customer_name'],
        customer_email=booking_data['customer_email'],
        customer_phone=booking_data['customer_phone'],
        booking_type=booking_data['booking_type'],
        preferred_date=datetime.fromisoformat(booking_data['preferred_date']) if booking_data.get('preferred_date') else None,
        message=booking_data.get('message', ''),
        payment_method='esewa',
        payment_amount=Decimal(booking_data['payment_amount']),
        transaction_id=booking_data['transaction_id'],
        payment_status='completed',
        payment_data={
            'esewa_ref_id': esewa_ref_id,
            'amount': booking_data['payment_amount'],
        }
    )
    booking.save()
    return booking


@login_required
def booking_detail_view(request, booking_id):
    """Display booking details"""
    booking = get_object_or_404(PropertyBooking, id=booking_id, customer=request.user)
    
    context = {
        'booking': booking,
    }
    return render(request, 'properties/booking_detail.html', context)


@login_required
def my_bookings_view(request):
    """Display user's bookings"""
    bookings = PropertyBooking.objects.filter(customer=request.user).order_by('-created_at')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'properties/my_bookings.html', context)


# Admin views for booking management
@method_decorator(login_required, name='dispatch')
class BookingListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Admin view to list all bookings"""
    model = PropertyBooking
    template_name = 'properties/admin_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_queryset(self):
        queryset = PropertyBooking.objects.select_related('property', 'customer').order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by booking type
        booking_type = self.request.GET.get('booking_type')
        if booking_type:
            queryset = queryset.filter(booking_type=booking_type)
        
        # Filter by payment method
        payment_method = self.request.GET.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        return queryset


@login_required
def verify_booking_view(request, booking_id):
    """Admin view to verify/reject bookings"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to verify bookings.')
        return redirect('properties:property_list')
    
    booking = get_object_or_404(PropertyBooking, id=booking_id)
    
    if request.method == 'POST':
        form = BookingVerificationForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.verified_by = request.user
            booking.save()
            
            # Send notification to customer (can be implemented later)
            status_msg = 'confirmed' if booking.status == 'confirmed' else 'rejected'
            messages.success(request, f'Booking has been {status_msg} successfully.')
            
            return redirect('properties:admin_bookings')
    else:
        form = BookingVerificationForm(instance=booking)
    
    context = {
        'booking': booking,
        'form': form,
    }
    return render(request, 'properties/verify_booking.html', context)
