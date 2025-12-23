"""
Parser Package

Decomposed components from TreeSitterUniversalEngine.
Each module handles a specific responsibility:

- import_extractor.py: Language-specific import extraction
- symbol_classifier.py: Symbol classification by name, inheritance, decorators
- python_parser.py: Python AST parsing
"""

from .import_extractor import (
    ImportExtractor,
    PythonImportExtractor,
    JavaScriptImportExtractor,
    JavaImportExtractor,
    GoImportExtractor,
    RustImportExtractor,
    CSharpImportExtractor,
    RubyImportExtractor,
    PHPImportExtractor,
    get_import_extractor,
    extract_imports,
    Import,
)

from .symbol_classifier import (
    SymbolClassifier,
    SymbolKind,
    ClassifiedSymbol,
    classify_symbol,
)

from .python_parser import (
    PythonASTParser,
    PythonSymbol,
    parse_python,
)

__all__ = [
    # Import extraction
    'ImportExtractor',
    'PythonImportExtractor',
    'JavaScriptImportExtractor',
    'JavaImportExtractor',
    'GoImportExtractor',
    'RustImportExtractor',
    'CSharpImportExtractor',
    'RubyImportExtractor',
    'PHPImportExtractor',
    'get_import_extractor',
    'extract_imports',
    'Import',
    
    # Symbol classification
    'SymbolClassifier',
    'SymbolKind',
    'ClassifiedSymbol',
    'classify_symbol',
    
    # Python parsing
    'PythonASTParser',
    'PythonSymbol',
    'parse_python',
]
