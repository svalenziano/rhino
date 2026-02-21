# sv_file_batcher — Implementation Plan & Checklist

Track progress here. Update checkboxes as tasks are completed.

---

## Context
The readme describes a batch-processing pipeline for Rhino 3D CAD files. The goal is to automate cleaning up downloaded DWG files (remove unnecessary layers/linework, consolidate geometry to layer `0`, set display properties to `ByParent`) and export them in multiple formats. The plan also includes unit tests for pure-Python functions.

## Current State
- **Main file:** `src/sv_rhino/sv_file_batcher.py` — has partial implementations:
  - `get_all_files(path)` → lists files in a dir (pure Python)
  - `filter_extension(paths, extensions)` → filters by extension (pure Python)
  - `filter_files_with_matching_3dm(paths, suffix)` → stub (`pass`)
  - `pick_folder()`, `pick_files()` → Rhino UI dialogs (Rhino-dependent)
- **Test file:** `tests/sv_file_batcher_test.py` — only tests `hello_world.func`, nothing from file batcher yet
- **Test data:** `tests/dwgs/` — 9 real DWG files available as fixtures
- ~~No `__init__.py` files; tests use `sys.path.append` to import from `src/sv_rhino/`~~ **Fixed:** `pyproject.toml` now has `[tool.pytest.ini_options] pythonpath = ["src"]`; test imports use `from sv_rhino.x import y`

---

## Approach

Rhino functions require a live Rhino environment and can't be unit-tested in isolation. Pure Python functions can be tested with pytest normally. Keep everything in `sv_file_batcher.py` but clearly mark which functions are Rhino-dependent via docstrings. Guard Rhino imports at the top so the file can be imported in a test environment without crashing.

```python
# Guard Rhino imports so module is importable in pure-Python test environments
try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
    import Rhino
    import System
    RHINO_AVAILABLE = True
except ImportError:
    RHINO_AVAILABLE = False
```

---

## Tasks: `src/sv_rhino/sv_file_batcher.py`

### Rhino Import Guard
- [x] Wrap `rhinoscriptsyntax`, `scriptcontext`, `Rhino`, `System` imports in `try/except ImportError`

### Pure Python Functions (unit-testable)

#### `create_file_list(directory_path, extensions=None)`
Replaces/supersedes `get_all_files()` + `filter_extension()`. Returns list of **full absolute paths**.
- Uses `os.listdir` + `os.path.join` to build full paths
- If `extensions` given, filters to only those extensions (case-insensitive)
- Sorts results for deterministic output
- Keep `get_all_files` and `filter_extension` as internal helpers

- [x] Implement `create_file_list`

#### `filter_files_with_matching_3dm(paths, suffix="_sv")`
Implement the existing stub. A file is "matched" (filtered OUT) if a `.3dm` file exists alongside it with the given suffix pattern.
- Pattern: `filename.dwg` is matched if `filename{suffix}.3dm` or `filename{suffix}-*.3dm` exists in the same directory
- Returns paths with no matching `.3dm` (i.e., files that still need processing)

- [x] Implement `filter_files_with_matching_3dm`

### Rhino-Dependent Functions (stubs with clear docstrings now; full impl later)
All Rhino functions accept a `RhinoDoc` object as their first argument.

#### `remove_layers(doc, regex_patterns: list[str])`
Delete all layers (and their geometry) whose names match any regex in the list.
- [x] Write stub + docstring

#### `explode_all_blocks(doc)`
Recursively explode all block instances until no blocks remain. Log failures.
- [x] Write stub + docstring

#### `layer0(doc)`
Create layer `0` if missing, move all geometry to it, purge all other layers.
- [x] Write stub + docstring

#### `join_all(doc)`
Join all curves/lines. Intent: clean up fragmented linework.
- [x] Write stub + docstring

#### `by_parent(doc)` *(renamed from `byParent` to snake_case)*
Set `DisplayColor`, `LinetypeSource`, `PlotColorSource`, etc. to `ByParent` on all objects.
- [x] Write stub + docstring

#### `dwg_exporter(doc, orig_filename: str, suffixes: list[str])`
Export one DWG file per suffix. E.g. `suffixes=['-elevation']` → `filename-elevation.dwg`.
- [x] Write stub + docstring

#### `svg_exporter(doc, orig_filename: str, suffixes: list[str])`
Same pattern as `dwg_exporter` but exports SVG.
- [x] Write stub + docstring

#### `process_document(input_path: str, funcs: list, exporters: list)`
Owns the document lifetime. Opens a headless RhinoDoc from `input_path` (creating `doc` internally), then calls `func(doc)` for each func in `funcs` and `exporter(doc, ...)` for each exporter. Wraps in `try/finally` to ensure `doc.Dispose()` always runs. Callers never touch `doc` directly.
- [x] Write stub + docstring

#### `doc_batcher(input_path: str, output_path: str, operations: list)`
Top-level orchestrator. For each file in `create_file_list(input_path)`:
- Call `process_document(file, funcs=operations, exporters=[...])`
- Catch exceptions, write to `error_log.txt` in `output_path`

- [x] Write stub + docstring

---

## Tasks: `tests/sv_file_batcher_test.py`

Replace current placeholder content. Keep the `sys.path.append` import pattern.

### Tests for `create_file_list`
Use `tests/dwgs/` as a real fixture directory (9 `.dwg` files).

- [x] `test_create_file_list_returns_full_paths` — all returned paths are absolute
- [x] `test_create_file_list_sorted` — results are sorted
- [x] `test_create_file_list_extension_filter` — filter to `.dwg` returns 9 files from `tests/dwgs/`
- [x] `test_create_file_list_empty_dir(tmp_path)` — empty directory returns `[]`
- [x] `test_create_file_list_case_insensitive_ext(tmp_path)` — `.DWG` and `.dwg` both matched when filtering for `'dwg'`

### Tests for `filter_extension`
- [x] `test_filter_extension_matches` — returns paths matching the given extension
- [x] `test_filter_extension_no_matches` — returns `[]` when nothing matches
- [x] `test_filter_extension_multiple_extensions` — all extensions in the list are matched

### Tests for `filter_files_with_matching_3dm`
- [x] `test_no_matching_3dm_files_returned(tmp_path)` — dwg with no `.3dm` alongside → included in result
- [x] `test_matched_file_excluded(tmp_path)` — dwg with matching `_sv.3dm` alongside → excluded from result
- [x] `test_custom_suffix(tmp_path)` — custom suffix works correctly
- [x] `test_partial_suffix_not_matched(tmp_path)` — `file.dwg` + `file.3dm` (no suffix) → not a match, file still included
- [x] `test_variant_suffix_excluded(tmp_path)` — `file_sv-elevation.3dm` counts as a match for `file.dwg`

---

## Verification
1. Run `pdm run pytest` from project root — all tests should pass
2. Manually verify `create_file_list` against `tests/dwgs/` (expect 9 `.dwg` files)
3. Rhino-dependent stubs verified later by running inside Rhino 8's script environment

---

## Meta
- [x] `CLAUDE.md` created
- [x] `claude_todo.md` created
- [ ] Commit updated `readme.md` (typos: "uneccessary", missing colon on `create_file_list`, raw string inconsistency in example)
