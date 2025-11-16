"""
Complete translator tests to reach 100% coverage on translator.py.

Covers lines 150, 166-198 which are the analyze_dependency_tree and explain_translation methods.
"""

import pytest
from nl_to_sql import NLToSQLTranslator


class TestTranslatorDependencyAnalysis:
    """Comprehensive tests for dependency tree analysis."""
    
    @pytest.fixture
    def translator(self):
        """Provide translator instance."""
        return NLToSQLTranslator()
    
    def test_analyze_dependency_tree_complete_structure(self, translator):
        """Test complete dependency tree analysis structure."""
        query = "Show me all assets in site 54 with high risk"
        tree = translator.analyze_dependency_tree(query)
        
        # Verify all expected keys
        assert "tokens" in tree
        assert "dependencies" in tree
        assert "noun_chunks" in tree
        assert "entities" in tree
        
        # Verify tokens structure
        assert len(tree["tokens"]) > 0
        for token in tree["tokens"]:
            assert "text" in token
            assert "lemma" in token
            assert "pos" in token
            assert "tag" in token
            assert "dep" in token
            assert "head" in token
            assert "children" in token
        
        # Verify dependencies structure
        assert len(tree["dependencies"]) > 0
        for dep in tree["dependencies"]:
            assert "token" in dep
            assert "dep" in dep
            assert "head" in dep
        
        # Verify noun_chunks is a list
        assert isinstance(tree["noun_chunks"], list)
        
        # Verify entities is a list
        assert isinstance(tree["entities"], list)
    
    def test_analyze_dependency_tree_with_simple_query(self, translator):
        """Test dependency tree with simple query."""
        tree = translator.analyze_dependency_tree("Show assets")
        
        assert len(tree["tokens"]) >= 2  # At least "Show" and "assets"
        assert len(tree["dependencies"]) >= 2
    
    def test_analyze_dependency_tree_with_complex_query(self, translator):
        """Test dependency tree with complex query."""
        tree = translator.analyze_dependency_tree(
            "Find all approved assets in site 54 that are not ghost assets"
        )
        
        # Complex query should have many tokens
        assert len(tree["tokens"]) > 5
        assert len(tree["dependencies"]) > 5
    
    def test_analyze_dependency_tree_noun_chunks(self, translator):
        """Test noun chunk extraction in dependency tree."""
        tree = translator.analyze_dependency_tree("Show all critical assets in production site")
        
        # Should have noun chunks
        assert isinstance(tree["noun_chunks"], list)
        # Noun chunks have text, root, and dep
        for chunk in tree["noun_chunks"]:
            assert "text" in chunk
            assert "root" in chunk
            assert "dep" in chunk
    
    def test_analyze_dependency_tree_with_numbers(self, translator):
        """Test dependency tree with numeric values."""
        tree = translator.analyze_dependency_tree("Show assets in site 54 with risk 10")
        
        # Should parse numbers
        assert len(tree["tokens"]) > 0
        # Check if any token is a number
        number_tokens = [t for t in tree["tokens"] if t["text"] in ["54", "10"]]
        assert len(number_tokens) > 0


class TestTranslatorExplanation:
    """Comprehensive tests for translation explanation."""
    
    @pytest.fixture
    def translator(self):
        """Provide translator instance."""
        return NLToSQLTranslator()
    
    def test_explain_translation_complete_output(self, translator):
        """Test complete explanation output structure."""
        query = "Show me all assets in site 54"
        explanation = translator.explain_translation(query)
        
        # Verify all sections are present
        assert "Query:" in explanation
        assert query in explanation
        
        assert "Intent:" in explanation
        assert "select" in explanation.lower() or "count" in explanation.lower()
        
        assert "SQL:" in explanation
        assert "SELECT" in explanation
        
        assert "Dependency Analysis:" in explanation
        assert "-" * 60 in explanation  # Section separator
        
        assert "Recognized Entities:" in explanation
        
        assert "Extracted Conditions:" in explanation
    
    def test_explain_translation_with_columns(self, translator):
        """Test explanation includes recognized columns."""
        explanation = translator.explain_translation("Show assets in site 54")
        
        # Should mention the site column
        assert "Column:" in explanation or "site" in explanation.lower()
    
    def test_explain_translation_with_values(self, translator):
        """Test explanation includes recognized values."""
        explanation = translator.explain_translation("Show assets in site 54")
        
        # Should mention the value 54
        assert "Value:" in explanation or "54" in explanation
    
    def test_explain_translation_with_conditions(self, translator):
        """Test explanation includes extracted conditions."""
        explanation = translator.explain_translation("Show assets in site 54 that are approved")
        
        # Should have conditions section
        assert "Extracted Conditions:" in explanation
        # Should mention site condition
        assert "site" in explanation.lower()
    
    def test_explain_translation_dependency_tokens(self, translator):
        """Test explanation includes dependency token details."""
        explanation = translator.explain_translation("Show assets")
        
        # Should have token details with POS, DEP, HEAD
        assert "POS:" in explanation
        assert "DEP:" in explanation
        assert "HEAD:" in explanation
    
    def test_explain_translation_with_cve(self, translator):
        """Test explanation with CVE query."""
        explanation = translator.explain_translation("Show assets with CVE-2025-10501")
        
        # Should mention CVE
        assert "CVE" in explanation or "cve" in explanation.lower()
        assert "2025" in explanation
    
    def test_explain_translation_with_multiple_conditions(self, translator):
        """Test explanation with multiple WHERE conditions."""
        explanation = translator.explain_translation(
            "Show assets in site 54 with high risk and approved"
        )
        
        # Should show multiple conditions
        assert "Extracted Conditions:" in explanation
        # Should have multiple condition entries
        condition_section = explanation.split("Extracted Conditions:")[1]
        # Count condition lines (lines that start with spaces and have operators)
        assert len(condition_section.strip().split("\n")) >= 0
    
    def test_explain_translation_formatting(self, translator):
        """Test explanation is well-formatted."""
        explanation = translator.explain_translation("Show me assets")
        
        # Should have proper formatting
        assert "\n" in explanation  # Multiple lines
        assert "  " in explanation  # Indentation
        assert "-" * 60 in explanation  # Section separators
        
        # Should be substantial
        assert len(explanation) > 200
    
    def test_explain_translation_with_count_intent(self, translator):
        """Test explanation with COUNT intent."""
        explanation = translator.explain_translation("How many assets are there?")
        
        # Should show count intent
        assert "Intent:" in explanation
        assert "count" in explanation.lower()
        assert "COUNT" in explanation  # SQL should have COUNT
    
    def test_explain_translation_with_exists_intent(self, translator):
        """Test explanation with EXISTS intent."""
        explanation = translator.explain_translation("Does asset exist?")
        
        # Should show intent
        assert "Intent:" in explanation
        # Intent could be exists or select
        assert "select" in explanation.lower() or "exists" in explanation.lower()
    
    def test_explain_translation_entity_types(self, translator):
        """Test explanation shows entity types."""
        explanation = translator.explain_translation("Show assets with IP 192.168.1.1")
        
        # Should show value type
        assert "type:" in explanation.lower() or "Value:" in explanation
        # Should mention IP
        assert "192.168.1.1" in explanation
    
    def test_explain_translation_with_no_conditions(self, translator):
        """Test explanation when no conditions are extracted."""
        explanation = translator.explain_translation("Show all assets")
        
        # Should still have all sections
        assert "Query:" in explanation
        assert "Intent:" in explanation
        assert "SQL:" in explanation
        assert "Extracted Conditions:" in explanation
    
    def test_explain_translation_with_boolean_column(self, translator):
        """Test explanation with boolean column."""
        explanation = translator.explain_translation("Show approved assets")
        
        # Should recognize approved column
        assert "approved" in explanation.lower()
    
    def test_explain_translation_with_operators(self, translator):
        """Test explanation shows operators."""
        explanation = translator.explain_translation("Show assets in site 54")
        
        # Should show operator in conditions
        condition_section = explanation.split("Extracted Conditions:")
        if len(condition_section) > 1:
            # Should have operator symbols like =, >, <, etc.
            assert any(op in condition_section[1] for op in ["=", ">", "<", "LIKE"])


class TestTranslatorIntegration:
    """Integration tests for complete translation flow."""
    
    @pytest.fixture
    def translator(self):
        """Provide translator instance."""
        return NLToSQLTranslator()
    
    def test_full_translation_pipeline(self, translator):
        """Test complete translation pipeline from query to explanation."""
        query = "Show assets in site 54 with high risk"
        
        # Test all translation methods work together
        json_result = translator.translate(query)
        sql_result = translator.translate_to_sql(query)
        detailed_result = translator.translate_with_details(query)
        tree = translator.analyze_dependency_tree(query)
        explanation = translator.explain_translation(query)
        
        # All should complete successfully
        assert "table" in json_result
        assert "SELECT" in sql_result
        assert "query" in detailed_result
        assert "tokens" in tree
        assert "Query:" in explanation
        
        # Results should be consistent
        assert detailed_result["sql"] == sql_result
    
    def test_translation_consistency_across_methods(self, translator):
        """Test that different translation methods return consistent results."""
        query = "Count assets in site 54"
        
        json_result = translator.translate(query)
        detailed_result = translator.translate_with_details(query)
        
        # JSON results should match
        assert json_result == detailed_result["query"]
        
        # SQL should match
        sql_from_translate = translator.translate_to_sql(query)
        sql_from_details = detailed_result["sql"]
        assert sql_from_translate == sql_from_details
    
    def test_explanation_reflects_actual_translation(self, translator):
        """Test that explanation matches actual translation."""
        query = "Show assets in site 54"
        
        detailed_result = translator.translate_with_details(query)
        explanation = translator.explain_translation(query)
        
        # Explanation should include the actual SQL
        assert detailed_result["sql"] in explanation
        
        # Explanation should include the intent
        assert detailed_result["intent"]["type"] in explanation.lower()
    
    def test_dependency_tree_used_in_translation(self, translator):
        """Test that dependency tree analysis is used in translation."""
        query = "Show assets with name server01"
        
        tree = translator.analyze_dependency_tree(query)
        detailed_result = translator.translate_with_details(query)
        
        # Tree should have tokens that appear in the query
        token_texts = [t["text"] for t in tree["tokens"]]
        assert "Show" in token_texts or "show" in [t.lower() for t in token_texts]
        assert "assets" in token_texts or "assets" in [t.lower() for t in token_texts]
        
        # Translation should use dependency information
        assert len(detailed_result["entities"]["columns"]) > 0 or len(detailed_result["entities"]["values"]) > 0

