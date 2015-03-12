#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2014

'''
This is an extra tool, not bundled with the default waf binary.
To add the Filesystem Utilities tool to the waf file:
    $ ./waf-light --tools=filesystem_utils
or, if you have waf >= 1.6.2
    $ ./waf update --files=filesystem_utils

When using this tool, the wscript will look like:

    from waflib.extras.filesystem_utils import removeSubdir

    def prepare(prep):
	removeSubdir('/some/dir', 'subdir1, 'subdir2', 'subdir3')
'''

import os
import shutil

def removeSubdir(dirPath, *subdirList):
    for subdir in subdirList:
	path = os.path.join(dirPath, subdir)
	if os.path.exists(path):
	    if os.path.isdir(path):
		shutil.rmtree(path)
	    else:
		os.remove(path)
