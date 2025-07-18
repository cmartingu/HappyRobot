from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from geopy.distance import geodesic
import json
import random
import os
from datetime import datetime

import gspread
from google.oauth2 import service_account
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("loads.json", "r") as f:
    loads = json.load(f)

city_coordinates = {
    "Atlanta, GA": (33.7490, -84.3880),
    "Miami, FL": (25.7617, -80.1918),
    "Dallas, TX": (32.7767, -96.7970),
    "Phoenix, AZ": (33.4484, -112.0740),
    "Chicago, IL": (41.8781, -87.6298),
    "New York, NY": (40.7128, -74.0060),
    "Los Angeles, CA": (34.0522, -118.2437),
    "Denver, CO": (39.7392, -104.9903),
    "Houston, TX": (29.7604, -95.3698),
    "Seattle, WA": (47.6062, -122.3321),
    "San Francisco, CA": (37.7749, -122.4194),
    "Orlando, FL": (28.5383, -81.3792),
    "Charlotte, NC": (35.2271, -80.8431),
    "Las Vegas, NV": (36.1699, -115.1398),
    "LANDISVILLE, PA": (40.0948, -76.4144)
}

@app.get("/search_loads")
def search_loads(equipment_type: str = Query(None)):
    filtered = [load for load in loads if not equipment_type or load["equipment_type"].lower() == equipment_type.lower()]
    if filtered:
        return random.choice(filtered)
    return {"message": "No load found"}

@app.get("/search_loads/{phy_city}")
def search_load_by_location(phy_city: str, equipment_type: str = Query(None)):
    city_upper = phy_city.strip().upper()
    matched_city = None

    for city in city_coordinates:
        if city_upper in city.upper():
            matched_city = city
            break

    filtered = [load for load in loads if not equipment_type or load["equipment_type"].lower() == equipment_type.lower()]
    if not filtered:
        return {"message": "No loads found with given criteria."}

    if not matched_city:
        return random.choice(filtered)

    origin_coord = city_coordinates[matched_city]

    closest_load = min(
        filtered,
        key=lambda load: geodesic(origin_coord, city_coordinates.get(load["origin"], (0, 0))).miles
    )

    return closest_load

@app.post("/log_result")
async def log_result(request: Request):
    data = await request.json()

    # Inicializar Google Sheets API
    creds_info = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    creds = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).sheet1

    # Extraer los campos individualmente
    timestamp = datetime.utcnow().isoformat()
    carrier_name = data.get("carrier_name", "")
    agreed_price = data.get("agreed_rate", "")
    load_id = data.get("load_id", "")
    sentiment = data.get("sentiment", "")
    outcome = data.get("outcome", "")

    # Insertar en la hoja
    row = [timestamp, carrier_name, agreed_price, load_id, sentiment, outcome]
    sheet.append_row(row, value_input_option="RAW")

    return {"message": "Log saved to Google Sheets"}
