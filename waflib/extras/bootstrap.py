#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2014

'''
This is an extra tool, not bundled with the default waf binary.
To add the BootStrap Utilities tool to the waf file:
    $ ./waf-light --tools=bootstrap_utils
or, if you have waf >= 1.6.2
    $ ./waf update --files=bootstrap_utils

When using this tool, the wscript will look like:

    from waflib.extras.bootstrap_utils import BuildStatus

    def prepare(prep):
	strap = BootStrap.init('/some/dir', 'http://some.url')
	if strap.boot('prepare', 'configure', 'build'):
	    prep.options.foo = strap.getPath()
'''

import os
import shutil
import subprocess
import sys
from waflib import Context
from waflib.extras.url_utils import extractRemoteZip

class BootStrap:

    def __init__(self, path, url):
	self.path = path
	self.url = url

    def __repr__(self):
	return "__import__('waflib').extras.bootstrap_utils.%s(%s, %s)" % (
		self.__class__.__name__,
		self.path.__repr__(),
		self.url.__repr__())

    @classmethod
    def init(cls, path, url):
	if os.access(os.path.join(path, Context.WSCRIPT_FILE), os.R_OK):
	    return BootStrap(path, url)
	else:
	    if os.path.isdir(path):
		shutil.rmtree(path)
	    else:
		os.remove(path)
	    os.mkdir(path)
	    if extractRemoteZip(url, path):
		return BootStrap(path, url)
	    else:
		return None

    def getPath(self):
	return self.path

    def getUrl(self):
	return self.url

    def boot(self, *commands):
	cmd = [os.path.abspath(sys.argv[0])] + [ cmd for cmd in commands]
	cwd = os.getcwd()
	returnCode = -1
	try:
	    os.chdir(self.path)
	    returnCode = subprocess.call(cmd)
	finally:
	    os.chdir(cwd)
	return returnCode == 0

