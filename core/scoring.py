from typing import Dict, Any
from core.config import settings

class LeadScorer:
    @staticmethod
    def calculate_score(analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates a lead score based on presence gaps and commercial potential.
        """
        score = 0
        reasons = []

        # 1. Website gap (Highest priority)
        if not analysis["has_website"]:
            score += settings.WEIGHT_NO_WEBSITE
            reasons.append("No professional website found")

        # 2. Social Media gap (Simulated/Heuristic)
        if not analysis["has_instagram"]:
            score += settings.WEIGHT_NO_SOCIAL
            reasons.append("Missing Instagram/Social presence")

        # 3. Quality assets gap
        if "quality_photos" in analysis["missing_assets"]:
            score += settings.WEIGHT_LOW_PHOTOS
            reasons.append("Limited visual content (photos)")

        # 4. Social Proof gap
        if "social_proof" in analysis["missing_assets"]:
            score += settings.WEIGHT_LOW_REVIEWS
            reasons.append("Low customer review volume")

        # 5. Bonus: High Rating but no site (Strong business, poor digital)
        if analysis["rating"] >= 4.0 and not analysis["has_website"]:
            score += settings.WEIGHT_HIGH_RATING_NO_SITE
            reasons.append("High customer satisfaction but lacks digital conversion tool")

        # Classification
        potential = "Low Potential"
        if score >= 70:
            potential = "High Potential"
        elif score >= 30:
            potential = "Medium Potential"

        return {
            "score": score,
            "potential": potential,
            "reasons": reasons
        }

scorer = LeadScorer()
