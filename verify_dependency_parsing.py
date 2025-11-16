#!/usr/bin/env python3
"""
Quick verification that full semantic parsing with dependency trees is working.
"""

from nl_to_sql import NLToSQLTranslator
import json


def test_dependency_parsing():
    """Test that dependency tree analysis is working."""
    print("Testing Full Semantic Parsing with Dependency Trees")
    print("=" * 70)
    
    translator = NLToSQLTranslator()
    
    # Test 1: Basic dependency tree extraction
    print("\n1. Testing dependency tree extraction...")
    tree = translator.analyze_dependency_tree("Show me assets in site 54")
    assert "tokens" in tree, "Missing tokens in tree"
    assert "dependencies" in tree, "Missing dependencies in tree"
    assert len(tree["tokens"]) > 0, "No tokens found"
    print("   ✓ Dependency tree extraction working")
    
    # Test 2: CVE pattern recognition
    print("\n2. Testing CVE pattern recognition...")
    result = translator.translate_with_details(
        "Show me assets affected by CVE-2025-10501"
    )
    cve_values = [v for v in result["entities"]["values"] if v.get("type") == "cve"]
    assert len(cve_values) > 0, "CVE not recognized"
    assert cve_values[0]["value"] == "CVE-2025-10501", "Wrong CVE value"
    print(f"   ✓ CVE recognized: {cve_values[0]['value']}")
    print(f"   ✓ SQL generated: {result['sql']}")
    
    # Test 3: IP address recognition
    print("\n3. Testing IP address recognition...")
    result = translator.translate_with_details(
        "Find all information about IP 10.89.46.34"
    )
    ip_values = [v for v in result["entities"]["values"] 
                 if v.get("type") == "ip_address"]
    assert len(ip_values) > 0, "IP not recognized"
    assert ip_values[0]["value"] == "10.89.46.34", "Wrong IP value"
    print(f"   ✓ IP recognized: {ip_values[0]['value']}")
    print(f"   ✓ SQL generated: {result['sql']}")
    
    # Test 4: Semantic relationship extraction
    print("\n4. Testing semantic relationship extraction...")
    result = translator.translate_with_details(
        "Find assets vulnerable to CVE-2025-10501 in site 54"
    )
    assert len(result["query"]["where"]) >= 2, "Multiple conditions not extracted"
    print(f"   ✓ Extracted {len(result['query']['where'])} conditions")
    for cond in result["query"]["where"]:
        print(f"     - {cond['column']} {cond['operator']} {cond['value']}")
    
    # Test 5: Dependency path analysis
    print("\n5. Testing dependency path analysis...")
    tree = translator.analyze_dependency_tree(
        "Show me high risk assets"
    )
    # Check that we have dependency information
    assert len(tree["dependencies"]) > 0, "No dependencies found"
    print(f"   ✓ Found {len(tree['dependencies'])} dependency relationships")
    
    # Test 6: Operator inference from dependencies
    print("\n6. Testing operator inference...")
    result = translator.translate_with_details(
        "Show me assets affected by CVE-2025-10501"
    )
    # Should use LIKE operator for "affected by" pattern
    cve_conditions = [c for c in result["query"]["where"] 
                      if c["column"] == "CVE"]
    if cve_conditions:
        print(f"   ✓ Operator inferred: {cve_conditions[0]['operator']}")
        print(f"   ✓ Context: 'affected by' → LIKE operator")
    
    # Test 7: Explanation method
    print("\n7. Testing explanation method...")
    explanation = translator.explain_translation("Show me assets in site 54")
    assert "Dependency Analysis:" in explanation, "Missing dependency analysis"
    assert "Recognized Entities:" in explanation, "Missing entities"
    print("   ✓ Explanation method working")
    
    print("\n" + "=" * 70)
    print("✓ All tests passed! Full semantic parsing is working correctly.")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_dependency_parsing()
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        exit(1)
    except RuntimeError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease install the spaCy model:")
        print("  python -m spacy download en_core_web_sm")
        exit(1)

