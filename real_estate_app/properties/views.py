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
from .models import Property, PropertyImage, Favorite
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
        queryset = Property.objects.filter(status='available')
        
        if self.request.GET.get('price_min'):
            queryset = queryset.filter(price__gte=self.request.GET.get('price_min'))
        if self.request.GET.get('price_max'):
            queryset = queryset.filter(price__lte=self.request.GET.get('price_max'))
        if self.request.GET.get('bedrooms'):
            queryset = queryset.filter(bedrooms__gte=self.request.GET.get('bedrooms'))
        if self.request.GET.get('bathrooms'):
            queryset = queryset.filter(bathrooms__gte=self.request.GET.get('bathrooms'))
        if self.request.GET.get('sqft_min'):
            queryset = queryset.filter(square_footage__gte=self.request.GET.get('sqft_min'))
        if self.request.GET.get('sqft_max'):
            queryset = queryset.filter(square_footage__lte=self.request.GET.get('sqft_max'))
        
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'bedrooms':
            queryset = queryset.order_by('-bedrooms')
        else:  
            queryset = queryset.order_by('-created_at')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        favorite_property_ids = []
        if self.request.user.is_authenticated and self.request.user.is_customer():
            favorite_property_ids = list(
                Favorite.objects.filter(user=self.request.user)
                .values_list('property__id', flat=True)
            )
        context['favorite_property_ids'] = favorite_property_ids
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
            
            if self.request.user.is_customer():
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
        
        similar = Property.objects.filter(
            status='available',
            bedrooms=property_obj.bedrooms,
        ).exclude(id=property_obj.id)[:4]
        
        data = []
        for prop in similar:
            data.append({
                'id': prop.id,
                'title': prop.title,
                'address': prop.address,
                'price': float(prop.price),
                'bedrooms': prop.bedrooms,
                'bathrooms': float(prop.bathrooms),
                'has_image': prop.images.exists()
            })
        
        return JsonResponse({'properties': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


#Testing
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Property, PropertyMessage
from django.views.decorators.http import require_POST

@require_POST
@login_required
def send_message(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    content = request.POST.get('message')

    if not content:
        messages.error(request, "Message cannot be empty.")
        return redirect('properties:property_detail', pk=property_id)

    if not request.user.is_customer and not request.user == property.agent:
        messages.error(request, "You are not authorized to send a message.")
        return redirect('properties:property_detail', pk=property_id)

    PropertyMessage.objects.create(
        property=property,
        sender=request.user,
        content=content
    )
    messages.success(request, "Your message has been sent.")
    return redirect('properties:property_detail', pk=property_id)



def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['is_favorite'] = Favorite.objects.filter(user=self.request.user, property=self.object).exists()
    context['messages'] = self.object.messages.order_by('timestamp').all()
    return context




from django.db.models import Q

@login_required
def message_inbox(request):
    # Get all properties where the user is either agent or customer who favorited it
    properties = Property.objects.filter(
        Q(agent=request.user) | Q(favorites__user=request.user)
    ).distinct()

    # Get all messages related to those properties
    messages = PropertyMessage.objects.filter(property__in=properties).select_related('sender', 'property')

    return render(request, 'properties/message_inbox.html', {
        'messages': messages,
    })