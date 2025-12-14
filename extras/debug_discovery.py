
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "core"))

from core.language_loader import LanguageLoader
from core.graph_extractor import GraphExtractor

print("DEBUG: Checking Language Loader...")
loader = LanguageLoader()
parsers, langs, extensions = loader.load_all()
print(f"Bindings: {list(parsers.keys())}")

typescript_exts = extensions.get("typescript", [])
print(f"TypeScript Extensions: {typescript_exts}")

print("\nDEBUG: Checking GraphExtractor...")
extractor = GraphExtractor()
target = "../../PROJECT_atman"
print(f"Target: {target}")

# Check files manual
path = Path(target)
found = list(path.rglob("*.ts"))
print(f"Manual rglob *.ts: {len(found)} files")
found_tsx = list(path.rglob("*.tsx"))
from core.complete_extractor import CompleteExtractor

print("\nDEBUG: Checking CompleteExtractor...")
comp = CompleteExtractor()
try:
    codebase = comp.extract(target, language="typescript")
    print(f"Codebase Stats (TS): {codebase.get_stats()}")
    print(f"Files: {list(codebase.files.keys())[:3]}")
except Exception as e:
    print(f"ERROR: {e}")

print("\nDEBUG: Running Extract(typescript)...")

try:
    graph = extractor.extract(target, language="typescript")
    print(f"Graph Nodes: {len(graph.nodes)}")
    for nid, node in list(graph.nodes.items())[:5]:
        print(f" - {node.node_type}: {node.name} ({node.file})")
except Exception as e:
    print(f"ERROR: {e}")

print("\nDEBUG: Running Extract(tsx)...")
try:
    graph = extractor.extract(target, language="tsx")
    print(f"Graph Nodes: {len(graph.nodes)}")
except Exception as e:
    print(f"ERROR: {e}")
