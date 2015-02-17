#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2014

'''
This is an extra tool, not bundled with the default waf binary.
To add the Build Status tool to the waf file:
    $ ./waf-light --tools=build_status
or, if you have waf >= 1.6.2
    $ ./waf update --files=build_status

When using this tool, the wscript will look like:

    from waflib.extras.build_status import BuildStatus

    def prepare(prep):
	depPath = getDepPath(prep)
	status = BuildStatus.load(depPath)
	if status.isFailure():
	    rebuildDep()
	fi

    def build(bld):
	status = BuildStatus.init(bld.path.abspath())
	bld.recurse('src')
	status.setSuccess()
'''

import os
if os.name == 'posix':
    import fcntl
elif os.name == 'nt':
    import msvcrt

def exclusive_lock(handle):
    if os.name == 'posix':
	fcntl.lockf(handle, fcntl.LOCK_EX)
    elif os.name == 'nt':
	fcntl.locking(handle, msvcrt.LK_NBLCK, 64)
    else:
	raise OSError('Unsupported OS %s' % os.name)

def shared_lock(handle):
    if os.name == 'posix':
	fcntl.lockf(handle, fcntl.LOCK_SH)
    elif os.name == 'nt':
	fcntl.locking(handle, msvcrt.LK_NBRLCK, 64)
    else:
	raise OSError('Unsupported OS %s' % os.name)

def unlock(handle):
    if os.name == 'posix':
	fcntl.lockf(handle, fcntl.LOCK_UN)
    elif os.name == 'nt':
	fcntl.locking(handle, msvcrt.LK_UNLCK, 64)
    else:
	raise OSError('Unsupported OS %s' % os.name)

class BuildStatus:

    __STATUS_FILE_NAME = 'build.status'
    __STATUS_SUCCESS = 'success'
    __STATUS_FAILURE = 'failure'

    def __init__(self, filePath):
	self.filePath = filePath

    def __repr__(self):
	return "__import__('waflib').extras.build_status.%s(%s)" % (
		self.__class__.__name__,
		self.filePath.__repr__())

    @classmethod
    def init(cls, dirPath):
	filePath = dirPath + os.sep + cls.__STATUS_FILE_NAME
	handle = open(filePath, 'w')
	try:
	    exclusive_lock(handle)
	    handle.write(cls.__STATUS_FAILURE)
	    handle.write('\n')
	    unlock(handle)
	finally:
	    handle.close()
	return BuildStatus(filePath)

    @classmethod
    def load(cls, dirPath):
	filePath = dirPath + os.sep + cls.__STATUS_FILE_NAME
	if not os.path.exists(filePath):
	    raise ValueError('%s does not exist' % filePath)
	elif not os.access(filePath, os.R_OK):
	    raise ValueError('%s is not readable' % filePath)
	else:
	    exclusive_lock(handle)
	    return BuildStatus(filePath)

    def setSuccess(self):
	handle = open(self.filePath, 'w')
	try:
	    exclusive_lock(handle)
	    handle.write(BuildStatus.__STATUS_SUCCESS)
	    handle.write('\n')
	    unlock(handle)
	finally:
	    handle.close()

    def setFailure(self):
	handle = open(self.filePath, 'w')
	try:
	    exclusive_lock(handle)
	    handle.write(BuildStatus.__STATUS_FAILURE)
	    handle.write('\n')
	    unlock(handle)
	finally:
	    handle.close()

    def isSuccess(self):
	status = ''
	handle = open(self.filePath, 'r')
	try:
	    shared_lock(handle)
	    status = handle.readline()
	    unlock(handle)
	finally:
	    handle.close()
	return status.lower() == BuildStatus.__STATUS_SUCCESS

    def isFailure(self):
	status = ''
	handle = open(self.filePath, 'r')
	try:
	    shared_lock(handle)
	    status = handle.readline()
	    unlock(handle)
	finally:
	    handle.close()
	return status.lower() == BuildStatus.__STATUS_FAILURE
