from flask import Flask, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# OpenWeatherMap API configuration
API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

# City mapping
CITIES = {
    'newyork': 'New York',
    'sydney': 'Sydney',
    'capetown': 'Cape Town',
    'bangkok': 'Bangkok'
}

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Weather Backend API',
        'available_cities': list(CITIES.keys())
    })

@app.route('/weather/<city>', methods=['GET'])
def get_weather(city):
    """
    Get weather data for a specific city
    
    Args:
        city (str): City key (newyork, sydney, capetown, bangkok)
    
    Returns:
        JSON response with weather data or error message
    """
    # Validate city
    city_lower = city.lower()
    if city_lower not in CITIES:
        return jsonify({
            'error': 'Invalid city',
            'message': f'City "{city}" not supported. Available cities: {list(CITIES.keys())}'
        }), 400
    
    # Check if API key is configured
    if not API_KEY:
        return jsonify({
            'error': 'Configuration error',
            'message': 'OpenWeatherMap API key not configured'
        }), 500
    
    # Get actual city name
    city_name = CITIES[city_lower]
    
    try:
        # Make request to OpenWeatherMap API
        params = {
            'q': city_name,
            'appid': API_KEY,
            'units': 'metric'  # Use Celsius
        }
        
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant weather information
        weather_data = {
            'city': city_name,
            'temperature': round(data['main']['temp'], 1),
            'description': data['weather'][0]['description'].capitalize(),
            'humidity': data['main']['humidity'],
            'wind_speed': round(data['wind']['speed'], 1)
        }
        
        return jsonify(weather_data)
    
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Timeout',
            'message': 'Request to OpenWeatherMap API timed out'
        }), 504
    
    except requests.exceptions.HTTPError as e:
        return jsonify({
            'error': 'API Error',
            'message': f'OpenWeatherMap API returned an error: {e.response.status_code}'
        }), 502
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Network Error',
            'message': 'Failed to connect to OpenWeatherMap API'
        }), 502
    
    except (KeyError, ValueError) as e:
        return jsonify({
            'error': 'Data Error',
            'message': 'Unexpected response format from OpenWeatherMap API'
        }), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
