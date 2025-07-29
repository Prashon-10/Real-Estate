from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
import json
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Property, PropertyImage, Favorite, PropertyMessage
from .forms import PropertyForm, PropertyImageForm
from search.models import SearchHistory

@login_required
def favorites_list(request):
    """
    Display user's favorite properties
    """
    if not request.user.is_customer():
        messages.warning(request, "This feature is only available to customers.")
        return redirect('properties:property_list')
    
    favorites = Favorite.objects.filter(user=request.user).select_related('property')
    
    return render(request, 'properties/favorites_list.html', {
        'favorites': favorites
    })

class PropertyListView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 9
    
    def get_queryset(self):
        # Show ALL properties, including booked ones, but not sold ones
        queryset = Property.objects.filter(status__in=['available', 'pending']).select_related('agent')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(address__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Property type filter
        property_type = self.request.GET.get('property_type')
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        # Listing type filter
        listing_type = self.request.GET.get('listing_type')
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)
        
        # Price filters
        min_price = self.request.GET.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        max_price = self.request.GET.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Bedroom filter
        bedrooms = self.request.GET.get('bedrooms')
        if bedrooms:
            queryset = queryset.filter(bedrooms__gte=bedrooms)
            
        # Bathroom filter
        bathrooms = self.request.GET.get('bathrooms')
        if bathrooms:
            queryset = queryset.filter(bathrooms__gte=bathrooms)
        
        # Sorting
        sort = self.request.GET.get('sort')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        else:  
            queryset = queryset.order_by('-created_at')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        favorite_property_ids = []
        booked_property_ids = []
        
        # Get properties that have been BOOKED (not visited) by any user (to gray them out)
        from .models import PropertyBooking
        all_booked_property_ids = list(
            PropertyBooking.objects.filter(
                booking_type='booking',  # Only actual bookings, not visits
                status='confirmed'  # Only confirmed bookings
            ).values_list('property_ref__id', flat=True)
        )
        
        # Get properties that have VISIT REQUESTS (to show "Being Visited" indicator)
        all_visited_property_ids = list(
            PropertyBooking.objects.filter(
                booking_type='visit',  # Only visit requests
                status__in=['pending', 'confirmed']  # Pending or confirmed visits
            ).values_list('property_ref__id', flat=True)
        )
        
        if self.request.user.is_authenticated and self.request.user.is_customer():
            favorite_property_ids = list(
                Favorite.objects.filter(user=self.request.user)
                .values_list('property__id', flat=True)
            )
            
            # Get properties that the current user has already booked (not visited)
            booked_property_ids = list(
                PropertyBooking.objects.filter(
                    customer=self.request.user,
                    booking_type='booking',  # Only actual bookings, not visits
                    status__in=['pending', 'confirmed']  # Don't show button if booking is pending or confirmed
                ).values_list('property_ref__id', flat=True)
            )
            
            # Get properties that the current user has already requested visits for
            visited_property_ids = list(
                PropertyBooking.objects.filter(
                    customer=self.request.user,
                    booking_type='visit',  # Only visit requests
                    status__in=['pending', 'confirmed']  # Don't show button if visit is pending or confirmed
                ).values_list('property_ref__id', flat=True)
            )
            
        context['favorite_property_ids'] = favorite_property_ids
        context['booked_property_ids'] = booked_property_ids
        context['visited_property_ids'] = visited_property_ids  # User's own visit requests
        context['all_booked_property_ids'] = all_booked_property_ids  # For graying out
        context['all_visited_property_ids'] = all_visited_property_ids  # For "Being Visited" indicator
        
        # Add total count for debugging
        context['total_properties'] = self.get_queryset().count()
        
        return context

class PropertyDetailView(LoginRequiredMixin, DetailView):
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user, 
                property=self.object
            ).exists()
            
            # Check if user has already booked this property (not visited)
            if self.request.user.is_customer():
                from .models import PropertyBooking
                context['has_booking'] = PropertyBooking.objects.filter(
                    customer=self.request.user,
                    property_ref=self.object,
                    booking_type='booking',  # Only actual bookings, not visits
                    status__in=['pending', 'confirmed']  # Don't show button if booking is pending or confirmed
                ).exists()
                
                # Check if user has already requested a visit for this property
                context['has_visit_request'] = PropertyBooking.objects.filter(
                    customer=self.request.user,
                    property_ref=self.object,
                    booking_type='visit',  # Only visit requests
                    status__in=['pending', 'confirmed']  # Don't show button if visit is pending or confirmed
                ).exists()
                
                # Check if ANY user has booked this property (not visited) - to disable booking
                context['is_booked_by_anyone'] = PropertyBooking.objects.filter(
                    property_ref=self.object,
                    booking_type='booking',  # Only actual bookings, not visits
                    status='confirmed'  # Only confirmed bookings
                ).exists()
                
                # Get all blocked visit dates for this property (dates already taken by other users)
                blocked_dates = list(
                    PropertyBooking.objects.filter(
                        property_ref=self.object,
                        booking_type='visit',
                        status__in=['pending', 'confirmed'],
                        preferred_date__isnull=False
                    ).values_list('preferred_date', flat=True)
                )
                
                # Convert datetime objects to date strings for JavaScript
                import json
                from django.core.serializers.json import DjangoJSONEncoder
                context['blocked_visit_dates'] = json.dumps(
                    [date.strftime('%Y-%m-%d') for date in blocked_dates if date],
                    cls=DjangoJSONEncoder
                )
                
                # Count of people visiting this property
                context['visit_count'] = PropertyBooking.objects.filter(
                    property_ref=self.object,
                    booking_type='visit',
                    status__in=['pending', 'confirmed']
                ).count()
                
                SearchHistory.objects.create(
                    user=self.request.user,
                    query=self.object.title,
                    property=self.object
                )
        return context

@method_decorator(login_required, name='dispatch')
class AgentPropertyListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Property
    template_name = 'properties/agent_properties.html'
    context_object_name = 'properties'
    
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_agent() if hasattr(self.request.user, 'is_agent') else False)
    
    def get_queryset(self):
        return Property.objects.filter(agent=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        properties = self.get_queryset()
        context['available_count'] = properties.filter(status='available').count()
        context['pending_count'] = properties.filter(status='pending').count()
        context['sold_count'] = properties.filter(status='sold').count()
        
        return context

@method_decorator(login_required, name='dispatch')
class PropertyCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    success_url = reverse_lazy('properties:agent_properties')
    
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_agent() if hasattr(self.request.user, 'is_agent') else False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = PropertyImageForm()  
        return context
    
    def form_valid(self, form):
        form.instance.agent = self.request.user
        response = super().form_valid(form)
        
        image_form = PropertyImageForm(self.request.POST, self.request.FILES)
        if image_form.is_valid():
            order = 0
            for i in range(1, 4):  
                field_name = f'image{i}'
                image = self.request.FILES.get(field_name)
                if image:
                    PropertyImage.objects.create(
                        property=self.object,
                        image=image,
                        order=order
                    )
                    order += 1
        messages.success(self.request, "Property listing created successfully.")
        return response

@method_decorator(login_required, name='dispatch')
class PropertyUpdateView(UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    success_url = reverse_lazy('properties:agent_properties')
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.agent != request.user:
            messages.error(request, "You can only edit your own listings.")
            return redirect('properties:agent_properties')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        image_form = PropertyImageForm(self.request.POST, self.request.FILES)
        if image_form.is_valid():
            current_max_order = self.object.images.order_by('-order').first()
            order = (current_max_order.order + 1) if current_max_order else 0
            
            for i in range(1, 4):  
                field_name = f'image{i}'
                image = self.request.FILES.get(field_name)
                if image:
                    PropertyImage.objects.create(
                        property=self.object,
                        image=image,
                        order=order
                    )
                    order += 1
        messages.success(self.request, "Property listing updated successfully.")
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = PropertyImageForm()  
        context['existing_images'] = self.object.images.all()
        return context

@method_decorator(login_required, name='dispatch')
class PropertyDeleteView(DeleteView):
    model = Property
    template_name = 'properties/property_confirm_delete.html'
    success_url = reverse_lazy('properties:agent_properties')
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.agent != request.user:
            messages.error(request, "You can only delete your own listings.")
            return redirect('properties:agent_properties')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Property listing deleted successfully.")
        return super().delete(request, *args, **kwargs)

@login_required
@require_POST
def toggle_favorite(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        property=property_obj
    )
    
    if not created:
        favorite.delete()
        is_favorite = False
        action = "removed from"
    else:
        is_favorite = True
        action = "added to"
        
        # Update recommendations when user adds a favorite
        if request.user.is_customer():
            from search.views import update_recommendations
            # Get similar properties based on the favorited property
            similar_properties = Property.objects.filter(
                status='available',
                property_type=property_obj.property_type,
                listing_type=property_obj.listing_type
            ).exclude(id=property_obj.id)[:10]
            
            if similar_properties:
                update_recommendations(request.user, f"Properties like {property_obj.title}", similar_properties)
    
    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite,
        'message': f"{property_obj.title} {action} favorites."
    })

@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('property')
    return render(request, 'properties/favorites.html', {'favorites': favorites})

@login_required
def delete_property_image(request, image_id):
    image = get_object_or_404(PropertyImage, pk=image_id)
    property_id = image.property.id
    
    # Check if the user is the agent of the property
    if request.user != image.property.agent:
        messages.error(request, "You can only delete images from your own listings.")
        return redirect('properties:property_update', pk=property_id)
    
    image.delete()
    messages.success(request, "Image deleted successfully.")
    return redirect('properties:property_update', pk=property_id)

@login_required
@require_POST
def update_property_status(request, pk):
    try:
        data = json.loads(request.body)
        status = data.get('status')
        
        if status not in [choice[0] for choice in Property.STATUS_CHOICES]:
            return JsonResponse({'success': False, 'message': 'Invalid status'})
        
        property_obj = Property.objects.get(pk=pk)
        
        # Check if the user is the agent of the property
        if request.user != property_obj.agent:
            return JsonResponse({'success': False, 'message': 'You can only update status of your own listings'})
        
        property_obj.status = status
        property_obj.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Property status updated to {property_obj.get_status_display()}',
            'status_display': property_obj.get_status_display()
        })
    except Property.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Property not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def similar_properties(request, pk):
    try:
        property_obj = get_object_or_404(Property, pk=pk)
        
        # Get similar properties based on bedrooms, bathrooms, and property type
        similar = Property.objects.filter(
            status='available',
            bedrooms=property_obj.bedrooms,
            property_type=property_obj.property_type
        ).exclude(id=property_obj.id).select_related('agent').prefetch_related('images')[:4]
        
        data = []
        for prop in similar:
            data.append({
                'id': prop.id,
                'title': prop.title,
                'address': prop.address,
                'price': float(prop.price),
                'bedrooms': prop.bedrooms,
                'bathrooms': float(prop.bathrooms),
                'thumbnail': prop.get_thumbnail(),
                'agent': prop.agent.get_full_name() or prop.agent.username,
                'has_image': prop.images.exists()
            })
        
        return JsonResponse({'properties': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


#Testing
@require_POST
@login_required
def send_message(request, property_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST method allowed'})
        
    property = get_object_or_404(Property, id=property_id)
    content = request.POST.get('message')

    if not content:
        return JsonResponse({'success': False, 'message': 'Message cannot be empty'})

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Please log in to send messages'})

    # Allow both customers and other users to send messages to agents
    try:
        PropertyMessage.objects.create(
            property=property,
            sender=request.user,
            content=content
        )
        
        # If this is an AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({
                'success': True, 
                'message': 'Your message has been sent successfully!',
                'agent_name': property.agent.get_full_name() or property.agent.username
            })
        else:
            messages.success(request, "Your message has been sent.")
            return redirect('properties:property_detail', pk=property_id)
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({'success': False, 'message': 'Failed to send message. Please try again.'})
        else:
            messages.error(request, "Failed to send message. Please try again.")
            return redirect('properties:property_detail', pk=property_id)



def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['is_favorite'] = Favorite.objects.filter(user=self.request.user, property=self.object).exists()
    context['messages'] = self.object.messages.order_by('timestamp').all()
    return context

@login_required
def message_inbox(request):
    """
    Agent's message inbox - shows all messages for their properties
    """
    if not request.user.is_agent():
        messages.warning(request, "This feature is only available to agents.")
        return redirect('properties:property_list')
    
    # Get all messages for agent's properties
    agent_messages = PropertyMessage.objects.filter(
        property__agent=request.user
    ).select_related('sender', 'property').order_by('-timestamp')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter == 'unread':
        agent_messages = agent_messages.filter(read=False)
    elif status_filter == 'read':
        agent_messages = agent_messages.filter(read=True)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        agent_messages = agent_messages.filter(
            Q(content__icontains=search) |
            Q(sender__first_name__icontains=search) |
            Q(sender__last_name__icontains=search) |
            Q(property__title__icontains=search)
        )
    
    context = {
        'messages': agent_messages,
        'unread_count': agent_messages.filter(read=False).count(),
        'total_count': agent_messages.count(),
        'status_filter': status_filter,
        'search': search,
    }
    
    return render(request, 'properties/message_inbox.html', context)

@login_required
@require_POST
def mark_message_read(request, message_id):
    """
    Mark a message as read (AJAX endpoint)
    """
    try:
        message = get_object_or_404(PropertyMessage, id=message_id, property__agent=request.user)
        message.read = True
        message.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Message marked as read'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)