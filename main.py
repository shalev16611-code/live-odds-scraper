from fastapi import FastAPI, Body
from typing import List, Dict, Any

app = FastAPI()

data: List[Dict[str, Any]] = []

# הסקרייפר שולח לכאן נתונים
@app.post("/api/update-odds")
def update_odds(new_data: List[Dict[str, Any]] = Body(...)):
    global data
    data = new_data
    return {"status": "updated", "count": len(data)}

# האתר שלך מושך מכאן נתונים
@app.get("/api/live-odds")
def get_odds():
    return data