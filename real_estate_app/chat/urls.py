from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('agent/overview/', views.agent_chat_overview, name='agent_overview'),
    path('property/<int:property_id>/', views.property_chat, name='property_chat'),
    path('property/<int:property_id>/send/', views.send_message, name='send_message'),
    path('property/<int:property_id>/messages/', views.get_messages, name='get_messages'),
    path('unread-counts/', views.unread_counts, name='unread_counts'),
    path('list/', views.chat_list, name='chat_list'),
]
