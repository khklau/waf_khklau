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

    from waflib.extras.cpuinfo import find_dcache_line_size, find_pointer_size

    def configure(conf):
	conf.env.append_value('CXXFLAGS', ['-DDCACHE_LINESIZE=%s' % find_dcache_line_size()])
	conf.env.append_value('CXXFLAGS', ['-m%s' % find_pointer_size()])
'''

import sys
from subprocess import Popen, PIPE

def find_dcache_line_size():
    result = None
    if sys.platform == 'linux2':
	result = Popen('getconf LEVEL1_DCACHE_LINESIZE', shell=True, stdout=PIPE).stdout.readline().strip()
    if result is not None and result == '':
	result = None
    return result

def find_pointer_size():
    result = None
    if sys.platform == 'linux2':
	result = Popen('getconf LONG_BIT', shell=True, stdout=PIPE).stdout.readline().strip()
    if result is not None and result == '':
	result = None
    return result

def find_cpu_isa():
    result = None
    if sys.platform == 'linux2':
	result = Popen('uname -p', shell=True, stdout=PIPE).stdout.readline().strip()
    if result is not None and result == '':
	result = None
    return result
