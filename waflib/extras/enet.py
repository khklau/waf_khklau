#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2015

'''
This is an extra tool, not bundled with the default waf binary.
To add the Enet plugin to the waf file:
    $ ./waf-light --tools=enet
or, if you have waf >= 1.6.2
    $ ./waf update --files=enet

When using this tool, the wscript will look like:

    def options(opt):
	opt.load('compiler_cxx cxx enet')

    def configure(conf):
	conf.load('compiler_cxx cxx enet')

    def build(bld):
	bld(source='msg.capnp', target='app', features = 'cxx', use='ENET_SHLIB')
	bld(source='foo.capnp', target='bar', features = 'cxx', use='ENET_STLIB')

Options available are:
    --enet-binpath : the directory containing the compiler
    --enet-incpath : the directory containing the header files
    --enet-libpath : the directory containing the library files
'''

import os
import sys
import subprocess
import tempfile
import zipfile
from waflib import Utils, Context
from waflib.Configure import conf
from waflib.extras.bootstrap import BootStrap

BOOTSTRAP_URL = 'https://github.com/khklau/enet_bootstrap/archive/%s'
BOOTSTRAP_FILE = 'enet_bootstrap-%s.zip'

def options(optCtx):
    optCtx.add_option('--enet-incpath', type='string',
	    default='', dest='enet_incpath',
	    help='''absolute path to the enet headers
	    e.g. /path/to/enet/include''')
    optCtx.add_option('--enet-libpath', type='string',
	    default='', dest='enet_libpath',
	    help='''absolute path to the enet libraries
	    e.g. /path/to/enet/lib''')

def prepare(prepCtx):
    if not prepCtx.env.dep_directory.contains('enet'):
	return
    product = prepCtx.env.dep_directory.find('enet')
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
    prepCtx.msg('Preparing Enet dependency in', strap.getPath())
    if strap.boot('prepare', 'configure', 'build'):
	inclPath = os.path.join(strap.getPath(), 'include')
	libPath = os.path.join(strap.getPath(), 'lib')
	if os.path.isdir(inclPath) and os.path.isdir(libPath):
	    prepCtx.msg('Setting Enet option enet_incpath to', inclPath)
	    prepCtx.options.enet_incpath = inclPath
	    prepCtx.msg('Setting Enet option enet_libpath to', libPath)
	    prepCtx.options.enet_libpath = libPath
	else:
	    prepCtx.fatal('Enet preparation failed: %s and %s not found' % (inclPath, libPath))

    else:
	prepCtx.fatal('Enet preparation failed')

@conf
def check_enet(self):
    self.start_msg('Checking Enet headers')
    headerPath = os.path.join(self.env['INCLUDES_ENET_SHLIB'], 'enet', 'enet.h')
    if not os.access(headerPath, os.R_OK):
	self.fatal('%s is not readable' % headerPath)
    self.end_msg('ok')
    self.start_msg('Checking Enet libraries')
    for lib in self.env['LIB_ENET_SHLIB']: 
	libPath = os.path.join(self.env['LIBPATH_ENET_SHLIB'], "lib%s.so" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
    for lib in self.env['STLIB_ENET_STLIB']: 
	libPath = os.path.join(self.env['STLIBPATH_ENET_STLIB'], "lib%s.a" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
	self.env['ENET_STLIB_PATH'].append(libPath)
    self.end_msg('ok')

def configure(confCtx):
    platform = Utils.unversioned_sys_platform()
    if not confCtx.env['CXX']:
	confCtx.fatal('load a c++ compiler first, conf.load("compiler_cxx")')

    if confCtx.options.enet_incpath is not None and confCtx.options.enet_incpath != '':
	incpath = confCtx.options.enet_incpath
    elif platform == 'win32':
	incpath = 'C:\enet\include'
    else:
	incpath = '/usr/local/include'

    if confCtx.options.enet_libpath is not None and confCtx.options.enet_libpath != '':
	libpath = confCtx.options.enet_libpath 
    elif platform == 'win32':
	libpath = 'C:\enet\lib'
    else:
	libpath = '/usr/local/lib'

    confCtx.env['INCLUDES_ENET_STLIB'] = incpath
    confCtx.env['INCLUDES_ENET_SHLIB'] = incpath
    confCtx.env['LIBPATH_ENET_SHLIB'] = libpath
    confCtx.env['STLIBPATH_ENET_STLIB'] = libpath
    confCtx.env['LIB_ENET_SHLIB'] = ['enet']
    confCtx.env['STLIB_ENET_STLIB'] = ['enet']
    confCtx.env['ENET_STLIB_PATH'] = []

    confCtx.check_enet()

