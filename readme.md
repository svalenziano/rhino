WORK IN PROGRESS (Sorry for the mess)

Misc. scripts for Rhino 3D v.8+

## Libraries
- pytest (testing)


## File Batcher Goals
File batcher is a script that batch-processes files using Rhino v8.

Example: I have ~100 files that I downloaded from dimensions.com.  I wish to use these files in my designs, but the layer structure makes that very difficult.  I want to batch the files into a format that makes them easy to use in my project:
- uneccessary linework is removed (eg titleblocks)
- all geometry is on the `0` layer
- displayColor, etc are set to `ByParent` so that the containing Rhino file can control their appearance

Bonus feature: the ability to setup multiple file exports for one run.

Here's what I have so far.  See also `sv_file_batcher.py`

```python
import Rhino
import os
import sys

print(sys.version)

def create_file_list(directory_path)
# CREATE LIST OF FILES TO BE PROCESSED
	# Get directory name
	# return list of files

def remove_layers(regex_patterns):
	# remove all layers that match regexes
	# geometry on these layers is deleted!

def explode_all_blocks():
	# recursively explode all blocks
	# no blocks should remain
	# if failed, write message to log

def layer0():
	# create `0` layer if it doesn't exist
	# move all geometry to `0` and purge remaining layers

def join_all():
	# join all lines together.  intent: clean things up

def byParent():
	# set all properties to byParent so that this file (if embedded in another doc as a block) can inherit linetypes & colors from the containing document

def dwg_exporter(RhinoDoc_object, orig_filename, suffixes:list):
	# export one file for each suffix in `suffixes` eg ['-elevation', '-plan']

def svg_exporter(RhinoDoc_object, orig_filename, suffixes:list):
	# ...

def process_document(doc_object, funcs:list, exporters:list):
	"""
	funcs: list of processing functions
	exporters: list of functions that will be used to export the document
	"""
	# Create a headless Rhino document
	
	# Set up options for reading DWG files
	
	# Specify the path to the DWG file
	
	# Import the DWG file into the document
	
	# invoke each function in `funcs`
		# Remove layers via regex (HELPER)
		# layer0 (HELPER)
		# join_all (HELPER)

	# invoke each exporter in `exporters`
		# 3dm
		# SVG

	doc.Dispose()
	
# handles all documents
def doc_batcher(input_path, output_path, operations):
	# for each document in input_path
	# conduct each operation
	# save each result to the output_path
	# write any errors to a log in the output_path


if (__name__ == "__main__"):
	# create file list
	# process all files
	# clean up!
	
	# It might look like this:
	
	"""
	A list of functions to be run by doc_batcher
	Use `functools partial` to partially apply arguments, if necessary?
	"""
	dimensions_com_to_dwg = [
	  # ...
	]
	  
	# run it!
	doc_batcher(
		input=r'C:\Users\senor\AppData\Roaming\McNeel\Rhinoceros\8.0\scripts\sv_scripts\tests\dwgs'
		output='C:\Users\senor\OneDrive\Desktop\temp\batch_test'
		operations=[dimensions_com_to_dwg]
	)
```