import logging
import os
from strands import Agent, tool
import requests
import math
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("weather_distance_app")

# Define our custom tools
@tool
def get_weather(city: str) -> Dict[str, Any]:
    """
    Get current weather information for a specified city.
    
    Args:
        city (str): The name of the city to get weather for
        
    Returns:
        Dict[str, Any]: Weather information including temperature, conditions, etc.
    """
    try:
        import os
        
        logger.info(f"Fetching weather for {city}")
        
        # Get API key from environment variable or use the hardcoded one as fallback
        api_key = os.environ.get("OPENWEATHER_API_KEY", "123455557777888899999999999")
        
        # Make the API call to OpenWeatherMap
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        
        response = requests.get(url, timeout=10)  # Add timeout for production reliability
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant weather information
            weather_data = {
                "city": city,
                "temperature": data["main"]["temp"],  # Celsius
                "temperature_f": round((data["main"]["temp"] * 9/5) + 32, 1),  # Fahrenheit
                "conditions": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],  # m/s
                "pressure": data["main"]["pressure"]  # hPa
            }
            
            return weather_data
        else:
            error_msg = f"API Error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return {"error": error_msg}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error getting weather: {str(e)}")
        return {"error": f"Network error: {str(e)}"}
    except KeyError as e:
        logger.error(f"Data parsing error: {str(e)}")
        return {"error": f"Could not parse weather data: {str(e)}"}
    except Exception as e:
        logger.error(f"Error getting weather: {str(e)}")
        return {"error": str(e)}

@tool
def calculate_distance(from_city: str, to_city: str) -> Dict[str, Any]:
    """
    Calculate the distance between two cities.
    
    Args:
        from_city (str): The origin city
        to_city (str): The destination city
        
    Returns:
        Dict[str, Any]: Distance information in kilometers and miles
    """
    try:
        logger.info(f"Calculating distance from {from_city} to {to_city}")
        
        # Expanded city coordinates database for production use
        city_coordinates = {
            # Spain
            "malaga": {"lat": 36.7213, "lon": -4.4213},
            "madrid": {"lat": 40.4168, "lon": -3.7038},
            "barcelona": {"lat": 41.3851, "lon": 2.1734},
            "valencia": {"lat": 39.4699, "lon": -0.3763},
            "seville": {"lat": 37.3891, "lon": -5.9845},
            "fuengirola": {"lat": 36.5393, "lon": -4.6249},
            "marbella": {"lat": 36.5100, "lon": -4.8861},
            
            # Europe
            "london": {"lat": 51.5074, "lon": -0.1278},
            "paris": {"lat": 48.8566, "lon": 2.3522},
            "berlin": {"lat": 52.5200, "lon": 13.4050},
            "rome": {"lat": 41.9028, "lon": 12.4964},
            "amsterdam": {"lat": 52.3676, "lon": 4.9041},
            "lisbon": {"lat": 38.7223, "lon": -9.1393},
            
            # Americas
            "new york": {"lat": 40.7128, "lon": -74.0060},
            "los angeles": {"lat": 34.0522, "lon": -118.2437},
            "chicago": {"lat": 41.8781, "lon": -87.6298},
            "toronto": {"lat": 43.6532, "lon": -79.3832},
            "mexico city": {"lat": 19.4326, "lon": -99.1332},
            "buenos aires": {"lat": 34.6037, "lon": -58.3816},
            
            # Asia & Oceania
            "tokyo": {"lat": 35.6762, "lon": 139.6503},
            "beijing": {"lat": 39.9042, "lon": 116.4074},
            "sydney": {"lat": 33.8688, "lon": 151.2093},
            "singapore": {"lat": 1.3521, "lon": 103.8198},
            "dubai": {"lat": 25.2048, "lon": 55.2708},
        }
        
        # Normalize city names to lowercase for lookup
        from_city_lower = from_city.lower()
        to_city_lower = to_city.lower()
        
        # Check if we have coordinates for both cities
        if from_city_lower not in city_coordinates:
            return {"error": f"Coordinates for {from_city} not found. Please try another city."}
        if to_city_lower not in city_coordinates:
            return {"error": f"Coordinates for {to_city} not found. Please try another city."}
        
        # Get coordinates
        from_coords = city_coordinates[from_city_lower]
        to_coords = city_coordinates[to_city_lower]
        
        # Calculate distance using Haversine formula
        distance_km = haversine_distance(
            from_coords["lat"], from_coords["lon"],
            to_coords["lat"], to_coords["lon"]
        )
        
        distance_miles = distance_km * 0.621371
        
        return {
            "from_city": from_city,
            "to_city": to_city,
            "distance_km": round(distance_km, 2),
            "distance_miles": round(distance_miles, 2)
        }
    except KeyError as e:
        logger.error(f"City lookup error: {str(e)}")
        return {"error": f"City not found: {str(e)}"}
    except Exception as e:
        logger.error(f"Error calculating distance: {str(e)}")
        return {"error": str(e)}

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

# Create our weather agent
weather_agent = Agent(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Using Claude 3.7 Sonnet
    tools=[get_weather],
    system_prompt="""You are a helpful weather assistant. 
    You can provide current weather information for cities around the world.
    Always provide weather information in a clear, concise format.
    Include temperature in both Celsius and Fahrenheit.
    """
)

# Create our distance calculator agent
distance_agent = Agent(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Using Claude 3.7 Sonnet
    tools=[calculate_distance],
    system_prompt="""You are a helpful distance calculator assistant.
    You can calculate the distance between two cities.
    Always provide distances in both kilometers and miles.
    Be precise and clear in your responses.
    """
)

# Create our coordinator agent that will use both specialized agents
@tool
def ask_weather_agent(query: str) -> str:
    """
    Ask the weather agent for information.
    
    Args:
        query (str): The weather-related question
        
    Returns:
        str: The weather agent's response
    """
    try:
        logger.info(f"Asking weather agent: {query}")
        response = weather_agent(query)
        return response.message
    except Exception as e:
        logger.error(f"Error in weather agent: {str(e)}")
        return f"Error getting weather information: {str(e)}"

@tool
def ask_distance_agent(query: str) -> str:
    """
    Ask the distance agent for information.
    
    Args:
        query (str): The distance-related question
        
    Returns:
        str: The distance agent's response
    """
    try:
        logger.info(f"Asking distance agent: {query}")
        response = distance_agent(query)
        return response.message
    except Exception as e:
        logger.error(f"Error in distance agent: {str(e)}")
        return f"Error calculating distance: {str(e)}"

# Create our main coordinator agent
coordinator_agent = Agent(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Using Claude 3.7 Sonnet
    tools=[ask_weather_agent, ask_distance_agent],
    system_prompt="""You are a helpful travel assistant that can provide weather information 
    and calculate distances between cities.
    
    You have access to two specialized agents:
    1. A weather agent that can provide current weather information
    2. A distance agent that can calculate distances between cities
    
    When asked about weather, delegate to the weather agent.
    When asked about distances, delegate to the distance agent.
    When asked about both, use both agents and combine the information.
    
    For distance calculations:
    - When the user asks "How far is X from Y?", interpret this as calculating distance from X to Y
    - When the user asks about distance without specifying two cities, use Malaga, Spain as the default starting point
    - Always explicitly mention both cities in your query to the distance agent
    - Format distance queries as "Calculate the distance from [city1] to [city2]"
    
    Be helpful, concise, and informative in your responses.
    """
)

def main():
    print("Welcome to the Weather & Distance Multi-Agent App!")
    print("This app can provide weather information and calculate distances between cities.")
    print("Type 'exit' to quit.")
    
    # Check for API key in environment
    if "OPENWEATHER_API_KEY" not in os.environ:
        print("\nNote: No OPENWEATHER_API_KEY environment variable found.")
        print("Using default API key. For production use, set your own API key with:")
        print("export OPENWEATHER_API_KEY=your_api_key_here")
    
    print("\nExample queries:")
    print("- What's the weather like in London?")
    print("- How far is Barcelona from Madrid?")
    print("- What's the weather in Tokyo and how far is it from New York?")
    
    while True:
        user_input = input("\nWhat would you like to know? ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("Thank you for using the Weather & Distance Multi-Agent App. Goodbye!")
            break
        
        # Process the user's query with our coordinator agent
        try:
            print("Processing your request...")
            response = coordinator_agent(user_input)
            print(f"\n{response.message}")
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            print(f"Sorry, I encountered an error: {str(e)}")
            print("Please try again with a different query.")

if __name__ == "__main__":
    main()
