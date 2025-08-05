from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
import json
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
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
        return redirect("properties:property_list")

    favorites = Favorite.objects.filter(user=request.user).select_related("property")

    return render(request, "properties/favorites_list.html", {"favorites": favorites})


class PropertyListView(LoginRequiredMixin, ListView):
    model = Property
    template_name = "properties/property_list.html"
    context_object_name = "properties"
    paginate_by = 9

    def get_queryset(self):
        # Show ALL properties, including booked ones, but not sold ones
        queryset = Property.objects.filter(
            status__in=["available", "pending"]
        ).select_related("agent")

        # Search functionality
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(address__icontains=search)
                | Q(description__icontains=search)
            )

        # Property type filter
        property_type = self.request.GET.get("property_type")
        if property_type:
            queryset = queryset.filter(property_type=property_type)

        # Listing type filter
        listing_type = self.request.GET.get("listing_type")
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)

        # Price filters
        min_price = self.request.GET.get("min_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        max_price = self.request.GET.get("max_price")
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Bedroom filter
        bedrooms = self.request.GET.get("bedrooms")
        if bedrooms:
            queryset = queryset.filter(bedrooms__gte=bedrooms)

        # Bathroom filter
        bathrooms = self.request.GET.get("bathrooms")
        if bathrooms:
            queryset = queryset.filter(bathrooms__gte=bathrooms)

        # Sorting
        sort = self.request.GET.get("sort")
        if sort == "price_low":
            queryset = queryset.order_by("price")
        elif sort == "price_high":
            queryset = queryset.order_by("-price")
        elif sort == "newest":
            queryset = queryset.order_by("-created_at")
        elif sort == "oldest":
            queryset = queryset.order_by("created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        favorite_property_ids = []
        booked_property_ids = []

        # Get properties that have been BOOKED (not visited) by any user (to gray them out)
        from .models import PropertyBooking

        all_booked_property_ids = list(
            PropertyBooking.objects.filter(
                booking_type="booking",  # Only actual bookings, not visits
                status="confirmed",  # Only confirmed bookings
            ).values_list("property_ref__id", flat=True)
        )

        # Get properties that have VISIT REQUESTS (to show "Being Visited" indicator)
        all_visited_property_ids = list(
            PropertyBooking.objects.filter(
                booking_type="visit",  # Only visit requests
                status__in=["pending", "confirmed"],  # Pending or confirmed visits
            ).values_list("property_ref__id", flat=True)
        )

        # Initialize default values
        favorite_property_ids = []
        booked_property_ids = []
        visited_property_ids = []

        if self.request.user.is_authenticated and self.request.user.is_customer():
            favorite_property_ids = list(
                Favorite.objects.filter(user=self.request.user).values_list(
                    "property__id", flat=True
                )
            )

            # Get properties that the current user has already booked (not visited)
            booked_property_ids = list(
                PropertyBooking.objects.filter(
                    customer=self.request.user,
                    booking_type="booking",  # Only actual bookings, not visits
                    status__in=[
                        "pending",
                        "confirmed",
                    ],  # Don't show button if booking is pending or confirmed
                ).values_list("property_ref__id", flat=True)
            )

            # Get properties that the current user has already requested visits for
            visited_property_ids = list(
                PropertyBooking.objects.filter(
                    customer=self.request.user,
                    booking_type="visit",  # Only visit requests
                    status__in=[
                        "pending",
                        "confirmed",
                    ],  # Don't show button if visit is pending or confirmed
                ).values_list("property_ref__id", flat=True)
            )

        context["favorite_property_ids"] = favorite_property_ids
        context["booked_property_ids"] = booked_property_ids
        context["visited_property_ids"] = (
            visited_property_ids  # User's own visit requests
        )
        context["all_booked_property_ids"] = all_booked_property_ids  # For graying out
        context["all_visited_property_ids"] = (
            all_visited_property_ids  # For "Being Visited" indicator
        )

        # Add total count for debugging
        context["total_properties"] = self.get_queryset().count()

        return context


class PropertyDetailView(LoginRequiredMixin, DetailView):
    model = Property
    template_name = "properties/property_detail.html"
    context_object_name = "property"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["is_favorite"] = Favorite.objects.filter(
                user=self.request.user, property=self.object
            ).exists()

            # Check if user has already booked this property (not visited)
            if self.request.user.is_customer():
                from .models import PropertyBooking

                context["has_booking"] = PropertyBooking.objects.filter(
                    customer=self.request.user,
                    property_ref=self.object,
                    booking_type="booking",  # Only actual bookings, not visits
                    status__in=[
                        "pending",
                        "confirmed",
                    ],  # Don't show button if booking is pending or confirmed
                ).exists()

                # Check if user has already requested a visit for this property
                context["has_visit_request"] = PropertyBooking.objects.filter(
                    customer=self.request.user,
                    property_ref=self.object,
                    booking_type="visit",  # Only visit requests
                    status__in=[
                        "pending",
                        "confirmed",
                    ],  # Don't show button if visit is pending or confirmed
                ).exists()

                # Check if ANY user has booked this property (not visited) - to disable booking
                context["is_booked_by_anyone"] = PropertyBooking.objects.filter(
                    property_ref=self.object,
                    booking_type="booking",  # Only actual bookings, not visits
                    status="confirmed",  # Only confirmed bookings
                ).exists()

                # Get all blocked visit dates for this property (dates already taken by other users)
                blocked_dates = list(
                    PropertyBooking.objects.filter(
                        property_ref=self.object,
                        booking_type="visit",
                        status__in=["pending", "confirmed"],
                        preferred_date__isnull=False,
                    ).values_list("preferred_date", flat=True)
                )

                # Convert datetime objects to date strings for JavaScript
                import json
                from django.core.serializers.json import DjangoJSONEncoder

                context["blocked_visit_dates"] = json.dumps(
                    [date.strftime("%Y-%m-%d") for date in blocked_dates if date],
                    cls=DjangoJSONEncoder,
                )

                # Count of people visiting this property
                context["visit_count"] = PropertyBooking.objects.filter(
                    property_ref=self.object,
                    booking_type="visit",
                    status__in=["pending", "confirmed"],
                ).count()

                SearchHistory.objects.create(
                    user=self.request.user,
                    query=self.object.title,
                    property=self.object,
                )
        return context


@method_decorator(login_required, name="dispatch")
class AgentPropertyListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Property
    template_name = "properties/agent_properties.html"
    context_object_name = "properties"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_agent()

    def get_queryset(self):
        return Property.objects.filter(agent=self.request.user).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        properties = self.get_queryset()
        context["available_count"] = properties.filter(status="available").count()
        context["pending_count"] = properties.filter(status="pending").count()
        context["sold_count"] = properties.filter(status="sold").count()

        return context


@method_decorator(login_required, name="dispatch")
class PropertyCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = "properties/property_form.html"
    success_url = reverse_lazy("properties:agent_properties")

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_agent()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["image_form"] = PropertyImageForm()
        return context

    def form_valid(self, form):
        form.instance.agent = self.request.user
        response = super().form_valid(form)

        image_form = PropertyImageForm(self.request.POST, self.request.FILES)
        if image_form.is_valid():
            images = self.request.FILES.getlist('images')
            order = 0
            for image in images:
                PropertyImage.objects.create(
                    property=self.object, 
                    image=image, 
                    order=order,
                    caption='',  # Default empty caption
                    is_primary=(order == 0)  # First image is primary
                )
                order += 1
        messages.success(self.request, "Property listing created successfully.")
        return response


@method_decorator(login_required, name="dispatch")
class PropertyUpdateView(UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = "properties/property_form.html"
    success_url = reverse_lazy("properties:agent_properties")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.agent != request.user:
            messages.error(request, "You can only edit your own listings.")
            return redirect("properties:agent_properties")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)

        image_form = PropertyImageForm(self.request.POST, self.request.FILES)
        if image_form.is_valid():
            images = self.request.FILES.getlist('images')
            current_max_order = self.object.images.order_by("-order").first()
            order = (current_max_order.order + 1) if current_max_order else 0

            for image in images:
                PropertyImage.objects.create(
                    property=self.object, 
                    image=image, 
                    order=order,
                    caption='',  # Default empty caption
                    is_primary=False  # New images are not primary by default
                )
                order += 1
        messages.success(self.request, "Property listing updated successfully.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["image_form"] = PropertyImageForm()
        context["existing_images"] = self.object.images.all()
        return context


@method_decorator(login_required, name="dispatch")
class PropertyDeleteView(DeleteView):
    model = Property
    template_name = "properties/property_confirm_delete.html"
    success_url = reverse_lazy("properties:agent_properties")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.agent != request.user:
            messages.error(request, "You can only delete your own listings.")
            return redirect("properties:agent_properties")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Property listing deleted successfully.")
        return super().delete(request, *args, **kwargs)


@login_required
@require_POST
def toggle_favorite(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user, property=property_obj
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
                status="available",
                property_type=property_obj.property_type,
                listing_type=property_obj.listing_type,
            ).exclude(id=property_obj.id)[:10]

            if similar_properties:
                update_recommendations(
                    request.user,
                    f"Properties like {property_obj.title}",
                    similar_properties,
                )

    return JsonResponse(
        {
            "success": True,
            "is_favorite": is_favorite,
            "message": f"{property_obj.title} {action} favorites.",
        }
    )


@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related("property")
    return render(request, "properties/favorites.html", {"favorites": favorites})


@login_required
def delete_property_image(request, image_id):
    if request.method == 'POST':
        try:
            image = get_object_or_404(PropertyImage, pk=image_id)
            
            # Check if the user is the agent of the property
            if request.user != image.property.agent:
                return JsonResponse({'success': False, 'error': 'You can only delete images from your own listings.'})

            image.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def set_primary_property_image(request, image_id):
    if request.method == 'POST':
        try:
            image = get_object_or_404(PropertyImage, pk=image_id)
            
            # Check if the user is the agent of the property
            if request.user != image.property.agent:
                return JsonResponse({'success': False, 'error': 'You can only modify images from your own listings.'})

            # Remove primary status from all images of this property
            PropertyImage.objects.filter(property=image.property).update(is_primary=False)
            
            # Set this image as primary
            image.is_primary = True
            image.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def update_image_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            images_data = data.get('images', [])
            
            for image_data in images_data:
                image_id = image_data.get('id')
                order = image_data.get('order')
                
                image = get_object_or_404(PropertyImage, pk=image_id)
                
                # Check if the user is the agent of the property
                if request.user != image.property.agent:
                    return JsonResponse({'success': False, 'error': 'You can only modify images from your own listings.'})
                
                image.order = order
                image.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
@require_POST
def update_property_status(request, pk):
    try:
        data = json.loads(request.body)
        status = data.get("status")

        if status not in [choice[0] for choice in Property.STATUS_CHOICES]:
            return JsonResponse({"success": False, "message": "Invalid status"})

        property_obj = Property.objects.get(pk=pk)

        # Check if the user is the agent of the property
        if request.user != property_obj.agent:
            return JsonResponse(
                {
                    "success": False,
                    "message": "You can only update status of your own listings",
                }
            )

        property_obj.status = status
        property_obj.save()

        return JsonResponse(
            {
                "success": True,
                "message": f"Property status updated to {property_obj.get_status_display()}",
                "status_display": property_obj.get_status_display(),
            }
        )
    except Property.DoesNotExist:
        return JsonResponse({"success": False, "message": "Property not found"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
def similar_properties(request, pk):
    try:
        property_obj = get_object_or_404(Property, pk=pk)

        # Define keyword groups for semantic similarity - separated by property category
        keyword_groups = {
            # Residential-specific keywords
            'luxury_residential': ['luxury', 'premium', 'elegant', 'upscale', 'high-end', 'deluxe', 'exclusive', 'sophisticated', 'executive', 'prestige'],
            'cozy': ['cozy', 'comfortable', 'warm', 'inviting', 'charming', 'intimate', 'homely', 'snug', 'cute', 'lovely'],
            'modern_residential': ['modern', 'contemporary', 'stylish', 'updated', 'renovated', 'new', 'sleek', 'chic', 'fresh', 'latest'],
            'spacious_residential': ['spacious', 'large', 'big', 'roomy', 'vast', 'expansive', 'wide', 'generous', 'huge', 'massive'],
            'beautiful': ['beautiful', 'stunning', 'gorgeous', 'lovely', 'attractive', 'magnificent', 'spectacular', 'amazing', 'wonderful', 'fantastic'],
            'quiet': ['quiet', 'peaceful', 'serene', 'tranquil', 'calm', 'silent', 'secluded', 'private', 'noise-free'],
            'family': ['family', 'kids', 'children', 'school', 'playground', 'safe', 'friendly', 'child-friendly', 'residential'],
            'garden': ['garden', 'yard', 'outdoor', 'green', 'lawn', 'patio', 'terrace', 'balcony', 'landscaped', 'park'],
            
            # Specific view categories for residential
            'lake_view': ['lake', 'lakeside', 'waterfront', 'lake view', 'lakefront'],
            'garden_view': ['garden view', 'garden facing', 'overlooks garden', 'garden-facing'],
            'mountain_view': ['mountain', 'mountain view', 'hills', 'hillside', 'mountainside'],
            'city_view': ['city view', 'cityscape', 'urban view', 'downtown view'],
            'sea_view': ['sea', 'ocean', 'sea view', 'ocean view', 'beachfront', 'seaside'],
            'river_view': ['river', 'river view', 'riverside', 'riverfront'],
            'park_view': ['park view', 'park facing', 'overlooks park', 'park-facing'],
            
            # Commercial/Office-specific keywords
            'office_space': ['office', 'workspace', 'business center', 'corporate', 'professional'],
            'commercial': ['commercial', 'business', 'shop', 'retail', 'store', 'showroom'],
            'modern_office': ['modern office', 'contemporary workspace', 'tech-ready', 'it-enabled', 'smart office'],
            'premium_office': ['premium office', 'grade a', 'class a', 'executive suite', 'corner office'],
            'shared_space': ['coworking', 'shared office', 'flexible workspace', 'hot desk', 'co-working'],
            
            # Common categories (applicable to both)
            'convenient': ['convenient', 'accessible', 'central', 'nearby', 'close', 'walking', 'transport', 'location'],
            'affordable': ['affordable', 'budget', 'cheap', 'economical', 'reasonable', 'value', 'low-cost'],
            'furnished': ['furnished', 'equipped', 'ready', 'complete', 'move-in'],
            'security': ['secure', 'gated', 'protected', 'safe', 'guard', 'security'],
            'parking': ['parking', 'garage', 'car', 'vehicle', 'covered'],
            'investment': ['investment', 'rental', 'income', 'profitable', 'return']
        }
        
        def extract_keywords(title):
            """Extract keywords from property title"""
            title_lower = title.lower()
            found_keywords = set()
            
            # Check for multi-word phrases first (more specific)
            for group_name, keywords in keyword_groups.items():
                for keyword in keywords:
                    if len(keyword.split()) > 1:  # Multi-word phrases
                        if keyword in title_lower:
                            found_keywords.add(group_name)
                            break
            
            # Then check for single words (only if no multi-word match in same group)
            for group_name, keywords in keyword_groups.items():
                if group_name not in found_keywords:  # Only if not already matched
                    for keyword in keywords:
                        if len(keyword.split()) == 1:  # Single words
                            if keyword in title_lower:
                                found_keywords.add(group_name)
                                break
            
            return found_keywords
        
        def calculate_title_similarity(title1, title2):
            """Calculate similarity score between two titles based on keywords and direct word matching"""
            keywords1 = extract_keywords(title1)
            keywords2 = extract_keywords(title2)
            
            # Calculate keyword group similarity
            keyword_similarity = 0.0
            if keywords1 or keywords2:
                intersection = len(keywords1.intersection(keywords2))
                union = len(keywords1.union(keywords2))
                keyword_similarity = intersection / union if union > 0 else 0.0
            
            # Calculate direct word similarity (excluding common words and being more precise)
            exclude_words = {'for', 'sale', 'rent', 'at', 'in', 'the', 'and', 'or', 'with', 'a', 'an', 'is', 'are', 'be', 'by', 'on', 'to', 'from'}
            
            title1_words = set()
            title2_words = set()
            
            # Extract meaningful words (length > 2, not common words)
            for word in title1.split():
                clean_word = word.lower().strip('.,!?()[]{}";:')
                if len(clean_word) > 2 and clean_word not in exclude_words:
                    title1_words.add(clean_word)
            
            for word in title2.split():
                clean_word = word.lower().strip('.,!?()[]{}";:')
                if len(clean_word) > 2 and clean_word not in exclude_words:
                    title2_words.add(clean_word)
            
            word_similarity = 0.0
            if title1_words or title2_words:
                # Only count exact word matches (no partial matches)
                word_intersection = len(title1_words.intersection(title2_words))
                word_union = len(title1_words.union(title2_words))
                word_similarity = word_intersection / word_union if word_union > 0 else 0.0
            
            # Combine both similarities (70% keyword groups, 30% direct words)
            final_similarity = (keyword_similarity * 0.7) + (word_similarity * 0.3)
            
            return final_similarity
        
        def get_property_category(property_obj):
            """Simple category detection - only separate clear commercial properties"""
            title_lower = property_obj.title.lower()
            
            # Only treat as commercial if explicitly commercial
            clear_commercial = ['office space', 'business center', 'commercial building', 'retail space', 'warehouse']
            
            if any(keyword in title_lower for keyword in clear_commercial):
                return 'commercial'
            else:
                return 'residential'  # Default to residential for broader matching
        
        # Get category of current property
        current_category = get_property_category(property_obj)
        
        # Get all available properties except the current one
        all_properties = Property.objects.filter(
            status="available"
        ).exclude(id=property_obj.id).select_related("agent").prefetch_related("images")
        
        # Be more inclusive with compatible properties
        compatible_properties = []
        for prop in all_properties:
            prop_category = get_property_category(prop)
            # Include if same category OR if we don't have many properties
            if prop_category == current_category or len(all_properties) <= 10:
                compatible_properties.append(prop)
        
        # If still no compatible properties, use all
        if not compatible_properties:
            compatible_properties = list(all_properties)
        
        # Score properties based on title similarity primarily
        property_scores = []
        
        for prop in compatible_properties:
            score = 0.0
            
            # 1. Title similarity (80% weight) - PRIMARY FACTOR
            title_similarity = calculate_title_similarity(property_obj.title, prop.title)
            score += title_similarity * 0.8
            
            # 2. Price range similarity (15% weight) - SECONDARY
            price_ratio = min(float(prop.price), float(property_obj.price)) / max(float(prop.price), float(property_obj.price))
            if price_ratio >= 0.5:  # Within 50% price range
                score += 0.15 * price_ratio
            
            # 3. Location similarity (5% weight) - MINOR
            # Check if they share similar location keywords
            prop_address_words = set(prop.address.lower().split())
            current_address_words = set(property_obj.address.lower().split())
            location_overlap = len(prop_address_words.intersection(current_address_words))
            if location_overlap > 0:
                score += 0.05 * min(location_overlap / 3, 1.0)  # Cap at 3 word matches
            
            # Extract words from both titles for comparison
            current_words = set(word.lower().strip('.,!?()[]{}";:') for word in property_obj.title.split() 
                               if len(word) > 2 and word.lower() not in ['for', 'sale', 'rent', 'at', 'in', 'the', 'and', 'or', 'with', 'a', 'an'])
            prop_words = set(word.lower().strip('.,!?()[]{}";:') for word in prop.title.split() 
                            if len(word) > 2 and word.lower() not in ['for', 'sale', 'rent', 'at', 'in', 'the', 'and', 'or', 'with', 'a', 'an'])
            
            shared_words = current_words.intersection(prop_words)
            
            # Simplified matching criteria - focus on title similarity
            has_strong_similarity = title_similarity > 0.2  # 20%+ similarity
            has_moderate_similarity = title_similarity > 0.1  # 10%+ similarity  
            has_word_match = len(shared_words) >= 2  # At least 2 shared words
            has_single_word_match = len(shared_words) >= 1  # At least 1 shared word
            has_same_type = prop.property_type == property_obj.property_type  # Same property type
            
            # Include property if it meets any criteria (be inclusive to ensure we get results)
            if (has_strong_similarity or has_moderate_similarity or 
                has_word_match or has_single_word_match or has_same_type):
                property_scores.append((prop, score))
        
        # Sort by score and get properties
        property_scores.sort(key=lambda x: x[1], reverse=True)
        similar = [prop for prop, score in property_scores[:6]]
        
        # If we don't have enough matches, be more lenient
        if len(similar) < 3:
            # Add properties from same category regardless of similarity score
            remaining_compatible = [p for p in compatible_properties if p not in similar]
            similar.extend(remaining_compatible[:3-len(similar)])
        
        # If still not enough, add any available properties
        if len(similar) < 2:
            any_available = [p for p in all_properties if p not in similar]
            similar.extend(any_available[:2-len(similar)])

        data = []
        for prop in similar:
            # Calculate title similarity percentage
            title_similarity = calculate_title_similarity(property_obj.title, prop.title)
            match_percentage = max(int(title_similarity * 100), 10)  # Minimum 10% to show something
            
            # Simple similarity reasons based on title analysis
            similarity_reasons = []
            
            # Check for shared keywords
            current_keywords = extract_keywords(property_obj.title)
            prop_keywords = extract_keywords(prop.title)
            shared_keywords = current_keywords.intersection(prop_keywords)
            
            if shared_keywords:
                similarity_reasons.append(f"Similar features: {', '.join(list(shared_keywords)[:2])}")
            
            # Check for shared words in title
            current_words = set(word.lower().strip('.,!?()[]{}";:') for word in property_obj.title.split() 
                               if len(word) > 2)
            prop_words = set(word.lower().strip('.,!?()[]{}";:') for word in prop.title.split() 
                            if len(word) > 2)
            shared_words = current_words.intersection(prop_words)
            
            if shared_words and not shared_keywords:
                word_list = [word for word in shared_words if word not in ['for', 'sale', 'rent', 'apartment', 'house']]
                if word_list:
                    similarity_reasons.append(f"Shared terms: {', '.join(list(word_list)[:2])}")
            
            # Add property type if same
            if prop.property_type == property_obj.property_type:
                similarity_reasons.append(f"Same type: {prop.get_property_type_display()}")
            
            # Add bedroom similarity
            if prop.bedrooms == property_obj.bedrooms:
                similarity_reasons.append(f"Same size: {prop.bedrooms} bedrooms")
            
            # If no specific reasons, add generic one
            if not similarity_reasons:
                similarity_reasons.append("Available property")
            
            data.append({
                "id": prop.id,
                "title": prop.title,
                "address": prop.address,
                "price": float(prop.price),
                "bedrooms": prop.bedrooms,
                "bathrooms": float(prop.bathrooms),
                "thumbnail": prop.get_thumbnail(),
                "agent": prop.agent.get_full_name() or prop.agent.username,
                "has_image": prop.images.exists(),
                "similarity_reasons": similarity_reasons,
                "similarity_score": match_percentage  # Show as percentage
            })

        return JsonResponse({"properties": data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Testing
@require_POST
@login_required
def send_message(request, property_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Only POST method allowed"})

    property = get_object_or_404(Property, id=property_id)
    content = request.POST.get("message")

    if not content:
        return JsonResponse({"success": False, "message": "Message cannot be empty"})

    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "message": "Please log in to send messages"}
        )

    # Allow both customers and other users to send messages to agents
    try:
        PropertyMessage.objects.create(
            property=property, sender=request.user, content=content
        )

        # If this is an AJAX request, return JSON
        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest" or "application/json" in request.headers.get(
            "Accept", ""
        ):
            return JsonResponse(
                {
                    "success": True,
                    "message": "Your message has been sent successfully!",
                    "agent_name": property.agent.get_full_name()
                    or property.agent.username,
                }
            )
        else:
            messages.success(request, "Your message has been sent.")
            return redirect("properties:property_detail", pk=property_id)

    except Exception as e:
        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest" or "application/json" in request.headers.get(
            "Accept", ""
        ):
            return JsonResponse(
                {
                    "success": False,
                    "message": "Failed to send message. Please try again.",
                }
            )
        else:
            messages.error(request, "Failed to send message. Please try again.")
            return redirect("properties:property_detail", pk=property_id)


def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["is_favorite"] = Favorite.objects.filter(
        user=self.request.user, property=self.object
    ).exists()
    context["messages"] = self.object.messages.order_by("timestamp").all()
    return context


@login_required
def message_inbox(request):
    """
    Agent's message inbox - shows all messages for their properties
    """
    if not request.user.is_agent():
        messages.warning(request, "This feature is only available to agents.")
        return redirect("properties:property_list")

    # Get all messages for agent's properties
    agent_messages = (
        PropertyMessage.objects.filter(property__agent=request.user)
        .select_related("sender", "property")
        .order_by("-timestamp")
    )

    # Filter by status if requested
    status_filter = request.GET.get("status")
    if status_filter == "unread":
        agent_messages = agent_messages.filter(read=False)
    elif status_filter == "read":
        agent_messages = agent_messages.filter(read=True)

    # Search functionality
    search = request.GET.get("search")
    if search:
        agent_messages = agent_messages.filter(
            Q(content__icontains=search)
            | Q(sender__first_name__icontains=search)
            | Q(sender__last_name__icontains=search)
            | Q(property__title__icontains=search)
        )

    context = {
        "messages": agent_messages,
        "unread_count": agent_messages.filter(read=False).count(),
        "total_count": agent_messages.count(),
        "status_filter": status_filter,
        "search": search,
    }

    return render(request, "properties/message_inbox.html", context)


@login_required
@require_POST
def mark_message_read(request, message_id):
    """
    Mark a message as read (AJAX endpoint)
    """
    try:
        message = get_object_or_404(
            PropertyMessage, id=message_id, property__agent=request.user
        )
        message.read = True
        message.save()

        return JsonResponse({"success": True, "message": "Message marked as read"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
