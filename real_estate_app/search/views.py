from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from properties.models import Property
from .models import SearchHistory, Recommendation
import datetime
from properties.models import Property, Favorite

try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except:
    model = None

@login_required
def search_properties(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Save search query
        SearchHistory.objects.create(
            user=request.user,
            query=query
        )
        
        # Basic keyword search
        basic_results = Property.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(address__icontains=query)
        ).filter(status='available')
        
        # Semantic search if model is available
        if model and len(basic_results) > 0:
            try:
                # Get all property descriptions and titles
                properties = Property.objects.filter(status='available')
                property_texts = [f"{p.title} {p.description}" for p in properties]
                
                # Encode query and property descriptions
                query_embedding = model.encode([query])
                property_embeddings = model.encode(property_texts)
                
                # Calculate similarity
                similarities = cosine_similarity(query_embedding, property_embeddings)[0]
                
                # Get most similar properties
                similar_indices = np.argsort(similarities)[::-1]
                
                # Get top results
                results = [properties[i] for i in similar_indices if similarities[i] > 0.2]
            except Exception as e:
                # Fallback to basic search if semantic search fails
                print(f"Semantic search failed: {str(e)}")
                results = basic_results
        else:
            results = basic_results
    
    favorite_property_ids = []
    if request.user.is_authenticated and hasattr(request.user, 'is_customer') and callable(getattr(request.user, 'is_customer', None)) and request.user.is_customer():
        favorite_property_ids = list(
            Favorite.objects.filter(user=request.user)
            .values_list('property__id', flat=True)
        )
        
        # Update recommendations based on search query and results
        if query and results:
            update_recommendations(request.user, query, results)
    
    return render(request, 'search/search_results.html', {
        'query': query,
        'results': results,
        'favorite_property_ids': favorite_property_ids,
        'current_time': datetime.datetime.now()
    })

@login_required
def recommendations_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
        
    recommendations = Recommendation.objects.filter(user=request.user).order_by('-score')
    
    # Get favorite property IDs for the current user
    favorite_property_ids = []
    if hasattr(request.user, 'is_customer') and callable(getattr(request.user, 'is_customer', None)):
        if request.user.is_customer():
            favorite_property_ids = list(
                Favorite.objects.filter(user=request.user)
                .values_list('property__id', flat=True)
            )
    
    return render(request, 'search/recommendations.html', {
        'recommendations': recommendations,
        'favorite_property_ids': favorite_property_ids,
        'current_time': datetime.datetime.now()
    })

def update_recommendations(user, query, results):
    # Clear old recommendations
    if len(results) > 0:
        for i, property_obj in enumerate(results):
            # Higher score for higher ranked properties
            score = 1.0 - (i * 0.05)  # Score decreases with rank
            
            # Create or update recommendation
            Recommendation.objects.update_or_create(
                user=user,
                property=property_obj,
                defaults={'score': score}
            )