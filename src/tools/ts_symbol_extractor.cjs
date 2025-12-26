#!/usr/bin/env node
/* eslint-disable no-console */

const fs = require("node:fs");
const fsp = require("node:fs/promises");
const path = require("node:path");

function toPosix(p) {
  return p.split(path.sep).join("/");
}

function isIgnoredDir(name) {
  return (
    name === ".git" ||
    name === "node_modules" ||
    name === "dist" ||
    name === "build" ||
    name === "coverage" ||
    name === ".next" ||
    name === ".turbo" ||
    name === ".cache" ||
    name === "__pycache__" ||
    name === ".venv" ||
    name === "venv"
  );
}

async function listFiles(rootDir) {
  const out = [];
  const queue = [rootDir];

  while (queue.length) {
    const dir = queue.pop();
    let entries;
    try {
      entries = await fsp.readdir(dir, { withFileTypes: true });
    } catch {
      continue;
    }

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (isIgnoredDir(entry.name)) continue;
        queue.push(fullPath);
        continue;
      }
      if (!entry.isFile()) continue;

      const lower = entry.name.toLowerCase();
      if (
        lower.endsWith(".ts") ||
        lower.endsWith(".tsx") ||
        lower.endsWith(".js") ||
        lower.endsWith(".jsx") ||
        lower.endsWith(".mjs") ||
        lower.endsWith(".cjs")
      ) {
        out.push(fullPath);
      }
    }
  }

  return out;
}

function findTypeScriptModule(repoRootAbs) {
  const candidates = [
    path.join(repoRootAbs, "node_modules", "typescript"),
    path.join(repoRootAbs, "ro-finance", "node_modules", "typescript"),
    path.join(repoRootAbs, "ui", "node_modules", "typescript"),
    path.join(repoRootAbs, "web", "node_modules", "typescript"),
  ];

  for (const p of candidates) {
    try {
      if (fs.existsSync(p)) return p;
    } catch {
      // ignore
    }
  }

  // Shallow search for nested workspaces (max depth 3) that have node_modules/typescript.
  const ignore = new Set(["node_modules", ".git", "dist", "build", "coverage", ".next", ".turbo", ".cache"]);
  const queue = [{ dir: repoRootAbs, depth: 0 }];

  while (queue.length) {
    const { dir, depth } = queue.pop();
    if (depth > 3) continue;

    const tsPath = path.join(dir, "node_modules", "typescript");
    try {
      if (fs.existsSync(tsPath)) return tsPath;
    } catch {
      // ignore
    }

    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      continue;
    }

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      if (ignore.has(entry.name)) continue;
      queue.push({ dir: path.join(dir, entry.name), depth: depth + 1 });
    }
  }

  return null;
}

function extractTouchpoints(content) {
  const touchpoints = [];
  const patterns = {
    identity: [/\b(id|uuid|identifier|key|_id)\b/gi],
    state: [/\b(property|attribute|field|member)\b/gi],
    data_access: [/\b(save|find|delete|query|persist|retrieve)\b/gi],
    immutability: [/\b(frozen|immutable|readonly|final|const)\b/gi],
    validation: [/\b(validate|check|verify|ensure|require)\b/gi],
    coordination: [/\b(coordinate|manage|orchestrate|mediate)\b/gi],
  };

  for (const [type, regs] of Object.entries(patterns)) {
    for (const re of regs) {
      let m;
      while ((m = re.exec(content)) != null) {
        const idx = m.index ?? 0;
        const line = content.slice(0, idx).split("\n").length;
        touchpoints.push({ type, evidence: m[0], line, confidence: 75.0 });
      }
    }
  }

  return touchpoints;
}

function scriptKindFor(ts, filePath) {
  const lower = filePath.toLowerCase();
  if (lower.endsWith(".tsx")) return ts.ScriptKind.TSX;
  if (lower.endsWith(".ts")) return ts.ScriptKind.TS;
  if (lower.endsWith(".jsx")) return ts.ScriptKind.JSX;
  if (lower.endsWith(".js") || lower.endsWith(".mjs") || lower.endsWith(".cjs")) return ts.ScriptKind.JS;
  return ts.ScriptKind.Unknown;
}

function languageFor(filePath) {
  const lower = filePath.toLowerCase();
  if (lower.endsWith(".ts") || lower.endsWith(".tsx")) return "typescript";
  return "javascript";
}

function nodeLine(ts, sourceFile, node) {
  const start = node.getStart(sourceFile, false);
  const end = node.getEnd();
  const startLc = sourceFile.getLineAndCharacterOfPosition(start);
  const endLc = sourceFile.getLineAndCharacterOfPosition(end);
  return { startLine: startLc.line + 1, endLine: endLc.line + 1 };
}

function nodeEvidence(sourceFile, node) {
  const start = node.getStart(sourceFile, false);
  const { line } = sourceFile.getLineAndCharacterOfPosition(start);
  const lineText = sourceFile.getFullText().split("\n")[line] || "";
  return lineText.trim().slice(0, 200);
}

function nameText(ts, nodeName) {
  if (!nodeName) return "";
  if (ts.isIdentifier(nodeName)) return nodeName.text;
  if (ts.isStringLiteral(nodeName) || ts.isNumericLiteral(nodeName)) return String(nodeName.text);
  return "";
}

function pushSymbol({ symbols, ts, sourceFile, node, name, symbolKind, parentName }) {
  if (!name) return;
  const { startLine, endLine } = nodeLine(ts, sourceFile, node);
  symbols.push({
    name,
    symbol_kind: symbolKind,
    line: startLine,
    end_line: endLine,
    parent: parentName || "",
    evidence: nodeEvidence(sourceFile, node),
  });
}

function pushImport({ imports, ts, sourceFile, node, kind, target }) {
  if (!target) return;
  const { startLine } = nodeLine(ts, sourceFile, node);
  imports.push({
    kind,
    target,
    line: startLine,
    is_relative: target.startsWith(".") || target.startsWith("/"),
    level: 0,
  });
}

function extractFromSourceFile(ts, sourceFile) {
  const symbols = [];
  const imports = [];

  const classStack = [];
  const funcStack = [];

  function currentParent() {
    if (funcStack.length) return funcStack[funcStack.length - 1];
    if (classStack.length) return classStack[classStack.length - 1];
    return "";
  }

  function visit(node) {
    // Imports (static)
    if (ts.isImportDeclaration(node)) {
      const target = node.moduleSpecifier && ts.isStringLiteral(node.moduleSpecifier) ? node.moduleSpecifier.text : "";
      pushImport({ imports, ts, sourceFile, node, kind: "import", target });
    } else if (ts.isExportDeclaration(node) && node.moduleSpecifier && ts.isStringLiteral(node.moduleSpecifier)) {
      pushImport({ imports, ts, sourceFile, node, kind: "export_from", target: node.moduleSpecifier.text });
    } else if (ts.isImportEqualsDeclaration(node)) {
      // import x = require('y')
      const mr = node.moduleReference;
      if (mr && ts.isCallExpression(mr) && mr.expression && mr.expression.getText(sourceFile) === "require") {
        const arg = mr.arguments && mr.arguments[0];
        if (arg && ts.isStringLiteral(arg)) {
          pushImport({ imports, ts, sourceFile, node, kind: "import_equals", target: arg.text });
        }
      }
    }

    // Dynamic require/import()
    if (ts.isCallExpression(node)) {
      // require('x')
      if (node.expression && ts.isIdentifier(node.expression) && node.expression.text === "require") {
        const arg = node.arguments && node.arguments[0];
        if (arg && ts.isStringLiteral(arg)) {
          pushImport({ imports, ts, sourceFile, node, kind: "require", target: arg.text });
        }
      }
      // import('x')
      if (node.expression && node.expression.kind === ts.SyntaxKind.ImportKeyword) {
        const arg = node.arguments && node.arguments[0];
        if (arg && ts.isStringLiteral(arg)) {
          pushImport({ imports, ts, sourceFile, node, kind: "dynamic_import", target: arg.text });
        }
      }
    }

    // Symbols (declarations)
    if (ts.isClassDeclaration(node)) {
      const cname = node.name ? node.name.text : "";
      pushSymbol({ symbols, ts, sourceFile, node, name: cname, symbolKind: "class", parentName: currentParent() });

      if (cname) classStack.push(cname);
      ts.forEachChild(node, visit);
      if (cname) classStack.pop();
      return;
    }

    if (ts.isFunctionDeclaration(node)) {
      const fname = node.name ? node.name.text : "";
      pushSymbol({ symbols, ts, sourceFile, node, name: fname, symbolKind: "function", parentName: currentParent() });

      if (fname) funcStack.push(fname);
      ts.forEachChild(node, visit);
      if (fname) funcStack.pop();
      return;
    }

    if (ts.isInterfaceDeclaration(node)) {
      pushSymbol({
        symbols,
        ts,
        sourceFile,
        node,
        name: node.name ? node.name.text : "",
        symbolKind: "interface",
        parentName: currentParent(),
      });
    } else if (ts.isTypeAliasDeclaration(node)) {
      pushSymbol({
        symbols,
        ts,
        sourceFile,
        node,
        name: node.name ? node.name.text : "",
        symbolKind: "type",
        parentName: currentParent(),
      });
    } else if (ts.isEnumDeclaration(node)) {
      pushSymbol({
        symbols,
        ts,
        sourceFile,
        node,
        name: node.name ? node.name.text : "",
        symbolKind: "enum",
        parentName: currentParent(),
      });
    }

    if (ts.isVariableStatement(node)) {
      for (const decl of node.declarationList.declarations || []) {
        if (!decl.name || !ts.isIdentifier(decl.name)) continue;
        const vname = decl.name.text;
        const init = decl.initializer;
        const isFn = init && (ts.isArrowFunction(init) || ts.isFunctionExpression(init));
        pushSymbol({
          symbols,
          ts,
          sourceFile,
          node: decl,
          name: vname,
          symbolKind: isFn ? "function" : "variable",
          parentName: currentParent(),
        });
      }
    }

    if (ts.isMethodDeclaration(node) || ts.isConstructorDeclaration(node) || ts.isGetAccessorDeclaration(node) || ts.isSetAccessorDeclaration(node)) {
      const parent = classStack.length ? classStack[classStack.length - 1] : currentParent();
      let mname = "constructor";
      if (!ts.isConstructorDeclaration(node)) {
        mname = nameText(ts, node.name);
      }
      const full = parent ? `${parent}.${mname}` : mname;
      pushSymbol({ symbols, ts, sourceFile, node, name: full, symbolKind: "method", parentName: parent });
    }

    ts.forEachChild(node, visit);
  }

  visit(sourceFile);
  return { symbols, imports };
}

async function main() {
  const repoRootArg = process.argv[2];
  if (!repoRootArg) {
    console.error("Usage: ts_symbol_extractor.cjs <repoRoot>");
    process.exit(2);
  }

  const repoRootAbs = path.resolve(repoRootArg);
  const tsModulePath = findTypeScriptModule(repoRootAbs);
  let ts;
  try {
    ts = tsModulePath ? require(tsModulePath) : require("typescript");
  } catch (err) {
    console.error(JSON.stringify({ ok: false, error: "typescript_not_found" }));
    process.exit(3);
  }

  const files = await listFiles(repoRootAbs);
  const results = [];

  for (const absPath of files) {
    let content;
    try {
      content = await fsp.readFile(absPath, "utf8");
    } catch {
      continue;
    }

    const scriptKind = scriptKindFor(ts, absPath);
    const sourceFile = ts.createSourceFile(absPath, content, ts.ScriptTarget.Latest, true, scriptKind);
    const { symbols, imports } = extractFromSourceFile(ts, sourceFile);

    const relToCwd = toPosix(path.relative(process.cwd(), absPath));
    results.push({
      file_path: relToCwd,
      language: languageFor(absPath),
      particles: symbols,
      raw_imports: imports,
      touchpoints: extractTouchpoints(content),
      lines_analyzed: content.split("\n").length,
      chars_analyzed: content.length,
    });
  }

  process.stdout.write(JSON.stringify({ ok: true, files: results }));
}

main().catch((err) => {
  console.error(JSON.stringify({ ok: false, error: String(err && err.message ? err.message : err) }));
  process.exit(1);
});

