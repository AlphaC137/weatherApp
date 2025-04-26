import urllib.request
import json
import time
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .models import FavoriteCity

# Weather data cache with 10-min expiration
WEATHER_CACHE = {}
CACHE_DURATION = 600

# API key from env vars with fallback
API_KEY = getattr(settings, 'OPENWEATHER_API_KEY', '6fcd6f7736ef7bf7c234dcb03a3e1df5')

def get_cached_weather(cache_key):
    """Returns cached data if valid, None otherwise"""
    if cache_key in WEATHER_CACHE:
        cache_entry = WEATHER_CACHE[cache_key]
        if time.time() - cache_entry['timestamp'] < CACHE_DURATION:
            return cache_entry['data']
    return None

def store_weather_cache(cache_key, data):
    """Stores data in cache with timestamp, prunes if needed"""
    WEATHER_CACHE[cache_key] = {
        'data': data,
        'timestamp': time.time()
    }
    # Prune oldest entries if cache exceeds 20 items
    if len(WEATHER_CACHE) > 20:
        oldest_key = min(WEATHER_CACHE.keys(), key=lambda k: WEATHER_CACHE[k]['timestamp'])
        WEATHER_CACHE.pop(oldest_key, None)

def index(request):
    data = {}
    
    # Add favorites for authenticated users
    if request.user.is_authenticated:
        data['favorite_cities'] = FavoriteCity.objects.filter(user=request.user)
    
    # Pre-fill search from favorites
    favorite_city = request.GET.get('favorite_city')
    if favorite_city:
        data['search_term'] = favorite_city
    
    if request.method == 'POST':
        city = request.POST['city']
        data['search_term'] = city
        
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')
        
        try:
            # Generate cache key based on coords or city
            cache_key = f"{lat}:{lon}" if lat and lon else city
            
            # Try cache first
            cached_data = get_cached_weather(cache_key)
            if cached_data:
                data.update(cached_data)
            else:
                # Build API URL with coords or city name
                if lat and lon:
                    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}'
                else:
                    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}'
                    
                source = urllib.request.urlopen(url).read()
                list_of_data = json.loads(source)
                
                # Handle API errors
                if 'cod' in list_of_data and list_of_data['cod'] != 200:
                    messages.error(request, f"Error: {list_of_data.get('message', 'City not found')}")
                    return render(request, "main/index.html", data)
                
                # Extract weather data
                weather_data = {
                    "city_name": city if city else list_of_data.get('name', 'Unknown'),
                    "country_code": str(list_of_data['sys']['country']),
                    "coordinate": str(list_of_data['coord']['lon']) + ', '
                    + str(list_of_data['coord']['lat']),
                    "temp": str(list_of_data['main']['temp']) + ' °C',
                    "pressure": str(list_of_data['main']['pressure']) + ' hPa',
                    "humidity": str(list_of_data['main']['humidity']) + '%',
                    'main': str(list_of_data['weather'][0]['main']),
                    'description': str(list_of_data['weather'][0]['description']),
                    'icon': list_of_data['weather'][0]['icon'],
                }
                
                # Add optional weather details if available
                if 'wind' in list_of_data:
                    weather_data['wind_speed'] = str(list_of_data['wind'].get('speed', 'N/A')) + ' m/s'
                    weather_data['wind_direction'] = str(list_of_data['wind'].get('deg', 'N/A')) + '°'
                    
                if 'visibility' in list_of_data:
                    weather_data['visibility'] = str(round(list_of_data['visibility'] / 1000, 1)) + ' km'
                
                # Cache for future requests
                store_weather_cache(cache_key, weather_data)
                data.update(weather_data)
                
        except urllib.error.HTTPError as e:
            messages.error(request, f"Error accessing weather service: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            messages.error(request, f"Error connecting to weather service: {e.reason}")
        except json.JSONDecodeError:
            messages.error(request, "Invalid response from weather service")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            data = {'error': 'City not found or connection error'}

    return render(request, "main/index.html", data)

@login_required
def add_favorite(request):
    if request.method == 'POST':
        city_name = request.POST.get('city_name')
        if city_name:
            # Skip if city already in favorites
            if not FavoriteCity.objects.filter(name=city_name, user=request.user).exists():
                FavoriteCity.objects.create(name=city_name, user=request.user)
                messages.success(request, f"{city_name} added to favorites.")
            else:
                messages.info(request, f"{city_name} is already in your favorites.")
    
    return redirect('index')

@login_required
def remove_favorite(request, city_id):
    try:
        city = FavoriteCity.objects.get(id=city_id, user=request.user)
        city_name = city.name
        city.delete()
        messages.success(request, f"{city_name} removed from favorites.")
    except FavoriteCity.DoesNotExist:
        messages.error(request, "City not found in favorites.")
    
    return redirect('index')

@login_required
def get_favorite_weather(request, city_id):
    try:
        city = FavoriteCity.objects.get(id=city_id, user=request.user)
        return redirect(f'/?favorite_city={city.name}')
    except FavoriteCity.DoesNotExist:
        messages.error(request, "City not found in favorites.")
        return redirect('index')

def location_suggestions(request):
    """API endpoint for location autocomplete"""
    query = request.GET.get('q', '')
    
    if len(query) < 3:
        return JsonResponse([], safe=False)
    
    try:
        # Query OpenWeatherMap Geocoding API
        url = f'http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={API_KEY}'
        source = urllib.request.urlopen(url).read()
        locations = json.loads(source)
        
        # Format response
        formatted_locations = []
        for loc in locations:
            formatted_locations.append({
                'name': loc.get('name', ''),
                'state': loc.get('state', ''),
                'country': loc.get('country', ''),
                'lat': loc.get('lat', 0),
                'lon': loc.get('lon', 0)
            })
        
        return JsonResponse(formatted_locations, safe=False)
    except Exception as e:
        print(f"Error fetching location suggestions: {str(e)}")
        return JsonResponse([], safe=False)
