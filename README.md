# Weather & Distance Multi-Agent App

A production-ready application built with Strands Agents that provides weather information and calculates distances between cities.

## Features

- Get current weather information for cities worldwide
- Calculate distances between cities using the Haversine formula
- Multi-agent architecture with specialized agents for different tasks
- Coordinator agent that delegates tasks to specialized agents

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your OpenWeatherMap API key:
   - Create a free account at [OpenWeatherMap](https://openweathermap.org/)
   - Get your API key
   - Create a `.env` file based on `.env.example` and add your API key

## Usage

Run the application:

```
python weather_distance_app.py
```

Example queries:
- "What's the weather like in London?"
- "How far is Barcelona from Madrid?"
- "What's the weather in Tokyo and how far is it from New York?"

## Configuration

- The application uses environment variables for configuration
- API keys and other sensitive information should be stored in a `.env` file
- See `.env.example` for required variables

## Error Handling

The application includes comprehensive error handling for:
- Network errors
- API errors
- City not found errors
- General exceptions

## License

MIT
