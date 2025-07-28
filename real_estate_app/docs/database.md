# Database Schema Documentation

## Overview
The Real Estate application uses a relational database schema designed to support multi-user property management, AI-powered search, and real-time messaging. The schema extends Django's built-in User model and implements efficient relationships for scalability.

## Tables

### auth_user (Extended)
Custom user model extending Django's AbstractUser.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique user identifier |
| username | CharField(150) | UNIQUE, NOT NULL | User login name |
| email | EmailField | NOT NULL | User email address |
| password | CharField(128) | NOT NULL | Hashed password |
| first_name | CharField(150) | | User's first name |
| last_name | CharField(150) | | User's last name |
| user_type | CharField(10) | NOT NULL, DEFAULT='customer' | Role: customer/agent/admin |
| profile_image | ImageField | NULLABLE | Profile photo path |
| unique_key | CharField(9) | UNIQUE, NOT NULL | Password reset key |
| phone_number | CharField(15) | | Contact number |
| bio | TextField | | User biography |
| date_joined | DateTimeField | NOT NULL | Account creation date |
| is_active | BooleanField | DEFAULT=True | Account status |
| is_staff | BooleanField | DEFAULT=False | Staff access |
| is_superuser | BooleanField | DEFAULT=False | Admin access |
| last_login | DateTimeField | NULLABLE | Last login timestamp |

**Indexes:**
- `idx_user_username` on username
- `idx_user_email` on email  
- `idx_user_type` on user_type
- `idx_user_unique_key` on unique_key

**Constraints:**
- `chk_user_type` CHECK (user_type IN ('customer', 'agent', 'admin'))

---

### properties_property
Core property listings table.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique property identifier |
| title | CharField(255) | NOT NULL | Property title |
| address | CharField(500) | NOT NULL | Full address |
| price | DecimalField(12,2) | NOT NULL | Property price |
| bedrooms | PositiveSmallIntegerField | NOT NULL | Number of bedrooms |
| bathrooms | DecimalField(3,1) | NOT NULL | Number of bathrooms |
| square_footage | PositiveIntegerField | NOT NULL | Area in square feet |
| description | TextField | NOT NULL | Detailed description |
| status | CharField(10) | NOT NULL, DEFAULT='available' | Property status |
| agent_id | ForeignKey | NOT NULL | Reference to User (agent) |
| created_at | DateTimeField | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last update timestamp |

**Indexes:**
- `idx_property_status` on status
- `idx_property_price` on price
- `idx_property_bedrooms` on bedrooms
- `idx_property_bathrooms` on bathrooms
- `idx_property_sqft` on square_footage
- `idx_property_created` on created_at
- `idx_property_agent` on agent_id

**Constraints:**
- `chk_property_status` CHECK (status IN ('available', 'sold', 'pending'))
- `chk_property_price` CHECK (price > 0)
- `chk_property_bedrooms` CHECK (bedrooms >= 0)
- `chk_property_bathrooms` CHECK (bathrooms >= 0)
- `chk_property_sqft` CHECK (square_footage > 0)

**Foreign Keys:**
- `fk_property_agent` REFERENCES auth_user(id) ON DELETE CASCADE

---

### properties_propertyimage
Property image storage with ordering.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique image identifier |
| property_id | ForeignKey | NOT NULL | Reference to Property |
| image | ImageField | NOT NULL | Image file path |
| order | PositiveSmallIntegerField | DEFAULT=0 | Display order |

**Indexes:**
- `idx_propertyimage_property` on property_id
- `idx_propertyimage_order` on (property_id, order)

**Foreign Keys:**
- `fk_propertyimage_property` REFERENCES properties_property(id) ON DELETE CASCADE

---

### properties_favorite
User favorites junction table.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique favorite identifier |
| user_id | ForeignKey | NOT NULL | Reference to User |
| property_id | ForeignKey | NOT NULL | Reference to Property |
| added_at | DateTimeField | AUTO_NOW_ADD | Favorite creation time |

**Indexes:**
- `idx_favorite_user` on user_id
- `idx_favorite_property` on property_id
- `idx_favorite_added` on added_at

**Constraints:**
- `uniq_favorite_user_property` UNIQUE (user_id, property_id)

**Foreign Keys:**
- `fk_favorite_user` REFERENCES auth_user(id) ON DELETE CASCADE
- `fk_favorite_property` REFERENCES properties_property(id) ON DELETE CASCADE

**Triggers:**
- Auto-delete favorites when property status = 'sold'

---

### search_searchhistory
User search activity tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique search identifier |
| user_id | ForeignKey | NOT NULL | Reference to User |
| query | TextField | NOT NULL | Search query text |
| property_id | ForeignKey | NULLABLE | Specific property viewed |
| timestamp | DateTimeField | AUTO_NOW_ADD | Search timestamp |

**Indexes:**
- `idx_searchhistory_user` on user_id
- `idx_searchhistory_timestamp` on timestamp
- `idx_searchhistory_property` on property_id

**Foreign Keys:**
- `fk_searchhistory_user` REFERENCES auth_user(id) ON DELETE CASCADE
- `fk_searchhistory_property` REFERENCES properties_property(id) ON DELETE SET NULL

---

### search_recommendation
AI-generated property recommendations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique recommendation ID |
| user_id | ForeignKey | NOT NULL | Reference to User |
| property_id | ForeignKey | NOT NULL | Reference to Property |
| score | FloatField | NOT NULL | Relevance score (0.0-1.0) |
| created_at | DateTimeField | AUTO_NOW_ADD | Recommendation timestamp |

**Indexes:**
- `idx_recommendation_user` on user_id
- `idx_recommendation_score` on score DESC
- `idx_recommendation_created` on created_at

**Constraints:**
- `uniq_recommendation_user_property` UNIQUE (user_id, property_id)
- `chk_recommendation_score` CHECK (score >= 0.0 AND score <= 1.0)

**Foreign Keys:**
- `fk_recommendation_user` REFERENCES auth_user(id) ON DELETE CASCADE
- `fk_recommendation_property` REFERENCES properties_property(id) ON DELETE CASCADE

---

### properties_propertymessage
Property-specific messaging system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Unique message identifier |
| property_id | ForeignKey | NOT NULL | Reference to Property |
| sender_id | ForeignKey | NOT NULL | Reference to User (sender) |
| content | TextField | NOT NULL | Message content |
| timestamp | DateTimeField | AUTO_NOW_ADD | Message timestamp |
| read | BooleanField | DEFAULT=False | Read status |

**Indexes:**
- `idx_propertymessage_property` on property_id
- `idx_propertymessage_sender` on sender_id
- `idx_propertymessage_timestamp` on timestamp
- `idx_propertymessage_read` on read

**Foreign Keys:**
- `fk_propertymessage_property` REFERENCES properties_property(id) ON DELETE CASCADE
- `fk_propertymessage_sender` REFERENCES auth_user(id) ON DELETE CASCADE

## Database Views

### property_summary_view
Aggregated property statistics for dashboard.

```sql
CREATE VIEW property_summary_view AS
SELECT 
    p.agent_id,
    COUNT(*) as total_properties,
    COUNT(CASE WHEN p.status = 'available' THEN 1 END) as available_count,
    COUNT(CASE WHEN p.status = 'pending' THEN 1 END) as pending_count,
    COUNT(CASE WHEN p.status = 'sold' THEN 1 END) as sold_count,
    AVG(p.price) as avg_price,
    MIN(p.price) as min_price,
    MAX(p.price) as max_price
FROM properties_property p
GROUP BY p.agent_id;
```

### user_activity_view
User engagement metrics.

```sql
CREATE VIEW user_activity_view AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(DISTINCT sh.id) as search_count,
    COUNT(DISTINCT f.id) as favorite_count,
    COUNT(DISTINCT pm.id) as message_count,
    MAX(sh.timestamp) as last_search,
    MAX(f.added_at) as last_favorite,
    MAX(pm.timestamp) as last_message
FROM auth_user u
LEFT JOIN search_searchhistory sh ON u.id = sh.user_id
LEFT JOIN properties_favorite f ON u.id = f.user_id  
LEFT JOIN properties_propertymessage pm ON u.id = pm.sender_id
WHERE u.user_type = 'customer'
GROUP BY u.id, u.username;
```

## Stored Procedures

### update_recommendations(user_id)
Updates recommendations based on user search history and favorites.

```sql
DELIMITER //
CREATE PROCEDURE update_recommendations(IN p_user_id INT)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE prop_id INT;
    DECLARE similarity_score DECIMAL(3,2);
    
    -- Cursor for similar properties based on user behavior
    DECLARE property_cursor CURSOR FOR
        SELECT p.id, calculate_similarity(p_user_id, p.id) as score
        FROM properties_property p
        WHERE p.status = 'available'
        AND p.id NOT IN (SELECT property_id FROM properties_favorite WHERE user_id = p_user_id)
        HAVING score > 0.2
        ORDER BY score DESC
        LIMIT 50;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Clear old recommendations
    DELETE FROM search_recommendation WHERE user_id = p_user_id;
    
    OPEN property_cursor;
    recommendation_loop: LOOP
        FETCH property_cursor INTO prop_id, similarity_score;
        IF done THEN
            LEAVE recommendation_loop;
        END IF;
        
        INSERT INTO search_recommendation (user_id, property_id, score, created_at)
        VALUES (p_user_id, prop_id, similarity_score, NOW());
    END LOOP;
    
    CLOSE property_cursor;
END //
DELIMITER ;
```

## Performance Considerations

### Query Optimization
- Composite indexes on frequently filtered columns
- Partial indexes for status-based queries
- Query result caching for expensive searches

### Data Archival
- Archive sold properties older than 2 years
- Compress old search history data
- Regular cleanup of expired recommendations

### Scalability
- Horizontal partitioning by geographical region
- Read replicas for search-heavy operations
- Connection pooling for high concurrency

## Backup Strategy
- Daily full backups
- Hourly incremental backups
- Point-in-time recovery capability
- Cross-region backup replication
