#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2015

'''
This is an extra tool, not bundled with the default waf binary.
To add the Cpuinfo tool to the waf file:
    $ ./waf-light --tools=cpuinfo
or, if you have waf >= 1.6.2
    $ ./waf update --files=cpuinfo

When using this tool, the wscript will look like:

    def configure(conf):
	conf.load('compiler_cxx cpuinfo')
	conf.env.append_value('CXXFLAGS', ['-DDCACHE_LINESIZE=%s' % conf.find_dcache_line_size()])
	conf.env.append_value('CXXFLAGS', ['-m%s' % conf.find_pointer_size()])
'''

import sys
from subprocess import Popen, PIPE
from waflib.Configure import conf


@conf
def find_dcache_line_size(self):
    self.start_msg('Detecting CPU dcache line size')
    result = ''
    if sys.platform == 'linux2':
	result = Popen('getconf LEVEL1_DCACHE_LINESIZE', shell=True, stdout=PIPE).stdout.readline().strip()
    if result != '':
	self.end_msg('%s bytes' % result)
    else:
	self.fatal('could not be detected')
    return result

@conf
def find_pointer_size(self):
    self.start_msg('Detecting native pointer size')
    result = ''
    if sys.platform == 'linux2':
	result = Popen('getconf LONG_BIT', shell=True, stdout=PIPE).stdout.readline().strip()
    if result != '':
	self.end_msg('%s bits' % result)
    else:
	self.fatal('could not be detected')
    return result
