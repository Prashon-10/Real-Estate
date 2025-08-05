from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.db.models.functions import Extract
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
import json
from datetime import datetime, timedelta

from accounts.models import User
from properties.models import Property, PropertyBooking


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard with overview statistics"""
    
    # Get statistics
    total_users = User.objects.count()
    total_agents = User.objects.filter(user_type='agent').count()
    total_customers = User.objects.filter(user_type='customer').count()
    total_properties = Property.objects.count()
    available_properties = Property.objects.filter(status='available').count()
    pending_properties = Property.objects.filter(status='pending').count()
    sold_properties = Property.objects.filter(status='sold').count()
    total_bookings = PropertyBooking.objects.count()
    pending_bookings = PropertyBooking.objects.filter(status='pending').count()
    confirmed_bookings = PropertyBooking.objects.filter(status='confirmed').count()
    
    # Recent activities
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_properties = Property.objects.order_by('-created_at')[:5]
    recent_bookings = PropertyBooking.objects.order_by('-created_at')[:5]
    
    # Property stats by agent
    top_agents = User.objects.filter(user_type='agent').annotate(
        property_count=Count('properties')
    ).order_by('-property_count')[:5]
    
    context = {
        'total_users': total_users,
        'total_agents': total_agents,
        'total_customers': total_customers,
        'total_properties': total_properties,
        'available_properties': available_properties,
        'pending_properties': pending_properties,
        'sold_properties': sold_properties,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'recent_users': recent_users,
        'recent_properties': recent_properties,
        'recent_bookings': recent_bookings,
        'top_agents': top_agents,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_users_list(request):
    """List all users with filtering and search"""
    
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Filter by user type
    user_type = request.GET.get('user_type', '')
    if user_type and hasattr(User, 'user_type'):
        users = users.filter(user_type=user_type)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users,
        'search': search,
        'user_type': user_type,
        'status': status,
        'total_count': paginator.count,
        'user_types': [
            ('customer', 'Customer'),
            ('agent', 'Agent'),
            ('admin', 'Admin'),
        ]
    }
    
    return render(request, 'admin_panel/users/list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    """View user details"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user's properties if agent
    user_properties = []
    if hasattr(user, 'user_type') and user.user_type == 'agent':
        user_properties = Property.objects.filter(agent=user).order_by('-created_at')
    
    # Get user's bookings if customer
    user_bookings = []
    if hasattr(user, 'user_type') and user.user_type == 'customer':
        user_bookings = PropertyBooking.objects.filter(customer=user).order_by('-created_at')
    
    context = {
        'user_obj': user,  # Using user_obj to avoid conflict with request.user
        'user_properties': user_properties,
        'user_bookings': user_bookings,
    }
    
    return render(request, 'admin_panel/users/detail.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_toggle_user_status(request, user_id):
    """Toggle user active status"""
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User {user.username} has been {status}.")
    
    return JsonResponse({
        'success': True,
        'is_active': user.is_active,
        'message': f"User {status} successfully."
    })


@login_required
@user_passes_test(is_admin)
def admin_properties_list(request):
    """List all properties with filtering"""
    
    properties = Property.objects.all().select_related('agent').order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        properties = properties.filter(
            Q(title__icontains=search) |
            Q(address__icontains=search) |
            Q(agent__username__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        properties = properties.filter(status=status)
    
    # Filter by property type
    property_type = request.GET.get('property_type')
    if property_type:
        properties = properties.filter(property_type=property_type)
    
    # Filter by listing type
    listing_type = request.GET.get('listing_type')
    if listing_type:
        properties = properties.filter(listing_type=listing_type)
    
    # Pagination
    paginator = Paginator(properties, 20)
    page_number = request.GET.get('page')
    properties = paginator.get_page(page_number)
    
    context = {
        'properties': properties,
        'search': search,
        'status': status,
        'property_type': property_type,
        'listing_type': listing_type,
        'total_count': paginator.count,
    }
    
    return render(request, 'admin_panel/properties/list.html', context)


@login_required
@user_passes_test(is_admin)
@login_required
@user_passes_test(is_admin)
def admin_property_detail(request, property_id):
    """View property details"""
    property_obj = get_object_or_404(Property, id=property_id)
    
    # Get property bookings
    bookings = PropertyBooking.objects.filter(property_ref=property_obj).order_by('-created_at')
    
    context = {
        'property': property_obj,
        'bookings': bookings,
    }
    
    return render(request, 'admin_panel/properties/detail.html', context)


@login_required
@user_passes_test(is_admin)
def admin_bookings_list(request):
    """List all bookings"""
    
    bookings = PropertyBooking.objects.all().select_related('property_ref', 'customer').order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        bookings = bookings.filter(
            Q(customer__username__icontains=search) |
            Q(property_ref__title__icontains=search) |
            Q(transaction_id__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    # Filter by booking type
    booking_type = request.GET.get('booking_type')
    if booking_type:
        bookings = bookings.filter(booking_type=booking_type)
    
    # Pagination
    paginator = Paginator(bookings, 20)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)
    
    context = {
        'bookings': bookings,
        'search': search,
        'status': status,
        'booking_type': booking_type,
        'total_count': paginator.count,
    }
    
    return render(request, 'admin_panel/bookings/list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_booking_detail(request, booking_id):
    """View booking details"""
    booking = get_object_or_404(PropertyBooking, id=booking_id)
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'admin_panel/bookings/detail.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_update_booking_status(request, booking_id):
    """Update booking status with payment handling"""
    try:
        booking = get_object_or_404(PropertyBooking, id=booking_id)
        
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        new_status = data.get('status')
        admin_notes = data.get('admin_notes', '')
        
        if not new_status:
            return JsonResponse({
                'success': False,
                'message': 'Status is required.'
            })
        
        if new_status not in dict(PropertyBooking.STATUS_CHOICES):
            return JsonResponse({
                'success': False,
                'message': 'Invalid status provided.'
            })
        
        old_status = booking.status
        booking.status = new_status
        if admin_notes:
            booking.admin_notes = admin_notes
        booking.verified_by = request.user
        
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
        
        # Set verification timestamp for confirmed/rejected/cancelled bookings
        if new_status in ['confirmed', 'rejected', 'cancelled']:
            from django.utils import timezone
            booking.verified_at = timezone.now()
        
        booking.save()
        
        messages.success(request, f"Booking status updated to {booking.get_status_display()}.{payment_message}")
        
        return JsonResponse({
            'success': True,
            'message': f'Booking status updated successfully.{payment_message}',
            'new_status': booking.get_status_display(),
            'payment_status': booking.payment_status,
            'payment_status_display': booking.payment_display_status
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request.'
    })


@login_required
@user_passes_test(is_admin)
def admin_analytics(request):
    """Admin analytics and reports"""
    
    # Get data for charts - Using Django's Extract function for SQLite compatibility
    user_stats = User.objects.annotate(
        month=Extract('date_joined', 'month')
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    property_stats = Property.objects.annotate(
        month=Extract('created_at', 'month')
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    booking_stats = PropertyBooking.objects.annotate(
        month=Extract('created_at', 'month')
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Revenue statistics 
    revenue_stats = PropertyBooking.objects.filter(
        status='confirmed'
    ).annotate(
        month=Extract('created_at', 'month')
    ).values('month').annotate(
        total_revenue=Sum('payment_amount')
    ).order_by('month')
    
    context = {
        'user_stats': list(user_stats),
        'property_stats': list(property_stats),
        'booking_stats': list(booking_stats),
        'revenue_stats': list(revenue_stats),
    }
    
    return render(request, 'admin_panel/analytics.html', context)


@login_required
@user_passes_test(is_admin)
def admin_settings(request):
    """Admin settings page"""
    
    if request.method == 'POST':
        # Handle settings updates here
        messages.success(request, "Settings updated successfully.")
        return redirect('admin_panel:settings')
    
    context = {
        # Add your settings context here
    }
    
    return render(request, 'admin_panel/settings.html', context)


@login_required
@user_passes_test(is_admin)
def admin_property_edit(request, property_id):
    """Edit property"""
    property_obj = get_object_or_404(Property, id=property_id)
    
    if request.method == 'POST':
        # Handle property update
        try:
            property_obj.title = request.POST.get('title', '').strip()
            property_obj.address = request.POST.get('address', '').strip()
            
            # Validate and set price
            try:
                price = float(request.POST.get('price', 0))
                if price <= 0:
                    raise ValueError("Price must be greater than 0")
                property_obj.price = price
            except (ValueError, TypeError):
                messages.error(request, "Please enter a valid price.")
                return redirect('admin_panel:property_edit', property_id=property_id)
            
            # Validate and set numeric fields
            try:
                property_obj.bedrooms = int(request.POST.get('bedrooms', 1))
                property_obj.bathrooms = float(request.POST.get('bathrooms', 1))
                property_obj.square_footage = int(request.POST.get('square_footage', 1000))
                
                if property_obj.bedrooms < 0 or property_obj.bathrooms < 0 or property_obj.square_footage <= 0:
                    raise ValueError("Invalid room or size values")
                    
            except (ValueError, TypeError):
                messages.error(request, "Please enter valid numeric values for bedrooms, bathrooms, and square footage.")
                return redirect('admin_panel:property_edit', property_id=property_id)
            
            property_obj.description = request.POST.get('description', '').strip()
            property_obj.status = request.POST.get('status', property_obj.status)
            property_obj.listing_type = request.POST.get('listing_type', property_obj.listing_type)
            property_obj.property_type = request.POST.get('property_type', property_obj.property_type)
            property_obj.is_featured = 'is_featured' in request.POST
            
            # Update agent if provided
            agent_id = request.POST.get('agent')
            if agent_id:
                try:
                    agent = User.objects.get(id=agent_id, user_type='agent', is_active=True)
                    property_obj.agent = agent
                except User.DoesNotExist:
                    messages.error(request, "Selected agent not found or inactive.")
                    return redirect('admin_panel:property_edit', property_id=property_id)
            
            # Validate required fields
            if not property_obj.title or not property_obj.address:
                messages.error(request, "Title and address are required.")
                return redirect('admin_panel:property_edit', property_id=property_id)
            
            property_obj.save()
            messages.success(request, f"Property '{property_obj.title}' updated successfully.")
            return redirect('admin_panel:property_detail', property_id=property_obj.id)
            
        except Exception as e:
            messages.error(request, f"Error updating property: {str(e)}")
    
    # Get all agents for the dropdown
    agents = User.objects.filter(user_type='agent', is_active=True)
    
    context = {
        'property': property_obj,
        'agents': agents,
        'STATUS_CHOICES': Property.STATUS_CHOICES,
        'LISTING_TYPE_CHOICES': Property.LISTING_TYPE_CHOICES,
        'PROPERTY_TYPE_CHOICES': Property.PROPERTY_TYPE_CHOICES,
    }
    
    return render(request, 'admin_panel/properties/edit.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_property_delete(request, property_id):
    """Delete property"""
    property_obj = get_object_or_404(Property, id=property_id)
    
    try:
        property_title = property_obj.title
        property_obj.delete()
        
        messages.success(request, f"Property '{property_title}' deleted successfully.")
        
        return JsonResponse({
            'success': True,
            'message': f"Property '{property_title}' deleted successfully."
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"Error deleting property: {str(e)}"
        })


@login_required
@user_passes_test(is_admin)
def admin_property_create(request):
    """Create new property"""
    
    if request.method == 'POST':
        try:
            # Validate required fields
            title = request.POST.get('title', '').strip()
            address = request.POST.get('address', '').strip()
            agent_id = request.POST.get('agent')
            
            if not title or not address or not agent_id:
                messages.error(request, "Title, address, and agent are required.")
                return redirect('admin_panel:property_create')
            
            # Validate agent
            try:
                agent = User.objects.get(id=agent_id, user_type='agent', is_active=True)
            except User.DoesNotExist:
                messages.error(request, "Selected agent not found or inactive.")
                return redirect('admin_panel:property_create')
            
            # Validate numeric fields
            try:
                price = float(request.POST.get('price', 0))
                bedrooms = int(request.POST.get('bedrooms', 1))
                bathrooms = float(request.POST.get('bathrooms', 1))
                square_footage = int(request.POST.get('square_footage', 1000))
                
                if price <= 0 or bedrooms < 0 or bathrooms < 0 or square_footage <= 0:
                    raise ValueError("Invalid numeric values")
                    
            except (ValueError, TypeError):
                messages.error(request, "Please enter valid numeric values for price, bedrooms, bathrooms, and square footage.")
                return redirect('admin_panel:property_create')
            
            # Create new property
            property_obj = Property.objects.create(
                title=title,
                address=address,
                price=price,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                square_footage=square_footage,
                description=request.POST.get('description', '').strip(),
                status=request.POST.get('status', 'available'),
                listing_type=request.POST.get('listing_type', 'sale'),
                property_type=request.POST.get('property_type', 'house'),
                is_featured='is_featured' in request.POST,
                agent=agent
            )
            
            messages.success(request, f"Property '{property_obj.title}' created successfully.")
            return redirect('admin_panel:property_detail', property_id=property_obj.id)
            
        except Exception as e:
            messages.error(request, f"Error creating property: {str(e)}")
    
    # Get all agents for the dropdown
    agents = User.objects.filter(user_type='agent', is_active=True)
    
    context = {
        'agents': agents,
        'STATUS_CHOICES': Property.STATUS_CHOICES,
        'LISTING_TYPE_CHOICES': Property.LISTING_TYPE_CHOICES,
        'PROPERTY_TYPE_CHOICES': Property.PROPERTY_TYPE_CHOICES,
    }
    
    return render(request, 'admin_panel/properties/create.html', context)


@login_required
@user_passes_test(is_admin)
def admin_user_edit(request, user_id):
    """Edit user"""
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        try:
            # Update basic fields
            user_obj.first_name = request.POST.get('first_name', '').strip()
            user_obj.last_name = request.POST.get('last_name', '').strip()
            user_obj.email = request.POST.get('email', '').strip()
            user_obj.is_active = 'is_active' in request.POST
            
            # Update additional fields if they exist
            if hasattr(user_obj, 'phone'):
                user_obj.phone = request.POST.get('phone', '').strip()
            if hasattr(user_obj, 'user_type'):
                user_obj.user_type = request.POST.get('user_type', 'customer')
            
            # Validate email
            if not user_obj.email:
                messages.error(request, "Email is required.")
                return redirect('admin_panel:user_edit', user_id=user_id)
            
            # Check for duplicate email
            if User.objects.filter(email=user_obj.email).exclude(id=user_obj.id).exists():
                messages.error(request, "Email already exists.")
                return redirect('admin_panel:user_edit', user_id=user_id)
            
            # Handle password change
            new_password = request.POST.get('new_password', '').strip()
            if new_password:
                if len(new_password) < 6:
                    messages.error(request, "Password must be at least 6 characters long.")
                    return redirect('admin_panel:user_edit', user_id=user_id)
                user_obj.set_password(new_password)
            
            user_obj.save()
            messages.success(request, f"User '{user_obj.username}' updated successfully.")
            return redirect('admin_panel:users_list')
            
        except Exception as e:
            messages.error(request, f"Error updating user: {str(e)}")
    
    context = {
        'user_obj': user_obj,
        'user_types': [
            ('customer', 'Customer'),
            ('agent', 'Agent'),
            ('admin', 'Admin'),
        ]
    }
    
    return render(request, 'admin_panel/users/edit.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_user_delete(request, user_id):
    """Delete user"""
    user_obj = get_object_or_404(User, id=user_id)
    
    # Prevent deleting superusers
    if user_obj.is_superuser:
        return JsonResponse({
            'success': False,
            'message': 'Cannot delete superuser accounts.'
        })
    
    # Prevent deleting self
    if user_obj.id == request.user.id:
        return JsonResponse({
            'success': False,
            'message': 'Cannot delete your own account.'
        })
    
    try:
        username = user_obj.username
        user_obj.delete()
        
        return JsonResponse({
            'success': True,
            'message': f"User '{username}' deleted successfully."
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"Error deleting user: {str(e)}"
        })


@login_required
@user_passes_test(is_admin)
def admin_user_create(request):
    """Create new user"""
    
    if request.method == 'POST':
        try:
            # Get form data
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            user_type = request.POST.get('user_type', 'customer')
            
            # Validate required fields
            if not username or not email or not password:
                messages.error(request, "Username, email, and password are required.")
                return redirect('admin_panel:user_create')
            
            # Check for duplicates
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect('admin_panel:user_create')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect('admin_panel:user_create')
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Set additional fields if they exist
            if hasattr(user, 'phone'):
                user.phone = phone
            if hasattr(user, 'user_type'):
                user.user_type = user_type
            
            user.is_active = True
            user.save()
            
            messages.success(request, f"User '{username}' created successfully.")
            return redirect('admin_panel:users_list')
            
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
    
    context = {
        'user_types': [
            ('customer', 'Customer'),
            ('agent', 'Agent'),
            ('admin', 'Admin'),
        ]
    }
    
    return render(request, 'admin_panel/users/create.html', context)
