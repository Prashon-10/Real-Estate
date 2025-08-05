from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.search_properties, name='search'),
    path('suggestions/', views.search_suggestions, name='suggestions'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
]