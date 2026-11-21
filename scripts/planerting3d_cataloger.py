#!/usr/bin/env python3
"""
Planerting3d Core Cataloger (v1.0)
==================================
Deterministic AST cataloging and 3D topology projection for OpenGraphify.
Based on structural-isomorphism principles:
- Python (.py) through the native AST and lightweight TypeScript/React extraction (.ts, .tsx, .js, .jsx).
- Resolution and emission of typed directed edges (connections).
- Projection of 3D spatial coordinates (x, y, z) from structural properties.
- Model-token cost: ZERO.
"""

import os
import sys
import json
import ast
import re
import math
import argparse
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

LAYER_DEFINITIONS = [
    {"id": "L1_PERSISTENCE", "name": "Persistence & Models", "color": "#ff7b72", "x_base": -80.0},
    {"id": "L2_API_LOGIC", "name": "API, Serializers & Views", "color": "#d2a8ff", "x_base": -40.0},
    {"id": "L3_REALTIME_CRDT", "name": "Realtime & CRDT", "color": "#58a6ff", "x_base": 0.0},
    {"id": "L4_CLIENT_STATE", "name": "Client State & Hooks", "color": "#3fb950", "x_base": 40.0},
    {"id": "L5_PRESENTATION", "name": "Presentation & React UI", "color": "#f0883e", "x_base": 80.0},
    {"id": "L6_TESTS", "name": "Tests", "color": "#7ee787", "x_base": 0.0, "z_base": 50.0}
]

class PythonASTScanner(ast.NodeVisitor):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.classes: List[str] = []
        self.functions: List[str] = []
        self.imports: List[str] = []
        self.docstring: str = ""
        self.lines: int = 0
        self.is_test: bool = "test" in filepath.lower()

    def scan(self, code: str):
        self.lines = len(code.splitlines())
        try:
            tree = ast.parse(code, filename=self.filepath)
            self.docstring = ast.get_docstring(tree) or ""
            self.visit(tree)
        except Exception:
            pass

    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes.append(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.functions.append(node.name)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

class TypeScriptScanner:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.classes: List[str] = []
        self.functions: List[str] = []
        self.imports: List[str] = []
        self.interfaces: List[str] = []
        self.lines: int = 0
        self.docstring: str = ""
        self.is_test: bool = any(k in filepath.lower() for k in ["test", "spec", "__tests__"])

    def scan(self, code: str):
        self.lines = len(code.splitlines())
        # Extract classes.
        self.classes = re.findall(r'\bclass\s+([A-Za-z0-9_]+)', code)
        # Extract interfaces and types.
        self.interfaces = re.findall(r'\b(?:interface|type)\s+([A-Za-z0-9_]+)', code)
        # Extract functions and hooks.
        funcs = re.findall(r'\bfunction\s+([A-Za-z0-9_]+)', code)
        arrow_funcs = re.findall(r'\bconst\s+([A-Za-z0-9_]+)\s*=\s*(?:\([^)]*\)|[A-Za-z0-9_]+)\s*=>', code)
        self.functions = list(set(funcs + arrow_funcs))
        # Extract imports.
        imports_single = re.findall(r'from\s+[\'"]([^\'"]+)[\'"]', code)
        imports_require = re.findall(r'require\([\'"]([^\'"]+)[\'"]\)', code)
        self.imports = list(set(imports_single + imports_require))

def classify_layer(filepath: str, is_test: bool) -> str:
    fp = filepath.lower()
    if is_test:
        return "L6_TESTS"
    if any(k in fp for k in ["models", "db", "migrations", "schema"]):
        return "L1_PERSISTENCE"
    if any(k in fp for k in ["api", "serializers", "views", "controllers", "services"]):
        return "L2_API_LOGIC"
    if any(k in fp for k in ["live", "crdt", "socket", "bgtasks", "celery", "realtime"]):
        return "L3_REALTIME_CRDT"
    if any(k in fp for k in ["hooks", "store", "state", "context", "lib"]):
        return "L4_CLIENT_STATE"
    if any(k in fp for k in ["components", "pages", "app", "ui", "views_ui", "web", "admin", "space"]):
        return "L5_PRESENTATION"
    return "L2_API_LOGIC"

def catalog_directory(target_dir: str, system_name: str = "Planerting3d-System") -> Dict[str, Any]:
    components = []
    symbol_index: Dict[str, str] = {} # symbol -> component_id
    module_index: Dict[str, str] = {} # module_name -> component_id

    # 1. Scan and index nodes.
    for root, _, files in os.walk(target_dir):
        if any(d in root for d in [".git", "node_modules", "__pycache__", ".next", "dist", "build"]):
            continue
        for f in sorted(files):
            ext = os.path.splitext(f)[1].lower()
            if ext not in [".py", ".ts", ".tsx", ".js", ".jsx"]:
                continue

            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, target_dir)
            comp_id = rel_path.replace(os.sep, "/")

            mod_stem = os.path.splitext(os.path.basename(f))[0]
            module_index[mod_stem] = comp_id
            module_index[comp_id] = comp_id

            with open(full_path, "r", encoding="utf-8", errors="ignore") as fh:
                code = fh.read()

            if ext == ".py":
                scanner = PythonASTScanner(rel_path)
                scanner.scan(code)
                is_test = scanner.is_test
                classes = scanner.classes
                functions = scanner.functions
                imports = scanner.imports
                docstring = scanner.docstring
                lines = scanner.lines
            else:
                ts_scanner = TypeScriptScanner(rel_path)
                ts_scanner.scan(code)
                is_test = ts_scanner.is_test
                classes = ts_scanner.classes + ts_scanner.interfaces
                functions = ts_scanner.functions
                imports = ts_scanner.imports
                docstring = ts_scanner.docstring
                lines = ts_scanner.lines

            layer_id = classify_layer(rel_path, is_test)

            for sym in classes + functions:
                symbol_index[sym] = comp_id

            components.append({
                "id": comp_id,
                "label": os.path.basename(f),
                "file": rel_path,
                "layer_id": layer_id,
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "lines": lines,
                "docstring": docstring,
                "is_test": is_test
            })

    # 2. Resolve edges and connections.
    connections = []
    conn_signatures: Set[str] = set()

    for comp in components:
        src_id = comp["id"]
        for imp in comp["imports"]:
            imp_base = imp.split("/")[-1].split(".")[-1]
            target_id = module_index.get(imp_base) or module_index.get(imp)
            if target_id and target_id != src_id:
                sig = f"{src_id}->{target_id}"
                if sig not in conn_signatures:
                    conn_signatures.add(sig)
                    connections.append({
                        "from": src_id,
                        "to": target_id,
                        "label": "imports",
                        "protocol": "static_import"
                    })

    # 3. Calculate 3D coordinates from structural properties.
    # Fan-in calculation.
    fan_in: Dict[str, int] = {c["id"]: 0 for c in components}
    for conn in connections:
        fan_in[conn["to"]] = fan_in.get(conn["to"], 0) + 1

    layer_x_map = {l["id"]: l["x_base"] for l in LAYER_DEFINITIONS}

    for idx, comp in enumerate(components):
        layer = comp["layer_id"]
        base_x = layer_x_map.get(layer, 0.0)
        # Controlled X-axis spread around the layer centroid.
        x = base_x + (math.sin(idx * 1.5) * 12.0)
        # Y axis: degree centrality / AST gravity.
        y = (fan_in.get(comp["id"], 0) * 18.0) - 20.0 + (math.cos(idx * 0.8) * 8.0)
        # Z axis: deterministic core versus external boundary.
        if comp["is_test"]:
            z = 45.0
        elif layer in ["L1_PERSISTENCE", "L2_API_LOGIC"]:
            z = -15.0 + (math.sin(idx) * 6.0)
        elif layer == "L3_REALTIME_CRDT":
            z = 0.0
        else:
            z = 15.0 + (math.cos(idx) * 6.0)

        comp["x"] = round(x, 2)
        comp["y"] = round(y, 2)
        comp["z"] = round(z, 2)
        comp["fan_in"] = fan_in.get(comp["id"], 0)

    # 4. Compile the canonical graph catalog.
    architecture = {
        "version": "2.1",
        "system_name": system_name,
        "meta": {
            "generator": "Planerting3d-AST-Cataloger",
            "methodology": "Structural Isomorphism & Deterministic Workers D*",
            "total_components": len(components),
            "total_connections": len(connections),
            "llm_token_cost": 0
        },
        "layers": LAYER_DEFINITIONS,
        "components": components,
        "connections": connections
    }

    return architecture

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenGraphify deterministic AST cataloger")
    parser.add_argument("target", nargs="?", default=".", help="directory to catalog")
    parser.add_argument("--output", default=None, help="output JSON file")
    args = parser.parse_args()
    target = Path(args.target).resolve()
    out_file = Path(args.output).resolve() if args.output else target / "planerting3d.architecture.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"[*] OpenGraphify cataloger scanning: {target}")
    catalog = catalog_directory(str(target), system_name="OpenGraphify Repository")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"[+] Catalog generated successfully: {out_file}")
    print(f"    - Components: {catalog['meta']['total_components']}")
    print(f"    - Connections (edges): {catalog['meta']['total_connections']}")
    print(f"    - Model-token cost: ZERO")
