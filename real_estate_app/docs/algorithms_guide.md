# Real Estate Application - Algorithms Guide
## Easy Reference for All Algorithms Used

### 🔍 **Search & Discovery Algorithms**

#### **1. Semantic Search Algorithm (SentenceTransformers)**
- **Where Used**: `search/views.py` - `search_properties()` function
- **How Used**: 
  ```python
  model = SentenceTransformer('all-MiniLM-L6-v2')
  query_embedding = model.encode([query])
  property_embeddings = model.encode(property_texts)
  ```
- **What It Does**: Converts text into numerical vectors (embeddings) to understand meaning
- **Remember**: Think "Smart Search" - understands "cozy apartment" = "comfortable flat"

#### **2. Cosine Similarity Algorithm**
- **Where Used**: `search/views.py` - after SentenceTransformers encoding
- **How Used**: 
  ```python
  from sklearn.metrics.pairwise import cosine_similarity
  similarities = cosine_similarity(query_embedding, property_embeddings)[0]
  ```
- **What It Does**: Measures how similar two text vectors are (0 = totally different, 1 = identical)
- **Remember**: Like measuring angles between arrows - smaller angle = more similar

---

### 🎯 **Recommendation Algorithms**

#### **3. Content-Based Filtering Algorithm**
- **Where Used**: `properties/views.py` - `toggle_favorite()` and `similar_properties()`
- **How Used**: 
  ```python
  similar_properties = Property.objects.filter(
      property_type=property_obj.property_type,
      listing_type=property_obj.listing_type
  ).exclude(id=property_obj.id)[:10]
  ```
- **What It Does**: Recommends properties with similar features (same type, bedrooms, etc.)
- **Remember**: "Birds of a feather flock together" - similar properties group together

#### **4. Score-Based Ranking Algorithm**
- **Where Used**: `search/views.py` - `update_recommendations()` function
- **How Used**: 
  ```python
  score = 1.0 - (i * 0.05)  # Score decreases with rank
  ```
- **What It Does**: Assigns relevance scores (1st result = 1.0, 2nd = 0.95, 3rd = 0.90...)
- **Remember**: Like grading exams - higher rank = higher score

---

### 🔄 **Data Processing Algorithms**

#### **5. Similarity Threshold Algorithm**
- **Where Used**: `search/views.py` - semantic search results filtering
- **How Used**: 
  ```python
  results = [properties[i] for i in similar_indices if similarities[i] > 0.2]
  ```
- **What It Does**: Filters out results below 20% similarity to avoid irrelevant matches
- **Remember**: Quality control - only show "good enough" matches

#### **6. Natural Language Processing (NLP) Algorithm**
- **Where Used**: Throughout search functionality via SentenceTransformers
- **How Used**: Automatically processes user search queries
- **What It Does**: Understands human language context and meaning
- **Remember**: The "translator" between human words and computer understanding

---

### 📊 **Sorting & Filtering Algorithms**

#### **7. Multi-Criteria Filtering Algorithm**
- **Where Used**: `properties/views.py` - `PropertyListView.get_queryset()`
- **How Used**: 
  ```python
  if search:
      queryset = queryset.filter(Q(title__icontains=search) | Q(address__icontains=search))
  if property_type:
      queryset = queryset.filter(property_type=property_type)
  ```
- **What It Does**: Applies multiple filters simultaneously (AND logic)
- **Remember**: Like using multiple sieves - each filter narrows down results

#### **8. Dynamic Sorting Algorithm**
- **Where Used**: `properties/views.py` - PropertyListView sorting
- **How Used**: 
  ```python
  if sort == 'price_low':
      queryset = queryset.order_by('price')
  elif sort == 'price_high':
      queryset = queryset.order_by('-price')
  ```
- **What It Does**: Reorganizes results by user preference (price, date, etc.)
- **Remember**: Like organizing your closet - by color, size, or style

---

### 🧠 **Machine Learning Algorithms**

#### **9. Collaborative Learning Algorithm (Implicit)**
- **Where Used**: `search/views.py` - recommendation updates based on user behavior
- **How Used**: Updates recommendations when users search or add favorites
- **What It Does**: Learns from user actions to improve future suggestions
- **Remember**: Like a personal shopper who remembers what you like

#### **10. Vector Space Model Algorithm**
- **Where Used**: Underlying SentenceTransformers implementation
- **How Used**: Automatically converts text to mathematical representations
- **What It Does**: Maps words/sentences to points in multi-dimensional space
- **Remember**: Like GPS coordinates but for words - similar meanings = nearby locations

---

### 🔒 **Security & Access Algorithms**

#### **11. Role-Based Access Control (RBAC) Algorithm**
- **Where Used**: Throughout views with `is_agent()`, `is_customer()` checks
- **How Used**: 
  ```python
  def test_func(self):
      return self.request.user.is_agent()
  ```
- **What It Does**: Controls who can access what features based on user type
- **Remember**: Like a bouncer at different club sections - VIP, General, Staff only

#### **12. Ownership Verification Algorithm**
- **Where Used**: `properties/views.py` - edit/delete property views
- **How Used**: 
  ```python
  if obj.agent != request.user:
      messages.error(request, "You can only edit your own listings.")
  ```
- **What It Does**: Ensures users can only modify their own content
- **Remember**: "You can only change your own diary entries"

---

### 📈 **Analytics Algorithms**

#### **13. Trend Analysis Algorithm**
- **Where Used**: Admin interface and agent dashboards
- **How Used**: Counts and aggregates data by status, dates, user behavior
- **What It Does**: Identifies patterns in property views, favorites, and sales
- **Remember**: Like a weather forecast but for property market trends

#### **14. Real-Time Update Algorithm**
- **Where Used**: AJAX functions throughout the application
- **How Used**: JavaScript updates without page refresh
- **What It Does**: Keeps data synchronized across user sessions
- **Remember**: Like live sports scores - always current, no refresh needed

---

## 🎯 **Quick Memory Tips**

### **Algorithm Categories**
1. **🔍 SEARCH**: Semantic + Cosine Similarity = "Smart Understanding"
2. **🎯 RECOMMEND**: Content-Based + Scoring = "Like This? Try That!"
3. **🔄 PROCESS**: Filtering + Sorting = "Find & Organize" 
4. **🧠 LEARN**: ML + Behavior Tracking = "Gets Smarter Over Time"
5. **🔒 SECURE**: RBAC + Ownership = "Right Person, Right Access"
6. **📊 ANALYZE**: Trends + Real-time = "Know What's Happening Now"

### **The Complete Flow**
1. **User searches** → Semantic Algorithm understands meaning
2. **System compares** → Cosine Similarity finds matches  
3. **Results filtered** → Multi-criteria narrows down options
4. **Results ranked** → Scoring Algorithm orders by relevance
5. **User interacts** → Behavior tracked for learning
6. **Recommendations updated** → Content-based suggestions improve
7. **Access controlled** → RBAC ensures security
8. **Analytics generated** → Trend analysis provides insights

**Remember**: It's like having a super-smart real estate assistant that understands what you want, learns from your preferences, keeps everything secure, and gets better over time!
