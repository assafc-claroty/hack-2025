#!/usr/bin/env python3
"""
Script to demonstrate all example queries including security, discovery, and incident response.
"""

from nl_to_sql import NLToSQLTranslator

def print_query_result(query, result, query_num):
    """Print formatted query result."""
    print(f"\n{query_num}. Natural Language Query:")
    print(f"   \"{query}\"")
    print()
    print(f"   Generated SQL:")
    print(f"   {result['sql']}")
    print()
    print(f"   Intent: {result['intent']['type']}")
    print(f"   Table: {result['query']['table']}")
    
    if result['query']['where']:
        print(f"   Conditions:")
        for condition in result['query']['where']:
            operator = condition.get('operator', '=')
            value = condition['value']
            if isinstance(value, bool):
                value = 'TRUE' if value else 'FALSE'
            elif isinstance(value, str):
                value = f"'{value}'"
            print(f"     - {condition['column']} {operator} {value}")
    
    print("-" * 80)

def main():
    """Run all example queries and display results."""
    
    # Initialize translator
    print("Initializing NL-to-SQL Translator...")
    translator = NLToSQLTranslator()
    print("✓ Translator ready\n")
    print("=" * 80)
    
    # Security prompts
    security_prompts = [
        "Show me all assets affected by CVE-2025-10501",
        "Find assets vulnerable to CVE-2025-10501 in site 54",
        "What vulnerabilities exist on 10.89.46.34?",
        "Show me high risk assets that need immediate patching",
        "Has CVE-2017-12819 been remediated on our assets?",
        "What's the vulnerability status of site 47?"
    ]

    # Asset Discovery & Investigation prompts
    discovery_prompts = [
        "Find all information about IP 10.89.46.34",
        "Show me assets last seen in the last 24 hours",
        "What assets are currently online in site 54?",
        "List all active assets excluding ghost devices",
        "Find assets that haven't been seen since November 10th",
        "Show me newly discovered assets this week",
        "What assets belong to site 5?",
        "Are there any duplicate or ghost assets in the system?",
        "Find all Siemens PLCs in our network",
        "Show me assets by risk level"
    ]

    # Targeted Searches prompts
    targeted_prompts = [
        "Find assets with IP starting with 10.89",
        "Show me all assets in the industrial control network",
        "What Rockwell devices do we have?",
        "Find all assets with open critical vulnerabilities",
        "Show me assets that are both vulnerable and recently active",
        "List production assets affected by any CVE",
        "Find assets in site 54 with relevance score 1"
    ]

    # Incident Response prompts
    incident_prompts = [
        "Is 10.89.46.34 vulnerable to anything critical?",
        "Find all assets that might be affected by the recent breach",
        "Show me assets communicating with suspicious IPs",
        "What assets were active during the incident window?",
        "List all high-risk assets in the affected site",
        "Which assets need immediate attention?",
        "Find all exposed assets in the DMZ"
    ]

    # Troubleshooting prompts
    troubleshooting_prompts = [
        "What assets haven't been updated recently?",
        "Find orphaned or disconnected assets",
        "List assets with incomplete data"
    ]

    # Most Realistic "I'd Actually Type This" Questions
    realistic_prompts = [
        "10.89.46.34",
        "CVE-2025-10501",
        "site 54 vulnerabilities",
        "show me critical CVEs",
        "assets in site 47",
        "what's vulnerable",
        "recently active assets",
        "high risk"
    ]
    
    # Process all categories
    categories = [
        ("SECURITY QUERIES", security_prompts),
        ("ASSET DISCOVERY & INVESTIGATION", discovery_prompts),
        ("TARGETED SEARCHES", targeted_prompts),
        ("INCIDENT RESPONSE", incident_prompts),
        ("TROUBLESHOOTING", troubleshooting_prompts),
        ("REALISTIC SHORT QUERIES", realistic_prompts)
    ]
    
    total_queries = 0
    
    for category_name, prompts in categories:
        print(f"\n\n{'=' * 80}")
        print(f"  {category_name}")
        print(f"{'=' * 80}")
        
        for i, query in enumerate(prompts, 1):
            total_queries += 1
            try:
                result = translator.translate_with_details(query)
                print_query_result(query, result, i)
            except Exception as e:
                print(f"\n{i}. Natural Language Query:")
                print(f"   \"{query}\"")
                print(f"\n   ❌ ERROR: {str(e)}")
                print("-" * 80)
    
    print(f"\n\n{'=' * 80}")
    print(f"✓ Successfully processed {total_queries} queries across {len(categories)} categories")
    print(f"{'=' * 80}\n")

if __name__ == "__main__":
    main()

