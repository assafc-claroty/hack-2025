"""
Test cases for typical query examples.
"""

import unittest
from nl_to_sql import NLToSQLTranslator


class TestTypicalQueries(unittest.TestCase):
    """Test cases for typical natural language queries."""
    
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
    
    def _print_result(self, query, result):
        """Helper to print query results for debugging."""
        print(f"\nQuery: {query}")
        print(f"Result: {result}")
        if "sql" in result:
            print(f"SQL: {result['sql']}")
    
    def test_show_all_assets(self):
        """Test: Show me all assets"""
        query = "Show me all assets"
        result = self.translator.translate_with_details(query)
        
        self.assertEqual(result["query"]["table"], "assets")
        self.assertEqual(result["query"]["select"], ["*"])
        self.assertEqual(result["intent"]["type"], "select")
    
    def test_find_assets_in_site(self):
        """Test: Find assets in site 54"""
        query = "Find assets in site 54"
        result = self.translator.translate_with_details(query)
        
        self.assertEqual(result["query"]["table"], "assets")
        self.assertTrue(any(
            c["column"] == "site" and c["value"] == 54 
            for c in result["query"]["where"]
        ))
    
    def test_show_approved_assets(self):
        """Test: Show me approved assets"""
        query = "Show me approved assets"
        result = self.translator.translate_with_details(query)
        
        self.assertTrue(any(
            c["column"] == "approved" and c["value"] is True
            for c in result["query"]["where"]
        ))
    
    def test_find_valid_assets(self):
        """Test: Find valid assets"""
        query = "Find valid assets"
        result = self.translator.translate_with_details(query)
        
        self.assertTrue(any(
            c["column"] == "valid" and c["value"] is True
            for c in result["query"]["where"]
        ))
    
    def test_get_assets_by_name(self):
        """Test: Get assets with name server01"""
        query = "Get assets with name server01"
        result = self.translator.translate_with_details(query)
        
        # Should have a name condition
        name_conditions = [
            c for c in result["query"]["where"] 
            if c["column"] == "name"
        ]
        self.assertTrue(len(name_conditions) > 0)
    
    def test_list_assets_in_site(self):
        """Test: List assets in site 100"""
        query = "List assets in site 100"
        result = self.translator.translate_with_details(query)
        
        self.assertTrue(any(
            c["column"] == "site" and c["value"] == 100
            for c in result["query"]["where"]
        ))
    
    def test_display_all_assets(self):
        """Test: Display all assets"""
        query = "Display all assets"
        result = self.translator.translate_with_details(query)
        
        self.assertEqual(result["query"]["table"], "assets")
        self.assertEqual(result["intent"]["type"], "select")
    
    def test_get_assets_by_resource(self):
        """Test: Get assets for resource 42"""
        query = "Get assets for resource 42"
        result = self.translator.translate_with_details(query)
        
        # Should have a resource condition
        resource_conditions = [
            c for c in result["query"]["where"]
            if c["column"] == "resource"
        ]
        self.assertTrue(len(resource_conditions) > 0)
    
    def test_show_ghost_assets(self):
        """Test: Show me ghost assets"""
        query = "Show me ghost assets"
        result = self.translator.translate_with_details(query)
        
        self.assertTrue(any(
            c["column"] == "ghost" and c["value"] is True
            for c in result["query"]["where"]
        ))
    
    def test_find_parsed_assets(self):
        """Test: Find parsed assets"""
        query = "Find parsed assets"
        result = self.translator.translate_with_details(query)
        
        self.assertTrue(any(
            c["column"] == "parsed" and c["value"] is True
            for c in result["query"]["where"]
        ))
    
    def test_multiple_conditions_site_and_approved(self):
        """Test: Show me approved assets in site 54"""
        query = "Show me approved assets in site 54"
        result = self.translator.translate_with_details(query)
        
        # Should have both conditions
        has_site = any(
            c["column"] == "site" and c["value"] == 54
            for c in result["query"]["where"]
        )
        has_approved = any(
            c["column"] == "approved" and c["value"] is True
            for c in result["query"]["where"]
        )
        
        self.assertTrue(has_site)
        self.assertTrue(has_approved)
    
    def test_count_query(self):
        """Test: How many assets are there?"""
        query = "How many assets are there?"
        result = self.translator.translate_with_details(query)
        
        self.assertEqual(result["intent"]["type"], "count")
        self.assertIn("COUNT", result["query"]["select"][0])


if __name__ == "__main__":
    unittest.main()

