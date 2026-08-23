import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.wes_analysis.service import analyze_wes_report

PDF_PATH = r"C:\Users\manukrishna\OneDrive\Desktop\main proj\wes\original\original_wes_report.pdf"


class TestWESAnalysis(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_wes_health_check(self):
        response = self.client.get("/api/v1/wes/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["module"], "wes_analysis")
        self.assertEqual(data["status"], "healthy")

    def test_analyze_original_wes_report_direct(self):
        self.assertTrue(os.path.exists(PDF_PATH), f"Test PDF file not found at {PDF_PATH}")
        
        with open(PDF_PATH, "rb") as f:
            pdf_bytes = f.read()

        res = analyze_wes_report(pdf_bytes)

        self.assertEqual(res.status, "success")
        self.assertIsNotNone(res.variants)
        self.assertTrue(len(res.variants) >= 2)

        # Variant 1: PYCR1 (CNV)
        var1 = res.variants[0]
        self.assertEqual(var1.reported_variant.gene, "PYCR1")
        self.assertEqual(var1.gene.symbol, "PYCR1")
        self.assertIn("Likely Pathogenic", var1.reported_variant.classification or "")

        # Variant 2: COL2A1 (SNV)
        var2 = res.variants[1]
        self.assertEqual(var2.reported_variant.gene, "COL2A1")
        self.assertEqual(var2.gene.symbol, "COL2A1")
        self.assertEqual(var2.reported_variant.cdna, "c.3559C>T")
        self.assertEqual(var2.reported_variant.protein, "p.Pro1187Ser")
        self.assertIn("Uncertain Significance", var2.reported_variant.classification or "")

        print("\n--- EXTRACTED JSON STRUCTURE FOR ORIGINAL WES REPORT ---")
        print(json.dumps(res.model_dump(exclude_none=True), indent=2))

    def test_analyze_wes_endpoint(self):
        self.assertTrue(os.path.exists(PDF_PATH), f"Test PDF file not found at {PDF_PATH}")

        with open(PDF_PATH, "rb") as f:
            files = {"file": ("original_wes_report.pdf", f, "application/pdf")}
            response = self.client.post("/api/v1/wes/analyze", files=files)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("variants", data)
        self.assertTrue(len(data["variants"]) >= 2)
        self.assertEqual(data["variants"][0]["reported_variant"]["gene"], "PYCR1")
        self.assertEqual(data["variants"][1]["reported_variant"]["gene"], "COL2A1")

    def test_test_variant_endpoint(self):
        payload = {
            "gene": "GNAO1",
            "transcript": "NM_020988.3",
            "cdna": "c.118G>T",
            "protein": "p.Gly40Trp",
            "zygosity": "HET",
            "classification": "PV"
        }
        response = self.client.post("/api/v1/wes/test-variant", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("reported_variant", data)
        self.assertEqual(data["reported_variant"]["gene"], "GNAO1")
        self.assertEqual(data["gene"]["symbol"], "GNAO1")
        self.assertEqual(data["annotations"]["clinvar"]["variation_id"], "666297")


if __name__ == "__main__":
    unittest.main()
