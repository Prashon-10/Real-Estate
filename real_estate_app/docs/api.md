# API Documentation

## Authentication Endpoints

### User Registration
```
POST /accounts/register/customer/
POST /accounts/register/agent/
```

**Request Body:**
```json
{
    "username": "string",
    "email": "email",
    "first_name": "string",
    "last_name": "string",
    "password1": "string",
    "password2": "string",
    "phone_number": "string", // agents only
    "bio": "text", // agents only
    "profile_image": "file" // optional
}
```

**Response:**
```json
{
    "success": true,
    "message": "Registration successful! Your unique key is: ABC123DEF",
    "unique_key": "ABC123DEF"
}
```

### User Login
```
POST /accounts/login/
```

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "success": true,
    "redirect_url": "/dashboard/",
    "user_type": "customer|agent|admin"
}
```

### Password Reset
```
POST /accounts/forgot-password/
```

**Request Body:**
```json
{
    "unique_key": "ABC123DEF",
    "new_password": "string",
    "confirm_password": "string"
}
```

## Property Endpoints

### List Properties
```
GET /properties/
```

**Query Parameters:**
- `price_min`: Minimum price filter
- `price_max`: Maximum price filter
- `bedrooms`: Minimum bedrooms
- `bathrooms`: Minimum bathrooms
- `sqft_min`: Minimum square footage
- `sqft_max`: Maximum square footage
- `sort`: Sorting option (newest, price_asc, price_desc, bedrooms)

**Response:**
```json
{
    "properties": [
        {
            "id": 1,
            "title": "Modern Downtown Apartment",
            "address": "123 Main St, City",
            "price": "450000.00",
            "bedrooms": 2,
            "bathrooms": "2.0",
            "square_footage": 1200,
            "status": "available",
            "agent": {
                "id": 5,
                "username": "agent_john",
                "first_name": "John",
                "last_name": "Doe"
            },
            "images": [
                {
                    "id": 1,
                    "image": "/media/property_images/image1.jpg",
                    "order": 0
                }
            ],
            "created_at": "2025-01-15T10:30:00Z"
        }
    ],
    "pagination": {
        "current_page": 1,
        "total_pages": 5,
        "has_next": true,
        "has_previous": false
    }
}
```

### Property Detail
```
GET /properties/{id}/
```

**Response:**
```json
{
    "id": 1,
    "title": "Modern Downtown Apartment",
    "description": "Beautiful modern apartment...",
    "address": "123 Main St, City",
    "price": "450000.00",
    "bedrooms": 2,
    "bathrooms": "2.0",
    "square_footage": 1200,
    "status": "available",
    "agent": {
        "id": 5,
        "username": "agent_john",
        "profile_image": "/media/profile_images/john.jpg",
        "phone_number": "+1234567890",
        "bio": "Experienced real estate agent..."
    },
    "images": [...],
    "is_favorite": false,
    "similar_properties": [...],
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-20T14:20:00Z"
}
```

### Create Property (Agents Only)
```
POST /properties/create/
```

**Request Body (multipart/form-data):**
```json
{
    "title": "string",
    "description": "text",
    "address": "string",
    "price": "decimal",
    "bedrooms": "integer",
    "bathrooms": "decimal",
    "square_footage": "integer",
    "status": "available|pending|sold",
    "image1": "file",
    "image2": "file",
    "image3": "file"
}
```

### Update Property Status
```
POST /properties/update-status/{id}/
```

**Request Body:**
```json
{
    "status": "available|pending|sold"
}
```

## Search Endpoints

### Search Properties
```
GET /search/?q={query}
```

**Query Parameters:**
- `q`: Search query (supports natural language)

**Response:**
```json
{
    "query": "luxury apartment downtown",
    "results": [
        {
            "id": 1,
            "title": "Luxury Downtown Condo",
            "relevance_score": 0.95,
            "price": "750000.00",
            "address": "456 Downtown Ave",
            "bedrooms": 3,
            "bathrooms": "2.5",
            "square_footage": 1800
        }
    ],
    "search_type": "semantic|keyword",
    "total_results": 15
}
```

### Get Recommendations
```
GET /search/recommendations/
```

**Response:**
```json
{
    "recommendations": [
        {
            "property": {
                "id": 10,
                "title": "Family Home in Suburbs",
                "price": "550000.00",
                "bedrooms": 4,
                "bathrooms": "3.0"
            },
            "score": 0.87,
            "reason": "Based on your search history"
        }
    ]
}
```

## Favorites Endpoints

### Toggle Favorite
```
POST /properties/favorite/{property_id}/
```

**Response:**
```json
{
    "success": true,
    "is_favorite": true,
    "message": "Property added to favorites"
}
```

### List Favorites
```
GET /properties/favorites/
```

**Response:**
```json
{
    "favorites": [
        {
            "id": 1,
            "property": {
                "id": 5,
                "title": "Cozy Cottage",
                "price": "325000.00"
            },
            "added_at": "2025-01-18T09:15:00Z"
        }
    ]
}
```

## Messaging Endpoints

### Send Message
```
POST /properties/property/{property_id}/send-message/
```

**Request Body:**
```json
{
    "message": "I'm interested in this property. Can we schedule a viewing?"
}
```

### Message Inbox
```
GET /properties/messages/
```

**Response:**
```json
{
    "messages": [
        {
            "id": 1,
            "property": {
                "id": 5,
                "title": "Downtown Apartment"
            },
            "sender": {
                "id": 10,
                "username": "customer_jane",
                "first_name": "Jane"
            },
            "content": "Is this property still available?",
            "timestamp": "2025-01-20T15:30:00Z",
            "read": false
        }
    ]
}
```

## WebSocket API

### Property Updates
```
ws://localhost:8000/ws/property/{property_id}/
```

**Message Types:**
```json
{
    "type": "status_update",
    "property_id": 1,
    "new_status": "sold"
}

{
    "type": "new_message",
    "property_id": 1,
    "sender": "customer_jane",
    "content": "Message content"
}

{
    "type": "price_update",
    "property_id": 1,
    "old_price": "450000.00",
    "new_price": "425000.00"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
    "success": false,
    "error": "Error message",
    "code": "ERROR_CODE",
    "details": {
        "field_errors": {
            "email": ["This field is required."],
            "password": ["Password too weak."]
        }
    }
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

- Search endpoints: 100 requests per hour
- Property creation: 10 properties per day
- Message sending: 50 messages per hour
- File uploads: 20 MB per file, 100 MB per hour
