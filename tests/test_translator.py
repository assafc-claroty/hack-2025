"""
Unit tests for the NLToSQLTranslator.
"""

import unittest
from nl_to_sql import NLToSQLTranslator


class TestNLToSQLTranslator(unittest.TestCase):
    """Test cases for the NLToSQLTranslator class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the translator instance for all tests."""
        try:
            cls.translator = NLToSQLTranslator()
        except RuntimeError as e:
            raise unittest.SkipTest(
                f"Skipping tests: {e}. Please install spaCy model with: "
                "python -m spacy download en_core_web_sm"
            )
    
    def test_simple_site_filter(self):
        """Test: Show me all assets in site 54"""
        query = "Show me all assets in site 54"
        result = self.translator.translate(query)
        
        self.assertEqual(result["table"], "assets")
        self.assertEqual(result["select"], ["*"])
        self.assertTrue(len(result["where"]) > 0)
        
        # Check for site condition
        site_condition = next(
            (c for c in result["where"] if c["column"] == "site"), None
        )
        self.assertIsNotNone(site_condition)
        self.assertEqual(site_condition["value"], 54)
    
    def test_find_assets_in_site(self):
        """Test: Find assets in site 54"""
        query = "Find assets in site 54"
        result = self.translator.translate(query)
        
        self.assertEqual(result["table"], "assets")
        self.assertTrue(len(result["where"]) > 0)
        
        site_condition = next(
            (c for c in result["where"] if c["column"] == "site"), None
        )
        self.assertIsNotNone(site_condition)
        self.assertEqual(site_condition["value"], 54)
    
    def test_boolean_filter_approved(self):
        """Test: Show me approved assets"""
        query = "Show me approved assets"
        result = self.translator.translate(query)
        
        self.assertEqual(result["table"], "assets")
        
        # Check for approved condition
        approved_condition = next(
            (c for c in result["where"] if c["column"] == "approved"), None
        )
        self.assertIsNotNone(approved_condition)
        self.assertEqual(approved_condition["value"], True)
    
    def test_boolean_filter_valid(self):
        """Test: Find valid assets"""
        query = "Find valid assets"
        result = self.translator.translate(query)
        
        self.assertEqual(result["table"], "assets")
        
        valid_condition = next(
            (c for c in result["where"] if c["column"] == "valid"), None
        )
        self.assertIsNotNone(valid_condition)
        self.assertEqual(valid_condition["value"], True)
    
    def test_multiple_conditions(self):
        """Test: Show me approved assets in site 54"""
        query = "Show me approved assets in site 54"
        result = self.translator.translate(query)
        
        self.assertEqual(result["table"], "assets")
        self.assertTrue(len(result["where"]) >= 2)
        
        # Check both conditions exist
        site_condition = next(
            (c for c in result["where"] if c["column"] == "site"), None
        )
        approved_condition = next(
            (c for c in result["where"] if c["column"] == "approved"), None
        )
        
        self.assertIsNotNone(site_condition)
        self.assertIsNotNone(approved_condition)
    
    def test_state_filter(self):
        """Test: Find assets with state active"""
        query = "Find assets with state active"
        result = self.translator.translate(query)
        
        self.assertEqual(result["table"], "assets")
    
    def test_all_assets(self):
        """Test: Show me all assets"""
        query = "Show me all assets"
        result = self.translator.translate(query)
        
        self.assertEqual(result["table"], "assets")
        self.assertEqual(result["select"], ["*"])
    
    def test_translate_to_sql(self):
        """Test SQL string generation"""
        query = "Show me all assets in site 54"
        sql = self.translator.translate_to_sql(query)
        
        self.assertIsInstance(sql, str)
        self.assertIn("SELECT", sql)
        self.assertIn("FROM assets", sql)
        self.assertIn("WHERE", sql)
    
    def test_translate_with_details(self):
        """Test detailed translation output"""
        query = "Show me all assets"
        result = self.translator.translate_with_details(query)
        
        self.assertIn("query", result)
        self.assertIn("sql", result)
        self.assertIn("intent", result)
        self.assertIn("entities", result)
        
        # Check intent
        self.assertIn("type", result["intent"])


if __name__ == "__main__":
    unittest.main()

