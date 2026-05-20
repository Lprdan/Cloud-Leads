import googlemaps
from core.config import settings
from typing import List, Dict, Any

class GoogleMapsService:
    def __init__(self):
        self.client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    def search_nearby_businesses(self, niche: str, lat: float, lng: float, radius_meters: int = 50000) -> List[Dict[str, Any]]:
        """
        Search for businesses of a specific niche around a specific point.
        """
        location = (lat, lng)

        try:
            # nearby_search is ideal for radius and coordinates
            # we use 'keyword' to target the niche
            results = self.client.places_nearby(
                location=location,
                radius=radius_meters,
                keyword=niche
            )

            leads = []
            if 'results' in results:
                for place in results['results']:
                    leads.append(place)

            return leads
        except Exception as e:
            print(f"Error searching Google Maps: {e}")
            return []

    def get_business_details(self, place_id: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific place.
        """
        try:
            # Fields we want to minimize API cost and maximize data
            fields = [
                "name", "formatted_address", "formatted_phone_number",
                "website", "rating", "user_ratings_total", "type",
                "geometry", "url", "photo"
            ]
            details = self.client.place(place_id=place_id, fields=fields)
            return details.get('result', {})
        except Exception as e:
            print(f"Error fetching details for {place_id}: {e}")
            return {}

# Singleton instance
google_service = GoogleMapsService()
