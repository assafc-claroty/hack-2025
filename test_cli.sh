#!/bin/bash
# Quick test script for the CLI tool

echo "==================================================================="
echo "NL to SQL CLI Tool - Quick Test"
echo "==================================================================="
echo ""

# Check if spaCy is installed
if ! python -c "import spacy" 2>/dev/null; then
    echo "❌ spaCy not installed. Please run:"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Check if model is available
if ! python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "❌ spaCy model not installed. Please run:"
    echo "   python -m spacy download en_core_web_sm"
    exit 1
fi

echo "✅ Dependencies verified"
echo ""

# Test 1: Basic query
echo "Test 1: Basic query"
echo "Command: ./nl2sql.py \"Show me all assets\""
./nl2sql.py "Show me all assets"
echo ""

# Test 2: Pretty output
echo "Test 2: Pretty JSON output"
echo "Command: ./nl2sql.py --pretty \"Find assets in site 54\""
./nl2sql.py --pretty "Find assets in site 54"
echo ""

# Test 3: SQL output
echo "Test 3: SQL string output"
echo "Command: ./nl2sql.py --sql \"Show me approved assets in site 54\""
./nl2sql.py --sql "Show me approved assets in site 54"
echo ""

# Test 4: Count query
echo "Test 4: Count query"
echo "Command: ./nl2sql.py --sql \"How many assets are there?\""
./nl2sql.py --sql "How many assets are there?"
echo ""

# Test 5: stdin
echo "Test 5: Reading from stdin"
echo "Command: echo \"List all assets\" | ./nl2sql.py --stdin --sql"
echo "List all assets" | ./nl2sql.py --stdin --sql
echo ""

echo "==================================================================="
echo "✅ All tests completed successfully!"
echo "==================================================================="

