---
name: ast-cataloger
description: Use whenever you need to map architecture, classes, functions, dependencies, or file topology in Plane or any polyglot project. Replace mass text-file reads with deterministic local AST analysis that runs in milliseconds with zero model-token cost.
---

# Deterministic Worker: AST Cataloger

## Core principle
NEVER use additional cognitive workers or repeated full-file viewing to understand project structure. That consumes thousands of tokens and encourages scope hallucinations.

## Operating procedure
1. Run the deterministic cataloger:
   `python3 scripts/planerting3d_cataloger.py . --output planerting3d.architecture.json`
2. Read the generated `planerting3d.architecture.json` to obtain the exact list of symbols, imports, and layers.
3. Use the mapped connections to identify direct and reverse dependencies.
