#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2015

'''
This is an extra tool, not bundled with the default waf binary.
To add the Turbo plugin to the waf file:
    $ ./waf-light --tools=turbo
or, if you have waf >= 1.6.2
    $ ./waf update --files=turbo

When using this tool, the wscript will look like:

    def options(opt):
	opt.load('compiler_cxx cxx turbo')

    def configure(conf):
	conf.load('compiler_cxx cxx turbo')

    def build(bld):
	bld(source='msg.capnp', target='app', features = 'cxx', use='TURBO_SHLIB')
	bld(source='foo.capnp', target='bar', features = 'cxx', use='TURBO_STLIB')

Options available are:
    --turbo-binpath : the directory containing the compiler
    --turbo-incpath : the directory containing the header files
    --turbo-libpath : the directory containing the library files
'''

import os
import sys
import subprocess
import tempfile
import zipfile
from waflib import Utils, Context
from waflib.Configure import conf
from waflib.extras.bootstrap import BootStrap

BOOTSTRAP_URL = 'https://github.com/khklau/turbo/archive/%s'
BOOTSTRAP_FILE = 'turbo-%s.zip'

def options(optCtx):
    optCtx.add_option('--turbo-incpath', type='string',
	    default='', dest='turbo_incpath',
	    help='''absolute path to the turbo headers
	    e.g. /path/to/turbo/include''')
    optCtx.add_option('--turbo-libpath', type='string',
	    default='', dest='turbo_libpath',
	    help='''absolute path to the turbo libraries
	    e.g. /path/to/turbo/lib''')

def prepare(prepCtx):
    if not prepCtx.env.dep_directory.contains('turbo'):
	return
    product = prepCtx.env.dep_directory.find('turbo')
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
    prepCtx.msg('Preparing Turbo dependency in', strap.getPath())
    if strap.boot('--prefix=%s' % productPath, 'prepare', 'configure', 'build', 'install'):
	inclPath = os.path.join(strap.getPath(), 'include')
	libPath = os.path.join(strap.getPath(), 'lib')
	if os.path.isdir(inclPath) and os.path.isdir(libPath):
	    prepCtx.msg('Setting Turbo option turbo_incpath to', inclPath)
	    prepCtx.options.turbo_incpath = inclPath
	    prepCtx.msg('Setting Turbo option turbo_libpath to', libPath)
	    prepCtx.options.turbo_libpath = libPath
	else:
	    prepCtx.fatal('Turbo preparation failed: %s and %s not found' % (inclPath, libPath))

    else:
	prepCtx.fatal('Turbo preparation failed')

@conf
def check_turbo(self):
    self.start_msg('Checking Turbo headers')
    headerPath = os.path.join(self.env['INCLUDES_TURBO_SHLIB'], 'turbo', 'toolset', 'attribute.hpp')
    if not os.access(headerPath, os.R_OK):
	self.fatal('%s is not readable' % headerPath)
    self.end_msg('ok')
    self.start_msg('Checking Turbo libraries')
    for lib in self.env['LIB_TURBO_SHLIB']: 
	libPath = os.path.join(self.env['LIBPATH_TURBO_SHLIB'], "lib%s.so" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
    for lib in self.env['STLIB_TURBO_STLIB']: 
	libPath = os.path.join(self.env['STLIBPATH_TURBO_STLIB'], "lib%s.a" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
    self.end_msg('ok')

def configure(confCtx):
    platform = Utils.unversioned_sys_platform()
    if not confCtx.env['CXX']:
	confCtx.fatal('load a c++ compiler first, conf.load("compiler_cxx")')

    if confCtx.options.turbo_incpath is not None and confCtx.options.turbo_incpath != '':
	incpath = confCtx.options.turbo_incpath
    elif platform == 'win32':
	incpath = 'C:\turbo\include'
    else:
	incpath = '/usr/local/include'

    if confCtx.options.turbo_libpath is not None and confCtx.options.turbo_libpath != '':
	libpath = confCtx.options.turbo_libpath 
    elif platform == 'win32':
	libpath = 'C:\turbo\lib'
    else:
	libpath = '/usr/local/lib'

    confCtx.env['INCLUDES_TURBO_STLIB'] = incpath
    confCtx.env['INCLUDES_TURBO_SHLIB'] = incpath
    confCtx.env['LIBPATH_TURBO_SHLIB'] = libpath
    confCtx.env['STLIBPATH_TURBO_STLIB'] = libpath
    confCtx.env['LIB_TURBO_SHLIB'] = ['turbo_algorithm', 'turbo_filesystem', 'turbo_ipc', 'turbo_process']
    confCtx.env['STLIB_TURBO_STLIB'] = ['turbo_algorithm', 'turbo_filesystem', 'turbo_ipc', 'turbo_process']

    confCtx.check_turbo()

