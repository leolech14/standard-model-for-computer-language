# Error Reference

[Home](../README.md) > [Docs](./README.md) > **Errors**

---

## FOR AI: When to Read This
- Read when: user reports error, build fails, unexpected output
- Search: grep for error message text in this file
- Pattern: Each row has error, cause, solution, source file

---

## Common Errors

| Error Pattern | Cause | Solution | File |
|---------------|-------|----------|------|
| `path argument is required` | No repository path provided | Run: `./collider full /path/to/repo` | `cli.py` |
| `No Python files found` | Empty directory or wrong path | Verify: `ls -la /path && find /path -name '*.py'` | `cli.py` |
| `Graph file not found` | Path doesn't exist or typo | Check: `ls -la <path>` | `cli.py` |
| `shortest-path format error` | Incorrect syntax | Use: `./collider graph <path> --shortest-path 'func_a:func_b'` | `cli.py` |
| `Full analysis failed` | Pipeline execution error | Run: `./collider full /path 2>&1` | `cli.py` |
| `Graph has no nodes` | Parser failed | Check encoding: `file -i /path/*.py` | `src/core/full_analysis.py` |
| `Missing required field` | Schema violation | Check: `grep 'required' schema/atom.schema.json` | `src/core/graph_builder.py` |
| `Circular dependency detected` | Import cycle | Run: `./collider graph graph.json --bottlenecks` | `src/core/topology_reasoning.py` |
| `Dead code percentage 100%` | No entry points found | Check for `__main__` blocks, re-run | `src/core/dead_code.py` |
| `RPBL calculation failed` | Missing metrics | Verify full_analysis completed all stages | `src/core/rpbl_calculator.py` |
| `Visualization generation failed` | Missing template/assets | Check: `ls -la src/core/viz/assets/` | `src/core/viz/` |
| `AI insights unavailable` | gcloud not authenticated | Run: `gcloud auth application-default login` | `src/core/ai_insights.py` |
| `JSONDecodeError` | Malformed JSON output | Validate: `python -m json.tool graph.json` | `src/core/full_analysis.py` |
| `FileNotFoundError schema` | Schema file missing | Verify: `find . -name 'atom.schema.json'` | `src/core/full_analysis.py` |
| `Ollama connection refused` | Ollama not running | Start: `ollama serve` (separate terminal) | `cli.py` |
| `Contract validation failed` | Output schema mismatch | Run: `./collider doctor /path` | `src/core/normalize_output.py` |

---

## Debug Commands

| Situation | Command |
|-----------|---------|
| Check version | `./collider --help` |
| Verbose output | `./collider full /path 2>&1` |
| Skip AI | `./collider full /path` (no --ai-insights) |
| Self-check | `./collider full src/core --output /tmp/debug` |
| Validate schema | `python -m jsonschema schema/atom.schema.json` |
| Inspect graph | `python -m json.tool .collider/graph.json` |
| Check syntax | `python -m py_compile /path/file.py` |
| Test graph | `./collider graph .collider/graph.json --bottlenecks` |

---

## Common Scenarios

### No Python files found
1. Verify directory: `ls -la /path/to/repo`
2. Check for Python: `find /path/to/repo -name '*.py' -type f`
3. If empty, may need other language support

### Graph has no nodes
1. Check parser: `./collider full /path --verbose-timing`
2. Check encoding: `file -i src/**/*.py`
3. Test repo: `./collider full tests/fixtures/toy_entry_click`

### Dead code 100%
1. No reachable entry points
2. Check for `__main__` or `if __name__ == '__main__':`
3. Inspect: `grep -i 'entry|reachable' output.md`

### AI insights failed (analysis works)
1. AI is optional enrichment only
2. Check gcloud: `which gcloud`
3. Authenticate: `gcloud auth application-default login`

---

## File Reference

| File | Can Raise |
|------|-----------|
| `cli.py` | Argument parsing, path validation |
| `src/core/full_analysis.py` | FileNotFoundError, JSONDecodeError |
| `src/core/graph_builder.py` | Missing fields, schema violations |
| `src/core/topology_reasoning.py` | Circular dependency, topology failures |
| `src/core/dead_code.py` | 100% dead code, entry point issues |
| `src/core/rpbl_calculator.py` | Metric calculation failures |
| `src/core/viz/` | Template/asset missing errors |
| `src/core/ai_insights.py` | gcloud auth, API failures |
