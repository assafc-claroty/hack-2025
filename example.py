#!/usr/bin/env python3
"""
Example usage of the NL to SQL Translator.

This script demonstrates how to use the translator with various query types.
"""

from nl_to_sql import NLToSQLTranslator
import json


def print_result(query, result):
    """Pretty print a translation result."""
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}")
    print("\nJSON Representation:")
    print(json.dumps(result["query"], indent=2))
    print(f"\nSQL: {result['sql']}")
    print(f"\nIntent: {result['intent']['type']}")
    print(f"{'='*80}\n")


def main():
    """Run example queries."""
    print("Natural Language to SQL Query Translator - Examples")
    print("=" * 80)
    
    try:
        # Initialize the translator
        translator = NLToSQLTranslator()
        print("✓ Translator initialized successfully")
        print("✓ Using spaCy model: en_core_web_sm")
        print()
        
        # Security & Vulnerability Management prompts
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
        
        # Combine all queries
        queries = (
            security_prompts +
            discovery_prompts +
            targeted_prompts +
            incident_prompts +
            troubleshooting_prompts +
            realistic_prompts
        )
        
        for query in queries:
            result = translator.translate_with_details(query)
            print_result(query, result)
        
        print("\n✓ All examples completed successfully!")
        
    except RuntimeError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease install the spaCy model:")
        print("  python -m spacy download en_core_web_sm")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

