"""
NOTE:

- Reference to RhinoCommmon.dll is added by default

- You can specify your script requirements like:

    # r: <package-specifier> [, <package-specifier>]
    # requirements: <package-specifier> [, <package-specifier>]

    For example this line will ask the runtime to install
    the listed packages before running the script:

    # requirements: pytoml, keras

    You can install specific versions of a package
    using pip-like package specifiers:

    # r: pytoml==0.10.2, keras>=2.6.0

- Use env directive to add an environment path to sys.path automatically
    # env: /path/to/your/site-packages/
"""
#! python3

import rhinoscriptsyntax as rs
import scriptcontext as sc
import math
import sys
import os

import System
import System.Collections.Generic
import Rhino
from Rhino.UI import OpenFileDialog

# import System.Windows.Forms  # Add this import

def pick_folder(msg="Pick a folder"):
    # https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.folderbrowserdialog?view=windowsdesktop-9.0
    dlg = System.Windows.Forms.FolderBrowserDialog()
    dlg.Description = msg
    dlg.ShowNewFolderButton = False

    if dlg.ShowDialog() == System.Windows.Forms.DialogResult.OK:
        return os.path.normpath(dlg.SelectedPath)
    else:
        print("User canceled.")
        return None

def pick_files(msg="Pick a file"):
    # works for files but not directories :(
    # workaround: pick file then extract directory
    # https://developer.rhino3d.com/api/rhinocommon/rhino.ui.openfiledialog

    dlg = OpenFileDialog()
    dlg.Title = msg
    dlg.MultiSelect = True

    if dlg.ShowOpenDialog():
        return list(dlg.FileNames)  # convert from .NET array into Python list
    else:
        print("User canceled.")
        return None

def get_all_files(path):
    """
    Input: normalized path (string)
    Return list of all files within that directory
    """
    files = os.listdir(path)
    files.sort()
    return files

def filter_extension(paths, lst_of_extensions=['obj', 'skp']):
    """
    Input: list of paths
    Return: filtered list of paths

    for each path:
        for each extension:
            if path ends in extension:
                append it to the results list
    """
    return [path 
            for path in paths
            for ext in lst_of_extensions
            if path.endswith(ext)]

def filter_files_with_matching_3dm(paths, suffix="_sv"):
    """
    Inputs:
        paths: list of normalized paths (strings)
        suffix: string that defines the expected suffix for matching files.  Example:
            # filename.dwg -> filename_suffix.3dm = match found!
            # filename.dwg -> filename_suffix-elevation.3dm = match found!
            # filename.dwg -> filename_xyz.3dm = no match found!
            # filename.dwg -> filename.3dm = no match found!
    """
    # filter out files that have a matching 3dm

    pass
    


if __name__ == "__main__":
    # folder = pick_folder()
    folder = os.path.normpath(r"C:\Users\senor\OneDrive\Desktop\temp\rhino test")
    files = get_all_files(folder)
    # files = filter_extension(files)
    for f in files:
        print(f)
