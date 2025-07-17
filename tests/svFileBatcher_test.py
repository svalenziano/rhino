import sys
import os
dir_to_search = os.path.join(os.path.dirname(__file__), '../src/sv_rhino/')
sys.path.append(os.path.abspath(dir_to_search))
from hello_world import func

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
    # r: pytest>=8.4.1

- Use env directive to add an environment path to sys.path automatically
    # env: /path/to/your/site-packages/
"""
#! python3

# import rhinoscriptsyntax as rs
# import scriptcontext as sc
# import math

# import System
# import System.Collections.Generic
# import Rhino


# content of test_sample.py



def test_answer():
    assert func(3) == 5

def test_should_pass():
    assert func(1) == 2

if __name__ == "__main__":
    test_answer()
    test_should_pass()