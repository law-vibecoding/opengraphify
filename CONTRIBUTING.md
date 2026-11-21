# Contributing to OpenGraphify

OpenGraphify evolves through language-specific reader backends, not through one monolithic parser. Every new language must preserve the same structural graph contract.

## Recommended workflow

1. Choose a language and describe the initial symbol subset to be read.
2. Add small, real fixtures, including valid cases and cases that require abstention.
3. Implement the backend without model calls or network access.
4. Compare its output with the canonical format: files, symbols, imports, connections, and locations.
5. Measure cold, repeated, and incremental execution; do not compare only a warmed run.
6. Run cataloging and the 3D explorer before opening a contribution.

## Rust

The Frontier laboratory contains a separate Rust prototype for deterministic enumerators. It is a performance and parity reference, not an existing OpenGraphify Rust reader. Proper integration should begin with a reader backend, an explicit contract, and cross-tests against Python/TypeScript fixtures.

## Acceptance criteria

- no API dependency for cataloging;
- deterministic output for the same tree and parser version;
- errors and unsupported syntax recorded as observable abstentions;
- coverage and reproducible measurements included;
- no speed claim without a reproducible measurement.
