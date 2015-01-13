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
	dcacheline = conf.find_dcache_line_size()
	conf.env.append_value('CXXFLAGS', ['-DDCACHE_LINESIZE=%s' % dcacheline])
'''

import os
from subprocess import Popen, PIPE
from waflib.Configure import conf


@conf
def find_dcache_line_size(self):
    self.start_msg('Detecting CPU dcache line size')
    result = ''
    if os.name == 'posix':
	result = Popen('getconf LEVEL1_DCACHE_LINESIZE', shell=True, stdout=PIPE).stdout.readline().strip()
    if result != '':
	self.end_msg('%s bytes' % result)
    else:
	self.fatal('could not be detected')
    return result
