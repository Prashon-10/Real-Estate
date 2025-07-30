from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),
    
    # Users Management
    path('users/', views.admin_users_list, name='users_list'),
    path('users/add/', views.admin_user_create, name='user_create'),
    path('users/<int:user_id>/', views.admin_user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.admin_user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.admin_user_delete, name='user_delete'),
    path('users/<int:user_id>/toggle-status/', views.admin_toggle_user_status, name='toggle_user_status'),
    
    # Properties Management
    path('properties/', views.admin_properties_list, name='properties_list'),
    path('properties/create/', views.admin_property_create, name='property_create'),
    path('properties/<int:property_id>/', views.admin_property_detail, name='property_detail'),
    path('properties/<int:property_id>/edit/', views.admin_property_edit, name='property_edit'),
    path('properties/<int:property_id>/delete/', views.admin_property_delete, name='property_delete'),
    
    # Bookings Management
    path('bookings/', views.admin_bookings_list, name='bookings_list'),
    path('bookings/<int:booking_id>/', views.admin_booking_detail, name='booking_detail'),
    path('bookings/<int:booking_id>/update-status/', views.admin_update_booking_status, name='update_booking_status'),
    
    # Analytics & Reports
    path('analytics/', views.admin_analytics, name='analytics'),
    
    # Settings
    path('settings/', views.admin_settings, name='settings'),
]
