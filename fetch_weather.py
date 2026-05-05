# Step 1 - Import all libraries we need
import requests        # to call the weather API
import boto3           # to connect to AWS S3
import json            # to convert data to JSON format
import time            # to add delay between fetches
from datetime import datetime   # to get current date and time
from dotenv import load_dotenv  # to read our .env file
import os              # to get values from .env file

# Step 2 - Load our secret keys from .env file
load_dotenv()

# Step 3 - Read all values from .env file
API_KEY       = os.getenv("API_KEY")        # OpenWeatherMap API key
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY") # AWS access key
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY") # AWS secret key
BUCKET_NAME   = os.getenv("BUCKET_NAME")    # S3 bucket name
REGION        = os.getenv("REGION")         # AWS region

# Step 4 - List of cities we want weather data for
CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"]

# Step 5 - Connect to AWS S3 using our keys
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)

# Step 6 - This function fetches weather data for one city
def fetch_weather(city):
    
    # Build the API URL for the city
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    # Call the API and get response
    response = requests.get(url)
    
    # Convert response to dictionary
    data = response.json()

    # Pick only the fields we need
    weather = {
        "city"              : city,
        "temperature"       : data["main"]["temp"],         # temperature in celsius
        "feels_like"        : data["main"]["feels_like"],   # feels like temperature
        "humidity"          : data["main"]["humidity"],     # humidity percentage
        "pressure"          : data["main"]["pressure"],     # air pressure
        "weather_condition" : data["weather"][0]["description"], # eg: haze, clear sky
        "wind_speed"        : data["wind"]["speed"],        # wind speed
        "timestamp"         : datetime.now().strftime("%Y-%m-%d %H:%M:%S") # current time
    }
    
    # Return the weather dictionary
    return weather

# Step 7 - This function uploads weather data to S3
def upload_to_s3(weather_data, city):
    
    # Create a unique file name using city name and current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"weather-data/{city}_{timestamp}.json"

    # Upload the data to S3 bucket
    s3_client.put_object(
        Bucket=BUCKET_NAME,       # which bucket to upload to
        Key=file_name,            # file name inside bucket
        Body=json.dumps(weather_data),  # convert data to JSON string
        ContentType="application/json"  # tell S3 it is a JSON file
    )
    
    # Print success message
    print(f"✅ Uploaded {city} data to S3 → {file_name}")

# Step 8 - Main function that runs everything
def main():
    print("🚀 Weather Pipeline Started...")
    
    # Keep running forever in a loop
    while True:
        
        # Go through each city one by one
        for city in CITIES:
            try:
                # Fetch weather for this city
                weather = fetch_weather(city)
                
                # Upload it to S3
                upload_to_s3(weather, city)
                
                # Print weather summary in terminal
                print(f"🌤️ {city}: {weather['temperature']}°C | Humidity: {weather['humidity']}% | {weather['weather_condition']}")
            
            except Exception as e:
                # If any error happens print it and continue
                print(f"❌ Error for {city}: {e}")

        # Wait 5 minutes before fetching again
        print(f"\n⏳ Waiting 5 minutes before next fetch...\n")
        time.sleep(300)  # 300 seconds = 5 minutes

# Step 9 - Start the program
if __name__ == "__main__":
    main()  