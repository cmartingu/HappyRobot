from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# CORS (por si lo llamas desde otra plataforma)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # puedes restringir esto si es necesario
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carga los datos de cargas
with open("loads.json", "r") as f:
    loads = json.load(f)

@app.get("/search_loads")
def search_loads(equipment_type: str = Query(None)):
    for load in loads:
        if not equipment_type or load["equipment_type"].lower() == equipment_type.lower():
            return load
    return {"message": "No load found"}