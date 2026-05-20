from typing import Dict, Any, List
from core.config import settings

class PresenceAnalyzer:
    @staticmethod
    def analyze_business(details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the business details to identify gaps in digital presence.
        """
        has_website = bool(details.get("website"))

        # Simple heuristics for social media detection
        # In a real scenario, we could search the website or use a specialized API
        # For this system, we check the business name and search for patterns
        business_name = details.get("name", "").lower()

        # We simulate Instagram/Social detection based on common patterns
        # (In a real product, we would implement a search for "Business Name Instagram")
        # For the prototype, we'll flag if they have no website as a primary indicator.

        analysis = {
            "has_website": has_website,
            "has_instagram": False, # Default to False, we'll use a heuristic in a real search
            "photo_count": len(details.get("photos", [])),
            "review_count": details.get("user_ratings_total", 0),
            "rating": details.get("rating", 0),
            "missing_assets": []
        }

        if not has_website:
            analysis["missing_assets"].append("website")

        if analysis["photo_count"] < 5:
            analysis["missing_assets"].append("quality_photos")

        if analysis["review_count"] < 10:
            analysis["missing_assets"].append("social_proof")

        return analysis

analyzer = PresenceAnalyzer()
