#!/usr/bin/env python3
"""
🌍 LANGUAGE LOADER — Dynamic Tree-sitter Binding Discovery
Automatically finds and loads ALL installed tree-sitter languages.
"""

import importlib
import pkgutil
from typing import Dict, Any, Tuple
from tree_sitter import Language, Parser

class LanguageLoader:
    """
    Dynamically discovers and loads tree-sitter language bindings 
    present in the current environment.
    """
    
    # Map of package name -> (language name in repo, extensions)
    # This guides the auto-discovery to know what to look for.
    KNOWN_BINDINGS = {
        "tree_sitter_python": ("python", [".py"]),
        "tree_sitter_typescript": ("typescript", [".ts", ".tsx"]), # Special handling for tsx
        "tree_sitter_javascript": ("javascript", [".js", ".jsx"]),
        "tree_sitter_go": ("go", [".go"]),
        "tree_sitter_java": ("java", [".java"]),
        "tree_sitter_rust": ("rust", [".rs"]),
        "tree_sitter_cpp": ("cpp", [".cpp", ".h", ".hpp"]),
        "tree_sitter_c_sharp": ("c_sharp", [".cs"]),
        "tree_sitter_ruby": ("ruby", [".rb"]),
        "tree_sitter_php": ("php", [".php"]),
    }

    @staticmethod
    def load_all() -> Tuple[Dict[str, Parser], Dict[str, Language], Dict[str, list]]:
        """
        Load all available parsers.
        Returns: (parsers, languages, extensions_map)
        """
        parsers = {}
        languages = {}
        extensions = {} # language_key -> [exts]
        
        for pkg_name, (lang_name, exts) in LanguageLoader.KNOWN_BINDINGS.items():
            try:
                module = importlib.import_module(pkg_name)
                
                # Get the language object
                # Most bindings expose a method like language()
                # TypeScript is special: language_typescript() and language_tsx()
                
                if pkg_name == "tree_sitter_typescript":
                    # Load TypeScript
                    try:
                        ts_lang = Language(module.language_typescript())
                        parsers["typescript"] = Parser(ts_lang)
                        languages["typescript"] = ts_lang
                        extensions["typescript"] = [".ts"]
                    except AttributeError:
                        pass
                        
                    # Load TSX
                    try:
                        tsx_lang = Language(module.language_tsx())
                        parsers["tsx"] = Parser(tsx_lang)
                        languages["tsx"] = tsx_lang
                        extensions["tsx"] = [".tsx"]
                    except AttributeError:
                        pass
                else:
                    # Standard bindings
                    if hasattr(module, "language"):
                        lang_obj = Language(module.language())
                        parsers[lang_name] = Parser(lang_obj)
                        languages[lang_name] = lang_obj
                        extensions[lang_name] = exts
                        
            except ImportError:
                continue
            except Exception as e:
                print(f"Warning: Failed to load {pkg_name}: {e}")
                
        return parsers, languages, extensions

    @staticmethod
    def get_supported_languages() -> list:
        """Return list of currently supported (installed) languages."""
        _, _, exts = LanguageLoader.load_all()
        return list(exts.keys())
