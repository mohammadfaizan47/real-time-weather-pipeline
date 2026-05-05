import streamlit as st
import boto3
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Athena client
client = boto3.client(
    "athena",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name=os.getenv("REGION")
)

RESULTS_BUCKET = f"s3://{os.getenv('BUCKET_NAME')}/athena-results/"

def run_athena_query(query):
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": "weather_db"},
        ResultConfiguration={"OutputLocation": RESULTS_BUCKET}
    )
    exec_id = response["QueryExecutionId"]

    # Wait for completion
    while True:
        status = client.get_query_execution(
            QueryExecutionId=exec_id
        )["QueryExecution"]["Status"]["State"]
        if status == "SUCCEEDED":
            break
        elif status == "FAILED":
            st.error("Athena query failed!")
            return None
        time.sleep(1)

    result = client.get_query_results(QueryExecutionId=exec_id)
    rows = result["ResultSet"]["Rows"]
    headers = [c["VarCharValue"] for c in rows[0]["Data"]]
    data = [
        [c.get("VarCharValue", "") for c in row["Data"]]
        for row in rows[1:]
    ]
    return pd.DataFrame(data, columns=headers)

# ── UI ──
st.set_page_config(page_title="Weather Pipeline", layout="wide")
st.title("🌦️ Live Weather Dashboard")
st.caption("OpenWeatherMap → S3 → Glue → Athena → Streamlit")

with st.spinner("Fetching data from Athena..."):
    df = run_athena_query("""
        SELECT city, temperature, feels_like, humidity,
               pressure, weather_condition, wind_speed, timestamp
        FROM weather_db.weather_processed
        ORDER BY timestamp DESC
    """)

if df is not None:
    df["temperature"] = pd.to_numeric(df["temperature"])
    df["humidity"]    = pd.to_numeric(df["humidity"])
    df["wind_speed"]  = pd.to_numeric(df["wind_speed"])

    # City metric cards
    st.subheader("📍 Current Conditions by City")
    cities = df["city"].unique()
    cols = st.columns(len(cities))
    for i, city in enumerate(cities):
        row = df[df["city"] == city].iloc[0]
        cols[i].metric(
            label=f"🏙️ {city}",
            value=f"{row['temperature']}°C",
            delta=f"Feels {row['feels_like']}°C"
        )

    st.divider()

    # Charts
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("🌡️ Temperature")
        temp = df.groupby("city")["temperature"].mean()
        st.bar_chart(temp)

    with col2:
        st.subheader("💧 Humidity")
        hum = df.groupby("city")["humidity"].mean()
        st.bar_chart(hum)

    with col3:
        st.subheader("💨 Wind Speed")
        wind = df.groupby("city")["wind_speed"].mean()
        st.bar_chart(wind)

    st.divider()
    st.subheader("📋 Raw Data")
    st.dataframe(df, use_container_width=True)