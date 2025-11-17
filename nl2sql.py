#!/usr/bin/env python3
"""
Command-line tool for Natural Language to SQL Query translation.

Usage:
    nl2sql.py "Show me all assets in site 54"
    nl2sql.py --sql "Find approved assets"
    nl2sql.py --details "How many assets are there?"
"""

import sys
import json
import argparse
from nl_to_sql import NLToSQLTranslator


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Translate natural language queries to SQL JSON representation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Output JSON (default)
  %(prog)s "Show me all assets in site 54"
  
  # Output SQL only
  %(prog)s --format sql "Find approved assets"
  %(prog)s --sql "Find approved assets"  # shorthand
  
  # Output both SQL and JSON
  %(prog)s --format both "List assets in site 100"
  %(prog)s --format both --pretty "List assets in site 100"
  
  # Pretty-print JSON
  %(prog)s --pretty "Show me all assets"
  
  # Get detailed translation info
  %(prog)s --details "How many assets are there?"
  
  # Read from stdin
  echo "Show me all assets" | %(prog)s --stdin
        """
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Natural language query to translate"
    )
    
    parser.add_argument(
        "--format",
        choices=["sql", "json", "both"],
        default="json",
        help="Output format: 'sql' for SQL string, 'json' for JSON representation, 'both' for both (default: json)"
    )
    
    parser.add_argument(
        "--sql",
        action="store_true",
        help="Output SQL string instead of JSON (shorthand for --format sql)"
    )
    
    parser.add_argument(
        "--details",
        action="store_true",
        help="Output detailed information including intent and entities"
    )
    
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (default: compact)"
    )
    
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read query from stdin"
    )
    
    parser.add_argument(
        "--model",
        default="en_core_web_sm",
        help="spaCy model to use (default: en_core_web_sm)"
    )
    
    parser.add_argument(
        "--table",
        default="assets",
        help="Database table name (default: assets)"
    )
    
    args = parser.parse_args()
    
    # Get the query
    if args.stdin:
        query = sys.stdin.read().strip()
    elif args.query:
        query = args.query
    else:
        parser.print_help()
        return 1
    
    if not query:
        print("Error: Empty query provided", file=sys.stderr)
        return 1
    
    # Determine output format
    output_format = args.format
    if args.sql:
        output_format = "sql"
    
    # Initialize translator
    try:
        translator = NLToSQLTranslator(
            model_name=args.model,
            table_name=args.table,
            output_format=output_format
        )
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nPlease install the spaCy model:", file=sys.stderr)
        print(f"  python -m spacy download {args.model}", file=sys.stderr)
        return 1
    
    # Translate the query
    try:
        if args.details:
            # Details mode - output full translation details
            result = translator.translate_with_details(query)
            if args.pretty:
                print(json.dumps(result, indent=2))
            else:
                print(json.dumps(result))
        else:
            # Use the new translate_with_format method
            result = translator.translate_with_format(query, output_format)
            
            if output_format == "sql":
                # SQL string output
                print(result)
            elif output_format == "json":
                # JSON output
                if args.pretty:
                    print(json.dumps(result, indent=2))
                else:
                    print(json.dumps(result))
            elif output_format == "both":
                # Both SQL and JSON
                if args.pretty:
                    print("SQL:")
                    print(result["sql"])
                    print("\nJSON:")
                    print(json.dumps(result["json"], indent=2))
                else:
                    print(f"SQL: {result['sql']}")
                    print(f"JSON: {json.dumps(result['json'])}")
        
        return 0
        
    except Exception as e:
        print(f"Error translating query: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

