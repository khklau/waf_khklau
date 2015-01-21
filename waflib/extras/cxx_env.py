#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2014

'''
This is an extra tool, not bundled with the default waf binary.
To add the Cxx Environment tool to the waf file:
    $ ./waf-light --tools=cxx_env
or, if you have waf >= 1.6.2
    $ ./waf update --files=cxx_env

When using this tool, the wscript will look like:

    def options(opt):
	opt.load('cxx_env')

    def configure(conf):
	conf.load('cxx_env')

    def build(bld):
	bld(source='main.cpp', target='app', use='ZEROMQ')

Options available are:
    --mode : the build mode
    --platform : the target build platform
    --env-conf-dir : the directory containing the build environment configuration
    --deps-base-dir : the base directory that will contain the build dependencies
'''

import sys
import re
import os
from os.path import join
from waflib import Utils, Logs, Errors
from waflib.Configure import conf
from waflib.extras.layout import Solution
from waflib.extras.cpuinfo import find_dcache_line_size, find_pointer_size


def options(optCtx):
    optCtx.load('compiler_cxx')
    optCtx.add_option('--env-conf-dir', type='string',
	    default='%s' % optCtx.path.abspath(), dest='env_conf_dir',
	    help='absolute path to the directory containing the build environment configuration e.g. /path/to/myproject/env')
    optCtx.add_option('--dep-base-dir', type='string',
	    default='%s' % optCtx.path.abspath(), dest='dep_base_dir',
	    help='absolute path to the directory that will contain the build dependencies e.g. /path/to/deps')

@conf
def check_hardware(self):
    self.start_msg('Detecting CPU dcache line size')
    self.env.dcache_line_size = find_dcache_line_size()
    if self.env.dcache_line_size is None:
	self.fatal('could not be detected')
    else:
	self.end_msg('%s bytes' % self.env.dcache_line_size)
    self.start_msg('Detecting native pointer size')
    self.env.pointer_size = find_pointer_size()
    if self.env.pointer_size is None:
	self.fatal('could not be detected')
    else:
	self.end_msg('%s bit' % self.env.pointer_size)

def configure(confCtx):
    confCtx.load('compiler_cxx')
    confCtx.check_hardware()
    confCtx.env.solution = Solution.fromContext(confCtx)
    confCtx.start_msg('Setting env_conf_dir to')
    confCtx.end_msg(confCtx.options.env_conf_dir)
    confCtx.start_msg('Setting dep_base_dir ')
    confCtx.end_msg(confCtx.options.dep_base_dir)
    cxx_conf_dir = confCtx.root.make_node(confCtx.options.env_conf_dir).find_dir('cxx')
    if cxx_conf_dir is not None:
	confCtx.recurse(cxx_conf_dir.abspath())
    else:
	confCtx.fatal('Could not find Cxx environment configuration under %s' % confCtx.options.env_conf_dir)
