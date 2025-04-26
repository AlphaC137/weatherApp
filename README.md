# Weather App

## Overview
A simple Django web application that displays current weather information for cities around the world using the OpenWeatherMap API.

## Features
- Search for any city to view its current weather conditions
- Display temperature, humidity, pressure, and weather description
- View weather icons representing current conditions
- Save favorite cities for quick access (requires login)
- Responsive design works on mobile and desktop

## Technology Stack
- Python 3.12
- Django 5.2
- Bootstrap 4.5
- OpenWeatherMap API

## Setup Instructions

1. Clone the repository
2. Activate the virtual environment:
   ```
   source Scripts/activate   # On Linux/Mac
   Scripts\activate          # On Windows
   ```
3. Install dependencies:
   ```
   pip install django requests
   ```
4. Get an API key from [OpenWeatherMap](https://openweathermap.org/api)
5. Add your API key to `mysite/weatherapp/views.py`
6. Run the development server:
   ```
   cd mysite
   python manage.py runserver
   ```
7. Access the app at http://127.0.0.1:8000/

## Project Structure
- `/mysite/weatherapp/`: Main application code
  - `views.py`: Handles API requests and rendering
  - `models.py`: Database models for favorite cities
  - `urls.py`: URL routing configuration
- `/mysite/weatherapp/templates/`: HTML templates
- `/mysite/mysite/`: Django project settings

## User Features
- Search for cities without an account
- Create an account to save favorite cities
- Click on saved cities to quickly view their weather