#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2014

'''
This is an extra tool, not bundled with the default waf binary.
To add the Zeromq tool to the waf file:
    $ ./waf-light --tools=zeromq
or, if you have waf >= 1.6.2
    $ ./waf update --files=zeromq

When using this tool, the wscript will look like:

    def options(opt):
	opt.load('compiler_cxx zeromq')

    def configure(conf):
	conf.load('compiler_cxx zeromq')

    def build(bld):
	bld(source='main.cpp', target='app', use='ZEROMQ')

Options available are:
    --zeromq-incpath : the directory containing the header files
    --zeromq-libpath : the directory containing the library files
'''

import os
import sys
import subprocess
import tempfile
import zipfile
from waflib import Utils, Context
from waflib.Configure import conf
from waflib.extras.bootstrap import BootStrap

BOOTSTRAP_URL = 'https://github.com/khklau/zero_bootstrap/archive/%s'
BOOTSTRAP_FILE = 'zeromq_bootstrap-%s.zip'

def options(optCtx):
    optCtx.add_option('--zeromq-incpath', type='string',
	    default='', dest='zeromq_incpath',
	    help='''absolute path to the zeromq headers
	    e.g. /path/to/zeromq/include''')
    optCtx.add_option('--zeromq-libpath', type='string',
	    default='', dest='zeromq_libpath',
	    help='''absolute path to the zeromq libraries
	    e.g. /path/to/zeromq/lib''')

def prepare(prepCtx):
    if not prepCtx.env.dep_directory.contains('zeromq'):
	return
    product = prepCtx.env.dep_directory.find('zeromq')
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
    prepCtx.msg('Preparing Zeromq dependency in', strap.getPath())
    if strap.boot('prepare', 'configure', 'build'):
	inclPath = os.path.join(strap.getPath(), 'include')
	libPath = os.path.join(strap.getPath(), 'lib')
	if os.path.isdir(inclPath) and os.path.isdir(libPath):
	    prepCtx.msg('Setting Zeromq option zeromq_incpath to', inclPath)
	    prepCtx.options.zeromq_incpath = inclPath
	    prepCtx.msg('Setting Zeromq option zeromq_libpath to', libPath)
	    prepCtx.options.zeromq_libpath = libPath
	else:
	    prepCtx.fatal('Zeromq preparation failed: %s and %s not found' % (inclPath, libPath))
    else:
	prepCtx.fatal('Zeromq preparation failed')

@conf
def check_zeromq(self):
    self.start_msg('Checking Zeromq headers')
    headerPath = os.path.join(self.env['INCLUDES_ZEROMQ'], 'zmq.hpp')
    if not os.access(headerPath, os.R_OK):
	self.fatal('%s is not readable' % headerPath)
    self.end_msg('ok')
    self.start_msg('Checking Zeromq libraries')
    for lib in self.env['LIB_ZEROMQ']: 
	libPath = os.path.join(self.env['LIBPATH_ZEROMQ'], "lib%s.so" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
    self.end_msg('ok')

def configure(confCtx):
    platform = Utils.unversioned_sys_platform()
    if not confCtx.env['CXX']:
	confCtx.fatal('load a c++ compiler first, conf.load("compiler_cxx")')

    if confCtx.options.zeromq_incpath is not None and confCtx.options.zeromq_incpath != '':
	incpath = confCtx.options.zeromq_incpath
    elif platform == 'win32':
	incpath = 'C:\zeromq\include'
    else:
	incpath = '/usr/local/include'

    if confCtx.options.zeromq_libpath is not None and confCtx.options.zeromq_libpath != '':
	libpath = confCtx.options.zeromq_libpath 
    elif platform == 'win32':
	libpath = 'C:\zeromq\lib'
    else:
	libpath = '/usr/local/lib'

    confCtx.env['INCLUDES_ZEROMQ'] = incpath
    confCtx.env['LIBPATH_ZEROMQ'] = libpath
    confCtx.env['LIB_ZEROMQ'] = ['zmq']

    confCtx.check_zeromq()
