---
description: Run native deterministic AST cataloging with zero model-token cost and compile the canonical architecture graph.
---

# /planerting-catalog

Instruct Claude Code to:
1. Identify the target directory supplied by the user, or use the current project directory.
2. Run the local deterministic worker:
   ```bash
   python3 scripts/planerting3d_cataloger.py [path] --output [path]/planerting3d.architecture.json
   ```
3. Do NOT dispatch neural workers to read text files.
4. Present the executive summary of components, resolved edges, and discovered layers directly from `planerting3d.architecture.json`.
