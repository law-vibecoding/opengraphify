# OpenGraphify — Deterministic Code Intelligence Plugin

OpenGraphify is the public cataloging layer of Planerting3d: an agent-agnostic deterministic plugin for **Claude Code, Codex, and other compatible coding agents**. It provides native AST cataloging, structural graph exploration, and 3D architecture visualization. Its goal is to turn a codebase into a reproducible structural map with low context overhead, without requiring a model call for every inspection.

## Project scope

OpenGraphify brings together two layers that evolve together:

- **`opengraphify-core`** — shared AST, hashing, cache, contracts, path, file-identity, and canonical graph-format primitives.
- **`opengraphify`** — structural cataloging, architecture, symbols, imports, connections, and 3D visualization.

Frontier Code L2, Obsidian indexing, external connectors, and other specialized agents will be separate projects built on this foundation, with independent release cycles.

It reduces unnecessary token consumption and cognitive guesswork by delegating symbol exploration and architecture mapping to local deterministic workers ($D^*$) that run in milliseconds with zero model-token cost.

## Available Slash Commands

- `/planerting-catalog [path]` -- Scan the repository with the supported AST readers and compile `planerting3d.architecture.json`.
- `/planerting-3d` -- Open the interactive spatial explorer in a browser.

## Agent integrations

The deterministic scripts and skills are shared across agents. The repository includes manifests for Claude Code and Codex; other agents can use the same `scripts/`, `skills/`, and canonical graph contract through their native plugin or extension format.

### Claude Code

### Option 1: Use directly in a repository
Copy `commands/`, `skills/`, and `scripts/` into your project's `.claude/` directory.

### Option 2: Install as a plugin
```bash
claude plugin install ./opengraphify
```

### Codex

Use the `.codex-plugin/plugin.json` manifest and expose the same `skills/` and `scripts/` directories through the Codex plugin installation flow.

## Local execution

The commands use the deterministic scripts included in `scripts/` and do not depend on files outside the repository. They generate JSON reports and an HTML explorer in the selected working directory.

## Measured cataloging speed comparison

On the same small Python/TypeScript fixture, the current OpenGraphify cataloger measured:

| Run | OpenGraphify | Graphify 0.9.48 | OpenGraphify speedup |
|---|---:|---:|---:|
| Cold run | 142 ms | 2,770 ms | **19.5× faster** |
| Repeated run | 109 ms | 1,031 ms | **9.5× faster** |

This comparison is intentionally limited to cataloging startup and extraction, not an overall product claim. Graphify has broader extraction and graph features, while the current OpenGraphify reader covers a narrower deterministic subset. The measured advantage is lower overhead for that subset. The benchmark fixture and methodology should be reproduced before making broader claims.

The measured **19.5×** is a throughput ratio for the complete fixture run, not a claim that speed becomes `19.5 × N` for `N` files. As a repository grows, the avoided exploration work and the token savings scale roughly with the number and size of files; the exact wall-clock ratio depends on file mix, parsing coverage, and filesystem overhead.

## Why the token savings scale

The cataloger skips repeated model-mediated steps: opening full files, chasing imports one by one, rebuilding the same symbol map, and carrying those dumps through later turns. It emits one compact, deterministic graph instead. In practical terms:

`tokens saved ≈ avoided full-file context − compact graph/report context`

The scan itself has **zero model-token cost**. For `N` comparable files, the avoided full-file context is approximately the sum of the tokens that would have been read from those files, while the report remains a structured summary. This is why the economic benefit compounds across a large repository even when the measured speedup is reported as a ratio rather than multiplied by `N`.

## Languages and reader evolution

The current reader prioritizes Python and provides lightweight extraction for TypeScript/JavaScript. The architecture is open to language-specific backends without mixing language rules into the graph format.

A Rust prototype developed in the Frontier laboratory (`exp004/rust_enum`) validated a compiled deterministic implementation and measured approximately a 2.5× speedup over Python/NumPy for that specific enumerator. This is **not** presented as an OpenGraphify reader benchmark; it is evidence for an engineering direction that must be ported and measured with parity.

We welcome collaboration to:

- build a Rust structural-reading backend with output identical to the Python backend;
- add readers for Go, Java, C/C++, C#, Kotlin, Swift, and other languages as contributors join;
- build real fixtures, parity tests, and cold/warm/incremental measurements for each language;
- document limitations, parser versions, symbol coverage, and cases where a reader must abstain;
- preserve the graph contract, reproducibility, and zero-token cost of the deterministic core.

Small contributions are welcome: a parser, fixture, measurement, path fix, or documentation improvement helps expand the map.

## Repository structure

- `.claude-plugin/` — Claude Code plugin manifest.
- `.codex-plugin/` — Codex plugin manifest.
- `commands/` — Claude Code slash commands.
- `skills/` — operational instructions for structural cataloging.
- `scripts/` — cataloger and 3D explorer.
- `docs/` — technical documentation for the cataloging layer.
