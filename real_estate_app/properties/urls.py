from django.urls import path
from . import views

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
]