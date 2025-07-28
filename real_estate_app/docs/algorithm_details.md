# Real Estate Application - Algorithm Details and Formulas

## Complete Algorithm Analysis Based on Workspace

### Table of Contents
1. [Semantic Search Algorithm](#semantic-search-algorithm)
2. [Property Filtering Algorithm](#property-filtering-algorithm)
3. [Recommendation Scoring Algorithm](#recommendation-scoring-algorithm)
4. [User Authentication Algorithm](#user-authentication-algorithm)
5. [Property Ranking Algorithm](#property-ranking-algorithm)
6. [Message Priority Algorithm](#message-priority-algorithm)

---

## 1. Semantic Search Algorithm

### Overview
The semantic search algorithm represents the core intelligence of the real estate application's property discovery system. Unlike traditional keyword-based search mechanisms that rely on exact text matching, this sophisticated algorithm leverages natural language processing and machine learning to understand the semantic meaning and context of user queries. The implementation utilizes SentenceTransformers, a state-of-the-art neural network architecture specifically designed for generating meaningful sentence embeddings, combined with cosine similarity calculations to measure the relevance between user queries and property descriptions.

The algorithm begins by preprocessing both the user's search query and all available property descriptions, converting them into high-dimensional vector representations that capture semantic relationships. These embeddings are then compared using mathematical similarity functions to identify properties that match not just the literal words in the query, but the underlying intent and meaning. For instance, when a user searches for "cozy family home," the algorithm can identify properties described as "warm family residence" or "comfortable dwelling for families" even though they don't share exact keywords.

This approach significantly enhances the user experience by providing more relevant search results, reducing the need for users to try multiple search terms, and enabling natural language queries. The system is particularly effective for real estate applications where properties can be described using varied terminology, and users often express their preferences in conversational language rather than structured search criteria.

### Mathematical Foundation

#### 1.1 Text Embedding Generation
```
Given: Query q and Property texts P = {p₁, p₂, ..., pₙ}

Step 1: Text Preprocessing
text_i = title_i + " " + description_i
where i ∈ [1, n]

Step 2: Vector Embedding
query_vector = SentenceTransformer.encode(q) ∈ ℝᵈ
property_vectors = {v₁, v₂, ..., vₙ} where vᵢ ∈ ℝᵈ
```

#### 1.2 Cosine Similarity Calculation
```
Formula: similarity(q, pᵢ) = (q⃗ · vᵢ⃗) / (||q⃗|| × ||vᵢ⃗||)

Where:
- q⃗ = query embedding vector
- vᵢ⃗ = property i embedding vector
- · = dot product
- ||·|| = Euclidean norm

Expanded:
similarity(q, pᵢ) = Σₖ₌₁ᵈ (qₖ × vᵢₖ) / (√(Σₖ₌₁ᵈ qₖ²) × √(Σₖ₌₁ᵈ vᵢₖ²))
```

#### 1.3 Result Ranking
```
Ranking Algorithm:
1. Calculate similarities: S = {s₁, s₂, ..., sₙ}
2. Apply threshold: S' = {sᵢ | sᵢ > θ}, where θ = 0.2
3. Sort descending: argsort(S')[::-1]
4. Return top-k results
```

### Implementation Code Flow
```python
# From search/views.py
def semantic_search_algorithm(query, properties):
    """
    Semantic Search Implementation
    
    Input: query (str), properties (QuerySet)
    Output: ranked_properties (list)
    """
    # Step 1: Text Preparation
    property_texts = [f"{p.title} {p.description}" for p in properties]
    
    # Step 2: Embedding Generation
    query_embedding = model.encode([query])  # Shape: (1, 384)
    property_embeddings = model.encode(property_texts)  # Shape: (n, 384)
    
    # Step 3: Similarity Calculation
    similarities = cosine_similarity(query_embedding, property_embeddings)[0]
    
    # Step 4: Ranking and Filtering
    similar_indices = np.argsort(similarities)[::-1]
    results = [properties[i] for i in similar_indices if similarities[i] > 0.2]
    
    return results
```

---

## 2. Property Filtering Algorithm

### Overview
Multi-criteria filtering system for property search with range-based and categorical filters.

### Mathematical Foundation

#### 2.1 Range Filter Formula
```
For numerical property attribute x and filter range [min, max]:

Filter(x, min, max) = {
    True,  if min ≤ x ≤ max
    False, otherwise
}

Combined Range Filter:
F(property) = ∧ᵢ Filter(attributeᵢ, minᵢ, maxᵢ)
```

#### 2.2 Categorical Filter Formula
```
For categorical attribute c and filter set S:

CategoricalFilter(c, S) = {
    True,  if c ∈ S
    False, otherwise
}
```

#### 2.3 Complete Filter Algorithm
```python
def property_filter_algorithm(queryset, filters):
    """
    Multi-criteria Property Filtering
    
    Filters Applied:
    - Price Range: [price_min, price_max]
    - Bedrooms: bedrooms ≥ min_bedrooms
    - Bathrooms: bathrooms ≥ min_bathrooms
    - Square Footage: [sqft_min, sqft_max]
    - Status: status ∈ {'available', 'pending', 'sold'}
    """
    
    # Price Range Filter
    if filters.get('price_min'):
        queryset = queryset.filter(price__gte=filters['price_min'])
    if filters.get('price_max'):
        queryset = queryset.filter(price__lte=filters['price_max'])
    
    # Minimum Requirement Filters
    if filters.get('bedrooms'):
        queryset = queryset.filter(bedrooms__gte=filters['bedrooms'])
    if filters.get('bathrooms'):
        queryset = queryset.filter(bathrooms__gte=filters['bathrooms'])
    
    # Square Footage Range
    if filters.get('sqft_min'):
        queryset = queryset.filter(square_footage__gte=filters['sqft_min'])
    if filters.get('sqft_max'):
        queryset = queryset.filter(square_footage__lte=filters['sqft_max'])
    
    return queryset
```

---

## 3. Recommendation Scoring Algorithm

### Overview
Ranking-based scoring system for property recommendations with decay function.

### Mathematical Foundation

#### 3.1 Ranking-Based Score Formula
```
For property at rank i in search results:

Score(i) = 1.0 - (i × decay_factor)

Where:
- i = 0-indexed ranking position
- decay_factor = 0.05 (5% decay per position)
- Score range: [0.0, 1.0]

Example:
- Rank 0 (1st): Score = 1.0 - (0 × 0.05) = 1.0
- Rank 1 (2nd): Score = 1.0 - (1 × 0.05) = 0.95
- Rank 2 (3rd): Score = 1.0 - (2 × 0.05) = 0.90
- ...
- Rank 20 (21st): Score = 1.0 - (20 × 0.05) = 0.0
```

#### 3.2 Time-Based Decay (Future Enhancement)
```
Time-weighted Score Formula:

Score_time(i, t) = Score(i) × e^(-λt)

Where:
- λ = decay constant (e.g., 0.1 per day)
- t = time elapsed since recommendation creation
- e = Euler's number (≈ 2.718)
```

### Implementation
```python
def update_recommendations_algorithm(user, query, results):
    """
    Recommendation Scoring Algorithm
    
    Input: user, query, search_results
    Output: Updated recommendation scores
    """
    for i, property_obj in enumerate(results):
        # Calculate ranking-based score
        score = max(0.0, 1.0 - (i * 0.05))
        
        # Store or update recommendation
        Recommendation.objects.update_or_create(
            user=user,
            property=property_obj,
            defaults={'score': score}
        )
```

---

## 4. User Authentication Algorithm

### Overview
Role-based authentication system with user type validation.

### Mathematical Foundation

#### 4.1 User Role Validation
```
UserRole = {customer, agent, admin}

Permission Matrix P:
                   View  Create  Update  Delete  Message
Customer    P =    [1,    0,      0,      0,      1    ]
Agent       P =    [1,    1,      1,      1,      1    ]
Admin       P =    [1,    1,      1,      1,      1    ]

Access Control Function:
Access(user, action) = P[user.role][action]
```

#### 4.2 Authentication Flow
```python
def authentication_algorithm(request, required_role=None):
    """
    Multi-level Authentication Algorithm
    
    Steps:
    1. Check if user is authenticated
    2. Validate user role if specified
    3. Grant or deny access
    """
    
    # Step 1: Basic Authentication
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Step 2: Role-based Authorization
    if required_role:
        if required_role == 'agent' and not request.user.is_agent():
            return deny_access()
        elif required_role == 'customer' and not request.user.is_customer():
            return deny_access()
        elif required_role == 'admin' and not request.user.is_admin_user():
            return deny_access()
    
    return grant_access()
```

---

## 5. Property Ranking Algorithm

### Overview
Multi-criteria sorting algorithm for property listings.

### Mathematical Foundation

#### 5.1 Sorting Criteria
```
Available Sort Options:
- newest: ORDER BY created_at DESC
- price_asc: ORDER BY price ASC
- price_desc: ORDER BY price DESC
- bedrooms: ORDER BY bedrooms DESC

SQL Translation:
Sort(properties, criteria) = SELECT * FROM properties 
                             WHERE status = 'available' 
                             ORDER BY criteria
```

#### 5.2 Pagination Algorithm
```
Pagination Formula:
page_size = 9
total_items = count(filtered_properties)
total_pages = ⌈total_items / page_size⌉

For page p:
start_index = (p - 1) × page_size
end_index = min(p × page_size, total_items)
page_items = properties[start_index:end_index]
```

---

## 6. Message Priority Algorithm

### Overview
Message processing and notification priority system.

### Mathematical Foundation

#### 6.1 Message Priority Score
```
Priority Score Calculation:

Priority(message) = w₁ × Recency + w₂ × UserType + w₃ × PropertyValue

Where:
- Recency = e^(-t/τ), t = hours since message, τ = 24 hours
- UserType = {1.0 for premium, 0.7 for regular, 0.5 for new}
- PropertyValue = normalized(property.price / max_price)
- Weights: w₁ = 0.4, w₂ = 0.3, w₃ = 0.3

Example:
For a message sent 2 hours ago by premium user on $500k property:
- Recency = e^(-2/24) ≈ 0.92
- UserType = 1.0
- PropertyValue = 500000/1000000 = 0.5
- Priority = 0.4×0.92 + 0.3×1.0 + 0.3×0.5 = 0.818
```

#### 6.2 Notification Delivery Algorithm
```python
def message_notification_algorithm(message):
    """
    Message Processing and Notification
    
    Steps:
    1. Calculate message priority
    2. Determine notification method
    3. Queue for delivery
    """
    
    # Step 1: Priority Calculation
    recency_score = calculate_recency(message.timestamp)
    user_type_score = get_user_type_score(message.sender)
    property_value_score = normalize_property_value(message.property.price)
    
    priority = (0.4 * recency_score + 
                0.3 * user_type_score + 
                0.3 * property_value_score)
    
    # Step 2: Notification Method Selection
    if priority > 0.8:
        notification_method = 'immediate_push'
    elif priority > 0.6:
        notification_method = 'email'
    else:
        notification_method = 'dashboard_only'
    
    return schedule_notification(message, notification_method, priority)
```

---

## Performance Optimization Algorithms

### 1. Database Query Optimization
```python
# Query optimization using select_related and prefetch_related
def optimized_property_query():
    return Property.objects.select_related('agent')\
                          .prefetch_related('images', 'messages')\
                          .filter(status='available')

# Time Complexity: O(1) for joins vs O(n) for separate queries
```

### 2. Search Result Caching
```python
# Redis caching for frequent searches
import hashlib

def cached_search_algorithm(query):
    cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}"
    
    # Check cache first
    cached_result = redis_client.get(cache_key)
    if cached_result:
        return pickle.loads(cached_result)
    
    # Perform search if not cached
    results = semantic_search_algorithm(query)
    
    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, pickle.dumps(results))
    
    return results
```

---

## Algorithm Complexity Analysis

### Time Complexities:
1. **Semantic Search**: O(n × d) where n = properties, d = embedding dimension
2. **Property Filtering**: O(n × f) where f = number of filters
3. **Recommendation Scoring**: O(n) for n search results
4. **Database Queries**: O(log n) with proper indexing
5. **Message Processing**: O(1) for priority calculation

### Space Complexities:
1. **Embeddings Storage**: O(n × d) for property embeddings
2. **Search Results**: O(k) where k = top results returned
3. **Cache Storage**: O(c) where c = cached queries
4. **User Sessions**: O(u) where u = active users

---

## Configuration and Constants

```python
# Algorithm Configuration
SEMANTIC_SEARCH_CONFIG = {
    'model_name': 'all-MiniLM-L6-v2',
    'similarity_threshold': 0.2,
    'max_results': 50,
    'embedding_dimension': 384
}

RECOMMENDATION_CONFIG = {
    'decay_factor': 0.05,
    'max_score': 1.0,
    'min_score': 0.0,
    'update_frequency': 'per_search'
}

PAGINATION_CONFIG = {
    'properties_per_page': 9,
    'max_pages': 100
}

MESSAGE_PRIORITY_CONFIG = {
    'recency_weight': 0.4,
    'user_type_weight': 0.3,
    'property_value_weight': 0.3,
    'time_decay_hours': 24
}
```

This comprehensive algorithm documentation covers all the major algorithms implemented in your Django real estate application, complete with mathematical formulas, implementation details, and performance analysis.
