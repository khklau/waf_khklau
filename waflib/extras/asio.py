#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2015

'''
This is an extra tool, not bundled with the default waf binary.
To add the Asio plugin to the waf file:
    $ ./waf-light --tools=asio
or, if you have waf >= 1.6.2
    $ ./waf update --files=asio

When using this tool, the wscript will look like:

    def options(opt):
	opt.load('compiler_cxx cxx asio')

    def configure(conf):
	conf.load('compiler_cxx cxx asio')

    def build(bld):
	bld(source='msg.capnp', target='app', features = 'cxx', use='ASIO_SHLIB')
	bld(source='foo.capnp', target='bar', features = 'cxx', use='ASIO_STLIB')

Options available are:
    --asio-binpath : the directory containing the compiler
    --asio-incpath : the directory containing the header files
    --asio-libpath : the directory containing the library files
'''

import os
import sys
import subprocess
import tempfile
import zipfile
from waflib import Utils, Context
from waflib.Configure import conf
from waflib.extras.bootstrap import BootStrap

BOOTSTRAP_URL = 'https://github.com/khklau/asio_bootstrap/archive/%s'
BOOTSTRAP_FILE = 'asio_bootstrap-%s.zip'

def options(optCtx):
    optCtx.add_option('--asio-incpath', type='string',
	    default='', dest='asio_incpath',
	    help='''absolute path to the asio headers
	    e.g. /path/to/asio/include''')
    optCtx.add_option('--asio-libpath', type='string',
	    default='', dest='asio_libpath',
	    help='''absolute path to the asio libraries
	    e.g. /path/to/asio/lib''')

def prepare(prepCtx):
    if not prepCtx.env.dep_directory.contains('asio'):
	return
    product = prepCtx.env.dep_directory.find('asio')
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
    prepCtx.msg('Preparing Asio dependency in', strap.getPath())
    if strap.boot('prepare', 'configure', 'build'):
	inclPath = os.path.join(strap.getPath(), 'include')
	libPath = os.path.join(strap.getPath(), 'lib')
	if os.path.isdir(inclPath) and os.path.isdir(libPath):
	    prepCtx.msg('Setting Asio option asio_incpath to', inclPath)
	    prepCtx.options.asio_incpath = inclPath
	    prepCtx.msg('Setting Asio option asio_libpath to', libPath)
	    prepCtx.options.asio_libpath = libPath
	else:
	    prepCtx.fatal('Asio preparation failed: %s and %s not found' % (inclPath, libPath))

    else:
	prepCtx.fatal('Asio preparation failed')

@conf
def check_asio(self):
    self.start_msg('Checking Asio headers')
    headerPath = os.path.join(self.env['INCLUDES_ASIO_SHLIB'], 'asio.hpp')
    if not os.access(headerPath, os.R_OK):
	self.fatal('%s is not readable' % headerPath)
    self.end_msg('ok')
    self.start_msg('Checking Asio libraries')
    for lib in self.env['LIB_ASIO_SHLIB']: 
	libPath = os.path.join(self.env['LIBPATH_ASIO_SHLIB'], "lib%s.so" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
    for lib in self.env['STLIB_ASIO_STLIB']: 
	libPath = os.path.join(self.env['STLIBPATH_ASIO_STLIB'], "lib%s.a" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
    self.end_msg('ok')

def configure(confCtx):
    platform = Utils.unversioned_sys_platform()
    if not confCtx.env['CXX']:
	confCtx.fatal('load a c++ compiler first, conf.load("compiler_cxx")')

    if confCtx.options.asio_incpath is not None and confCtx.options.asio_incpath != '':
	incpath = confCtx.options.asio_incpath
    elif platform == 'win32':
	incpath = 'C:\asio\include'
    else:
	incpath = '/usr/local/include'

    if confCtx.options.asio_libpath is not None and confCtx.options.asio_libpath != '':
	libpath = confCtx.options.asio_libpath 
    elif platform == 'win32':
	libpath = 'C:\asio\lib'
    else:
	libpath = '/usr/local/lib'

    confCtx.env['INCLUDES_ASIO_STLIB'] = incpath
    confCtx.env['INCLUDES_ASIO_SHLIB'] = incpath
    confCtx.env['LIBPATH_ASIO_SHLIB'] = libpath
    confCtx.env['STLIBPATH_ASIO_STLIB'] = libpath
    confCtx.env['LIB_ASIO_SHLIB'] = ['asio']
    confCtx.env['STLIB_ASIO_STLIB'] = ['asio']

    confCtx.check_asio()

