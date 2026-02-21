import os
import pytest
from unittest.mock import patch, MagicMock, call

import sv_rhino.sv_file_batcher as batcher


# ---------------------------------------------------------------------------
# process_document
# ---------------------------------------------------------------------------

def test_process_document_calls_funcs_in_order():
    mock_doc = MagicMock()
    func_a = MagicMock()
    func_b = MagicMock()
    manager = MagicMock()
    manager.attach_mock(func_a, "func_a")
    manager.attach_mock(func_b, "func_b")

    with patch("sv_rhino.sv_file_batcher.Rhino") as mock_rhino:
        mock_rhino.RhinoDoc.OpenHeadless.return_value = mock_doc
        batcher.process_document("/in/file.dwg", funcs=[func_a, func_b], exporters=[])

    assert func_a.call_args_list == [call(mock_doc)]
    assert func_b.call_args_list == [call(mock_doc)]
    # verify order: func_a before func_b
    func_a_idx = manager.mock_calls.index(call.func_a(mock_doc))
    func_b_idx = manager.mock_calls.index(call.func_b(mock_doc))
    assert func_a_idx < func_b_idx


def test_process_document_calls_exporters():
    mock_doc = MagicMock()
    exporter = MagicMock()

    with patch("sv_rhino.sv_file_batcher.Rhino") as mock_rhino:
        mock_rhino.RhinoDoc.OpenHeadless.return_value = mock_doc
        batcher.process_document("/in/file.dwg", funcs=[], exporters=[exporter])

    exporter.assert_called_once_with(mock_doc, "/in/file")


def test_process_document_disposes_on_success():
    mock_doc = MagicMock()

    with patch("sv_rhino.sv_file_batcher.Rhino") as mock_rhino:
        mock_rhino.RhinoDoc.OpenHeadless.return_value = mock_doc
        batcher.process_document("/in/file.dwg", funcs=[], exporters=[])

    mock_doc.Dispose.assert_called_once()


def test_process_document_disposes_on_exception():
    mock_doc = MagicMock()
    bad_func = MagicMock(side_effect=RuntimeError("boom"))

    with patch("sv_rhino.sv_file_batcher.Rhino") as mock_rhino:
        mock_rhino.RhinoDoc.OpenHeadless.return_value = mock_doc
        with pytest.raises(RuntimeError, match="boom"):
            batcher.process_document("/in/file.dwg", funcs=[bad_func], exporters=[])

    mock_doc.Dispose.assert_called_once()


# ---------------------------------------------------------------------------
# doc_batcher
# ---------------------------------------------------------------------------

def test_doc_batcher_calls_process_for_each_file(tmp_path):
    files = ["/input/a.dwg", "/input/b.dwg"]

    with patch("sv_rhino.sv_file_batcher.create_file_list", return_value=files), \
         patch("sv_rhino.sv_file_batcher.filter_files_with_matching_3dm", return_value=files), \
         patch("sv_rhino.sv_file_batcher.process_document") as mock_proc:
        batcher.doc_batcher("/input", str(tmp_path), operations=[])

    assert mock_proc.call_count == 2
    mock_proc.assert_any_call("/input/a.dwg", funcs=[], exporters=[])
    mock_proc.assert_any_call("/input/b.dwg", funcs=[], exporters=[])


def test_doc_batcher_skips_already_processed(tmp_path):
    files = ["/input/a.dwg"]

    with patch("sv_rhino.sv_file_batcher.create_file_list", return_value=files), \
         patch("sv_rhino.sv_file_batcher.filter_files_with_matching_3dm", return_value=[]), \
         patch("sv_rhino.sv_file_batcher.process_document") as mock_proc:
        batcher.doc_batcher("/input", str(tmp_path), operations=[])

    mock_proc.assert_not_called()


def test_doc_batcher_writes_error_log_on_failure(tmp_path):
    files = ["/input/bad.dwg"]

    with patch("sv_rhino.sv_file_batcher.create_file_list", return_value=files), \
         patch("sv_rhino.sv_file_batcher.filter_files_with_matching_3dm", return_value=files), \
         patch("sv_rhino.sv_file_batcher.process_document", side_effect=RuntimeError("failed")):
        batcher.doc_batcher("/input", str(tmp_path), operations=[])

    error_log = tmp_path / "error_log.txt"
    assert error_log.exists()
    content = error_log.read_text()
    assert "/input/bad.dwg" in content
    assert "failed" in content
