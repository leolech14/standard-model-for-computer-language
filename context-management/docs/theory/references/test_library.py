#!/usr/bin/env python3
"""Unit tests for reference library processing."""

import unittest
import json
from pathlib import Path
import sys

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from extract_with_captions import (
    CaptionDetector,
    calculate_spatial_distance,
)

REFS_DIR = Path(__file__).parent


class TestCaptionDetection(unittest.TestCase):
    """Test caption pattern matching."""

    def test_standard_figure_prefix(self):
        """Test standard 'Figure N' format."""
        self.assertTrue(CaptionDetector.is_caption_header("Figure 1. This is a caption"))
        self.assertTrue(CaptionDetector.is_caption_header("Fig. 2: Another caption"))
        self.assertTrue(CaptionDetector.is_caption_header("FIG. 3 - Caption text"))

    def test_case_insensitive(self):
        """Test case variations."""
        self.assertTrue(CaptionDetector.is_caption_header("figure 1. caption"))
        self.assertTrue(CaptionDetector.is_caption_header("FIGURE 2. caption"))

    def test_number_extraction(self):
        """Test extracting figure numbers."""
        self.assertEqual(CaptionDetector.extract_caption_number("Figure 1. caption"), "1")
        self.assertEqual(CaptionDetector.extract_caption_number("Fig. 2.5: caption"), "2.5")
        self.assertIsNone(CaptionDetector.extract_caption_number("Not a caption"))

    def test_false_positives(self):
        """Test rejecting non-caption text."""
        self.assertFalse(CaptionDetector.is_caption_header("This figure shows..."))
        self.assertFalse(CaptionDetector.is_caption_header("In figure 1 we see..."))


class TestSpatialDistance(unittest.TestCase):
    """Test spatial distance calculations."""

    def test_caption_below_image(self):
        """Caption directly below image should have positive distance."""
        img_bbox = (100, 500, 400, 600)  # x0, y0, x1, y1
        txt_bbox = (100, 650, 400, 700)  # 50 points below
        distance = calculate_spatial_distance(img_bbox, txt_bbox)
        self.assertEqual(distance, 50)

    def test_caption_above_image(self):
        """Caption above image should have negative distance."""
        img_bbox = (100, 500, 400, 600)
        txt_bbox = (100, 400, 400, 450)  # 50 points above
        distance = calculate_spatial_distance(img_bbox, txt_bbox)
        self.assertEqual(distance, -50)

    def test_overlapping(self):
        """Overlapping should return 0."""
        img_bbox = (100, 500, 400, 600)
        txt_bbox = (100, 550, 400, 650)  # Overlaps
        distance = calculate_spatial_distance(img_bbox, txt_bbox)
        self.assertEqual(distance, 0)


class TestLibraryStructure(unittest.TestCase):
    """Test library file structure."""

    def test_directories_exist(self):
        """All required directories exist."""
        self.assertTrue((REFS_DIR / "pdf").exists())
        self.assertTrue((REFS_DIR / "txt").exists())
        self.assertTrue((REFS_DIR / "metadata").exists())
        self.assertTrue((REFS_DIR / "index").exists())
        self.assertTrue((REFS_DIR / "images").exists())

    def test_catalog_exists(self):
        """Master catalog exists and is valid JSON."""
        catalog_file = REFS_DIR / "index/catalog.json"
        self.assertTrue(catalog_file.exists())

        catalog = json.loads(catalog_file.read_text())
        self.assertIn("total_refs", catalog)
        self.assertIn("references", catalog)
        self.assertIsInstance(catalog["references"], list)

    def test_concept_index_exists(self):
        """Concept index exists and maps concepts to refs."""
        concept_file = REFS_DIR / "index/concept_index.json"
        self.assertTrue(concept_file.exists())

        concepts = json.loads(concept_file.read_text())
        self.assertIn("holons", concepts)
        self.assertIn("free_energy_principle", concepts)
        self.assertIsInstance(concepts["holons"], list)

    def test_schemas_exist(self):
        """Required schemas exist."""
        self.assertTrue((REFS_DIR / "library_schema.json").exists())
        self.assertTrue((REFS_DIR / "holon_hierarchy_schema.json").exists())


class TestMetadataIntegrity(unittest.TestCase):
    """Test metadata file integrity."""

    def test_all_metadata_valid_json(self):
        """All metadata files are valid JSON."""
        meta_dir = REFS_DIR / "metadata"
        for meta_file in meta_dir.glob("*.json"):
            if "_analysis" in meta_file.name:
                continue
            try:
                json.loads(meta_file.read_text())
            except json.JSONDecodeError as e:
                self.fail(f"{meta_file.name} has invalid JSON: {e}")

    def test_metadata_has_required_fields(self):
        """All metadata has required fields."""
        meta_dir = REFS_DIR / "metadata"
        required = ["ref_id", "title", "authors", "source_type", "category"]

        for meta_file in meta_dir.glob("*.json"):
            if "_analysis" in meta_file.name:
                continue

            meta = json.loads(meta_file.read_text())
            for field in required:
                self.assertIn(field, meta, f"{meta_file.name} missing {field}")


class TestFileCorrespondence(unittest.TestCase):
    """Test that files correspond correctly."""

    def test_metadata_matches_pdfs(self):
        """Each metadata file has a corresponding PDF."""
        meta_dir = REFS_DIR / "metadata"
        pdf_dir = REFS_DIR / "pdf"

        for meta_file in meta_dir.glob("*.json"):
            if "_analysis" in meta_file.name:
                continue

            ref_id = meta_file.stem
            # Should have at least one PDF with this ref_id
            matching_pdfs = list(pdf_dir.glob(f"{ref_id}*.pdf"))
            self.assertGreater(len(matching_pdfs), 0,
                             f"No PDF found for {ref_id}")


if __name__ == "__main__":
    # Run tests
    unittest.main(argv=[''], verbosity=2, exit=False)
