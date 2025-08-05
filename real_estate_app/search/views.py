from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import json
import re
import datetime
from collections import Counter

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    model = SentenceTransformer('all-MiniLM-L6-v2')
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError:
    model = None
    SEMANTIC_SEARCH_AVAILABLE = False
    print("Warning: Semantic search dependencies not available. Install sentence-transformers and scikit-learn for enhanced search.")

from properties.models import Property, Favorite
from .models import SearchHistory, Recommendation

class SmartSearchEngine:
    """Advanced search engine with semantic understanding"""
    
    def __init__(self):
        self.property_type_synonyms = {
            'house': ['home', 'villa', 'residence', 'dwelling', 'mansion'],
            'apartment': ['flat', 'unit', 'condo', 'condominium', 'studio'],
            'villa': ['mansion', 'estate', 'luxury home'],
            'condo': ['condominium', 'apartment', 'unit']
        }
        
        self.feature_keywords = {
            'luxury': ['premium', 'high-end', 'upscale', 'deluxe', 'exclusive'],
            'modern': ['contemporary', 'new', 'updated', 'renovated', 'stylish'],
            'spacious': ['large', 'big', 'roomy', 'wide', 'expansive'],
            'cozy': ['comfortable', 'intimate', 'charming', 'warm'],
            'family': ['kids', 'children', 'school', 'playground'],
            'downtown': ['city center', 'urban', 'central', 'metro'],
            'quiet': ['peaceful', 'serene', 'calm', 'tranquil'],
            'view': ['scenery', 'vista', 'outlook', 'panoramic']
        }
        
        self.location_keywords = {
            'near': ['close to', 'nearby', 'walking distance', 'next to'],
            'downtown': ['city center', 'central', 'urban core'],
            'suburban': ['suburbs', 'residential area', 'quiet neighborhood']
        }

    def extract_search_intent(self, query):
        """Extract search intent and key features from query"""
        query_lower = query.lower()
        intent = {
            'property_types': [],
            'features': [],
            'price_range': None,
            'bedrooms': None,
            'bathrooms': None,
            'location_hints': [],
            'semantic_keywords': []
        }
        
        # Extract property types
        for prop_type, synonyms in self.property_type_synonyms.items():
            if prop_type in query_lower or any(syn in query_lower for syn in synonyms):
                intent['property_types'].append(prop_type)
        
        # Extract features
        for feature, keywords in self.feature_keywords.items():
            if feature in query_lower or any(kw in query_lower for kw in keywords):
                intent['features'].append(feature)
        
        # Extract numbers (bedrooms, bathrooms, price)
        numbers = re.findall(r'\d+', query)
        
        # Look for bedroom/bathroom indicators
        if 'bedroom' in query_lower or 'bed' in query_lower:
            bed_match = re.search(r'(\d+)\s*(?:bedroom|bed)', query_lower)
            if bed_match:
                intent['bedrooms'] = int(bed_match.group(1))
        
        if 'bathroom' in query_lower or 'bath' in query_lower:
            bath_match = re.search(r'(\d+)\s*(?:bathroom|bath)', query_lower)
            if bath_match:
                intent['bathrooms'] = int(bath_match.group(1))
        
        # Extract price indicators
        price_keywords = ['under', 'below', 'max', 'budget', 'affordable', 'cheap']
        expensive_keywords = ['luxury', 'premium', 'expensive', 'high-end']
        
        if any(kw in query_lower for kw in price_keywords):
            intent['price_range'] = 'low'
        elif any(kw in query_lower for kw in expensive_keywords):
            intent['price_range'] = 'high'
        
        # Extract location hints
        for location, keywords in self.location_keywords.items():
            if location in query_lower or any(kw in query_lower for kw in keywords):
                intent['location_hints'].append(location)
        
        # Store original query words for semantic matching
        intent['semantic_keywords'] = [word for word in query_lower.split() 
                                     if len(word) > 2 and word not in ['the', 'and', 'with', 'for', 'near']]
        
        return intent

    def build_smart_query(self, intent):
        """Build Django Q query based on extracted intent"""
        query = Q(status='available')
        
        # Property type filtering
        if intent['property_types']:
            type_query = Q()
            for prop_type in intent['property_types']:
                type_query |= Q(property_type=prop_type)
            query &= type_query
        
        # Bedroom filtering
        if intent['bedrooms']:
            query &= Q(bedrooms__gte=intent['bedrooms'])
        
        # Bathroom filtering  
        if intent['bathrooms']:
            query &= Q(bathrooms__gte=intent['bathrooms'])
        
        # Price range filtering
        if intent['price_range']:
            if intent['price_range'] == 'low':
                query &= Q(price__lte=5000000)  # Under 50 lakh
            elif intent['price_range'] == 'high':
                query &= Q(price__gte=10000000)  # Above 1 crore
        
        # Text-based filtering (title, description, address)
        text_query = Q()
        for keyword in intent['semantic_keywords']:
            text_query |= (
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(address__icontains=keyword)
            )
        
        if text_query:
            query &= text_query
        
        return query

    def perform_semantic_search(self, query, properties):
        """Perform semantic search using sentence transformers"""
        if not SEMANTIC_SEARCH_AVAILABLE or not properties.exists():
            return properties
        
        try:
            # Prepare property texts for embedding
            property_texts = []
            property_objects = list(properties)
            
            for prop in property_objects:
                # Create rich text representation
                text = f"{prop.title} {prop.description} {prop.address} "
                text += f"{prop.get_property_type_display()} {prop.get_listing_type_display()} "
                text += f"{prop.bedrooms} bedroom {prop.bathrooms} bathroom "
                text += f"{prop.square_footage} square feet"
                property_texts.append(text)
            
            # Generate embeddings
            query_embedding = model.encode([query])
            property_embeddings = model.encode(property_texts)
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, property_embeddings)[0]
            
            # Sort by similarity and filter by threshold
            similarity_threshold = 0.15  # Lowered threshold for more results
            property_scores = list(zip(property_objects, similarities))
            property_scores = [(prop, score) for prop, score in property_scores if score > similarity_threshold]
            property_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return sorted properties
            sorted_properties = [prop for prop, score in property_scores]
            return sorted_properties
            
        except Exception as e:
            print(f"Semantic search error: {str(e)}")
            return properties

search_engine = SmartSearchEngine()

@login_required
def search_properties(request):
    """Enhanced property search with semantic understanding"""
    query = request.GET.get('q', '').strip()
    results = []
    search_metadata = {
        'semantic_available': SEMANTIC_SEARCH_AVAILABLE,
        'intent': None,
        'total_properties': Property.objects.filter(status='available').count()
    }
    
    if query:
        # Save search history
        SearchHistory.objects.create(user=request.user, query=query)
        
        # Extract search intent
        intent = search_engine.extract_search_intent(query)
        search_metadata['intent'] = intent
        
        # Build smart query
        smart_query = search_engine.build_smart_query(intent)
        filtered_properties = Property.objects.filter(smart_query)
        
        # Apply semantic search if available
        if SEMANTIC_SEARCH_AVAILABLE and len(query.split()) > 1:
            results = search_engine.perform_semantic_search(query, filtered_properties)
        else:
            # Fallback to filtered results
            results = list(filtered_properties.order_by('-created_at'))
        
        # Limit results for performance
        results = results[:50]
        
        # Update user recommendations
        if results:
            update_recommendations(request.user, query, results[:10])
    
    # Get user favorites
    favorite_property_ids = []
    if request.user.is_authenticated and hasattr(request.user, 'is_customer'):
        if callable(getattr(request.user, 'is_customer', None)) and request.user.is_customer():
            favorite_property_ids = list(
                Favorite.objects.filter(user=request.user)
                .values_list('property__id', flat=True)
            )
    
    context = {
        'query': query,
        'results': results,
        'favorite_property_ids': favorite_property_ids,
        'current_time': datetime.datetime.now(),
        'search_metadata': search_metadata,
        'semantic_available': SEMANTIC_SEARCH_AVAILABLE
    }
    
    return render(request, 'search/search_results.html', context)

@require_GET
def search_suggestions(request):
    """API endpoint for search suggestions"""
    query = request.GET.get('q', '').strip()
    suggestions = []
    
    if len(query) >= 2:
        # Get recent searches
        recent_searches = SearchHistory.objects.filter(
            query__icontains=query
        ).values_list('query', flat=True).distinct()[:5]
        
        # Get property titles and addresses that match
        property_matches = Property.objects.filter(
            Q(title__icontains=query) | Q(address__icontains=query),
            status='available'
        ).values_list('title', 'address')[:5]
        
        # Combine suggestions
        suggestions.extend(list(recent_searches))
        suggestions.extend([f"{title} - {address}" for title, address in property_matches])
        
        # Remove duplicates and limit
        suggestions = list(set(suggestions))[:8]
    
    return JsonResponse({'suggestions': suggestions})

@login_required
def recommendations_view(request):
    """Display personalized property recommendations"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    # Get user's recommendations
    recommendations = Recommendation.objects.filter(
        user=request.user
    ).select_related('property').order_by('-score')[:20]
    
    # Get user's search history for context
    recent_searches = SearchHistory.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:10]
    
    # Analyze user preferences
    user_preferences = analyze_user_preferences(request.user)
    
    # Get favorite property IDs
    favorite_property_ids = []
    if hasattr(request.user, 'is_customer') and callable(getattr(request.user, 'is_customer', None)):
        if request.user.is_customer():
            favorite_property_ids = list(
                Favorite.objects.filter(user=request.user)
                .values_list('property__id', flat=True)
            )
    
    context = {
        'recommendations': recommendations,
        'recent_searches': recent_searches,
        'user_preferences': user_preferences,
        'favorite_property_ids': favorite_property_ids,
        'current_time': datetime.datetime.now()
    }
    
    return render(request, 'search/recommendations.html', context)

def analyze_user_preferences(user):
    """Analyze user's search and favorite patterns"""
    # Get user's search queries
    searches = SearchHistory.objects.filter(user=user).values_list('query', flat=True)
    
    # Get user's favorite properties
    favorites = Favorite.objects.filter(user=user).select_related('property')
    
    preferences = {
        'property_types': Counter(),
        'price_ranges': Counter(),
        'common_keywords': Counter(),
        'bedroom_preferences': Counter(),
        'favorite_count': favorites.count()
    }
    
    # Analyze favorite properties
    for favorite in favorites:
        prop = favorite.property
        preferences['property_types'][prop.property_type] += 1
        preferences['bedroom_preferences'][prop.bedrooms] += 1
        
        # Categorize price ranges
        if prop.price < 3000000:
            preferences['price_ranges']['budget'] += 1
        elif prop.price < 8000000:
            preferences['price_ranges']['mid-range'] += 1
        else:
            preferences['price_ranges']['luxury'] += 1
    
    # Analyze search queries
    all_words = []
    for search_query in searches:
        words = search_query.lower().split()
        all_words.extend([word for word in words if len(word) > 3])
    
    preferences['common_keywords'] = Counter(all_words).most_common(10)
    
    return preferences

def update_recommendations(user, query, results):
    """Update user recommendations based on search results with enhanced keyword matching"""
    if not results:
        return
    
    # Define keyword groups for semantic similarity (same as in properties/views.py)
    keyword_groups = {
        'luxury': ['luxury', 'premium', 'elegant', 'upscale', 'high-end', 'deluxe', 'exclusive', 'sophisticated'],
        'cozy': ['cozy', 'comfortable', 'warm', 'inviting', 'charming', 'intimate', 'homely', 'snug'],
        'modern': ['modern', 'contemporary', 'stylish', 'updated', 'renovated', 'new', 'sleek', 'chic'],
        'spacious': ['spacious', 'large', 'big', 'roomy', 'vast', 'expansive', 'wide', 'generous'],
        'beautiful': ['beautiful', 'stunning', 'gorgeous', 'lovely', 'attractive', 'magnificent', 'spectacular'],
        'quiet': ['quiet', 'peaceful', 'serene', 'tranquil', 'calm', 'silent', 'secluded'],
        'family': ['family', 'kids', 'children', 'school', 'playground', 'safe', 'friendly'],
        'garden': ['garden', 'yard', 'outdoor', 'green', 'lawn', 'patio', 'terrace', 'balcony'],
        'view': ['view', 'scenic', 'mountain', 'valley', 'city', 'panoramic', 'overlooking'],
        'convenient': ['convenient', 'accessible', 'central', 'nearby', 'close', 'walking', 'transport']
    }
    
    def extract_keywords_from_query(query_text):
        """Extract semantic keywords from search query"""
        query_lower = query_text.lower()
        found_keywords = set()
        
        for group_name, keywords in keyword_groups.items():
            for keyword in keywords:
                if keyword in query_lower:
                    found_keywords.add(group_name)
                    break
        
        return found_keywords
    
    def calculate_property_relevance(property_obj, query_keywords):
        """Calculate how relevant a property is to the search query"""
        property_title_lower = property_obj.title.lower()
        property_desc_lower = property_obj.description.lower()
        
        property_keywords = set()
        for group_name, keywords in keyword_groups.items():
            for keyword in keywords:
                if keyword in property_title_lower or keyword in property_desc_lower:
                    property_keywords.add(group_name)
                    break
        
        if not query_keywords or not property_keywords:
            return 0.5  # Base relevance for non-semantic matches
        
        # Calculate Jaccard similarity
        intersection = len(query_keywords.intersection(property_keywords))
        union = len(query_keywords.union(property_keywords))
        
        return intersection / union if union > 0 else 0.5
    
    # Extract semantic keywords from the search query
    query_keywords = extract_keywords_from_query(query)
    
    # Clear old recommendations older than 30 days
    old_date = datetime.datetime.now() - datetime.timedelta(days=30)
    Recommendation.objects.filter(user=user, created_at__lt=old_date).delete()
    
    # Add new recommendations with enhanced scoring
    for i, property_obj in enumerate(results):
        # Calculate base score based on search rank
        rank_score = 1.0 - (i * 0.1)  # Decreasing score for lower ranked results
        
        # Calculate semantic relevance
        semantic_score = calculate_property_relevance(property_obj, query_keywords)
        
        # Combine scores
        final_score = (rank_score * 0.6) + (semantic_score * 0.4)
        final_score = min(final_score, 1.0)
        
        # Only add if score is meaningful
        if final_score > 0.3:
            # Create or update recommendation
            recommendation, created = Recommendation.objects.get_or_create(
                user=user,
                property=property_obj,
                defaults={'score': final_score}
            )
            
            if not created:
                # Update existing recommendation (weighted average)
                recommendation.score = (recommendation.score * 0.7) + (final_score * 0.3)
                recommendation.save()