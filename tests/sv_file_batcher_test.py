import os
import pytest

from sv_rhino.sv_file_batcher import (
    create_file_list,
    filter_extension,
    filter_files_with_matching_3dm,
)

DWG_DIR = os.path.join(os.path.dirname(__file__), "dwgs")


# ---------------------------------------------------------------------------
# create_file_list
# ---------------------------------------------------------------------------

def test_create_file_list_returns_full_paths():
    paths = create_file_list(DWG_DIR)
    assert len(paths) > 0
    assert all(os.path.isabs(p) for p in paths)


def test_create_file_list_sorted():
    paths = create_file_list(DWG_DIR)
    assert paths == sorted(paths)


def test_create_file_list_extension_filter():
    paths = create_file_list(DWG_DIR, extensions=["dwg"])
    assert len(paths) == 9
    assert all(p.lower().endswith(".dwg") for p in paths)


def test_create_file_list_empty_dir(tmp_path):
    paths = create_file_list(str(tmp_path))
    assert paths == []


def test_create_file_list_case_insensitive_ext(tmp_path):
    (tmp_path / "file1.dwg").touch()
    (tmp_path / "file2.DWG").touch()
    (tmp_path / "file3.txt").touch()
    paths = create_file_list(str(tmp_path), extensions=["dwg"])
    assert len(paths) == 2


# ---------------------------------------------------------------------------
# filter_extension
# ---------------------------------------------------------------------------

def test_filter_extension_matches():
    paths = ["/foo/file.dwg", "/foo/file.obj", "/foo/file.txt"]
    result = filter_extension(paths, ["dwg"])
    assert result == ["/foo/file.dwg"]


def test_filter_extension_no_matches():
    paths = ["/foo/file.txt", "/foo/file.png"]
    result = filter_extension(paths, ["dwg"])
    assert result == []


def test_filter_extension_multiple_extensions():
    paths = ["/foo/file.dwg", "/foo/file.obj", "/foo/file.txt"]
    result = filter_extension(paths, ["dwg", "obj"])
    assert result == ["/foo/file.dwg", "/foo/file.obj"]


# ---------------------------------------------------------------------------
# filter_files_with_matching_3dm
# ---------------------------------------------------------------------------

def test_no_matching_3dm_files_returned(tmp_path):
    dwg = tmp_path / "file.dwg"
    dwg.touch()
    result = filter_files_with_matching_3dm([str(dwg)])
    assert str(dwg) in result


def test_matched_file_excluded(tmp_path):
    dwg = tmp_path / "file.dwg"
    match = tmp_path / "file_sv.3dm"
    dwg.touch()
    match.touch()
    result = filter_files_with_matching_3dm([str(dwg)])
    assert str(dwg) not in result


def test_custom_suffix(tmp_path):
    dwg = tmp_path / "file.dwg"
    match = tmp_path / "file_done.3dm"
    dwg.touch()
    match.touch()
    result = filter_files_with_matching_3dm([str(dwg)], suffix="_done")
    assert str(dwg) not in result


def test_partial_suffix_not_matched(tmp_path):
    dwg = tmp_path / "file.dwg"
    no_match = tmp_path / "file.3dm"
    dwg.touch()
    no_match.touch()
    result = filter_files_with_matching_3dm([str(dwg)])
    assert str(dwg) in result


def test_variant_suffix_excluded(tmp_path):
    """file_sv-elevation.3dm should count as a match for file.dwg."""
    dwg = tmp_path / "file.dwg"
    match = tmp_path / "file_sv-elevation.3dm"
    dwg.touch()
    match.touch()
    result = filter_files_with_matching_3dm([str(dwg)])
    assert str(dwg) not in result
