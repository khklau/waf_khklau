#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2014

'''
This is an extra tool, not bundled with the default waf binary.
To add the Gmock tool to the waf file:
    $ ./waf-light --tools=gmock
or, if you have waf >= 1.6.2
    $ ./waf update --files=gmock

When using this tool, the wscript will look like:

    def options(opt):
	opt.load('compiler_cxx gmock')

    def configure(conf):
	conf.load('compiler_cxx gmock')

    def build(bld):
	bld(source='main.cpp', target='app', use='GMOCK')

Options available are:
    --gmock-incpath : the directory containing the header files
    --gmock-libpath : the directory containing the library files
'''

import os
import sys
import subprocess
import tempfile
import zipfile
from waflib import Utils, Context
from waflib.Configure import conf
from waflib.extras.bootstrap import BootStrap

BOOTSTRAP_URL = 'https://github.com/khklau/gmock_bootstrap/archive/%s'
BOOTSTRAP_FILE = 'gmock_bootstrap-%s.zip'

def options(optCtx):
    optCtx.add_option('--gmock-binpath', type='string',
	    default='', dest='gmock_binpath',
	    help='''absolute path to the gmock scripts
	    e.g. /path/to/gmock/bin''')
    optCtx.add_option('--gmock-incpath', type='string',
	    default='', dest='gmock_incpath',
	    help='''absolute path to the gmock headers
	    e.g. /path/to/gmock/include''')
    optCtx.add_option('--gmock-libpath', type='string',
	    default='', dest='gmock_libpath',
	    help='''absolute path to the gmock libraries
	    e.g. /path/to/gmock/lib''')

def prepare(prepCtx):
    if not prepCtx.env.dep_directory.contains('gmock'):
	return
    product = prepCtx.env.dep_directory.find('gmock')
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
    prepCtx.msg('Preparing Google Mock dependency in', strap.getPath())
    if strap.boot('prepare', 'configure', 'build'):
	binPath = os.path.join(strap.getPath(), 'bin')
	inclPath = os.path.join(strap.getPath(), 'include')
	libPath = os.path.join(strap.getPath(), 'lib')
	if os.path.isdir(binPath) and os.path.isdir(inclPath) and os.path.isdir(libPath):
	    prepCtx.msg('Setting Google Mock option gmock_binpath to', binPath)
	    prepCtx.options.gmock_binpath = binPath
	    prepCtx.msg('Setting Google Mock option gmock_incpath to', inclPath)
	    prepCtx.options.gmock_incpath = inclPath
	    prepCtx.msg('Setting Google Mock option gmock_libpath to', libPath)
	    prepCtx.options.gmock_libpath = libPath
	else:
	    prepCtx.fatal('Google Mock preparation failed: %s, %s and %s not found' % (binPath, inclPath, libPath))
    else:
	prepCtx.fatal('Google Mock preparation failed')

@conf
def check_gmock(self):
    self.start_msg('Checking Gmock headers')
    headerPath = os.path.join(self.env['INCLUDES_GMOCK'], 'gmock', 'gmock.h')
    if not os.access(headerPath, os.R_OK):
	self.fatal('%s is not readable' % headerPath)
    self.end_msg('ok')
    self.start_msg('Checking Gmock libraries')
    for lib in self.env['STLIB_GMOCK']: 
	libPath = os.path.join(self.env['STLIBPATH_GMOCK'], "lib%s.a" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
    self.end_msg('ok')

def configure(confCtx):
    platform = Utils.unversioned_sys_platform()
    if not confCtx.env['CXX']:
	confCtx.fatal('load a c++ compiler first, conf.load("compiler_cxx")')

    if confCtx.options.gmock_incpath is not None and confCtx.options.gmock_incpath != '':
	incpath = confCtx.options.gmock_incpath
    elif platform == 'win32':
	incpath = 'C:\gmock\include'
    else:
	incpath = '/usr/local/include'

    if confCtx.options.gmock_libpath is not None and confCtx.options.gmock_libpath != '':
	libpath = confCtx.options.gmock_libpath 
    elif platform == 'win32':
	libpath = 'C:\gmock\lib'
    else:
	libpath = '/usr/local/lib'

    confCtx.env['INCLUDES_GMOCK'] = incpath
    confCtx.env['STLIBPATH_GMOCK'] = libpath
    confCtx.env['STLIB_GMOCK'] = ['gmock', 'gmock_main']

    confCtx.check_gmock()
