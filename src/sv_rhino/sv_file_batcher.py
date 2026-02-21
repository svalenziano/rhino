"""
sv_file_batcher.py — Batch-processes DWG files for Rhino 3D.

Pipeline: open DWG → remove unwanted layers → explode blocks →
consolidate geometry to layer 0 → set display to ByParent → export.

Rhino-dependent functions require a live Rhino 8 environment and
cannot be unit-tested with pytest. They are marked with
"Rhino-dependent" in their docstrings and only run when RHINO_AVAILABLE.
"""
#! python3

import os
import glob

try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
    import Rhino
    import System
    import System.Collections.Generic
    from Rhino.UI import OpenFileDialog
    RHINO_AVAILABLE = True
except ImportError:
    RHINO_AVAILABLE = False
    Rhino = rs = sc = System = None


# ---------------------------------------------------------------------------
# Pure Python helpers (unit-testable)
# ---------------------------------------------------------------------------

def get_all_files(path):
    """
    Return a sorted list of all filenames within the directory at path.
    Note: returns filenames only, not full paths. See create_file_list for full paths.
    """
    files = os.listdir(path)
    files.sort()
    return files


def filter_extension(paths, lst_of_extensions=None):
    """
    Filter a list of paths to only those ending with one of the given extensions.

    Args:
        paths: list of path strings
        lst_of_extensions: list of extension strings (e.g. ['dwg', 'obj']).
                           Comparison is case-sensitive and suffix-based.

    Returns:
        Filtered list of paths.
    """
    if lst_of_extensions is None:
        lst_of_extensions = ['obj', 'skp']
    return [path
            for path in paths
            for ext in lst_of_extensions
            if os.path.splitext(path)[1].lstrip('.') == ext]


def create_file_list(directory_path, extensions=None):
    """
    Return a sorted list of full absolute paths for all files in directory_path.

    Args:
        directory_path: path to directory to list.
        extensions: optional list of extension strings to filter by
                    (e.g. ['dwg', 'obj']). Matching is case-insensitive.
                    Leading dots are stripped ('dwg' and '.dwg' both work).

    Returns:
        Sorted list of absolute file paths.
    """
    norm_exts = None
    if extensions is not None:
        norm_exts = {e.lower().lstrip('.') for e in extensions}

    files = []
    for name in os.listdir(directory_path):
        full_path = os.path.join(directory_path, name)
        if not os.path.isfile(full_path):
            continue
        if norm_exts is not None:
            ext = os.path.splitext(name)[1].lower().lstrip('.')
            if ext not in norm_exts:
                continue
        files.append(full_path)

    files.sort()
    return files


def filter_files_with_matching_3dm(paths, suffix="_sv"):
    """
    Filter out paths that already have a matching .3dm export alongside them.

    A file is considered "matched" (already processed) if, in the same
    directory, there exists:
      - <basename><suffix>.3dm        (e.g. file_sv.3dm)
      - <basename><suffix>-*.3dm      (e.g. file_sv-elevation.3dm)

    Returns only paths with no such match (i.e. files still needing processing).

    Args:
        paths: list of absolute path strings
        suffix: string suffix identifying processed exports (default "_sv")

    Returns:
        List of paths with no matching .3dm file.
    """
    result = []
    for path in paths:
        directory = os.path.dirname(path)
        base = os.path.splitext(os.path.basename(path))[0]
        exact = os.path.join(directory, f"{base}{suffix}.3dm")
        pattern = os.path.join(directory, f"{base}{suffix}-*.3dm")
        if not os.path.exists(exact) and not glob.glob(pattern):
            result.append(path)
    return result


# ---------------------------------------------------------------------------
# Rhino-dependent UI helpers
# ---------------------------------------------------------------------------

def pick_folder(msg="Pick a folder"):
    """
    Rhino-dependent. Show a folder browser dialog and return the selected path.

    Returns:
        Normalized path string, or None if user cancelled.
    """
    dlg = System.Windows.Forms.FolderBrowserDialog()
    dlg.Description = msg
    dlg.ShowNewFolderButton = False

    if dlg.ShowDialog() == System.Windows.Forms.DialogResult.OK:
        return os.path.normpath(dlg.SelectedPath)
    else:
        print("User canceled.")
        return None


def pick_files(msg="Pick a file"):
    """
    Rhino-dependent. Show a multi-file open dialog and return selected paths.

    Returns:
        List of path strings, or None if user cancelled.
    """
    dlg = OpenFileDialog()
    dlg.Title = msg
    dlg.MultiSelect = True

    if dlg.ShowOpenDialog():
        return list(dlg.FileNames)
    else:
        print("User canceled.")
        return None


# ---------------------------------------------------------------------------
# Rhino-dependent document operations
# ---------------------------------------------------------------------------

def remove_layers(doc, regex_patterns):
    """
    Rhino-dependent. Delete all layers (and their geometry) whose names match
    any regex pattern in regex_patterns.

    Args:
        doc: RhinoDoc instance
        regex_patterns: list of regex strings to match layer names against
    """
    import re
    compiled = [re.compile(p) for p in regex_patterns]
    to_delete = [
        layer.Index for layer in doc.Layers
        if not layer.IsDeleted and any(p.search(layer.Name) for p in compiled)
    ]
    for idx in to_delete:
        for obj in doc.Objects.FindByLayer(doc.Layers[idx]):
            doc.Objects.Delete(obj, True)
    for idx in sorted(to_delete, reverse=True):
        doc.Layers.Delete(idx, True)


def explode_all_blocks(doc):
    """
    Rhino-dependent. Recursively explode all block instances until no blocks
    remain in the document. Logs any block instances that fail to explode.

    Args:
        doc: RhinoDoc instance
    """
    while True:
        instances = list(doc.Objects.FindByObjectType(
            Rhino.DocObjects.ObjectType.InstanceReference))
        if not instances:
            break
        any_exploded = False
        for inst in instances:
            idef = inst.InstanceDefinition
            xform = inst.InstanceXform
            added = False
            for sub_obj in idef.GetObjects():
                geo = sub_obj.Geometry.Duplicate()
                if geo.Transform(xform):
                    doc.Objects.Add(geo, sub_obj.Attributes.Duplicate())
                    added = True
            if added:
                doc.Objects.Delete(inst, True)
                any_exploded = True
            else:
                print(f"Warning: could not explode block {inst.Attributes.ObjectId}")
        if not any_exploded:
            break


def layer0(doc):
    """
    Rhino-dependent. Ensure layer '0' exists, move all geometry onto it,
    and purge all other layers.

    Args:
        doc: RhinoDoc instance
    """
    existing = doc.Layers.FindName("0")
    layer0_idx = existing.Index if existing else doc.Layers.Add(
        "0", System.Drawing.Color.Black)
    for obj in doc.Objects:
        attr = obj.Attributes.Duplicate()
        attr.LayerIndex = layer0_idx
        doc.Objects.ModifyAttributes(obj, attr, True)
    to_delete = [l.Index for l in doc.Layers
                 if not l.IsDeleted and l.Index != layer0_idx]
    for idx in sorted(to_delete, reverse=True):
        doc.Layers.Delete(idx, True)


def join_all(doc):
    """
    Rhino-dependent. Join all curves and lines in the document to clean up
    fragmented linework.

    Args:
        doc: RhinoDoc instance
    """
    curve_objs = list(doc.Objects.FindByObjectType(
        Rhino.DocObjects.ObjectType.Curve))
    if not curve_objs:
        return
    curves = [obj.CurveGeometry for obj in curve_objs]
    joined = Rhino.Geometry.Curve.JoinCurves(curves, doc.ModelAbsoluteTolerance)
    if not joined:
        return
    for obj in curve_objs:
        doc.Objects.Delete(obj, True)
    for curve in joined:
        doc.Objects.AddCurve(curve)


def by_parent(doc):
    """
    Rhino-dependent. Set display properties (DisplayColor, LinetypeSource,
    PlotColorSource, etc.) to ByParent on all objects in the document.

    Args:
        doc: RhinoDoc instance
    """
    CS  = Rhino.DocObjects.ObjectColorSource
    LS  = Rhino.DocObjects.ObjectLinetypeSource
    PCS = Rhino.DocObjects.ObjectPlotColorSource
    PWS = Rhino.DocObjects.ObjectPlotWeightSource
    for obj in doc.Objects:
        attr = obj.Attributes.Duplicate()
        attr.ColorSource      = CS.ColorFromParent
        attr.LinetypeSource   = LS.LinetypeFromParent
        attr.PlotColorSource  = PCS.PlotColorFromParent
        attr.PlotWeightSource = PWS.PlotWeightFromParent
        doc.Objects.ModifyAttributes(obj, attr, True)


def dwg_exporter(doc, orig_filename, suffixes):
    """
    Rhino-dependent. Export the document as one DWG file per suffix.

    Example: suffixes=['-elevation'] → '<orig_filename>-elevation.dwg'

    Args:
        doc: RhinoDoc instance
        orig_filename: original input filename stem (without extension)
        suffixes: list of suffix strings (e.g. ['-plan', '-elevation'])
    """
    for suffix in suffixes:
        out_path = orig_filename + suffix + ".dwg"
        opts = Rhino.FileIO.FileDwgWriteOptions()
        Rhino.FileIO.FileDwg.Write(out_path, doc, opts)


def svg_exporter(doc, orig_filename, suffixes):
    """
    Rhino-dependent. Export the document as one SVG file per suffix.
    Same pattern as dwg_exporter but produces SVG output.

    Args:
        doc: RhinoDoc instance
        orig_filename: original input filename stem (without extension)
        suffixes: list of suffix strings (e.g. ['-plan', '-elevation'])
    """
    for suffix in suffixes:
        out_path = orig_filename + suffix + ".svg"
        opts = Rhino.FileIO.FileSvgWriteOptions()
        Rhino.FileIO.FileSvg.Write(out_path, doc, opts)


def process_document(input_path, funcs, exporters):
    """
    Rhino-dependent. Own the lifetime of a RhinoDoc opened from input_path.

    Opens the document headlessly, calls func(doc) for each func in funcs,
    then calls each exporter(doc, orig_filename) in exporters.
    Guarantees doc.Dispose() runs even if an exception occurs.

    Callers never touch doc directly.

    Args:
        input_path: absolute path to the input file
        funcs: list of callables accepting (doc,)
        exporters: list of callables accepting (doc, orig_filename)
    """
    orig_filename = os.path.splitext(input_path)[0]
    doc = Rhino.RhinoDoc.OpenHeadless(input_path)
    try:
        for func in funcs:
            func(doc)
        for exporter in exporters:
            exporter(doc, orig_filename)
    finally:
        doc.Dispose()


def doc_batcher(input_path, output_path, operations, exporters=None):
    """
    Rhino-dependent. Top-level orchestrator for batch processing.

    Scans input_path for DWG files, skips any that already have a matching
    _sv.3dm export alongside them, then calls process_document() on each
    remaining file. Exceptions are caught per-file and appended to
    error_log.txt in output_path rather than aborting the whole batch.

    Args:
        input_path: directory containing input DWG files
        output_path: directory for exported files and error_log.txt
        operations: list of doc-operation callables (e.g. remove_layers,
                    explode_all_blocks, layer0, join_all, by_parent)
        exporters: list of exporter callables accepting (doc, orig_filename);
                   use functools.partial to pre-bind suffixes. Defaults to [].
    """
    if exporters is None:
        exporters = []
    files = create_file_list(input_path, extensions=["dwg"])
    files = filter_files_with_matching_3dm(files)
    error_log_path = os.path.join(output_path, "error_log.txt")
    for file_path in files:
        try:
            process_document(file_path, funcs=operations, exporters=exporters)
        except Exception as e:
            with open(error_log_path, "a") as f:
                f.write(f"{file_path}: {e}\n")


def run():
    """
    Interactive entry point for running the batch pipeline from Rhino's script editor.
    Prompts for input and output folders, then runs doc_batcher with the full
    default operations list.
    """
    import functools

    input_path = pick_folder("Pick input folder (DWG files)")
    if input_path is None:
        return
    output_path = pick_folder("Pick output folder (exports + error_log)")
    if output_path is None:
        return

    ops = [
        explode_all_blocks,
        layer0,
        join_all,
        by_parent,
    ]
    exporters = [
        functools.partial(dwg_exporter, suffixes=["_sv"]),
    ]

    doc_batcher(input_path, output_path, operations=ops, exporters=exporters)
    print("Done. Check output folder and error_log.txt if any files failed.")


if __name__ == "__main__":
    run()
