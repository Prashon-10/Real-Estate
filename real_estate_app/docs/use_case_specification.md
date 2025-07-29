# Real Estate Application - Use Case Specification

## Overview
This document provides a detailed specification of all use cases for the Real Estate Management System, organized by actor roles.

---

## 🔐 Admin Use Cases

### UC1: Manage Users
- **Description**: Admin can create, view, update, and delete user accounts
- **Actors**: Admin
- **Preconditions**: Admin is logged in
- **Main Flow**:
  1. Admin navigates to user management section
  2. Admin can view list of all users (agents and customers)
  3. Admin can create new user accounts
  4. Admin can edit user details and permissions
  5. Admin can deactivate/delete user accounts
  6. Admin can reset user passwords
- **Postconditions**: User data is updated in the system

### UC2: Manage Property Listings
- **Description**: Admin has full control over all property listings
- **Actors**: Admin
- **Preconditions**: Admin is logged in
- **Main Flow**:
  1. Admin views all property listings across all agents
  2. Admin can edit any property details
  3. Admin can delete inappropriate listings
  4. Admin can approve/reject new listings
  5. Admin can feature properties on homepage
- **Postconditions**: Property data is updated

### UC3: Manage Content
- **Description**: Admin manages website content and configuration
- **Actors**: Admin
- **Preconditions**: Admin is logged in
- **Main Flow**:
  1. Admin updates website content (homepage, about page, etc.)
  2. Admin manages system-wide announcements
  3. Admin configures search parameters
  4. Admin manages email templates
- **Postconditions**: Content is updated across the system

### UC4: View Analytics & Reports
- **Description**: Admin views comprehensive system analytics
- **Actors**: Admin
- **Preconditions**: Admin is logged in
- **Main Flow**:
  1. Admin accesses analytics dashboard
  2. Views user registration trends
  3. Views property listing statistics
  4. Views message/inquiry analytics
  5. Generates and exports reports
- **Postconditions**: Analytics data is displayed

### UC5: Moderate Messages
- **Description**: Admin can monitor and moderate user communications
- **Actors**: Admin
- **Preconditions**: Admin is logged in
- **Main Flow**:
  1. Admin views all conversations between agents and customers
  2. Admin can flag inappropriate messages
  3. Admin can delete messages if necessary
  4. Admin can ban users for policy violations
- **Postconditions**: Messages are moderated

### UC6: System Configuration
- **Description**: Admin configures system-wide settings
- **Actors**: Admin
- **Preconditions**: Admin is logged in
- **Main Flow**:
  1. Admin configures email settings
  2. Admin sets up payment gateways
  3. Admin manages API integrations
  4. Admin configures search algorithms
- **Postconditions**: System configuration is updated

---

## 🏠 Agent Use Cases

### UC7: Register & Manage Profile
- **Description**: Agent can register and maintain their professional profile
- **Actors**: Agent
- **Preconditions**: None for registration
- **Main Flow**:
  1. Agent registers with email and basic details
  2. Agent verifies email address
  3. Agent completes profile with professional information
  4. Agent uploads profile picture and license documents
  5. Agent updates contact information and bio
- **Postconditions**: Agent profile is created/updated

### UC8: Add Property Listing
- **Description**: Agent creates new property listings
- **Actors**: Agent
- **Preconditions**: Agent is logged in and verified
- **Main Flow**:
  1. Agent navigates to "Add Property" page
  2. Agent fills in property details (title, description, price, etc.)
  3. Agent specifies property features and amenities
  4. Agent uploads multiple property images
  5. Agent sets property location and contact preferences
  6. Agent submits listing for review/publication
- **Postconditions**: New property is added to database

### UC9: Edit Property Listing
- **Description**: Agent modifies existing property listings
- **Actors**: Agent
- **Preconditions**: Agent owns the property listing
- **Main Flow**:
  1. Agent views their property listings
  2. Agent selects property to edit
  3. Agent updates property information
  4. Agent adds/removes/reorders images
  5. Agent saves changes
- **Postconditions**: Property data is updated

### UC10: Delete Property Listing
- **Description**: Agent removes property listings
- **Actors**: Agent
- **Preconditions**: Agent owns the property listing
- **Main Flow**:
  1. Agent views their property listings
  2. Agent selects property to delete
  3. System confirms deletion action
  4. Property is marked as deleted/archived
- **Postconditions**: Property is removed from active listings

### UC11: Upload Property Images
- **Description**: Agent manages property image galleries
- **Actors**: Agent
- **Preconditions**: Agent is editing a property
- **Main Flow**:
  1. Agent selects images from device
  2. System validates image format and size
  3. Images are uploaded and processed
  4. Agent can set featured image
  5. Agent can reorder images
- **Postconditions**: Property images are stored and associated

### UC12: Update Property Status
- **Description**: Agent changes property availability status
- **Actors**: Agent
- **Preconditions**: Agent owns the property
- **Main Flow**:
  1. Agent accesses property management
  2. Agent selects property status (Available, Pending, Sold, Rented)
  3. Agent optionally adds status notes
  4. System updates property visibility accordingly
- **Postconditions**: Property status is updated

### UC13: View Property Analytics
- **Description**: Agent views performance metrics for their properties
- **Actors**: Agent
- **Preconditions**: Agent is logged in
- **Main Flow**:
  1. Agent accesses analytics dashboard
  2. Views property view counts
  3. Views favorite/save statistics
  4. Views inquiry and message counts
  5. Views conversion rates
- **Postconditions**: Analytics data is displayed

### UC14: Respond to Customer Messages
- **Description**: Agent communicates with interested customers
- **Actors**: Agent
- **Preconditions**: Customer has initiated conversation
- **Main Flow**:
  1. Agent receives notification of new message
  2. Agent opens conversation interface
  3. Agent reads customer inquiry
  4. Agent types and sends response
  5. Conversation continues in real-time
- **Postconditions**: Message is sent to customer

### UC15: Manage Customer Conversations
- **Description**: Agent organizes and manages multiple customer conversations
- **Actors**: Agent
- **Preconditions**: Agent has active conversations
- **Main Flow**:
  1. Agent views conversation dashboard
  2. Conversations are grouped by property
  3. Agent can see unread message counts
  4. Agent can prioritize urgent inquiries
  5. Agent can archive completed conversations
- **Postconditions**: Conversations are organized

### UC16: View Property Views/Favorites
- **Description**: Agent monitors customer interest in their properties
- **Actors**: Agent
- **Preconditions**: Agent has published properties
- **Main Flow**:
  1. Agent views property dashboard
  2. System shows view counts per property
  3. System shows favorite/save counts
  4. Agent can see trending properties
- **Postconditions**: Engagement data is displayed

### UC17: Real-time Message Notifications
- **Description**: Agent receives instant notifications for new messages
- **Actors**: Agent
- **Preconditions**: Agent is logged in
- **Main Flow**:
  1. Customer sends message to agent
  2. System immediately notifies agent
  3. Agent sees notification badge/popup
  4. Agent can quick-reply or open full conversation
- **Postconditions**: Agent is notified of new message

---

## 👥 Customer/User Use Cases

### UC18: Register & Manage Profile
- **Description**: Customer creates and maintains their account
- **Actors**: Customer
- **Preconditions**: None for registration
- **Main Flow**:
  1. Customer registers with email and password
  2. Customer verifies email address
  3. Customer completes profile with preferences
  4. Customer uploads profile picture
  5. Customer sets notification preferences
- **Postconditions**: Customer profile is created/updated

### UC19: Search Properties
- **Description**: Customer searches for properties using various methods
- **Actors**: Customer
- **Preconditions**: None (public access)
- **Main Flow**:
  1. Customer enters search criteria
  2. System processes search query
  3. Results are displayed with sorting options
  4. Customer can refine search
  5. Customer can save search criteria
- **Postconditions**: Search results are displayed

### UC20: AI-Powered Semantic Search
- **Description**: Advanced search using natural language processing
- **Actors**: Customer
- **Preconditions**: None
- **Main Flow**:
  1. Customer enters natural language query
  2. AI system interprets intent and requirements
  3. System matches properties based on semantic meaning
  4. Results include confidence scores
  5. System explains why properties were matched
- **Postconditions**: Intelligent search results are provided

### UC21: Filter Properties
- **Description**: Customer narrows down search results using filters
- **Actors**: Customer
- **Preconditions**: Customer is viewing property results
- **Main Flow**:
  1. Customer applies price range filters
  2. Customer selects property type
  3. Customer filters by location/distance
  4. Customer filters by features (bedrooms, bathrooms, etc.)
  5. Results update dynamically
- **Postconditions**: Filtered results are displayed

### UC22: View Property Details
- **Description**: Customer views comprehensive property information
- **Actors**: Customer
- **Preconditions**: Property exists and is available
- **Main Flow**:
  1. Customer clicks on property from search results
  2. System displays detailed property page
  3. Customer views property specifications
  4. Customer sees location map
  5. Customer can contact agent directly
- **Postconditions**: Property details are viewed

### UC23: View Image Galleries
- **Description**: Customer browses property images
- **Actors**: Customer
- **Preconditions**: Property has uploaded images
- **Main Flow**:
  1. Customer opens image gallery
  2. Customer navigates through images
  3. Customer can zoom and view full-size images
  4. Customer can share images
- **Postconditions**: Images are displayed

### UC24: Save/Favorite Properties
- **Description**: Customer saves properties for later review
- **Actors**: Customer
- **Preconditions**: Customer is logged in
- **Main Flow**:
  1. Customer clicks "Save" or "Favorite" on property
  2. Property is added to customer's saved list
  3. Customer can add personal notes
  4. Customer can organize saved properties
- **Postconditions**: Property is saved to favorites

### UC25: Contact Agents
- **Description**: Customer initiates communication with property agents
- **Actors**: Customer
- **Preconditions**: Customer is viewing a property
- **Main Flow**:
  1. Customer clicks "Contact Agent" button
  2. Customer writes initial inquiry message
  3. Message is sent to agent
  4. Conversation thread is created
- **Postconditions**: Communication is initiated

### UC26: Real-time Messaging
- **Description**: Customer engages in live chat with agents
- **Actors**: Customer
- **Preconditions**: Conversation exists with agent
- **Main Flow**:
  1. Customer opens conversation
  2. Customer types and sends messages
  3. Messages appear instantly for agent
  4. Customer sees read receipts
  5. Customer receives agent responses in real-time
- **Postconditions**: Real-time communication occurs

### UC27: Receive Property Recommendations
- **Description**: System provides personalized property suggestions
- **Actors**: Customer
- **Preconditions**: Customer has search/browsing history
- **Main Flow**:
  1. System analyzes customer preferences
  2. System identifies matching properties
  3. Recommendations are displayed on dashboard
  4. Customer can adjust recommendation settings
  5. Customer can provide feedback on suggestions
- **Postconditions**: Recommendations are provided

### UC28: View Search History
- **Description**: Customer reviews their past searches
- **Actors**: Customer
- **Preconditions**: Customer is logged in and has search history
- **Main Flow**:
  1. Customer accesses search history
  2. Past searches are displayed chronologically
  3. Customer can re-run previous searches
  4. Customer can delete search history
- **Postconditions**: Search history is displayed

### UC29: View Favorite History
- **Description**: Customer manages their saved properties
- **Actors**: Customer
- **Preconditions**: Customer has saved properties
- **Main Flow**:
  1. Customer opens favorites list
  2. Saved properties are displayed
  3. Customer can sort and filter favorites
  4. Customer can remove properties from favorites
  5. Customer can add notes to saved properties
- **Postconditions**: Favorites are managed

### UC30: Advanced Property Filtering
- **Description**: Customer uses sophisticated filtering options
- **Actors**: Customer
- **Preconditions**: Customer is searching properties
- **Main Flow**:
  1. Customer accesses advanced filters
  2. Customer sets multiple criteria simultaneously
  3. Customer uses range sliders for numeric values
  4. Customer applies location-based filters
  5. Customer saves filter combinations
- **Postconditions**: Advanced filters are applied

---

## 🔑 Authentication & Common Use Cases

### UC31: Login
- **Description**: User authenticates to access system
- **Actors**: Admin, Agent, Customer
- **Preconditions**: User has valid account
- **Main Flow**:
  1. User enters email and password
  2. System validates credentials
  3. User is redirected to appropriate dashboard
  4. Session is established
- **Postconditions**: User is authenticated

### UC32: Logout
- **Description**: User ends their session
- **Actors**: Admin, Agent, Customer
- **Preconditions**: User is logged in
- **Main Flow**:
  1. User clicks logout
  2. System clears session data
  3. User is redirected to login page
- **Postconditions**: User session is terminated

### UC33: Password Reset
- **Description**: User resets forgotten password
- **Actors**: Agent, Customer
- **Preconditions**: User has registered email
- **Main Flow**:
  1. User requests password reset
  2. System sends reset email
  3. User clicks reset link
  4. User enters new password
  5. Password is updated
- **Postconditions**: Password is changed

### UC34: Email Verification
- **Description**: User verifies their email address
- **Actors**: Agent, Customer
- **Preconditions**: User has registered account
- **Main Flow**:
  1. System sends verification email
  2. User clicks verification link
  3. Email is marked as verified
  4. Account is activated
- **Postconditions**: Email is verified

### UC35: Profile Picture Upload
- **Description**: User uploads profile picture
- **Actors**: Agent, Customer
- **Preconditions**: User is logged in
- **Main Flow**:
  1. User selects image file
  2. System validates image format
  3. Image is processed and stored
  4. Profile picture is updated
- **Postconditions**: Profile picture is set

---

## 🔗 Use Case Relationships

### Include Relationships
- **Add Property** includes **Upload Property Images**
- **Edit Property** includes **Upload Property Images**
- **Search Properties** includes **Filter Properties**
- **View Property Details** includes **View Image Galleries**
- **Contact Agents** includes **Real-time Messaging**
- **Respond to Customer Messages** includes **Real-time Message Notifications**

### Extend Relationships
- **Search Properties** extends to **AI-Powered Semantic Search**
- **Filter Properties** extends to **Advanced Property Filtering**
- **Register & Manage Profile** extends to **Profile Picture Upload** (both Agent and Customer)

### Precondition Dependencies
- Most authenticated actions require **Login** as a precondition
- Property management actions require agent authentication
- Messaging actions require active user sessions

---

## 📊 Key Features Summary

### Real-time Messaging System
- WhatsApp-style grouped conversations
- Instant message delivery and read receipts
- Unread message counts and notifications
- Mobile-responsive chat interface

### AI-Powered Search
- Natural language query processing
- Semantic understanding of property requirements
- Intelligent matching algorithms
- Personalized recommendations

### Comprehensive Analytics
- Property view tracking
- User engagement metrics
- Conversion rate analysis
- Performance dashboards for agents

### Advanced Property Management
- Multi-image galleries with drag-and-drop ordering
- Status management (Available, Pending, Sold)
- Feature-rich property descriptions
- Location mapping integration

This use case specification provides a complete overview of all system functionality organized by user roles, ensuring comprehensive coverage of the Real Estate Management System requirements.
