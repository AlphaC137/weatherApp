import urllib.request
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FavoriteCity

def index(request):
    data = {}
    
    # Add favorite cities to context if user is logged in
    if request.user.is_authenticated:
        data['favorite_cities'] = FavoriteCity.objects.filter(user=request.user)
    
    # Pre-fill search field if coming from favorite city link
    favorite_city = request.GET.get('favorite_city')
    if favorite_city:
        data['search_term'] = favorite_city
    
    if request.method == 'POST':
        city = request.POST['city']
        data['search_term'] = city
        
        try:
            # TODO: Replace '<API-KEY-GOES-HERE>' with your actual OpenWeatherMap API key
            # Sign up at https://openweathermap.org/api to get your API key
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=6fcd6f7736ef7bf7c234dcb03a3e1df5'
            source = urllib.request.urlopen(url).read()
            list_of_data = json.loads(source)
            
            # Check if API returned an error
            if 'cod' in list_of_data and list_of_data['cod'] != 200:
                messages.error(request, f"Error: {list_of_data.get('message', 'City not found')}")
                return render(request, "main/index.html", data)
            
            # Process weather data
            data.update({
                "city_name": city,
                "country_code": str(list_of_data['sys']['country']),
                "coordinate": str(list_of_data['coord']['lon']) + ', '
                + str(list_of_data['coord']['lat']),
                "temp": str(list_of_data['main']['temp']) + ' °C',
                "pressure": str(list_of_data['main']['pressure']) + ' hPa',
                "humidity": str(list_of_data['main']['humidity']) + '%',
                'main': str(list_of_data['weather'][0]['main']),
                'description': str(list_of_data['weather'][0]['description']),
                'icon': list_of_data['weather'][0]['icon'],
            })
            
            # If there are additional weather details available
            if 'wind' in list_of_data:
                data['wind_speed'] = str(list_of_data['wind'].get('speed', 'N/A')) + ' m/s'
                data['wind_direction'] = str(list_of_data['wind'].get('deg', 'N/A')) + '°'
                
            if 'visibility' in list_of_data:
                data['visibility'] = str(round(list_of_data['visibility'] / 1000, 1)) + ' km'
                
        except urllib.error.HTTPError as e:
            messages.error(request, f"Error accessing weather service: {e.code} {e.reason}")
        except urllib.error.URLError as e:
            messages.error(request, f"Error connecting to weather service: {e.reason}")
        except json.JSONDecodeError:
            messages.error(request, "Invalid response from weather service")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")

    return render(request, "main/index.html", data)

@login_required
def add_favorite(request):
    if request.method == 'POST':
        city_name = request.POST.get('city_name')
        if city_name:
            # Check if city already exists for this user
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
        # Redirect to index with city name as GET parameter
        return redirect(f'/?favorite_city={city.name}')
    except FavoriteCity.DoesNotExist:
        messages.error(request, "City not found in favorites.")
        return redirect('index')
