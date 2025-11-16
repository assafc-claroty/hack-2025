# Command Line Tool Usage Guide

## Overview

The `nl2sql.py` command-line tool provides a simple interface for translating natural language queries to SQL JSON representations.

## Installation

Ensure you have completed the setup:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Basic Commands

### 1. Simple Query (JSON Output)

```bash
./nl2sql.py "Show me all assets in site 54"
```

**Output:**
```json
{"table":"assets","select":["*"],"where":[{"column":"site","operator":"=","value":54}],"order_by":[],"limit":null}
```

### 2. Pretty-Printed JSON

```bash
./nl2sql.py --pretty "Show me all assets in site 54"
```

**Output:**
```json
{
  "table": "assets",
  "select": [
    "*"
  ],
  "where": [
    {
      "column": "site",
      "operator": "=",
      "value": 54
    }
  ],
  "order_by": [],
  "limit": null
}
```

### 3. SQL String Output

```bash
./nl2sql.py --sql "Show me all assets in site 54"
```

**Output:**
```sql
SELECT * FROM assets WHERE site = 54
```

### 4. Detailed Output

```bash
./nl2sql.py --details --pretty "Show me approved assets"
```

**Output:**
```json
{
  "query": {
    "table": "assets",
    "select": ["*"],
    "where": [
      {
        "column": "approved",
        "operator": "=",
        "value": true
      }
    ],
    "order_by": [],
    "limit": null
  },
  "sql": "SELECT * FROM assets WHERE approved = TRUE",
  "intent": {
    "type": "select",
    "confidence": 1.0,
    "aggregation": null,
    "select_columns": ["*"]
  },
  "entities": {
    "columns": [...],
    "operators": [...],
    "values": [...]
  }
}
```

### 5. Reading from Standard Input

```bash
echo "Find assets in site 100" | ./nl2sql.py --stdin --pretty
```

Or with a file:
```bash
cat queries.txt | ./nl2sql.py --stdin --sql
```

## Common Use Cases

### Query a specific site

```bash
./nl2sql.py --sql "Show me all assets in site 54"
# SELECT * FROM assets WHERE site = 54
```

### Filter by boolean flags

```bash
./nl2sql.py --sql "Find approved assets"
# SELECT * FROM assets WHERE approved = TRUE

./nl2sql.py --sql "Show me valid assets"
# SELECT * FROM assets WHERE valid = TRUE
```

### Multiple conditions

```bash
./nl2sql.py --sql "Show me approved assets in site 54"
# SELECT * FROM assets WHERE approved = TRUE AND site = 54
```

### Count queries

```bash
./nl2sql.py --sql "How many assets are there?"
# SELECT COUNT(*) FROM assets

./nl2sql.py --sql "Count assets in site 54"
# SELECT COUNT(*) FROM assets WHERE site = 54
```

### All assets

```bash
./nl2sql.py --sql "Show me all assets"
# SELECT * FROM assets
```

## Advanced Options

### Custom spaCy Model

Use a larger, more accurate model:

```bash
# First download the model
python -m spacy download en_core_web_lg

# Then use it
./nl2sql.py --model en_core_web_lg "Show me all assets"
```

### Custom Table Name

```bash
./nl2sql.py --table my_custom_table "Show me all records"
```

**Output:**
```json
{"table":"my_custom_table","select":["*"],"where":[],"order_by":[],"limit":null}
```

## Batch Processing

Process multiple queries from a file:

```bash
# Create a file with queries
cat > queries.txt << EOF
Show me all assets in site 54
Find approved assets
How many assets are there?
EOF

# Process each query
while IFS= read -r query; do
  echo "Query: $query"
  ./nl2sql.py --sql "$query"
  echo ""
done < queries.txt
```

## Integration Examples

### Shell Script Integration

```bash
#!/bin/bash
# translate_and_execute.sh

QUERY="$1"
JSON=$(./nl2sql.py "$QUERY")
echo "Generated query: $JSON"

# Could pipe to database query tool
# echo "$JSON" | your_query_executor
```

### Python Integration

```python
import subprocess
import json

def translate_query(nl_query):
    result = subprocess.run(
        ['./nl2sql.py', nl_query],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

query_json = translate_query("Show me all assets in site 54")
print(query_json)
```

### API Endpoint Integration

```python
from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__)

@app.route('/translate', methods=['POST'])
def translate():
    query = request.json.get('query')
    result = subprocess.run(
        ['./nl2sql.py', query],
        capture_output=True,
        text=True
    )
    return jsonify(json.loads(result.stdout))
```

## Troubleshooting

### Error: spaCy model not found

```bash
Error: spaCy model 'en_core_web_sm' not found. Please install it with: python -m spacy download en_core_web_sm
```

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Error: Empty query provided

Make sure to quote your query:
```bash
# Wrong
./nl2sql.py Show me all assets

# Correct
./nl2sql.py "Show me all assets"
```

### Getting Help

```bash
./nl2sql.py --help
```

## Tips

1. **Always quote your queries** to prevent shell interpretation
2. **Use `--pretty`** for human-readable output during development
3. **Use `--sql`** for direct SQL string output
4. **Use `--details`** for debugging and understanding how the query was parsed
5. **Pipe with `--stdin`** for batch processing or integration with other tools

