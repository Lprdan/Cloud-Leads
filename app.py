from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import json

from core.cache import save_to_cache, load_from_cache
from services.lead_service import lead_service
from services.export_service import export_service
from core.broker import broker
from tasks.lead_tasks import process_leads_task

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.startup()
    yield
    await broker.shutdown()

app = FastAPI(title="CloudLeads Finder API", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "CloudLeads Finder Dashboard"})

@app.get("/api/search")
async def search_leads(niche: str = "restaurants", radius: int = 50000, lat: float = -23.3522, lng: float = -46.9185):
    """
    Triggers the lead generation process in the background.
    """
    print(f"API: Scheduling search for {niche} | Radius: {radius} | Lat: {lat} | Lng: {lng}")

    # Instead of calling the service directly, we send a task to Redis
    await process_leads_task.kiq(niche, lat, lng, radius)

    return {
        "status": "processing",
        "message": f"Search for {niche} has been started in the background. Please check stats or export in a few moments.",
        "details": {
            "niche": niche,
            "radius": radius
        }
    }

@app.get("/api/leads")
async def get_leads():
    """
    Returns the current list of leads from cache.
    Ensures it always returns a list to avoid frontend crashes.
    """
    try:
        leads = load_from_cache()
        if leads is None or not isinstance(leads, list):
            return []
        return leads
    except Exception as e:
        print(f"Error loading leads from cache: {e}")
        return []

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
