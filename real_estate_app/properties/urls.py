from django.urls import path
from . import views
from . import booking_views

app_name = 'properties'

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='property_list'),
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('agent/properties/', views.AgentPropertyListView.as_view(), name='agent_properties'),
    path('create/', views.PropertyCreateView.as_view(), name='property_create'),
    path('update/<int:pk>/', views.PropertyUpdateView.as_view(), name='property_update'),
    path('delete/<int:pk>/', views.PropertyDeleteView.as_view(), name='property_delete'),
    path('favorite/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('delete-image/<int:image_id>/', views.delete_property_image, name='delete_image'),
    path('update-status/<int:pk>/', views.update_property_status, name='update_status'),
    path('similar/<int:pk>/', views.similar_properties, name='similar_properties'),

    #Testing
    path('property/<int:property_id>/send-message/', views.send_message, name='send_message'),
    path('messages/', views.message_inbox, name='message_inbox'),
    path('messages/<int:message_id>/mark-read/', views.mark_message_read, name='mark_message_read'),
    
    # Booking URLs
    path('booking/<int:property_id>/', booking_views.property_booking_view, name='property_booking'),
    path('booking/stripe-payment/', booking_views.stripe_payment_view, name='stripe_payment'),
    path('booking/esewa-payment/', booking_views.esewa_payment_view, name='esewa_payment'),
    path('booking/esewa-success/', booking_views.esewa_success_view, name='esewa_success'),
    path('booking/esewa-failure/', booking_views.esewa_failure_view, name='esewa_failure'),
    path('booking/detail/<int:booking_id>/', booking_views.BookingDetailView.as_view(), name='booking_detail'),
    path('my-bookings/', booking_views.MyBookingsView.as_view(), name='my_bookings'),
    
    # Admin booking management
    path('admin/bookings/', booking_views.AdminBookingsView.as_view(), name='admin_bookings'),
    path('admin/booking/verify/<int:booking_id>/', booking_views.VerifyBookingView.as_view(), name='verify_booking'),
    
    # Webhook
    path('webhook/stripe/', booking_views.stripe_webhook_view, name='stripe_webhook'),
]