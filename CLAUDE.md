# CLAUDE.md — sv_scripts Project Context

## Project Overview
Misc. scripts for Rhino 3D v.8+. The primary deliverable is `sv_file_batcher.py`: a pipeline that batch-processes downloaded DWG files — stripping unnecessary layers, consolidating geometry to layer `0`, setting display properties to `ByParent`, and exporting in multiple formats.

## Project Structure
```
sv_scripts/
├── src/sv_rhino/
│   ├── sv_file_batcher.py   ← main file
│   └── hello_world.py
├── tests/
│   ├── sv_file_batcher_test.py
│   └── dwgs/                ← 9 real DWG files for use as test fixtures
├── CLAUDE.md
├── claude_todo.md
└── readme.md
```

## Running Tests
```bash
pdm run pytest
```
Tests must pass without a Rhino environment. Rhino-dependent code is guarded by a try/except import block.

## Key Conventions
- **Snake_case** for all function names (e.g. `by_parent`, not `byParent`)
- **Rhino import guard:** wrap all Rhino/System imports in `try/except ImportError` so the module can be imported in a pure-Python test environment
- **Test imports:** tests add `src/sv_rhino/` to `sys.path` via `sys.path.append` (no `__init__.py` needed)
- **Full paths:** `create_file_list` and similar functions return absolute paths, not bare filenames
- **Package manager:** PDM (`pdm run pytest`, `pdm add <pkg>`) — not pip or poetry

## Rhino-Dependent Functions
The following functions require a live Rhino 8 environment and **cannot** be unit-tested with pytest. They are implemented as stubs and verified manually by running inside Rhino's script editor:
- `remove_layers`, `explode_all_blocks`, `layer0`, `join_all`, `by_parent`
- `dwg_exporter`, `svg_exporter`
- `process_document`, `doc_batcher` (partially Rhino-dependent)

## Todo
See `claude_todo.md` for the current implementation checklist.
