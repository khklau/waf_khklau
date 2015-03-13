#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2014

'''
This is an extra tool, not bundled with the default waf binary.
To add the Url Utilities tool to the waf file:
    $ ./waf-light --tools=url_utils
or, if you have waf >= 1.6.2
    $ ./waf update --files=url_utils

When using this tool, the wscript will look like:

    from waflib.extras.url_utils import tryDownload

    def prepare(prep):
	srcUrl = 'http://foobar.com/file.zip'
	tgtPath = '/some/local/directory/file.zip'
	if tryDownload(srcUrl, tgtPath, 10):
	    handle = open(tgtPath, 'r')
	else:
	    prep.fatal('Could not download %s' % srcUrl)
'''

import hashlib
import os
import tarfile
import tempfile
import urllib
import zipfile

def tryDownload(srcUrl, tgtPath, maxAttempts):
    triesRemaining = maxAttempts
    while triesRemaining > 1:
	try:
	    urllib.urlretrieve(srcUrl, tgtPath)
	    return True
	except urllib.ContentTooShortError:
	    triesRemaining -= 1
	if os.path.exists(tgtPath):
	    os.remove(tgtPath)
    else:
	return False

def extractRemoteTar(srcUrl, tgtDir):
    result = False
    tempDir = tempfile.mkdtemp(prefix='url_utils-')
    try:
	tempFile = os.path.join(tempDir, 'temp.zip')
	if tryDownload(url, tempFile, 10):
	    handle = tarfile.open(tempFile, 'r:*')
	    handle.extractall(tgtDir)
	    result = True
    finally:
	shutil.rmtree(tempDir)
    return result

def extractRemoteZip(srcUrl, tgtDir):
    result = False
    tempDir = tempfile.mkdtemp(prefix='url_utils-')
    try:
	tempFile = os.path.join(tempDir, 'temp.zip')
	if tryDownload(url, tempFile, 10):
	    handle = zipfile.Zipfile(tempFile, 'r')
	    handle.extractall(tgtDir)
	    result = True
    finally:
	shutil.rmtree(tempDir)
    return result

def syncRemoteFile(sha256sum, srcUrl, tgtPath, maxAttempts):
    if os.access(tgtPath, os.R_OK):
	hasher = hashlib.sha256()
	handle = open(tgtPath, 'rb')
	try:
	    hasher.update(handle.read())
	finally:
	    handle.close()
	if hasher.digest() != sha256sum:
	    os.remove(tgtPath)
    elif os.path.exists(tgtPath):
	os.remove(tgtPath)
    if os.access(tgtPath, os.R_OK):
	return True
    else:
	return tryDownload(srcUrl, tgtPath, maxAttempts)
