from core.broker import broker
from services.lead_service import lead_service
import asyncio

@broker.task
async def process_leads_task(niche: str, lat: float, lng: float, radius: int):
    """
    Background task to process niche search.
    This runs inside the Worker process.
    """
    print(f"WORKER: Starting background processing for {niche}...")

    # We call the service we created in Phase 1
    # Since process_niche_search is synchronous in the current service,
    # we run it in a thread to not block the async loop.
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None,
        lead_service.process_niche_search,
        niche, lat, lng, radius
    )

    print(f"WORKER: Finished processing {len(results)} leads for {niche}")
    return f"Processed {len(results)} leads"
