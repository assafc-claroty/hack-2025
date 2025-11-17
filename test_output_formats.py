#!/usr/bin/env python3
"""
Quick test script for output format functionality.
"""

from nl_to_sql import NLToSQLTranslator

def test_output_formats():
    """Test all output format options."""
    query = "Show me all assets in site 54"
    
    print("Testing Output Format Options")
    print("=" * 60)
    
    # Test 1: SQL format
    print("\n1. Testing SQL format...")
    translator = NLToSQLTranslator(output_format="sql")
    result = translator.translate_with_format(query)
    assert isinstance(result, str), "SQL format should return string"
    assert "SELECT" in result, "SQL should contain SELECT"
    assert "site = 54" in result, "SQL should contain condition"
    print(f"   ✓ SQL format works: {result}")
    
    # Test 2: JSON format
    print("\n2. Testing JSON format...")
    translator = NLToSQLTranslator(output_format="json")
    result = translator.translate_with_format(query)
    assert isinstance(result, dict), "JSON format should return dict"
    assert result["table"] == "assets", "JSON should have correct table"
    assert len(result["where"]) > 0, "JSON should have conditions"
    print(f"   ✓ JSON format works: {result['table']}, {len(result['where'])} conditions")
    
    # Test 3: Both format
    print("\n3. Testing both format...")
    translator = NLToSQLTranslator(output_format="both")
    result = translator.translate_with_format(query)
    assert isinstance(result, dict), "Both format should return dict"
    assert "sql" in result, "Both format should have 'sql' key"
    assert "json" in result, "Both format should have 'json' key"
    assert isinstance(result["sql"], str), "SQL should be string"
    assert isinstance(result["json"], dict), "JSON should be dict"
    print(f"   ✓ Both format works: has 'sql' and 'json' keys")
    
    # Test 4: Override format
    print("\n4. Testing format override...")
    translator = NLToSQLTranslator(output_format="json")  # Default JSON
    sql_result = translator.translate_with_format(query, output_format="sql")
    assert isinstance(sql_result, str), "Override to SQL should return string"
    json_result = translator.translate_with_format(query)  # Use default
    assert isinstance(json_result, dict), "Default JSON should return dict"
    print(f"   ✓ Format override works")
    
    # Test 5: format_output helper
    print("\n5. Testing format_output helper...")
    translator = NLToSQLTranslator()
    query_json = translator.translate(query)
    sql_str = translator.format_output(query_json, "sql")
    json_str = translator.format_output(query_json, "json", pretty=True)
    both_str = translator.format_output(query_json, "both", pretty=True)
    assert isinstance(sql_str, str), "format_output SQL should return string"
    assert isinstance(json_str, str), "format_output JSON should return string"
    assert isinstance(both_str, str), "format_output both should return string"
    assert "SELECT" in sql_str, "Formatted SQL should contain SELECT"
    assert "{" in json_str, "Formatted JSON should contain {"
    assert "SQL:" in both_str and "JSON:" in both_str, "Both should contain both labels"
    print(f"   ✓ format_output helper works")
    
    # Test 6: Backward compatibility
    print("\n6. Testing backward compatibility...")
    translator = NLToSQLTranslator()
    json_result = translator.translate(query)
    sql_result = translator.translate_to_sql(query)
    details = translator.translate_with_details(query)
    assert isinstance(json_result, dict), "translate() should still return dict"
    assert isinstance(sql_result, str), "translate_to_sql() should still return string"
    assert isinstance(details, dict), "translate_with_details() should still return dict"
    assert "sql" in details, "Details should contain sql"
    print(f"   ✓ Backward compatibility maintained")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_output_formats()

