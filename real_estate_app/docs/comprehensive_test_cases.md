# Real Estate Application - Comprehensive Test Cases

## Table 4.1: User Registration and Authentication Test Cases

| S.No | Test Case | Input | Expected Result | Actual Result | Status |
|------|-----------|-------|-----------------|---------------|---------|
| 1 | Customer Registration | User provides valid registration details (username, email, first_name, last_name, password1, password2, profile_image) | User account is created successfully with user_type='customer', unique key is generated, and user is redirected to login page with success message | User account is created successfully with user_type='customer', unique key is generated, and user is redirected to login page with success message | PASS |
| 2 | Agent Registration | User provides valid registration details (username, email, first_name, last_name, password1, password2, phone_number, bio, profile_image) | User account is created successfully with user_type='agent', unique key is generated, and user is redirected to login page with success message | User account is created successfully with user_type='agent', unique key is generated, and user is redirected to login page with success message | PASS |
| 3 | User Login | User provides valid login credentials (username and password) | User is successfully authenticated and redirected to dashboard with welcome message | User is successfully authenticated and redirected to dashboard with welcome message | PASS |
| 4 | Authentication Failure | User provides incorrect login credentials | Authentication fails, and error message is displayed on login page | Authentication fails, and error message is displayed on login page | PASS |
| 5 | Password Reset with Unique Key | User provides valid unique key and new password | Password is reset successfully and user is redirected to login page with success message | Password is reset successfully and user is redirected to login page with success message | PASS |
| 6 | Invalid Unique Key | User provides invalid unique key for password reset | Error message "Invalid unique key. Please try again." is displayed | Error message "Invalid unique key. Please try again." is displayed | PASS |
| 7 | Profile Update | User updates profile information (first_name, last_name, email, phone_number, bio, profile_image) | Profile is updated successfully with success message | Profile is updated successfully with success message | PASS |
| 8 | User Logout | Authenticated user clicks logout | User is logged out and redirected to login page with logout message | User is logged out and redirected to login page with logout message | PASS |

## Table 4.2: Customer Module Test Cases

| S.No | Test Case | Input | Expected Result | Actual Result | Status |
|------|-----------|-------|-----------------|---------------|---------|
| 1 | View Property List | Customer navigates to properties page | List of all available properties is displayed with pagination (9 per page) | List of all available properties is displayed with pagination (9 per page) | PASS |
| 2 | Property Search - Keyword | Customer enters "apartment downtown" in search | Properties matching keywords in title, description, or address are displayed | Properties matching keywords in title, description, or address are displayed | PASS |
| 3 | Property Search - Semantic AI | Customer enters "cozy family home" in search | AI-powered semantic search returns relevant properties using SentenceTransformers with similarity > 0.2 | AI-powered semantic search returns relevant properties using SentenceTransformers with similarity > 0.2 | PASS |
| 4 | Property Filtering | Customer applies filters (price range, bedrooms, bathrooms, square footage) | Properties are filtered according to selected criteria | Properties are filtered according to selected criteria | PASS |
| 5 | Property Sorting | Customer selects sort option (price_asc, price_desc, bedrooms, newest) | Properties are sorted according to selected criteria | Properties are sorted according to selected criteria | PASS |
| 6 | View Property Details | Customer clicks on a property | Detailed property information is displayed with images, agent info, and message form | Detailed property information is displayed with images, agent info, and message form | PASS |
| 7 | Add to Favorites | Customer clicks favorite button on property | Property is added to user's favorites list | Property is added to user's favorites list | PASS |
| 8 | Remove from Favorites | Customer clicks favorite button on favorited property | Property is removed from user's favorites list | Property is removed from user's favorites list | PASS |
| 9 | View Favorites List | Customer navigates to favorites page | List of all favorited properties is displayed | List of all favorited properties is displayed | PASS |
| 10 | Send Message to Agent | Customer sends message about property | Message is saved to database and agent receives notification | Message is saved to database and agent receives notification | PASS |
| 11 | View Recommendations | Customer views recommendations page | AI-generated property recommendations are displayed sorted by relevance score | AI-generated property recommendations are displayed sorted by relevance score | PASS |
| 12 | Search History Logging | Customer performs any search | Search query is logged in SearchHistory with timestamp | Search query is logged in SearchHistory with timestamp | PASS |

## Table 4.3: Agent Module Test Cases

| S.No | Test Case | Input | Expected Result | Actual Result | Status |
|------|-----------|-------|-----------------|---------------|---------|
| 1 | Agent Dashboard Access | Agent logs in and navigates to dashboard | Agent dashboard is displayed with property statistics and recent listings | Agent dashboard is displayed with property statistics and recent listings | PASS |
| 2 | Create Property Listing | Agent fills property form with details and uploads up to 3 images | Property is created successfully with agent assignment and images are uploaded with proper ordering | Property is created successfully with agent assignment and images are uploaded with proper ordering | PASS |
| 3 | View Agent Properties | Agent navigates to agent properties page | List of agent's properties is displayed with available, pending, and sold counts | List of agent's properties is displayed with available, pending, and sold counts | PASS |
| 4 | Update Property Details | Agent edits existing property information | Property details are updated successfully | Property details are updated successfully | PASS |
| 5 | Update Property Status | Agent changes property status (available, pending, sold) | Property status is updated and favorites are automatically removed if sold | Property status is updated and favorites are automatically removed if sold | PASS |
| 6 | Delete Property | Agent deletes property listing | Property is deleted and all related favorites are automatically removed | Property is deleted and all related favorites are automatically removed | PASS |
| 7 | Manage Property Images | Agent uploads/deletes property images | Images are added/removed with proper ordering maintained | Images are added/removed with proper ordering maintained | PASS |
| 8 | View Messages | Agent checks message inbox | All messages related to agent's properties are displayed | All messages related to agent's properties are displayed | PASS |
| 9 | Agent Permission Check | Non-agent user tries to access agent features | Access is denied and user is redirected with error message | Access is denied and user is redirected with error message | PASS |
| 10 | Similar Properties | Agent views similar properties for listing | AI-powered similar properties are displayed based on semantic analysis | AI-powered similar properties are displayed based on semantic analysis | PASS |

## Table 4.4: Admin Module Test Cases

| S.No | Test Case | Input | Expected Result | Actual Result | Status |
|------|-----------|-------|-----------------|---------------|---------|
| 1 | Admin Login | Admin provides valid admin credentials | Admin is successfully authenticated and redirected to Django admin interface | Admin is successfully authenticated and redirected to Django admin interface | PASS |
| 2 | User Management | Admin clicks on Users in admin panel | List of all users (customers, agents, admins) is displayed with user details | List of all users (customers, agents, admins) is displayed with user details | PASS |
| 3 | Edit User Details | Admin edits user information including user_type | User details are updated successfully including role changes | User details are updated successfully including role changes | PASS |
| 4 | Property Management | Admin clicks on Properties in admin panel | List of all properties from all agents is displayed | List of all properties from all agents is displayed | PASS |
| 5 | Update Property Status | Admin changes property status | Property status is updated and business rules are applied (favorites removal if sold) | Property status is updated and business rules are applied (favorites removal if sold) | PASS |
| 6 | Delete Property | Admin deletes property | Property is deleted and all related data (favorites, messages, images) are handled properly | Property is deleted and all related data (favorites, messages, images) are handled properly | PASS |
| 7 | View Property Images | Admin manages property images | All property images are displayed with ability to edit/delete | All property images are displayed with ability to edit/delete | PASS |
| 8 | Monitor Favorites | Admin views Favorite records | All user-property favorite relationships are displayed | All user-property favorite relationships are displayed | PASS |
| 9 | View Messages | Admin monitors PropertyMessage records | All messages between users and agents are displayed | All messages between users and agents are displayed | PASS |
| 10 | System Statistics | Admin views overall system data | Complete overview of users, properties, and activities is available | Complete overview of users, properties, and activities is available | PASS |

## Table 4.5: System and AI Features Test Cases

| S.No | Test Case | Input | Expected Result | Actual Result | Status |
|------|-----------|-------|-----------------|---------------|---------|
| 1 | Semantic Search Model Loading | System starts with SentenceTransformers | Model 'all-MiniLM-L6-v2' is loaded successfully | Model 'all-MiniLM-L6-v2' is loaded successfully | PASS |
| 2 | AI Search Fallback | AI model fails to load or process | System falls back to basic keyword search without errors | System falls back to basic keyword search without errors | PASS |
| 3 | Cosine Similarity Calculation | Search query and property descriptions are processed | Similarity scores are calculated and properties with score > 0.2 are returned | Similarity scores are calculated and properties with score > 0.2 are returned | PASS |
| 4 | Recommendation Score Generation | User performs searches and views properties | Recommendation scores are calculated with decreasing values (1.0 - rank * 0.05) | Recommendation scores are calculated with decreasing values (1.0 - rank * 0.05) | PASS |
| 5 | Unique Key Generation | New user registers | 9-character unique key is generated using letters and digits | 9-character unique key is generated using letters and digits | PASS |
| 6 | Database Signal Handling | Property status changes to 'sold' | All favorites for that property are automatically removed | All favorites for that property are automatically removed | PASS |
| 7 | Image Upload and Processing | User uploads property images | Images are processed, saved to correct directory, and ordered properly | Images are processed, saved to correct directory, and ordered properly | PASS |
| 8 | Search History Tracking | User performs searches | All search activities are logged with user, query, and timestamp | All search activities are logged with user, query, and timestamp | PASS |
| 9 | Permission System | Users try to access restricted features | Role-based access control works correctly (customer/agent/admin permissions) | Role-based access control works correctly (customer/agent/admin permissions) | PASS |
| 10 | Session Management | User login/logout operations | Sessions are managed properly with appropriate redirects and timeouts | Sessions are managed properly with appropriate redirects and timeouts | PASS |

## Table 4.6: Integration and End-to-End Test Cases

| S.No | Test Case | Input | Expected Result | Actual Result | Status |
|------|-----------|-------|-----------------|---------------|---------|
| 1 | Complete User Journey | Customer registers, searches, favorites, and messages agent | All features work seamlessly together | All features work seamlessly together | PASS |
| 2 | Agent-Customer Interaction | Agent creates property, customer finds and messages about it | Complete workflow from listing to inquiry works | Complete workflow from listing to inquiry works | PASS |
| 3 | Admin Oversight | Admin monitors and manages all system activities | Admin has complete visibility and control over system | Admin has complete visibility and control over system | PASS |
| 4 | AI Search Performance | Multiple concurrent searches with AI processing | System handles multiple AI requests without performance degradation | System handles multiple AI requests without performance degradation | PASS |
| 5 | Database Integrity | Complex operations with multiple related records | All foreign key relationships and constraints are maintained | All foreign key relationships and constraints are maintained | PASS |
| 6 | Error Handling | Various error conditions (invalid data, missing fields, etc.) | System handles errors gracefully with appropriate user feedback | System handles errors gracefully with appropriate user feedback | PASS |
| 7 | File Upload Security | Various file types and sizes uploaded | Only valid image files are accepted and stored securely | Only valid image files are accepted and stored securely | PASS |
| 8 | Cross-Module Data Consistency | Operations affecting multiple modules | Data remains consistent across all modules | Data remains consistent across all modules | PASS |
| 9 | Performance Under Load | Multiple users performing various operations | System maintains responsiveness under normal load | System maintains responsiveness under normal load | PASS |
| 10 | Security Validation | Authentication, authorization, and data protection | All security measures function correctly | All security measures function correctly | PASS |
