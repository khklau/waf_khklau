#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2017

'''
This is an extra tool, not bundled with the default waf binary.
To add the SnapBox2D plugin to the waf file:
    $ ./waf-light --tools=snapbox2D
or, if you have waf >= 1.6.2
    $ ./waf update --files=snapbox2D

When using this tool, the wscript will look like:

    def options(opt):
	opt.load('compiler_cxx cxx snapbox2D')

    def configure(conf):
	conf.load('compiler_cxx cxx snapbox2D')

    def build(bld):
	bld(source='sim.cxx', target='sim', features = 'cxx', use='SNAPBOX2D_SHLIB')
	bld(source='sim.cxx', target='sim', features = 'cxx', use='SNAPBOX2D_STLIB')

Options available are:
    --snapbox2D-binpath : the directory containing the compiler
    --snapbox2D-incpath : the directory containing the header files
    --snapbox2D-libpath : the directory containing the library files
'''

import os
import sys
import subprocess
import tempfile
import zipfile
from waflib import Utils, Context
from waflib.Configure import conf
from waflib.extras.bootstrap import BootStrap

BOOTSTRAP_URL = 'https://github.com/khklau/snapbox2D/archive/%s'
BOOTSTRAP_FILE = 'snapbox2D-%s.zip'

def options(optCtx):
    optCtx.add_option('--snapbox2D-incpath', type='string',
	    default='', dest='snapbox2D_incpath',
	    help='''absolute path to the snapbox2D headers
	    e.g. /path/to/snapbox2D/include''')
    optCtx.add_option('--snapbox2D-libpath', type='string',
	    default='', dest='snapbox2D_libpath',
	    help='''absolute path to the snapbox2D libraries
	    e.g. /path/to/snapbox2D/lib''')

def prepare(prepCtx):
    if not prepCtx.env.dep_directory.contains('snapbox2D'):
	return
    product = prepCtx.env.dep_directory.find('snapbox2D')
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
    prepCtx.msg('Preparing SnapBox2D dependency in', strap.getPath())
    if strap.boot('--prefix=%s' % productPath, 'prepare', 'configure', 'build', 'install'):
	inclPath = os.path.join(strap.getPath(), 'include')
	libPath = os.path.join(strap.getPath(), 'lib')
	if os.path.isdir(inclPath) and os.path.isdir(libPath):
	    prepCtx.msg('Setting SnapBox2D option snapbox2D_incpath to', inclPath)
	    prepCtx.options.snapbox2D_incpath = inclPath
	    prepCtx.msg('Setting SnapBox2D option snapbox2D_libpath to', libPath)
	    prepCtx.options.snapbox2D_libpath = libPath
	else:
	    prepCtx.fatal('SnapBox2D preparation failed: %s and %s not found' % (inclPath, libPath))

    else:
	prepCtx.fatal('SnapBox2D preparation failed')

@conf
def check_snapbox2D(self):
    self.start_msg('Checking SnapBox2D headers')
    headerPath = os.path.join(self.env['INCLUDES_SNAPBOX2D_SHLIB'], 'SnapBox2D', 'snapshot.hpp')
    if not os.access(headerPath, os.R_OK):
	self.fatal('%s is not readable' % headerPath)
    self.end_msg('ok')
    self.start_msg('Checking SnapBox2D libraries')
    for lib in self.env['LIB_SNAPBOX2D_SHLIB']: 
	libPath = os.path.join(self.env['LIBPATH_SNAPBOX2D_SHLIB'], "lib%s.so" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
    for lib in self.env['STLIB_SNAPBOX2D_STLIB']: 
	libPath = os.path.join(self.env['STLIBPATH_SNAPBOX2D_STLIB'], "lib%s.a" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
	self.env['SNAPBOX2D_STLIB_PATH'].append(libPath)
    self.end_msg('ok')

def configure(confCtx):
    platform = Utils.unversioned_sys_platform()
    if not confCtx.env['CXX']:
	confCtx.fatal('load a c++ compiler first, conf.load("compiler_cxx")')

    if confCtx.options.snapbox2D_incpath is not None and confCtx.options.snapbox2D_incpath != '':
	incpath = confCtx.options.snapbox2D_incpath
    elif platform == 'win32':
	incpath = 'C:\snapbox2D\include'
    else:
	incpath = '/usr/local/include'

    if confCtx.options.snapbox2D_libpath is not None and confCtx.options.snapbox2D_libpath != '':
	libpath = confCtx.options.snapbox2D_libpath 
    elif platform == 'win32':
	libpath = 'C:\snapbox2D\lib'
    else:
	libpath = '/usr/local/lib'

    confCtx.env['INCLUDES_SNAPBOX2D_STLIB'] = incpath
    confCtx.env['INCLUDES_SNAPBOX2D_SHLIB'] = incpath
    confCtx.env['LIBPATH_SNAPBOX2D_SHLIB'] = libpath
    confCtx.env['STLIBPATH_SNAPBOX2D_STLIB'] = libpath
    confCtx.env['LIB_SNAPBOX2D_SHLIB'] = ['SnapBox2D']
    confCtx.env['STLIB_SNAPBOX2D_STLIB'] = ['SnapBox2D']
    confCtx.env['SNAPBOX2D_STLIB_PATH'] = []

    confCtx.check_snapbox2D()

