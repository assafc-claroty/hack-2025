#!/usr/bin/env python3
"""
Show all example queries with JSON output.
"""

import json
from nl_to_sql import NLToSQLTranslator

def main():
    """Run all example queries and display JSON output."""
    
    # Initialize translator with JSON format
    print("Initializing NL-to-SQL Translator...")
    translator = NLToSQLTranslator(output_format="json")
    print("✓ Translator ready\n")
    
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
    
    all_results = []
    
    for category_name, prompts in categories:
        category_results = {
            "category": category_name,
            "queries": []
        }
        
        for query in prompts:
            try:
                result = translator.translate_with_format(query, output_format="json")
                
                query_result = {
                    "query": query,
                    "json": result,
                    "sql": translator.query_builder.to_sql(result)
                }
                
                category_results["queries"].append(query_result)
                
            except Exception as e:
                category_results["queries"].append({
                    "query": query,
                    "error": str(e)
                })
        
        all_results.append(category_results)
    
    # Output as JSON
    print(json.dumps(all_results, indent=2))

if __name__ == "__main__":
    main()

