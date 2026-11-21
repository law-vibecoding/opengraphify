# PLANERTING3D — OPENGRAPHIFY CATALOGING SPECIFICATION

**Project:** Planerting3d / OpenGraphify
**Status:** Cataloging and 3D visualization layer
**Methodology:** Deterministic AST analysis and structural graph generation

## 1. Scope

OpenGraphify converts a source tree into a reproducible architecture map for Claude Code, Codex, and other compatible coding agents. It focuses on structural facts that can be extracted locally: files, symbols, imports, connections, layers, and spatial coordinates.

The shared `opengraphify-core` layer is intended to provide AST primitives, hashes, cache, contracts, paths, file identity, and a canonical graph format. The `opengraphify` layer consumes that foundation to catalog architecture and render the 3D explorer.

Guards, Frontier Code L2, Obsidian indexing, external connectors, and other specialized tools are intentionally outside this repository and will be published separately.

## 2. Catalog pipeline

1. `planerting3d_cataloger.py` walks the selected source tree.
2. The reader extracts supported symbols and imports without model calls or network access.
3. The cataloger resolves structural connections and emits `planerting3d.architecture.json`.
4. `planerting3d_3d_engine.py` renders the catalog as a self-contained Three.js/WebGL explorer.

## 3. Spatial model

Each component receives coordinates $(x, y, z)$ derived from structural properties:

* **X axis:** functional-flow direction.
* **Y axis:** AST centrality, based on incoming connections.
* **Z axis:** deterministic core versus external-I/O boundary.

The coordinates are a visualization aid; the canonical source of truth remains the JSON graph.

## 4. Measured cataloging result

On the same small fixture, the current OpenGraphify cataloger measured **142 ms cold** and **109 ms repeated**, compared with **2,770 ms cold** and **1,031 ms repeated** for Graphify 0.9.48. That is approximately **19.5× faster cold** and **9.5× faster repeated** for this narrower cataloging subset. Graphify has broader extraction coverage, so this is not a universal product-speed claim.

The ratio is a fixture-level throughput measurement, not `19.5 × N` for `N` files. The token and exploration savings do scale with corpus size because the cataloger avoids repeated full-file reads, import chasing, and context accumulation. Exact total runtime and report size should be measured for each repository.

## 5. Language evolution

The current reader prioritizes Python with lightweight TypeScript/JavaScript extraction. Language-specific backends may be added when they preserve deterministic output, explicit abstention for unsupported syntax, and the canonical graph contract. The Frontier Rust enumerator is a separate performance/parity reference, not an integrated Rust reader.
