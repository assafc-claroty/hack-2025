"""
Extended tests for NLToSQLTranslator - covering debugging and explanation features.
"""

import pytest
from nl_to_sql import NLToSQLTranslator


class TestTranslatorDebugFeatures:
    """Test debugging and explanation features of the translator."""
    
    @pytest.fixture
    def translator(self):
        """Provide translator instance."""
        return NLToSQLTranslator()
    
    def test_analyze_dependency_tree(self, translator):
        """Test dependency tree analysis."""
        tree = translator.analyze_dependency_tree("Show me assets in site 54")
        
        # Verify structure
        assert "tokens" in tree
        assert "dependencies" in tree
        assert "noun_chunks" in tree
        assert "entities" in tree
        
        # Verify tokens are populated
        assert len(tree["tokens"]) > 0
        assert isinstance(tree["tokens"], list)
        
        # Verify token structure
        first_token = tree["tokens"][0]
        assert "text" in first_token
        assert "lemma" in first_token
        assert "pos" in first_token
        assert "dep" in first_token
        assert "head" in first_token
        assert "children" in first_token
    
    def test_analyze_dependency_tree_with_cve(self, translator):
        """Test dependency tree analysis with CVE query."""
        tree = translator.analyze_dependency_tree("Has CVE-2017-12819 been remediated?")
        
        assert "tokens" in tree
        assert len(tree["tokens"]) > 0
        
        # Should have dependencies
        assert "dependencies" in tree
        assert len(tree["dependencies"]) > 0
    
    def test_explain_translation_basic(self, translator):
        """Test translation explanation for basic query."""
        explanation = translator.explain_translation("Show me assets in site 54")
        
        # Verify explanation contains key sections
        assert "Query:" in explanation
        assert "Intent:" in explanation
        assert "SQL:" in explanation
        assert "Dependency Analysis:" in explanation
        assert "Recognized Entities:" in explanation
        assert "Extracted Conditions:" in explanation
        
        # Verify it's a string
        assert isinstance(explanation, str)
        assert len(explanation) > 100  # Should be substantial
    
    def test_explain_translation_with_multiple_conditions(self, translator):
        """Test explanation for query with multiple conditions."""
        explanation = translator.explain_translation(
            "Find assets in site 54 that are approved"
        )
        
        assert "Query:" in explanation
        assert "site 54" in explanation.lower() or "54" in explanation
        assert "approved" in explanation.lower()
    
    def test_explain_translation_with_cve(self, translator):
        """Test explanation for CVE query."""
        explanation = translator.explain_translation(
            "Show assets affected by CVE-2025-10501"
        )
        
        assert "CVE" in explanation or "cve" in explanation.lower()
        assert "2025" in explanation
    
    def test_dependency_tree_tokens_have_correct_structure(self, translator):
        """Test that dependency tree tokens have all required fields."""
        tree = translator.analyze_dependency_tree("Find assets with high risk")
        
        for token in tree["tokens"]:
            # Verify all required fields are present
            assert "text" in token
            assert "lemma" in token
            assert "pos" in token
            assert "tag" in token
            assert "dep" in token
            assert "head" in token
            assert "children" in token
            
            # Verify types
            assert isinstance(token["text"], str)
            assert isinstance(token["lemma"], str)
            assert isinstance(token["pos"], str)
            assert isinstance(token["children"], list)
    
    def test_dependency_tree_dependencies_structure(self, translator):
        """Test that dependency relationships are captured correctly."""
        tree = translator.analyze_dependency_tree("Show me all assets")
        
        assert "dependencies" in tree
        assert len(tree["dependencies"]) > 0
        
        for dep in tree["dependencies"]:
            assert "token" in dep
            assert "dep" in dep
            assert "head" in dep
            assert isinstance(dep["token"], str)
            assert isinstance(dep["dep"], str)
            assert isinstance(dep["head"], str)
    
    def test_explain_translation_formatting(self, translator):
        """Test that explanation is well-formatted."""
        explanation = translator.explain_translation("Show me assets")
        
        # Should have section separators
        assert "-" * 60 in explanation
        
        # Should have newlines for readability
        assert "\n" in explanation
        
        # Should have indentation for structure
        assert "  " in explanation  # Indented content
    
    def test_analyze_dependency_tree_noun_chunks(self, translator):
        """Test that noun chunks are identified."""
        tree = translator.analyze_dependency_tree("Show me all critical assets in site 54")
        
        assert "noun_chunks" in tree
        # May or may not have noun chunks depending on spaCy parsing
        assert isinstance(tree["noun_chunks"], list)
    
    def test_analyze_dependency_tree_with_complex_query(self, translator):
        """Test dependency tree with complex multi-condition query."""
        tree = translator.analyze_dependency_tree(
            "Find all approved assets in site 54 with high risk"
        )
        
        # Should have many tokens
        assert len(tree["tokens"]) > 5
        
        # Should have dependencies
        assert len(tree["dependencies"]) > 5
        
        # Verify structure is intact
        assert "tokens" in tree
        assert "dependencies" in tree
        assert "noun_chunks" in tree
        assert "entities" in tree


class TestTranslatorEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def translator(self):
        """Provide translator instance."""
        return NLToSQLTranslator()
    
    def test_empty_query(self, translator):
        """Test handling of empty query."""
        result = translator.translate("")
        
        # Should return valid structure even for empty query
        assert "table" in result
        assert "select" in result
        assert "where" in result
        assert "order_by" in result
        assert "limit" in result
    
    def test_single_word_query(self, translator):
        """Test handling of single word query."""
        result = translator.translate("assets")
        
        # Should return valid structure
        assert "table" in result
        assert result["select"] == ["*"]
    
    def test_translate_with_details_structure(self, translator):
        """Test that translate_with_details returns all expected fields."""
        result = translator.translate_with_details("Show me assets")
        
        # Verify all expected fields
        assert "query" in result
        assert "sql" in result
        assert "intent" in result
        assert "entities" in result
        
        # Verify nested structure
        assert "table" in result["query"]
        assert "type" in result["intent"]
        assert "columns" in result["entities"]
    
    def test_translate_to_sql_returns_string(self, translator):
        """Test that translate_to_sql returns a string."""
        sql = translator.translate_to_sql("Show me assets")
        
        assert isinstance(sql, str)
        assert "SELECT" in sql
        assert "FROM" in sql
    
    def test_multiple_translations_independent(self, translator):
        """Test that multiple translations don't interfere with each other."""
        result1 = translator.translate("Show me assets in site 54")
        result2 = translator.translate("Find approved assets")
        
        # Results should be different
        assert result1 != result2
        
        # First should have site condition
        assert any(c["column"] == "site" for c in result1["where"])
        
        # Second should have approved condition
        assert any(c["column"] == "approved" for c in result2["where"])

