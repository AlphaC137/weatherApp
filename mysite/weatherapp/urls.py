from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('favorite/add/', views.add_favorite, name='add_favorite'),
    path('favorite/remove/<int:city_id>/', views.remove_favorite, name='remove_favorite'),
    path('favorite/weather/<int:city_id>/', views.get_favorite_weather, name='get_favorite_weather'),
    path('api/location-suggestions/', views.location_suggestions, name='location_suggestions'),
]