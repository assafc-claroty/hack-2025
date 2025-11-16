# Natural Language to SQL Query Translator

A Python library for translating natural language queries to JSON-structured SQL representations using spaCy for linguistic analysis. This library is specifically designed for querying a single database table (no joins required) and supports SELECT queries only.

## Features

- **Natural Language Processing**: Uses spaCy's advanced NLP features including dependency parsing, part-of-speech tagging, and named entity recognition
- **Intent Classification**: Automatically identifies query intent (SELECT, COUNT, EXISTS)
- **Entity Recognition**: Extracts columns, operators, values, and logical connectors from natural language
- **JSON Output**: Generates structured JSON representations of SQL queries
- **SQL Generation**: Optional conversion to SQL strings
- **Extensible**: Easy to customize for different table schemas

## Installation

### Prerequisites

1. Install Python 3.7 or higher
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Download the spaCy language model:

```bash
python -m spacy download en_core_web_sm
```

For better accuracy, you can use a larger model:

```bash
python -m spacy download en_core_web_md
# or
python -m spacy download en_core_web_lg
```

## Quick Start

### Command Line Tool

```bash
# Basic usage - outputs JSON
./nl2sql.py "Show me all assets in site 54"

# Pretty-printed JSON
./nl2sql.py --pretty "Find approved assets"

# Output SQL string
./nl2sql.py --sql "Show me all assets in site 54"

# Get detailed information
./nl2sql.py --details "How many assets are there?"

# Read from stdin
echo "List assets in site 100" | ./nl2sql.py --stdin
```

### Python Library

```python
from nl_to_sql import NLToSQLTranslator

# Initialize the translator
translator = NLToSQLTranslator()

# Translate a natural language query
query = "Show me all assets in site 54"
result = translator.translate(query)

print(result)
# Output:
# {
#     "table": "assets",
#     "select": ["*"],
#     "where": [
#         {"column": "site", "operator": "=", "value": 54}
#     ],
#     "order_by": [],
#     "limit": None
# }
```

## Usage Examples

### Basic Queries

```python
from nl_to_sql import NLToSQLTranslator

translator = NLToSQLTranslator()

# Simple filter
result = translator.translate("Show me all assets")
# {"table": "assets", "select": ["*"], "where": [], ...}

# Filter by site
result = translator.translate("Find assets in site 54")
# {"table": "assets", "select": ["*"], "where": [{"column": "site", "operator": "=", "value": 54}], ...}

# Boolean filter
result = translator.translate("Show me approved assets")
# {"table": "assets", "select": ["*"], "where": [{"column": "approved", "operator": "=", "value": true}], ...}
```

### Multiple Conditions

```python
# Multiple filters with AND logic
result = translator.translate("Show me approved assets in site 54")
# {
#     "table": "assets",
#     "select": ["*"],
#     "where": [
#         {"column": "approved", "operator": "=", "value": true, "logic": "AND"},
#         {"column": "site", "operator": "=", "value": 54, "logic": "AND"}
#     ],
#     ...
# }
```

### Count Queries

```python
# Count intent
result = translator.translate("How many assets are there?")
# {"table": "assets", "select": ["COUNT(*)"], "where": [], ...}

result = translator.translate("Count assets in site 54")
# {"table": "assets", "select": ["COUNT(*)"], "where": [{"column": "site", "operator": "=", "value": 54}], ...}
```

### Getting SQL Output

```python
# Get SQL string directly
sql = translator.translate_to_sql("Show me all assets in site 54")
print(sql)
# Output: SELECT * FROM assets WHERE site = 54

# Get detailed information
details = translator.translate_with_details("Show me approved assets")
print(details["sql"])
# Output: SELECT * FROM assets WHERE approved = TRUE
print(details["intent"])
# Output: {"type": "select", "confidence": 1.0, ...}
```

## Supported Query Patterns

### Column References

The translator recognizes the following columns from the assets table:

- `id` (aliases: asset_id)
- `site` (aliases: location, site_id)
- `resource` (aliases: resource_id)
- `timestamp` (aliases: time, created)
- `last_updated` (aliases: updated, modified)
- `name` (aliases: asset_name)
- `display_name` (aliases: display, displayname)
- `approved` (aliases: approve)
- `valid` (aliases: validated)
- `ghost`
- `parsed`
- `special_hint` (aliases: hint, special)
- `state` (aliases: status)

### Operators

- **Equality**: `is`, `equals`, `=`
- **Inequality**: `not`, `is not`, `!=`
- **Comparison**: `greater than`, `less than`, `>`, `<`
- **Pattern matching**: `contains`, `like`, `includes`
- **Set membership**: `in`

### Intent Keywords

- **SELECT**: show, display, list, get, find, fetch, give, return
- **COUNT**: count, how many, number of
- **EXISTS**: has, have, does, is, are, exists

### Value Types

- **Integers**: `54`, `100`, `42`
- **Booleans**: `true`, `false`, `yes`, `no`, `approved`, `valid`
- **Strings**: Quoted strings or recognized patterns like IP addresses
- **Timestamps**: Date/time expressions

## Command Line Interface

The `nl2sql.py` script provides a convenient command-line interface for translating queries.

### Basic Usage

```bash
# Translate to JSON (compact)
./nl2sql.py "Show me all assets in site 54"

# Pretty-printed JSON
./nl2sql.py --pretty "Find approved assets"

# Output SQL string instead of JSON
./nl2sql.py --sql "Show me all assets in site 54"

# Get detailed output with intent and entities
./nl2sql.py --details "How many assets are there?"

# Read from stdin
echo "List assets in site 100" | ./nl2sql.py --stdin

# Use a different spaCy model
./nl2sql.py --model en_core_web_lg "Show me all assets"

# Use a different table name
./nl2sql.py --table my_table "Show me all records"
```

### CLI Options

- `query`: Natural language query (positional argument)
- `--sql`: Output SQL string instead of JSON
- `--details`: Include intent and entity information
- `--pretty`: Pretty-print JSON output
- `--stdin`: Read query from standard input
- `--model MODEL`: Specify spaCy model (default: en_core_web_sm)
- `--table TABLE`: Specify table name (default: assets)
- `--help`: Show help message

### Examples

```bash
# Basic query
$ ./nl2sql.py "Show me all assets"
{"table":"assets","select":["*"],"where":[],"order_by":[],"limit":null}

# Pretty output
$ ./nl2sql.py --pretty "Find assets in site 54"
{
  "table": "assets",
  "select": ["*"],
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

# SQL output
$ ./nl2sql.py --sql "Show me approved assets in site 54"
SELECT * FROM assets WHERE approved = TRUE AND site = 54

# Piping
$ echo "How many assets are there?" | ./nl2sql.py --stdin --sql
SELECT COUNT(*) FROM assets
```

## API Reference

### NLToSQLTranslator

Main class for translating natural language to SQL.

#### `__init__(model_name="en_core_web_sm", table_name="assets")`

Initialize the translator.

**Parameters:**
- `model_name` (str): Name of the spaCy model to use. Default: "en_core_web_sm"
- `table_name` (str): Name of the database table. Default: "assets"

#### `translate(query: str) -> Dict[str, Any]`

Translate a natural language query to JSON representation.

**Parameters:**
- `query` (str): Natural language query string

**Returns:**
- Dictionary with keys: `table`, `select`, `where`, `order_by`, `limit`

#### `translate_to_sql(query: str) -> str`

Translate a natural language query directly to SQL string.

**Parameters:**
- `query` (str): Natural language query string

**Returns:**
- SQL query string

#### `translate_with_details(query: str) -> Dict[str, Any]`

Translate with detailed information about the translation process.

**Parameters:**
- `query` (str): Natural language query string

**Returns:**
- Dictionary with keys: `query`, `sql`, `intent`, `entities`

## JSON Query Format

The JSON representation follows this structure:

```json
{
  "table": "assets",
  "select": ["*"],
  "where": [
    {
      "column": "site",
      "operator": "=",
      "value": 54,
      "logic": "AND"
    }
  ],
  "order_by": [
    {
      "column": "name",
      "direction": "ASC"
    }
  ],
  "limit": 10
}
```

### Fields

- **table** (str): Name of the database table
- **select** (list): List of columns or expressions to select (e.g., `["*"]`, `["COUNT(*)"]`)
- **where** (list): List of condition objects
  - **column** (str): Column name
  - **operator** (str): Comparison operator (`=`, `!=`, `>`, `<`, `LIKE`, `IN`)
  - **value** (any): Value to compare against
  - **logic** (str, optional): Logical connector for multiple conditions (`AND`, `OR`)
- **order_by** (list): List of ordering objects
  - **column** (str): Column to order by
  - **direction** (str): Sort direction (`ASC`, `DESC`)
- **limit** (int or null): Maximum number of rows to return

## Customization

### Using a Different Table

```python
translator = NLToSQLTranslator(table_name="my_table")
```

### Using a Larger spaCy Model

```python
translator = NLToSQLTranslator(model_name="en_core_web_lg")
```

### Extending Column Synonyms

Edit `nl_to_sql/schema.py` to add or modify column synonyms:

```python
COLUMN_SYNONYMS = {
    "site": ["site", "location", "site_id", "datacenter"],  # Add "datacenter"
    # ... other columns
}
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_translator

# Run with verbose output
python -m unittest discover tests -v
```

## Architecture

The library consists of five main components:

1. **Query Parser** (`parser.py`): Uses spaCy to parse natural language and extract linguistic features
2. **Entity Recognizer** (`entity_recognizer.py`): Identifies entities like columns, operators, and values using pattern matching
3. **Intent Classifier** (`intent_classifier.py`): Determines query intent using dependency tree analysis
4. **Query Builder** (`query_builder.py`): Constructs JSON representations from parsed components
5. **Translator** (`translator.py`): Main interface that orchestrates the pipeline

## Limitations

- **SELECT queries only**: No support for INSERT, UPDATE, DELETE, or other DML operations
- **Single table**: No support for JOINs or multi-table queries
- **English only**: Currently supports English language queries only
- **Pattern-based**: Uses rule-based patterns rather than machine learning models

## Future Enhancements

Possible improvements for future versions:

- Support for aggregation functions (SUM, AVG, MIN, MAX)
- GROUP BY and HAVING clauses
- Subqueries
- More sophisticated operator inference
- Custom NER model training for domain-specific entities
- Multi-language support
- Confidence scoring for ambiguous queries

## License

This project is provided as-is for educational and commercial use.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For issues, questions, or suggestions, please open an issue on the project repository.

