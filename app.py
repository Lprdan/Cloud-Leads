from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json

from core.config import settings
from services.google_maps import google_service
from core.analyzer import analyzer
from core.scoring import scorer
from services.sales_generator import generator
from services.export_service import export_service

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="CloudLeads Finder API")

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Local cache path
CACHE_FILE = os.path.join(BASE_DIR, "data", "cache.json")

def save_to_cache(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_from_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "CloudLeads Finder Dashboard"})

@app.get("/api/search")
async def search_leads(niche: str = "restaurants", radius: int = 50000, lat: float = -23.3522, lng: float = -46.9185):
    """
    Triggers the lead generation process.
    """
    print(f"DEBUG: Searching for {niche} | Radius: {radius} | Lat: {lat} | Lng: {lng}")
    # 1. Search for businesses
    # Convert radius from km to meters
    radius_meters = radius * 1000
    raw_results = google_service.search_nearby_businesses(niche, lat, lng, radius_meters)

    processed_leads = []
    for place in raw_results:
        # 2. Get Full Details
        details = google_service.get_business_details(place["place_id"])

        # 3. Analyze Presence
        analysis = analyzer.analyze_business(details)

        # 4. Score Lead
        score_data = scorer.calculate_score(analysis)

        # 5. Generate Sales Approach
        approach = generator.generate_approach(details.get("name", "Business"), score_data, analysis)

        # Combine everything into a Lead object
        lead = {
            "id": place["place_id"],
            "name": details.get("name"),
            "address": details.get("formatted_address"),
            "phone": details.get("formatted_phone_number"),
            "website": details.get("website"),
            "rating": details.get("rating"),
            "reviews": details.get("user_ratings_total"),
            "lat": details.get("geometry", {}).get("location", {}).get("lat"),
            "lng": details.get("geometry", {}).get("location", {}).get("lng"),
            "score": score_data["score"],
            "potential": score_data["potential"],
            "reasons": score_data["reasons"],
            "approach": approach,
            "niche": niche
        }
        processed_leads.append(lead)

    save_to_cache(processed_leads)
    return processed_leads

@app.get("/api/export")
async def export_leads(format: str = "csv"):
    leads = load_from_cache()
    if not leads:
        return JSONResponse(status_code=404, content={"error": "No leads found in cache to export"})

    filepath = export_service.export_leads(leads, format)
    return {"message": "Export successful", "path": filepath}

@app.get("/api/stats")
async def get_stats():
    leads = load_from_cache()
    total = len(leads)
    no_website = len([l for l in leads if not l["website"]])
    high_potential = len([l for l in leads if l["potential"] == "High Potential"])

    return {
        "total_leads": total,
        "no_website": no_website,
        "high_potential": high_potential
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
