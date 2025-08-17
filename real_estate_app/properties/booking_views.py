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
    after_visit_id = request.GET.get('after_visit')  # ID of completed visit for after-visit booking
    
    # Check if user has already ACTUALLY BOOKED this property (not just visited)
    if request.user.is_authenticated and booking_type == 'booking':
        existing_property_booking = PropertyBooking.objects.filter(
            customer=request.user,
            property_ref=property_obj,
            booking_type='booking',  # Only check actual property bookings, not visits
            status__in=['pending', 'confirmed']  # Don't include cancelled
        ).first()
        
        if existing_property_booking:
            messages.error(
                request, 
                f"You have already booked this property on {existing_property_booking.preferred_date.strftime('%Y-%m-%d at %H:%M')} "
                f"(Status: {existing_property_booking.get_status_display()}). You cannot book the same property multiple times."
            )
            return redirect('properties:property_detail', pk=property_obj.id)
    
    # Check if user has already requested a visit (separate check)
    if request.user.is_authenticated and booking_type == 'visit':
        # First check if user has already completed a visit for this property
        completed_visit_exists = PropertyBooking.objects.filter(
            customer=request.user,
            property_ref=property_obj,
            booking_type='visit',
            status='confirmed',
            visit_completed=True
        ).exists()
        
        if completed_visit_exists:
            messages.error(
                request, 
                f"You have already completed a visit for this property. "
                f"You can now book this property directly or choose a different property. "
                f"Multiple visits for the same property are not allowed."
            )
            return redirect('properties:property_detail', pk=property_obj.id)
        
        # Then check for pending/confirmed visit requests
        existing_visit_request = PropertyBooking.objects.filter(
            customer=request.user,
            property_ref=property_obj,
            booking_type='visit',  # Only check visit requests
            status__in=['pending', 'confirmed'],  # Don't include cancelled
            visit_completed=False  # Only incomplete visits
        ).first()
        
        if existing_visit_request:
            messages.error(
                request, 
                f"You have already requested a visit for this property on {existing_visit_request.preferred_date.strftime('%Y-%m-%d at %H:%M')} "
                f"(Status: {existing_visit_request.get_status_display()}). Please wait for the current visit to be completed."
            )
            return redirect('properties:property_detail', pk=property_obj.id)
    
    # Handle after-visit booking
    completed_visit = None
    if after_visit_id and booking_type == 'booking':
        try:
            completed_visit = PropertyBooking.objects.get(
                id=after_visit_id,
                customer=request.user,
                property_ref=property_obj,
                booking_type='visit',
                visit_completed=True
            )
            if not completed_visit.can_book_now:
                messages.error(request, "The booking deadline for this visit has expired.")
                return redirect('properties:property_detail', pk=property_obj.id)
        except PropertyBooking.DoesNotExist:
            messages.error(request, "Invalid visit reference.")
            return redirect('properties:property_detail', pk=property_obj.id)
    
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
                'additional_properties': form.cleaned_data.get('additional_properties', ''),
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
    
    # Calculate the actual payment amount for this user (considering repeat customer discount for visits)
    if hasattr(form, 'get_initial_payment_amount'):
        actual_visit_fee = form.get_initial_payment_amount('visit')
        actual_booking_fee = form.get_initial_payment_amount('booking')
        fees['visit_fee'] = actual_visit_fee
        fees['booking_fee'] = actual_booking_fee
    
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
    
    # Get user's existing booking dates across ALL properties for conflict checking
    user_booking_dates = []
    if request.user.is_authenticated:
        user_bookings = PropertyBooking.objects.filter(
            customer=request.user,
            status__in=['pending', 'confirmed'],
            preferred_date__isnull=False
        ).exclude(property_ref=property_obj)  # Exclude current property
        
        user_booking_dates = [
            {
                'date': booking.preferred_date.strftime('%Y-%m-%d'),
                'time': booking.preferred_date.strftime('%I:%M %p'),
                'property': booking.property_ref.title,
                'agent': booking.property_ref.agent.get_full_name() or booking.property_ref.agent.username,
                'type': booking.get_booking_type_display()
            }
            for booking in user_bookings
        ]
    
    user_booking_dates_json = json.dumps(user_booking_dates, cls=DjangoJSONEncoder)
    
    # Get nearby properties by the same agent (within 5km)
    from .utils import get_properties_within_distance
    nearby_properties = get_properties_within_distance(property_obj, max_distance_km=5.0, user=request.user)
    
    # Check if user has already completed a visit for this property (for template logic)
    has_completed_visit = False
    if request.user.is_authenticated:
        has_completed_visit = PropertyBooking.objects.filter(
            customer=request.user,
            property_ref=property_obj,
            booking_type='visit',
            status='confirmed',
            visit_completed=True
        ).exists()
    
    context = {
        'form': form,
        'property': property_obj,
        'fees': fees,
        'booking_type': booking_type,
        'blocked_visit_dates': blocked_dates_json,
        'user_booking_dates': user_booking_dates_json,
        'nearby_properties': nearby_properties,
        'completed_visit': completed_visit,
        'is_after_visit_booking': completed_visit is not None,
        'has_completed_visit': has_completed_visit,  # Add this for template logic
        'current_agent_name': property_obj.agent.get_full_name() or property_obj.agent.username,  # Add current agent info
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
    """Create a booking with demo payment authorization (not immediate charge)"""
    from django.utils import timezone
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
        payment_intent_id=f"pi_demo_{uuid.uuid4().hex[:16]}",  # Demo payment intent ID
        payment_amount=Decimal(str(booking_data['payment_amount'])),
        payment_status='authorized',  # Start with authorized status (money on hold)
        payment_authorized_at=timezone.now(),  # Record when authorization happened
        payment_data={
            'demo': True, 
            'payment_method': payment_method,
            'authorization_demo': True,
            'note': 'Demo payment - Money is held until booking confirmation'
        }
    )
    
    # Set preferred date if it exists
    if booking_data.get('preferred_date'):
        from django.utils.dateparse import parse_datetime
        booking.preferred_date = parse_datetime(booking_data['preferred_date'])
    
    # Handle additional properties
    if booking_data.get('additional_properties'):
        booking.additional_properties = booking_data['additional_properties']
    
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
            old_status = booking.status
            booking = form.save(commit=False)
            booking.verified_by = request.user
            
            if booking.status in ['confirmed', 'rejected']:
                from django.utils import timezone
                booking.verified_at = timezone.now()
                
                # Handle payment based on booking status
                if booking.status == 'confirmed' and old_status != 'confirmed':
                    # CONFIRM: First check if payment needs re-authorization, then capture
                    if booking.payment_status == 'cancelled':
                        # Re-authorize cancelled payment
                        if booking.reauthorize_payment():
                            messages.info(request, 
                                f'Payment re-authorized for booking {booking.id}.')
                            # Now capture the re-authorized payment
                            if booking.capture_payment():
                                messages.success(request, 
                                    f'Booking confirmed and payment of Rs. {booking.payment_amount} has been charged successfully.')
                            else:
                                messages.warning(request, 
                                    'Payment re-authorized but capture failed. Please check payment manually.')
                        else:
                            messages.error(request, 
                                'Failed to re-authorize cancelled payment. Please check payment manually.')
                    elif booking.payment_status == 'authorized':
                        # Normal capture for authorized payment
                        success = booking.capture_payment()
                        if success:
                            messages.success(request, 
                                f'Booking confirmed and payment of Rs. {booking.payment_amount} has been charged successfully.')
                        else:
                            messages.warning(request, 
                                'Booking confirmed but payment capture failed. Please check payment manually.')
                    else:
                        messages.success(request, f'Booking has been confirmed.')
                        
                elif booking.status == 'rejected' and old_status != 'rejected':
                    # REJECT: Cancel the authorization (release held money)
                    if booking.payment_status == 'authorized':
                        success = booking.cancel_authorization()
                        if success:
                            messages.success(request, 
                                f'Booking rejected and held payment of Rs. {booking.payment_amount} has been released back to customer.')
                        else:
                            messages.warning(request, 
                                'Booking rejected but payment cancellation failed. Please check payment manually.')
                    elif booking.payment_status == 'captured':
                        # If somehow payment was already captured, refund it
                        success = booking.refund_payment()
                        if success:
                            messages.success(request, 
                                f'Booking rejected and payment of Rs. {booking.payment_amount} has been refunded.')
                        else:
                            messages.warning(request, 
                                'Booking rejected but refund failed. Please process refund manually.')
                    else:
                        messages.success(request, f'Booking has been rejected.')
                        
                elif booking.status == 'cancelled' and old_status != 'cancelled':
                    # CANCEL: Refund captured payments or cancel authorization
                    if booking.payment_status == 'captured':
                        success = booking.refund_payment()
                        if success:
                            messages.success(request, 
                                f'Booking cancelled and payment of Rs. {booking.payment_amount} has been refunded to customer.')
                        else:
                            messages.warning(request, 
                                'Booking cancelled but refund failed. Please process refund manually.')
                    elif booking.payment_status == 'authorized':
                        success = booking.cancel_authorization()
                        if success:
                            messages.success(request, 
                                f'Booking cancelled and held payment of Rs. {booking.payment_amount} has been released back to customer.')
                        else:
                            messages.warning(request, 
                                'Booking cancelled but payment cancellation failed. Please check payment manually.')
                    else:
                        messages.success(request, f'Booking has been cancelled.')
            
            booking.save()
            
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
                
                # Handle payment based on booking status change
                payment_message = ""
                if new_status == 'confirmed' and old_status != 'confirmed':
                    # CONFIRM: First check if payment needs re-authorization, then capture
                    if booking.payment_status == 'cancelled':
                        # Re-authorize cancelled payment
                        if booking.reauthorize_payment():
                            # Now capture the re-authorized payment
                            if booking.capture_payment():
                                payment_message = f" Payment re-authorized and Rs. {booking.payment_amount} charged successfully."
                            else:
                                payment_message = f" Payment re-authorized but capture failed - check manually."
                        else:
                            payment_message = f" Failed to re-authorize cancelled payment - check manually."
                    elif booking.payment_status == 'authorized':
                        # Normal capture for authorized payment
                        success = booking.capture_payment()
                        payment_message = f" Payment of Rs. {booking.payment_amount} charged successfully." if success else " Payment capture failed - check manually."
                    else:
                        payment_message = f" Booking confirmed (payment status: {booking.get_payment_status_display()})."
                        
                elif new_status == 'rejected' and old_status != 'rejected':
                    # REJECT: Cancel authorization or refund if captured
                    if booking.payment_status == 'authorized':
                        success = booking.cancel_authorization()
                        payment_message = f" Held payment of Rs. {booking.payment_amount} released to customer." if success else " Payment cancellation failed - check manually."
                    elif booking.payment_status == 'captured':
                        success = booking.refund_payment()
                        payment_message = f" Payment of Rs. {booking.payment_amount} refunded to customer." if success else " Refund failed - process manually."
                        
                elif new_status == 'cancelled' and old_status != 'cancelled':
                    # CANCEL: Refund captured payments or cancel authorization
                    if booking.payment_status == 'captured':
                        success = booking.refund_payment()
                        payment_message = f" Booking cancelled - Payment of Rs. {booking.payment_amount} refunded to customer." if success else " Booking cancelled but refund failed - process manually."
                    elif booking.payment_status == 'authorized':
                        success = booking.cancel_authorization()
                        payment_message = f" Booking cancelled - Held payment of Rs. {booking.payment_amount} released to customer." if success else " Booking cancelled but payment cancellation failed - check manually."
                    else:
                        payment_message = f" Booking cancelled (payment status: {booking.get_payment_status_display()})."
            
            booking.save()
            
            # Return JSON response for AJAX calls
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Booking status updated from {old_status} to {new_status}.{payment_message}',
                    'new_status': new_status,
                    'new_status_display': booking.get_status_display(),
                    'payment_status': booking.payment_status,
                    'payment_status_display': booking.payment_display_status,
                    'verified_by': request.user.get_full_name() or request.user.email,
                    'verified_at': booking.verified_at.strftime('%Y-%m-%d %H:%M:%S') if booking.verified_at else None
                })
            else:
                messages.success(request, f'Booking status updated to {booking.get_status_display()}.{payment_message}')
                
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


@login_required
@require_POST
def complete_visit_view(request, booking_id):
    """Allow agents to confirm visit completion (part of dual confirmation system)"""
    booking = get_object_or_404(PropertyBooking, id=booking_id)
    
    # Check if user is the agent for this property
    if request.user != booking.property_ref.agent:
        messages.error(request, "You can only confirm visits for your own properties.")
        return redirect('properties:agent_bookings')
    
    # Check if this is a confirmed visit
    if booking.booking_type != 'visit':
        messages.error(request, "This is not a visit request.")
        return redirect('properties:agent_bookings')
    
    if booking.status != 'confirmed':
        messages.error(request, "Only confirmed visits can be marked as completed.")
        return redirect('properties:agent_bookings')
    
    # Check if visit time has passed (time authentication)
    from django.utils import timezone
    from datetime import timedelta
    
    current_time = timezone.now()
    
    # Check if the scheduled visit time has passed
    if booking.preferred_date and booking.preferred_date > current_time:
        time_remaining = booking.preferred_date - current_time
        hours = int(time_remaining.total_seconds() // 3600)
        minutes = int((time_remaining.total_seconds() % 3600) // 60)
        
        messages.error(
            request, 
            f"Cannot confirm visit completion before the scheduled time. "
            f"Visit is scheduled for {booking.preferred_date.strftime('%Y-%m-%d at %H:%M')}. "
            f"Time remaining: {hours}h {minutes}m"
        )
        return redirect('properties:agent_bookings')
    
    # Allow confirmation within 30 minutes of scheduled time (buffer for early arrivals)
    buffer_time = timedelta(minutes=30)
    if booking.preferred_date and booking.preferred_date - buffer_time > current_time:
        messages.error(
            request, 
            f"Visit confirmation is available from 30 minutes before the scheduled time. "
            f"Visit scheduled for {booking.preferred_date.strftime('%Y-%m-%d at %H:%M')}."
        )
        return redirect('properties:agent_bookings')
    
    agent_confirmed = getattr(booking, 'agent_confirmed_completion', False)
    if agent_confirmed:
        messages.info(request, "You have already confirmed this visit completion.")
        return redirect('properties:agent_bookings')
    
    # Agent confirms the visit
    if booking.confirm_visit_completion(request.user):
        if booking.visit_completed:
            messages.success(
                request, 
                f"Visit fully completed! Both you and {booking.customer_name} have confirmed. "
                f"Customer can now book this property until {booking.booking_deadline_display}."
            )
        else:
            messages.success(
                request, 
                f"You confirmed the visit completion. Waiting for {booking.customer_name} to also confirm. "
                f"Once both parties confirm, booking will be available."
            )
    else:
        messages.error(request, "Failed to confirm the visit.")
    
    return redirect('properties:agent_bookings')


@login_required
@require_POST
def customer_confirm_visit_view(request, booking_id):
    """Allow customers to confirm visit completion (part of dual confirmation system)"""
    booking = get_object_or_404(PropertyBooking, id=booking_id)
    
    # Check if user is the customer for this booking
    if request.user != booking.customer:
        messages.error(request, "You can only confirm your own visit completions.")
        return redirect('properties:property_detail', pk=booking.property_ref.id)
    
    # Check if this is a confirmed visit
    if booking.booking_type != 'visit':
        messages.error(request, "This is not a visit request.")
        return redirect('properties:property_detail', pk=booking.property_ref.id)
    
    if booking.status != 'confirmed':
        messages.error(request, "Only confirmed visits can be marked as completed.")
        return redirect('properties:property_detail', pk=booking.property_ref.id)
    
    # Check if visit time has passed (time authentication)
    from django.utils import timezone
    from datetime import timedelta
    
    current_time = timezone.now()
    
    # Check if the scheduled visit time has passed
    if booking.preferred_date and booking.preferred_date > current_time:
        time_remaining = booking.preferred_date - current_time
        hours = int(time_remaining.total_seconds() // 3600)
        minutes = int((time_remaining.total_seconds() % 3600) // 60)
        
        messages.error(
            request, 
            f"Cannot confirm visit completion before the scheduled time. "
            f"Visit is scheduled for {booking.preferred_date.strftime('%Y-%m-%d at %H:%M')}. "
            f"Time remaining: {hours}h {minutes}m"
        )
        return redirect('properties:property_detail', pk=booking.property_ref.id)
    
    # Allow confirmation within 30 minutes of scheduled time (buffer for early arrivals)
    buffer_time = timedelta(minutes=30)
    if booking.preferred_date and booking.preferred_date - buffer_time > current_time:
        messages.error(
            request, 
            f"Visit confirmation is available from 30 minutes before the scheduled time. "
            f"Visit scheduled for {booking.preferred_date.strftime('%Y-%m-%d at %H:%M')}."
        )
        return redirect('properties:property_detail', pk=booking.property_ref.id)
    
    customer_confirmed = getattr(booking, 'customer_confirmed_completion', False)
    if customer_confirmed:
        messages.info(request, "You have already confirmed this visit completion.")
        return redirect('properties:property_detail', pk=booking.property_ref.id)
    
    # Customer confirms the visit
    if booking.confirm_visit_completion(request.user):
        if booking.visit_completed:
            messages.success(
                request, 
                f"Visit fully completed! Both you and the agent have confirmed. "
                f"You can now book this property until {booking.booking_deadline_display}."
            )
        else:
            messages.success(
                request, 
                f"You confirmed the visit completion. Waiting for the agent to also confirm. "
                f"Once both parties confirm, booking will be available."
            )
    else:
        messages.error(request, "Failed to confirm the visit.")
    
    return redirect('properties:property_detail', pk=booking.property_ref.id)
