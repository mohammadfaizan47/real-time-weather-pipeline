# 🌦️ Real-Time Weather Data Pipeline

## 📌 Overview
An end-to-end real-time data pipeline fetching live weather 
data for 5 Indian cities using OpenWeatherMap API and AWS.

## 🏗️ Architecture
OpenWeatherMap API → Python → AWS S3 → AWS Glue → AWS Athena → Streamlit

## 🛠️ Tech Stack
- Python
- AWS S3
- AWS Glue
- AWS Athena
- Streamlit

## ⚙️ Setup
1. Clone the repo
2. Install dependencies
   pip install -r requirements.txt
3. Create .env file with your keys
   API_KEY=your_openweathermap_key
   AWS_ACCESS_KEY=your_aws_key
   AWS_SECRET_KEY=your_aws_secret
   BUCKET_NAME=your_bucket_name
   REGION=your_region
4. Run the pipeline
   python fetch_weather.py
5. Run the dashboard
   streamlit run dashboard.py

## 📊 Dashboard
Live Streamlit dashboard displaying real-time city-wise 
weather metrics connected to AWS Athena.
