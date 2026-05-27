import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional
from core.config import settings

class DorkService:
    def __init__(self):
        # In Docker, we use the service name 'searxng'
        self.base_url = "http://searxng:8080/search"

    def _perform_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Performs a search via SearXNG and returns the results.
        """
        try:
            params = {
                "q": query,
                "format": "json",
                "engines": "google", # Only Google for speed and stability
            }
            response = requests.get(self.base_url, params=params, timeout=7)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            print(f"Dork search error for query {query}: {e}")
            return []

    def enrich_lead(self, business_name: str, city: str, website: Optional[str] = None) -> Dict[str, Any]:
        """
        Enriches a lead using a "Cascade Strategy": reducing requests by combining queries
        and short-circuiting unnecessary searches.
        """
        enrichment = {
            "instagram": None,
            "linkedin": None,
            "email": None,
            "tech_stack": "Unknown",
            "digital_footprint": "Low"
        }

        # --- STRATEGY 1: Combined Social Dork (1 request instead of 2) ---
        social_query = f'"{business_name}" "{city}" (site:instagram.com OR site:linkedin.com/company)'
        social_results = self._perform_search(social_query)

        if social_results:
            for res in social_results:
                url = res.get("url", "").lower()
                if "instagram.com" in url and not enrichment["instagram"]:
                    enrichment["instagram"] = res.get("url")
                elif "linkedin.com/company" in url and not enrichment["linkedin"]:
                    enrichment["linkedin"] = res.get("url")
                if enrichment["instagram"] and enrichment["linkedin"]:
                    break

        # --- STRATEGY 2: Targeted Email Search (Short-circuit) ---
        # Only search for email if the lead has some digital presence
        if website or enrichment["instagram"] or enrichment["linkedin"]:
            email_query = f'"{business_name}" "{city}" email OR contact'
            email_results = self._perform_search(email_query)
            if email_results:
                for res in email_results:
                    content = res.get("content", "").lower()
                    if "@" in content and "." in content:
                        enrichment["email"] = "Found (Check Snippets)"
                        break

        # --- STRATEGY 3: Tech Stack (Only if website exists) ---
        if website:
            tech_query = f'site:{website} "wordpress" OR "shopify" OR "wix" OR "elementor"'
            tech_results = self._perform_search(tech_query)
            if tech_results:
                content = " ".join([r.get("content", "").lower() for r in tech_results])
                if "wordpress" in content: enrichment["tech_stack"] = "WordPress"
                elif "shopify" in content: enrichment["tech_stack"] = "Shopify"
                elif "wix" in content: enrichment["tech_stack"] = "Wix"
                elif "elementor" in content: enrichment["tech_stack"] = "Elementor"

        # Footprint Score
        found_assets = [enrichment["instagram"], enrichment["linkedin"], website]
        found_count = len([x for x in found_assets if x])
        if found_count >= 3: enrichment["digital_footprint"] = "High"
        elif found_count >= 1: enrichment["digital_footprint"] = "Medium"
        else: enrichment["digital_footprint"] = "Low"

        return enrichment

dork_service = DorkService()
