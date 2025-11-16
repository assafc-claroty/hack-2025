#!/usr/bin/env python3
"""
Verify that the NL to SQL Translator is properly set up.
"""

import sys


def check_spacy():
    """Check if spaCy is installed."""
    try:
        import spacy
        print("✓ spaCy is installed (version: {})".format(spacy.__version__))
        return True
    except ImportError:
        print("✗ spaCy is not installed")
        print("  Install with: pip install spacy")
        return False


def check_spacy_model():
    """Check if the spaCy model is downloaded."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✓ spaCy model 'en_core_web_sm' is available")
        return True
    except OSError:
        print("✗ spaCy model 'en_core_web_sm' is not installed")
        print("  Install with: python -m spacy download en_core_web_sm")
        return False
    except ImportError:
        return False


def check_package():
    """Check if the nl_to_sql package can be imported."""
    try:
        from nl_to_sql import NLToSQLTranslator
        print("✓ nl_to_sql package can be imported")
        return True
    except ImportError as e:
        print(f"✗ Cannot import nl_to_sql package: {e}")
        return False


def test_basic_functionality():
    """Test basic translator functionality."""
    try:
        from nl_to_sql import NLToSQLTranslator
        
        translator = NLToSQLTranslator()
        result = translator.translate("Show me all assets")
        
        if result["table"] == "assets" and result["select"] == ["*"]:
            print("✓ Basic translation works correctly")
            return True
        else:
            print("✗ Translation produced unexpected results")
            return False
    except Exception as e:
        print(f"✗ Error during basic test: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 80)
    print("NL to SQL Translator - Setup Verification")
    print("=" * 80)
    print()
    
    checks = [
        ("spaCy Installation", check_spacy),
        ("spaCy Model", check_spacy_model),
        ("Package Import", check_package),
        ("Basic Functionality", test_basic_functionality),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        results.append(check_func())
    
    print("\n" + "=" * 80)
    if all(results):
        print("✓ All checks passed! The translator is ready to use.")
        print("\nTry running: python example.py")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("\nQuick fix:")
        print("  1. pip install -r requirements.txt")
        print("  2. python -m spacy download en_core_web_sm")
        return 1


if __name__ == "__main__":
    sys.exit(main())

