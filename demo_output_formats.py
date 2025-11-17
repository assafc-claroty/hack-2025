#!/usr/bin/env python3
"""
Demonstration of output format options in NL-to-SQL Translator.

This script shows how to use the different output formats:
- SQL: Get SQL query string
- JSON: Get structured JSON representation
- Both: Get both SQL and JSON
"""

from nl_to_sql import NLToSQLTranslator

def demo_output_formats():
    """Demonstrate all output format options."""
    
    query = "Show me all assets in site 54"
    
    print("=" * 80)
    print("NL-to-SQL Translator - Output Format Demo")
    print("=" * 80)
    print(f"\nQuery: \"{query}\"\n")
    
    # Demo 1: SQL format (default)
    print("-" * 80)
    print("1. SQL Format (output_format='sql')")
    print("-" * 80)
    translator_sql = NLToSQLTranslator(output_format="sql")
    result = translator_sql.translate_with_format(query)
    print(f"Type: {type(result)}")
    print(f"Result:\n{result}\n")
    
    # Demo 2: JSON format
    print("-" * 80)
    print("2. JSON Format (output_format='json')")
    print("-" * 80)
    translator_json = NLToSQLTranslator(output_format="json")
    result = translator_json.translate_with_format(query)
    print(f"Type: {type(result)}")
    print(f"Result:")
    import json
    print(json.dumps(result, indent=2))
    print()
    
    # Demo 3: Both formats
    print("-" * 80)
    print("3. Both Formats (output_format='both')")
    print("-" * 80)
    translator_both = NLToSQLTranslator(output_format="both")
    result = translator_both.translate_with_format(query)
    print(f"Type: {type(result)}")
    print(f"Result has keys: {list(result.keys())}")
    print(f"\nSQL:\n{result['sql']}")
    print(f"\nJSON:")
    print(json.dumps(result['json'], indent=2))
    print()
    
    # Demo 4: Override format at call time
    print("-" * 80)
    print("4. Override Format at Call Time")
    print("-" * 80)
    translator = NLToSQLTranslator(output_format="json")  # Default is JSON
    print("Translator default format: json")
    print("\nOverride to SQL:")
    result = translator.translate_with_format(query, output_format="sql")
    print(result)
    print()
    
    # Demo 5: Format output helper
    print("-" * 80)
    print("5. Using format_output() Helper")
    print("-" * 80)
    translator = NLToSQLTranslator()
    query_json = translator.translate(query)
    
    print("Format as SQL:")
    print(translator.format_output(query_json, "sql"))
    
    print("\nFormat as JSON (pretty):")
    print(translator.format_output(query_json, "json", pretty=True))
    
    print("\nFormat as both:")
    print(translator.format_output(query_json, "both", pretty=True))
    print()
    
    # Demo 6: Multiple queries with different formats
    print("-" * 80)
    print("6. Multiple Queries with Different Formats")
    print("-" * 80)
    
    queries = [
        "Find all Siemens PLCs",
        "What Rockwell devices do we have?",
        "Show me high risk assets"
    ]
    
    translator = NLToSQLTranslator(output_format="sql")
    
    for q in queries:
        sql = translator.translate_with_format(q)
        print(f"Query: {q}")
        print(f"SQL:   {sql}")
        print()
    
    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)

if __name__ == "__main__":
    demo_output_formats()

