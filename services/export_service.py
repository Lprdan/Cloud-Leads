import pandas as pd
import json
import os
from core.config import settings
from typing import List, Dict, Any

class ExportService:
    def __init__(self):
        self.export_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def export_leads(self, leads: List[Dict[str, Any]], format: str = "csv") -> str:
        """
        Exports the list of leads to the specified format.
        """
        if not leads:
            return "No data to export"

        df = pd.DataFrame(leads)
        filename = f"leads_export_{format}"
        filepath = os.path.join(self.export_dir, filename)

        if format == "csv":
            filepath += ".csv"
            df.to_csv(filepath, index=False, encoding="utf-8-sig")
        elif format == "xlsx":
            filepath += ".xlsx"
            df.to_excel(filepath, index=False)
        elif format == "json":
            filepath += ".json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(leads, f, indent=4, ensure_ascii=False)
        else:
            return "Unsupported format"

        return filepath

export_service = ExportService()
