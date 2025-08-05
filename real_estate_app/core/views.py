from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from properties.models import Property
from search.models import Recommendation
from accounts.models import User

def index(request):
    featured_properties = Property.objects.filter(status='available').order_by('-created_at')[:6]
    return render(request, 'core/index.html', {
        'featured_properties': featured_properties
    })

@login_required
def dashboard(request):
    context = {
        'user': request.user,
    }
    
    if request.user.is_agent():
        # For agents, show their properties and statistics
        agent_properties = Property.objects.filter(agent=request.user).order_by('-created_at')
        context['properties'] = agent_properties[:5]
        context['user_properties'] = agent_properties
        context['total_properties'] = agent_properties.count()
        context['available_properties'] = agent_properties.filter(status='available').count()
        context['sold_properties'] = agent_properties.filter(status='sold').count()
        context['pending_properties'] = agent_properties.filter(status='pending').count()
        
        # Calculate total value of agent's properties
        total_value = agent_properties.aggregate(
            total=Sum('price')
        )['total'] or 0
        context['total_value'] = total_value
        
        # Get recent messages for agent's properties
        from properties.models import PropertyMessage
        recent_messages = PropertyMessage.objects.filter(
            property__agent=request.user
        ).select_related('sender', 'property').order_by('-timestamp')[:5]
        context['recent_messages'] = recent_messages
        context['unread_messages_count'] = PropertyMessage.objects.filter(
            property__agent=request.user,
            read=False
        ).count()
        context['total_messages'] = PropertyMessage.objects.filter(
            property__agent=request.user
        ).count()
        
    else:
        # For customers, show recommendations and favorites
        try:
            recommendations = Recommendation.objects.filter(
                user=request.user,
                property__status='available'
            ).select_related('property')
            context['recommendations'] = recommendations[:5]
            context['total_recommendations'] = recommendations.count()
        except:
            context['recommendations'] = []
            context['total_recommendations'] = 0
        
        # Get user's favorites
        try:
            favorites = request.user.favorites.all().select_related('property')
            context['favorites'] = favorites[:5]
            context['recent_favorites'] = favorites[:5]  # Also pass as recent_favorites for template
            context['total_favorites'] = favorites.count()
        except:
            context['favorites'] = []
            context['recent_favorites'] = []
            context['total_favorites'] = 0
        
        # Get total available properties
        context['total_properties'] = Property.objects.filter(status='available').count()
        
        # Calculate days since user joined
        from datetime import date
        days_since_joined = (date.today() - request.user.date_joined.date()).days
        context['days_since_joined'] = days_since_joined
    
    return render(request, 'core/dashboard.html', context)