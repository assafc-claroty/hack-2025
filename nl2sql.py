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
  %(prog)s "Show me all assets in site 54"
  %(prog)s --sql "Find approved assets"
  %(prog)s --details "How many assets are there?"
  %(prog)s --pretty "List assets in site 100"
  echo "Show me all assets" | %(prog)s --stdin
        """
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Natural language query to translate"
    )
    
    parser.add_argument(
        "--sql",
        action="store_true",
        help="Output SQL string instead of JSON"
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
    
    # Initialize translator
    try:
        translator = NLToSQLTranslator(
            model_name=args.model,
            table_name=args.table
        )
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nPlease install the spaCy model:", file=sys.stderr)
        print(f"  python -m spacy download {args.model}", file=sys.stderr)
        return 1
    
    # Translate the query
    try:
        if args.details:
            result = translator.translate_with_details(query)
        elif args.sql:
            result = translator.translate_to_sql(query)
            print(result)
            return 0
        else:
            result = translator.translate(query)
        
        # Output the result
        if args.pretty:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result))
        
        return 0
        
    except Exception as e:
        print(f"Error translating query: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

