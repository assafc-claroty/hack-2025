# Full Semantic Parsing with Dependency Trees

This document describes the comprehensive semantic parsing capabilities of the NL-to-SQL translator, which uses spaCy's dependency tree analysis to understand natural language queries.

## Overview

The translator employs **full semantic parsing** using dependency trees to:
1. Understand the grammatical structure of queries
2. Extract semantic relationships between entities
3. Infer operators based on linguistic context
4. Recognize complex patterns (CVEs, IPs, vendors)

## Architecture

### 1. Dependency Tree Analysis (`parser.py`)

The `QueryParser` class uses spaCy's dependency parsing to analyze the syntactic structure of queries:

```python
from nl_to_sql import NLToSQLTranslator

translator = NLToSQLTranslator()
tree = translator.analyze_dependency_tree("Show me assets in site 54")

# Access token-level information
for token in tree["tokens"]:
    print(f"{token['text']}: {token['pos']} ({token['dep']})")
```

#### Key Features:

- **Token Analysis**: POS tags, lemmas, dependency labels
- **Dependency Relationships**: Parent-child relationships in the parse tree
- **Noun Chunks**: Multi-word expressions
- **Named Entities**: Recognized entities from spaCy's NER

### 2. Semantic Relationship Extraction

The parser uses dependency paths to find relationships between columns and values:

#### Strategy 1: Direct Children/Descendants
```
"assets in site 54"
         ↓
    [site] → [54]  (prepositional object)
```

#### Strategy 2: Ancestor Relationships
```
"Show me assets affected by CVE-2025-10501"
              ↓
    [affected] → [CVE-2025-10501]  (agent/passive)
```

#### Strategy 3: Sibling Relationships
```
"high risk assets"
   ↓      ↓
[risk] [assets]  (attribute modification)
```

#### Strategy 4: Prepositional Attachments
```
"assets with IP 10.89.46.34"
         ↓
    [with] → [IP] → [10.89.46.34]
```

### 3. Operator Inference from Dependencies

The `_infer_operator_from_dependency()` method analyzes the dependency path to determine SQL operators:

| Linguistic Pattern | Dependency Path | SQL Operator |
|-------------------|----------------|--------------|
| "affected by CVE" | affected → CVE | `LIKE` |
| "not in site" | not → in → site | `!=` |
| "greater than 100" | greater → 100 | `>` |
| "contains value" | contains → value | `LIKE` |
| "starts with 10.89" | starts → 10.89 | `LIKE` (10.89%) |

### 4. Advanced Pattern Recognition (`entity_recognizer.py`)

#### CVE Identifiers
```python
Pattern: CVE-YYYY-NNNNN
Examples:
  - CVE-2025-10501
  - CVE-2017-12819
  - cve-2024-1234
```

#### IP Addresses
```python
Patterns:
  - Full IPv4: 192.168.1.1
  - Partial: 10.89
  - With wildcards: 10.89.*
```

#### MAC Addresses
```python
Pattern: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
Example: 00:1A:2B:3C:4D:5E
```

#### Vendor/Model Names
```python
Known vendors: Siemens, Rockwell, Schneider, ABB, GE, Honeywell, etc.
Automatically recognized as PROPN (proper nouns)
```

## Usage Examples

### Basic Dependency Analysis

```python
from nl_to_sql import NLToSQLTranslator

translator = NLToSQLTranslator()

# Get full explanation with dependency tree
explanation = translator.explain_translation(
    "Show me assets affected by CVE-2025-10501"
)
print(explanation)
```

Output:
```
Query: Show me assets affected by CVE-2025-10501

Intent: select

SQL: SELECT * FROM assets WHERE CVE LIKE '%CVE-2025-10501%'

Dependency Analysis:
------------------------------------------------------------
  Show            | POS: VERB  | DEP: ROOT       | HEAD: Show
  me              | POS: PRON  | DEP: dative     | HEAD: Show
  assets          | POS: NOUN  | DEP: dobj       | HEAD: Show
  affected        | POS: VERB  | DEP: acl        | HEAD: assets
  by              | POS: ADP   | DEP: agent      | HEAD: affected
  CVE-2025-10501  | POS: PROPN | DEP: pobj       | HEAD: by

Recognized Entities:
------------------------------------------------------------
  Column: CVE ('CVE')
  Value: CVE-2025-10501 (type: cve, text: 'CVE-2025-10501')

Extracted Conditions:
------------------------------------------------------------
  CVE LIKE %CVE-2025-10501%
```

### CVE Query Analysis

```python
query = "Find assets vulnerable to CVE-2025-10501 in site 54"
result = translator.translate_with_details(query)

print(f"SQL: {result['sql']}")
# SQL: SELECT * FROM assets WHERE CVE LIKE '%CVE-2025-10501%' AND site = 54

# Check recognized CVEs
cve_values = [v for v in result["entities"]["values"] if v.get("type") == "cve"]
print(f"CVEs: {[v['value'] for v in cve_values]}")
# CVEs: ['CVE-2025-10501']
```

### IP Address Query Analysis

```python
query = "Find all information about IP 10.89.46.34"
result = translator.translate_with_details(query)

print(f"SQL: {result['sql']}")
# SQL: SELECT * FROM assets WHERE ipv4 = '10.89.46.34'

# Check recognized IPs
ip_values = [v for v in result["entities"]["values"] if v.get("type") == "ip_address"]
print(f"IPs: {[v['value'] for v in ip_values]}")
# IPs: ['10.89.46.34']
```

### Vendor Recognition

```python
query = "Find all Siemens PLCs in our network"
result = translator.translate_with_details(query)

print(f"SQL: {result['sql']}")
# SQL: SELECT * FROM assets WHERE vendor = 'Siemens'

# Check recognized vendors
vendor_values = [v for v in result["entities"]["values"] if v.get("type") == "vendor"]
print(f"Vendors: {[v['value'] for v in vendor_values]}")
# Vendors: ['Siemens']
```

### Complex Multi-Condition Queries

```python
query = "Show me high risk assets that need immediate patching"
result = translator.translate_with_details(query)

print(f"SQL: {result['sql']}")
# SQL: SELECT * FROM assets WHERE risk = 'high' AND patch_count > 0

# Analyze dependency tree
tree = translator.analyze_dependency_tree(query)
for token in tree["tokens"]:
    print(f"{token['text']:15} {token['dep']:10} -> {token['head']}")
```

## Dependency Path Algorithm

The `_get_dependency_path()` method finds the shortest path between two tokens through their lowest common ancestor (LCA):

```python
def _get_dependency_path(token1, token2):
    # 1. Find all ancestors of both tokens
    ancestors1 = set([token1] + list(token1.ancestors))
    ancestors2 = set([token2] + list(token2.ancestors))
    
    # 2. Find lowest common ancestor
    common = ancestors1 & ancestors2
    lca = min(common, key=lambda t: t.i)
    
    # 3. Build path: token1 → lca → token2
    path = build_path_to_lca(token1, lca)
    path.extend(build_path_from_lca(lca, token2))
    
    return path
```

This allows the parser to understand relationships like:
- "assets **affected by** CVE" → passive relationship
- "assets **in** site 54" → prepositional location
- "assets **with** high risk" → attribute possession

## Debugging Tools

### 1. Dependency Tree Visualization

```python
translator = NLToSQLTranslator()
tree = translator.analyze_dependency_tree("your query here")

# Inspect tokens
print(json.dumps(tree["tokens"], indent=2))

# Inspect dependencies
print(json.dumps(tree["dependencies"], indent=2))

# Inspect noun chunks
print(json.dumps(tree["noun_chunks"], indent=2))
```

### 2. Full Translation Explanation

```python
explanation = translator.explain_translation("your query here")
print(explanation)
```

This provides:
- Original query
- Detected intent
- Generated SQL
- Complete dependency analysis
- Recognized entities
- Extracted conditions

### 3. Demo Script

Run the comprehensive demo:

```bash
python demo_dependency_analysis.py
```

This demonstrates:
- Basic dependency tree analysis
- CVE pattern recognition
- IP address recognition
- Semantic relationship extraction
- Complex query parsing
- Dependency path analysis

## Implementation Details

### Parser Methods

| Method | Purpose |
|--------|---------|
| `_find_related_values_by_dependency()` | Find values related to columns via dependency tree |
| `_infer_operator_from_dependency()` | Infer SQL operator from dependency path |
| `_get_dependency_path()` | Get shortest path between two tokens |
| `get_dependency_tree_info()` | Extract complete tree information for debugging |

### Entity Recognizer Methods

| Method | Purpose |
|--------|---------|
| `_is_cve_identifier()` | Detect CVE patterns (CVE-YYYY-NNNNN) |
| `_is_ip_address()` | Detect full/partial IP addresses |
| `_is_mac_address()` | Detect MAC address patterns |
| `_is_vendor_or_model()` | Recognize known vendors/models |

### Translator Methods

| Method | Purpose |
|--------|---------|
| `analyze_dependency_tree()` | Get detailed linguistic analysis |
| `explain_translation()` | Human-readable translation explanation |
| `translate_with_details()` | Get full translation with entities |

## Benefits of Dependency-Based Parsing

1. **Context-Aware**: Understands relationships beyond word proximity
2. **Robust**: Handles varied sentence structures
3. **Semantic**: Captures meaning, not just patterns
4. **Extensible**: Easy to add new relationship types
5. **Debuggable**: Full visibility into parsing decisions

## Supported Query Patterns

### Security Queries
- "Show me assets affected by CVE-2025-10501"
- "Find assets vulnerable to CVE in site 54"
- "Has CVE-2017-12819 been remediated?"

### Asset Discovery
- "Find all information about IP 10.89.46.34"
- "Show me assets last seen in the last 24 hours"
- "What assets belong to site 5?"

### Vendor/Model Queries
- "Find all Siemens PLCs"
- "What Rockwell devices do we have?"
- "Show me Schneider equipment"

### Risk Assessment
- "Show me high risk assets"
- "Find critical vulnerabilities"
- "List assets that need patching"

### Network Queries
- "Find assets with IP starting with 10.89"
- "Show me assets in the industrial control network"
- "What devices are in subnet 192.168.1.0/24?"

## Performance Considerations

- **spaCy Model**: Uses `en_core_web_sm` (small, fast)
- **Dependency Parsing**: O(n) where n = number of tokens
- **Path Finding**: O(d) where d = tree depth (typically < 10)
- **Pattern Matching**: Compiled regex patterns for efficiency

## Future Enhancements

Potential improvements to semantic parsing:

1. **Coreference Resolution**: Handle pronouns ("it", "they")
2. **Temporal Expressions**: Parse dates/times ("last week", "yesterday")
3. **Negation Scope**: Better handling of negation boundaries
4. **Coordination**: Complex AND/OR structures
5. **Semantic Role Labeling**: Identify agents, patients, instruments
6. **Entity Linking**: Connect mentions to knowledge base

## References

- [spaCy Dependency Parsing](https://spacy.io/usage/linguistic-features#dependency-parse)
- [Universal Dependencies](https://universaldependencies.org/)
- [Dependency Grammar](https://en.wikipedia.org/wiki/Dependency_grammar)

