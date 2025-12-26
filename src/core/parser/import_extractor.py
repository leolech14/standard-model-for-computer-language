"""
Import Extractor Base and Language-Specific Implementations

Extracts import statements from source code across multiple languages.
Part of the TreeSitterUniversalEngine decomposition (GOD_CLASS_DECOMPOSITION).
"""
import re
from abc import ABC, abstractmethod
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Import:
    """Represents a single import statement."""
    module: str
    alias: str = ""
    items: List[str] = None
    is_relative: bool = False
    
    def __post_init__(self):
        if self.items is None:
            self.items = []


class ImportExtractor(ABC):
    """Abstract base class for language-specific import extraction."""
    
    @abstractmethod
    def extract(self, content: str) -> List[Import]:
        """Extract imports from source content."""
        pass


class PythonImportExtractor(ImportExtractor):
    """Extract imports from Python source code."""
    
    def extract(self, content: str) -> List[Import]:
        imports = []
        
        # Standard imports: import x, import x as y
        for match in re.finditer(r'^import\s+(\S+)(?:\s+as\s+(\S+))?', content, re.MULTILINE):
            imports.append(Import(
                module=match.group(1),
                alias=match.group(2) or ""
            ))
        
        # From imports: from x import y, z
        for match in re.finditer(r'^from\s+(\S+)\s+import\s+(.+?)(?:\s*$|\s*#)', content, re.MULTILINE):
            module = match.group(1)
            is_relative = module.startswith('.')
            items_str = match.group(2)
            
            # Parse items (handle multiline with backslash)
            if '(' in items_str:
                # Handle parenthesized imports - find closing paren
                start = content.find(items_str)
                end = content.find(')', start)
                if end > start:
                    items_str = content[start:end]
            
            items = [item.strip().split(' as ')[0] for item in items_str.split(',')]
            items = [item.strip() for item in items if item.strip() and item.strip() != '(']
            
            imports.append(Import(
                module=module,
                items=items,
                is_relative=is_relative
            ))
        
        return imports


class JavaScriptImportExtractor(ImportExtractor):
    """Extract imports from JavaScript/TypeScript source code."""
    
    def extract(self, content: str) -> List[Import]:
        imports = []
        
        # ES6 imports: import x from 'y'
        for match in re.finditer(
            r'import\s+(?:(\w+)(?:\s*,\s*)?)?(?:\{([^}]+)\})?\s*from\s*[\'"]([^\'"]+)[\'"]',
            content
        ):
            default_import = match.group(1)
            named_imports = match.group(2)
            module = match.group(3)
            
            items = []
            if named_imports:
                items = [item.strip().split(' as ')[0].strip() 
                        for item in named_imports.split(',')]
            
            imports.append(Import(
                module=module,
                alias=default_import or "",
                items=items,
                is_relative=module.startswith('.')
            ))
        
        # CommonJS: require('x')
        for match in re.finditer(r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)', content):
            imports.append(Import(module=match.group(1)))
        
        # Dynamic imports: import('x')
        for match in re.finditer(r'import\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)', content):
            imports.append(Import(module=match.group(1)))
        
        return imports


class JavaImportExtractor(ImportExtractor):
    """Extract imports from Java/Kotlin source code."""
    
    def extract(self, content: str) -> List[Import]:
        imports = []
        
        for match in re.finditer(r'^import\s+(static\s+)?([a-zA-Z0-9_.]+)(?:\.\*)?;', content, re.MULTILINE):
            is_static = bool(match.group(1))
            module = match.group(2)
            imports.append(Import(
                module=module,
                alias="static" if is_static else ""
            ))
        
        return imports


class GoImportExtractor(ImportExtractor):
    """Extract imports from Go source code."""
    
    def extract(self, content: str) -> List[Import]:
        imports = []
        
        # Single import: import "fmt"
        for match in re.finditer(r'^import\s+"([^"]+)"', content, re.MULTILINE):
            imports.append(Import(module=match.group(1)))
        
        # Grouped imports: import ( ... )
        for match in re.finditer(r'import\s*\((.*?)\)', content, re.DOTALL):
            block = match.group(1)
            for line in block.split('\n'):
                line = line.strip()
                if line and not line.startswith('//'):
                    # Handle alias: alias "path"
                    alias_match = re.match(r'(\w+)\s+"([^"]+)"', line)
                    if alias_match:
                        imports.append(Import(
                            module=alias_match.group(2),
                            alias=alias_match.group(1)
                        ))
                    else:
                        path_match = re.match(r'"([^"]+)"', line)
                        if path_match:
                            imports.append(Import(module=path_match.group(1)))
        
        return imports


class RustImportExtractor(ImportExtractor):
    """Extract imports from Rust source code."""
    
    def extract(self, content: str) -> List[Import]:
        imports = []
        
        for match in re.finditer(r'use\s+([a-zA-Z0-9_:{}]+);', content):
            imports.append(Import(module=match.group(1)))
        
        return imports


class CSharpImportExtractor(ImportExtractor):
    """Extract imports from C# source code."""
    
    def extract(self, content: str) -> List[Import]:
        imports = []
        
        for match in re.finditer(r'^using\s+(?:static\s+)?([a-zA-Z0-9_.]+)\s*;', content, re.MULTILINE):
            imports.append(Import(module=match.group(1)))
        
        return imports


class RubyImportExtractor(ImportExtractor):
    """Extract imports from Ruby source code."""
    
    def extract(self, content: str) -> List[Import]:
        imports = []
        
        for match in re.finditer(r"require\s*['\"]([^'\"]+)['\"]", content):
            imports.append(Import(module=match.group(1)))
        
        for match in re.finditer(r"require_relative\s*['\"]([^'\"]+)['\"]", content):
            imports.append(Import(module=match.group(1), is_relative=True))
        
        return imports


class PHPImportExtractor(ImportExtractor):
    """Extract imports from PHP source code."""
    
    def extract(self, content: str) -> List[Import]:
        imports = []
        
        for match in re.finditer(r'use\s+([a-zA-Z0-9_\\]+)(?:\s+as\s+(\w+))?;', content):
            imports.append(Import(
                module=match.group(1),
                alias=match.group(2) or ""
            ))
        
        for match in re.finditer(r"(?:include|require)(?:_once)?\s*['\"]([^'\"]+)['\"]", content):
            imports.append(Import(module=match.group(1)))
        
        return imports


# Factory for language-specific extractors
IMPORT_EXTRACTORS = {
    'python': PythonImportExtractor,
    'javascript': JavaScriptImportExtractor,
    'typescript': JavaScriptImportExtractor,
    'java': JavaImportExtractor,
    'kotlin': JavaImportExtractor,
    'go': GoImportExtractor,
    'rust': RustImportExtractor,
    'csharp': CSharpImportExtractor,
    'ruby': RubyImportExtractor,
    'php': PHPImportExtractor,
}


def get_import_extractor(language: str) -> ImportExtractor:
    """Get the appropriate import extractor for a language."""
    extractor_class = IMPORT_EXTRACTORS.get(language.lower())
    if extractor_class:
        return extractor_class()
    return PythonImportExtractor()  # Default fallback


def extract_imports(content: str, language: str) -> List[Import]:
    """Convenience function to extract imports from content."""
    extractor = get_import_extractor(language)
    return extractor.extract(content)


if __name__ == "__main__":
    # Test Python imports
    python_code = '''
import os
import json as js
from typing import Dict, List
from .local_module import something
'''
    
    extractor = PythonImportExtractor()
    imports = extractor.extract(python_code)
    print("Python imports:")
    for imp in imports:
        print(f"  {imp}")
    
    # Test JavaScript imports
    js_code = '''
import React from 'react';
import { useState, useEffect } from 'react';
const fs = require('fs');
'''
    
    extractor = JavaScriptImportExtractor()
    imports = extractor.extract(js_code)
    print("\nJavaScript imports:")
    for imp in imports:
        print(f"  {imp}")
