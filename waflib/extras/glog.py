#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2015

'''
This is an extra tool, not bundled with the default waf binary.
To add the GLog tool to the waf file:
    $ ./waf-light --tools=glog
or, if you have waf >= 1.6.2
    $ ./waf update --files=glog

When using this tool, the wscript will look like:

    def options(opt):
	opt.load('compiler_cxx glog')

    def configure(conf):
	conf.load('compiler_cxx glog')

    def build(bld):
	bld(source='main.cpp', target='app', use='GLOG')

Options available are:
    --glog-incpath : the directory containing the header files
    --glog-libpath : the directory containing the library files
'''

import os
import string
import sys
import subprocess
import tempfile
import zipfile
from waflib import Utils, Context
from waflib.Configure import conf
from waflib.extras.bootstrap import BootStrap

BOOTSTRAP_URL = 'https://github.com/khklau/glog_bootstrap/archive/%s'
BOOTSTRAP_FILE = 'glog_bootstrap-%s.zip'

def options(optCtx):
    optCtx.add_option('--glog-incpath', type='string',
	    default='', dest='glog_incpath',
	    help='''absolute path to the glog headers
	    e.g. /path/to/glog/include''')
    optCtx.add_option('--glog-libpath', type='string',
	    default='', dest='glog_libpath',
	    help='''absolute path to the glog libraries
	    e.g. /path/to/glog/lib''')

def prepare(prepCtx):
    if not prepCtx.env.dep_directory.contains('glog'):
	return
    product = prepCtx.env.dep_directory.find('glog')
    if len(product.dep_file_path) > 0:
	productPath = os.path.dirname(product.dep_file_path)
    else:
	productPath = os.path.join(prepCtx.options.dep_base_dir,
		'%s-%s' % (product.getName(), product.getVersion()))
    if product.getVersion().lower() == 'master':
	sourceFile = 'master.zip'
    else:
	sourceFile = BOOTSTRAP_FILE % product.getVersion()
    url = BOOTSTRAP_URL % sourceFile
    prepCtx.msg('Downloading and extracting', url)
    strap = BootStrap.init(productPath, url)
    if strap is None:
	prepCtx.fatal('Could not download and extract %s' % url)
    prepCtx.msg('Preparing GLog dependency in', strap.getPath())
    if strap.boot('prepare', 'configure', 'build'):
	inclPath = os.path.join(strap.getPath(), 'include')
	libPath = os.path.join(strap.getPath(), 'lib')
	if os.path.isdir(inclPath) and os.path.isdir(libPath):
	    prepCtx.msg('Setting GLog option glog_incpath to', inclPath)
	    prepCtx.options.glog_incpath = inclPath
	    prepCtx.msg('Setting GLog option glog_libpath to', libPath)
	    prepCtx.options.glog_libpath = libPath
	else:
	    prepCtx.fatal('GLog preparation failed: %s and %s not found' % (inclPath, libPath))

    else:
	prepCtx.fatal('GLog preparation failed')

@conf
def check_glog(self):
    product = self.env.product
    self.start_msg('Checking GLog headers')
    headerPath = os.path.join(self.env['INCLUDES_GLOG'], 'glog', 'logging.h')
    if not os.access(headerPath, os.R_OK):
	self.fatal('%s is not readable' % headerPath)
    self.end_msg('ok')
    self.start_msg('Checking GLog libraries')
    for lib in self.env['LIB_GLOG']: 
	libPath = os.path.join(self.env['LIBPATH_GLOG'], "lib%s.so" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
    self.end_msg('ok')

def configure(confCtx):
    platform = Utils.unversioned_sys_platform()
    if not confCtx.env['CXX']:
	confCtx.fatal('load a c++ compiler first, conf.load("compiler_cxx")')

    if confCtx.options.glog_incpath is not None and confCtx.options.glog_incpath != '':
	incpath = confCtx.options.glog_incpath
    elif platform == 'win32':
	incpath = 'C:\glog\include'
    else:
	incpath = '/usr/local/include'

    if confCtx.options.glog_libpath is not None and confCtx.options.glog_libpath != '':
	libpath = confCtx.options.glog_libpath 
    elif platform == 'win32':
	libpath = 'C:\glog\lib'
    else:
	libpath = '/usr/local/lib'

    confCtx.env['INCLUDES_GLOG'] = incpath
    confCtx.env['LIBPATH_GLOG'] = libpath
    confCtx.env['LIB_GLOG'] = ['glog']
    if platform == 'linux2':
	if os.uname()[4] == 'x86_64':
	    confCtx.env['LIB_GLOG'].append('libunwind-x86_64')
	else:
	    confCtx.env['LIB_GLOG'].append('libunwind')

    confCtx.check_glog()
