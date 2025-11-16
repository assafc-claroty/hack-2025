# Getting Started with NL to SQL Translator

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Run Example

```bash
python example.py
```

## Basic Usage

### Command Line Tool

```bash
# Simple query (outputs JSON)
./nl2sql.py "Show me all assets in site 54"

# Pretty-printed output
./nl2sql.py --pretty "Find approved assets"

# Get SQL string
./nl2sql.py --sql "Show me all assets in site 54"

# Get detailed information
./nl2sql.py --details "How many assets are there?"
```

### Python Library

```python
from nl_to_sql import NLToSQLTranslator

# Initialize
translator = NLToSQLTranslator()

# Translate a query
result = translator.translate("Show me all assets in site 54")

# Output:
# {
#     "table": "assets",
#     "select": ["*"],
#     "where": [{"column": "site", "operator": "=", "value": 54}],
#     "order_by": [],
#     "limit": None
# }
```

## Run Tests

```bash
# Run all tests
python -m unittest discover tests -v
```

## Project Structure

```
test1/
├── nl_to_sql/              # Main package
│   ├── __init__.py         # Package initialization
│   ├── translator.py       # Main interface
│   ├── parser.py           # spaCy-based parser
│   ├── entity_recognizer.py # Entity extraction
│   ├── intent_classifier.py # Intent detection
│   ├── query_builder.py    # JSON query construction
│   └── schema.py           # Table schema definition
├── tests/                  # Test suite
│   ├── test_translator.py  # Unit tests
│   └── test_examples.py    # Example queries
├── nl2sql.py              # Command-line tool ⭐
├── requirements.txt        # Dependencies
├── example.py             # Example usage script
├── verify_setup.py        # Setup verification
├── README.md              # Full documentation
├── GETTING_STARTED.md     # This file
└── CLI_USAGE.md           # CLI detailed guide
```

## Key Features

✓ **Command-Line Tool** for easy query translation  
✓ **Natural Language Processing** with spaCy  
✓ **Dependency Tree Analysis** for semantic understanding  
✓ **Intent Classification** (SELECT, COUNT, EXISTS)  
✓ **Entity Recognition** (columns, operators, values)  
✓ **JSON Output** for structured queries  
✓ **SQL String Generation** (optional)  
✓ **SELECT queries only** (no INSERT/UPDATE/DELETE)

## Example Queries

| Natural Language | Result |
|-----------------|--------|
| "Show me all assets" | SELECT * FROM assets |
| "Find assets in site 54" | SELECT * FROM assets WHERE site = 54 |
| "Show me approved assets" | SELECT * FROM assets WHERE approved = TRUE |
| "How many assets are there?" | SELECT COUNT(*) FROM assets |

## Next Steps

1. Try the CLI tool: `./nl2sql.py --pretty "Show me all assets"`
2. Read [CLI_USAGE.md](CLI_USAGE.md) for detailed CLI examples
3. Read the full [README.md](README.md) for API documentation
4. Run [example.py](example.py) to see the Python library in action
5. Customize [schema.py](nl_to_sql/schema.py) for your table structure
6. Extend entity patterns in [entity_recognizer.py](nl_to_sql/entity_recognizer.py)

## Need Help?

- Check the README.md for full API reference
- Run tests to see expected behavior
- Review example.py for usage patterns

