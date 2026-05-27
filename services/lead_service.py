from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.google_maps import google_service
from core.analyzer import analyzer
from core.scoring import scorer
from services.sales_generator import generator
from services.dork_service import dork_service
from core.cache import save_to_cache

class LeadService:
    def _process_single_lead(self, place: Dict[str, Any], niche: str) -> Dict[str, Any]:
        """
        Processes a single lead: fetches details, enriches via dorks, analyzes and scores.
        """
        try:
            details = google_service.get_business_details(place["place_id"])

            # --- Enriquecimento via Dorks ---
            business_name = details.get("name", "Business")
            address = details.get("formatted_address", "")
            city = address.split(",")[-1].strip() if address else "Brazil"
            website = details.get("website")

            enrichment = dork_service.enrich_lead(business_name, city, website)

            analysis = analyzer.analyze_business(details)
            score_data = scorer.calculate_score(analysis)
            approach = generator.generate_approach(business_name, score_data, analysis)

            return {
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
                "niche": niche,
                "instagram": enrichment.get("instagram"),
                "linkedin": enrichment.get("linkedin"),
                "email": enrichment.get("email"),
                "tech_stack": enrichment.get("tech_stack"),
                "digital_footprint": enrichment.get("digital_footprint")
            }
        except Exception as e:
            print(f"Error processing lead {place.get('place_id')}: {e}")
            return None

    def process_niche_search(self, niche: str, lat: float, lng: float, radius: int) -> List[Dict[str, Any]]:
        """
        Orchestrates the full lead generation process using parallel processing.
        """
        radius_meters = radius * 1000
        raw_results = google_service.search_nearby_businesses(niche, lat, lng, radius_meters)

        if not raw_results:
            return []

        # Limit to 30 leads to keep processing time reasonable
        # Note: Google Maps typically returns up to 20 results per page.
        leads_to_process = raw_results[:30]

        processed_leads = []

        # Use ThreadPoolExecutor to process leads in parallel
        # We reduce max_workers from 10 to 5 to avoid triggering rate limits on SearXNG/Google
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Create a list of futures
            future_to_lead = {executor.submit(self._process_single_lead, place, niche): place for place in leads_to_process}

            for future in as_completed(future_to_lead):
                result = future.result()
                if result:
                    processed_leads.append(result)

        save_to_cache(processed_leads)
        return processed_leads

lead_service = LeadService()
