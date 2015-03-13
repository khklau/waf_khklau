#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2014

'''
This is an extra tool, not bundled with the default waf binary.
To add the Mirror tool to the waf file:
    $ ./waf-light --tools=mirror
or, if you have waf >= 1.6.2
    $ ./waf update --files=mirror

When using this tool, the wscript will look like:

    from waflib.extras.mirror import MirroredTarFile

    def prepare(prep):
	file = MirroredTarFile('http://some.url/file.tar.gz', '/some/dir/file.tar.gz')
	if file.sync(10):
	    file.extract('/extract/dir')
	else:
	    prep.fatal('Could not sync %s' % file)
'''

import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from waflib import Context
from waflib.extras.url_utils import syncRemoteFile


class MirroredTarFile:

    def __init__(self, sha256Checksum, srcUrl, tgtPath):
	self.sha256Checksum = sha256Checksum
	self.srcUrl = srcUrl
	self.tgtPath = tgtPath

    def __repr__(self):
	return "__import__('waflib').extras.bootstrap_utils.%s(%s, %s, %s)" % (
		self.__class__.__name__,
		self.sha256Checksum.__repr__(),
		self.srcUrl.__repr__(),
		self.tgtPath.__repr__())

    def __str__(self):
	return '%s<%d>(%s, %s, %s)' % (
		self.__class__.__name__,
		self,
		self.sha256Checksum.__str__(),
		self.srcUrl.__str__(),
		self.tgtPath.__str__())

    def getSha256Checksum(self):
	return self.sha256Checksum

    def getSrcUrl(self):
	return self.srcUrl

    def getTgtPath(self):
	return self.tgtPath

    def sync(self, maxAttempts):
	return syncRemoteFile(self.sha256Checksum, self.srcUrl, self.tgtPath, maxAttempts)

    def extract(self, tgtDir):
	handle = tarfile.open(self.tgtPath, 'r:*')
	handle.extractall(tgtDir)


class MirroredZipFile:

    def __init__(self, sha256Checksum, srcUrl, tgtPath):
	self.sha256Checksum = sha256Checksum
	self.srcUrl = srcUrl
	self.tgtPath = tgtPath

    def __repr__(self):
	return "__import__('waflib').extras.bootstrap_utils.%s(%s, %s, %s)" % (
		self.__class__.__name__,
		self.sha256Checksum.__repr__(),
		self.srcUrl.__repr__(),
		self.tgtPath.__repr__())

    def __str__(self):
	return '%s<%d>(%s, %s, %s)' % (
		self.__class__.__name__,
		self,
		self.sha256Checksum.__str__(),
		self.srcUrl.__str__(),
		self.tgtPath.__str__())

    def getSha256Checksum(self):
	return self.sha256Checksum

    def getSrcUrl(self):
	return self.srcUrl

    def getTgtPath(self):
	return self.tgtPath

    def sync(self, maxAttempts):
	return syncRemoteFile(self.sha256Checksum, self.srcUrl, self.tgtPath, maxAttempts)

    def extract(self, tgtDir):
	handle = zipfile.ZipFile(self.tgtPath, 'r')
	handle.extractall(tgtDir)
