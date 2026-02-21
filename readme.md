Misc. scripts for Rhino 3D v.8+

## sv_file_batcher.py

Batch-processes DWG files downloaded from sources like dimensions.com, which tend to have cluttered layer structures unsuitable for direct reuse.

**Processing pipeline (per file):**

1. `remove_layers` — deletes layers matching regex patterns (e.g. titleblocks, annotations) along with their geometry
2. `explode_all_blocks` — recursively explodes all block instances until none remain
3. `layer0` — moves all remaining geometry to layer `0` and purges all other layers
4. `join_all` — joins fragmented curves and lines
5. `by_parent` — sets display color, linetype, and plot color to `ByParent` so the embedding document controls appearance

Processed files are then exported via `dwg_exporter` and/or `svg_exporter`, each producing one output file per suffix (e.g. `file-plan.dwg`, `file-elevation.dwg`).

The top-level entry point is `doc_batcher(input_path, output_path, operations)`, which scans the input folder, skips files that already have a matching `_sv.3dm` export, processes each remaining file, and writes any errors to `error_log.txt`.

## Setup
```bash
pdm install
pdm run pre-commit install
```

## Running tests
```bash
pdm run pytest
```

Rhino-dependent functions (`remove_layers`, `explode_all_blocks`, `layer0`, `join_all`, `by_parent`, `dwg_exporter`, `svg_exporter`) require a live Rhino 8 environment and are verified manually inside Rhino's script editor.

## Libraries
- pytest (testing)
- pre-commit (git hooks — blocks commits if tests fail)
