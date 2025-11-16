#!/usr/bin/env python3
"""
Demonstration of full semantic parsing with dependency tree analysis.

This script showcases the enhanced NL-to-SQL translator's ability to:
1. Parse natural language using spaCy's dependency trees
2. Extract semantic relationships between entities
3. Recognize complex patterns (CVEs, IPs, vendors)
4. Visualize the parsing process for debugging
"""

from nl_to_sql import NLToSQLTranslator
import json


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def demo_basic_dependency_analysis():
    """Demonstrate basic dependency tree analysis."""
    print_section("Basic Dependency Tree Analysis")
    
    translator = NLToSQLTranslator()
    query = "Show me all assets affected by CVE-2025-10501 in site 54"
    
    print(f"Query: {query}\n")
    
    # Get dependency tree information
    tree = translator.analyze_dependency_tree(query)
    
    print("Token Analysis:")
    print("-" * 80)
    print(f"{'Token':<15} {'Lemma':<15} {'POS':<8} {'Tag':<8} {'Dep':<12} {'Head':<15}")
    print("-" * 80)
    
    for token in tree["tokens"]:
        print(
            f"{token['text']:<15} {token['lemma']:<15} {token['pos']:<8} "
            f"{token['tag']:<8} {token['dep']:<12} {token['head']:<15}"
        )
    
    print("\n\nDependency Relationships:")
    print("-" * 80)
    for dep in tree["dependencies"]:
        print(f"  {dep['token']:15} --[{dep['dep']}]--> {dep['head']}")
    
    print("\n\nNoun Chunks:")
    print("-" * 80)
    for chunk in tree["noun_chunks"]:
        print(f"  '{chunk['text']}' (root: {chunk['root']}, dep: {chunk['dep']})")


def demo_cve_recognition():
    """Demonstrate CVE pattern recognition."""
    print_section("CVE Pattern Recognition")
    
    translator = NLToSQLTranslator()
    
    queries = [
        "Show me all assets affected by CVE-2025-10501",
        "Find assets vulnerable to CVE-2017-12819 in site 54",
        "Has CVE-2025-10501 been remediated?",
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = translator.translate_with_details(query)
        
        print(f"SQL: {result['sql']}")
        
        # Show recognized CVE values
        cve_values = [v for v in result["entities"]["values"] if v.get("type") == "cve"]
        if cve_values:
            print(f"Recognized CVEs: {[v['value'] for v in cve_values]}")


def demo_ip_recognition():
    """Demonstrate IP address pattern recognition."""
    print_section("IP Address Pattern Recognition")
    
    translator = NLToSQLTranslator()
    
    queries = [
        "Find all information about IP 10.89.46.34",
        "Show me assets with IP starting with 10.89",
        "What vulnerabilities exist on 192.168.1.100?",
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = translator.translate_with_details(query)
        
        print(f"SQL: {result['sql']}")
        
        # Show recognized IP values
        ip_values = [v for v in result["entities"]["values"] if v.get("type") == "ip_address"]
        if ip_values:
            print(f"Recognized IPs: {[v['value'] for v in ip_values]}")


def demo_semantic_relationships():
    """Demonstrate semantic relationship extraction."""
    print_section("Semantic Relationship Extraction")
    
    translator = NLToSQLTranslator()
    query = "Show me high risk assets that need immediate patching"
    
    print(f"Query: {query}\n")
    
    # Get full explanation
    explanation = translator.explain_translation(query)
    print(explanation)


def demo_complex_queries():
    """Demonstrate parsing of complex security queries."""
    print_section("Complex Security Query Parsing")
    
    translator = NLToSQLTranslator()
    
    queries = [
        "Find all Siemens PLCs in our network",
        "Show me assets that are both vulnerable and recently active",
        "List all high-risk assets in the affected site",
        "What Rockwell devices do we have?",
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = translator.translate_with_details(query)
        
        print(f"Intent: {result['intent']['type']}")
        print(f"SQL: {result['sql']}")
        
        # Show vendor recognition
        vendor_values = [v for v in result["entities"]["values"] if v.get("type") == "vendor"]
        if vendor_values:
            print(f"Recognized Vendors: {[v['value'] for v in vendor_values]}")


def demo_dependency_paths():
    """Demonstrate dependency path analysis between entities."""
    print_section("Dependency Path Analysis")
    
    translator = NLToSQLTranslator()
    query = "Find assets vulnerable to CVE-2025-10501 in site 54"
    
    print(f"Query: {query}\n")
    
    result = translator.translate_with_details(query)
    tree = translator.analyze_dependency_tree(query)
    
    print("Extracted Conditions:")
    print("-" * 80)
    for cond in result["query"]["where"]:
        print(f"  Column: {cond['column']}")
        print(f"  Operator: {cond['operator']}")
        print(f"  Value: {cond['value']}")
        print()
    
    print("\nEntity Recognition:")
    print("-" * 80)
    print(f"Columns found: {len(result['entities']['columns'])}")
    for col in result['entities']['columns']:
        print(f"  - {col['column']} (text: '{col['text']}')")
    
    print(f"\nValues found: {len(result['entities']['values'])}")
    for val in result['entities']['values']:
        print(f"  - {val['value']} (type: {val['type']}, text: '{val['text']}')")


def main():
    """Run all demonstrations."""
    print("\n" + "="*80)
    print("NL-to-SQL Translator: Full Semantic Parsing with Dependency Trees")
    print("="*80)
    
    try:
        # Run all demos
        demo_basic_dependency_analysis()
        demo_cve_recognition()
        demo_ip_recognition()
        demo_semantic_relationships()
        demo_complex_queries()
        demo_dependency_paths()
        
        print("\n" + "="*80)
        print("All demonstrations completed successfully!")
        print("="*80 + "\n")
        
    except RuntimeError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease install the spaCy model:")
        print("  python -m spacy download en_core_web_sm")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

