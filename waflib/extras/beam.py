#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2015

'''
This is an extra tool, not bundled with the default waf binary.
To add the Beam plugin to the waf file:
    $ ./waf-light --tools=beam
or, if you have waf >= 1.6.2
    $ ./waf update --files=beam

When using this tool, the wscript will look like:

    def options(opt):
	opt.load('compiler_cxx cxx beam')

    def configure(conf):
	conf.load('compiler_cxx cxx beam')

    def build(bld):
	bld(source='msg.capnp', target='app', features = 'cxx', use='BEAM_SHLIB')
	bld(source='foo.capnp', target='bar', features = 'cxx', use='BEAM_STLIB')

Options available are:
    --beam-binpath : the directory containing the compiler
    --beam-incpath : the directory containing the header files
    --beam-libpath : the directory containing the library files
'''

import os
import sys
import subprocess
import tempfile
import zipfile
from waflib import Utils, Context
from waflib.Configure import conf
from waflib.extras.bootstrap import BootStrap

BOOTSTRAP_URL = 'https://github.com/khklau/beam/archive/%s'
BOOTSTRAP_FILE = 'beam-%s.zip'

def options(optCtx):
    optCtx.add_option('--beam-incpath', type='string',
	    default='', dest='beam_incpath',
	    help='''absolute path to the beam headers
	    e.g. /path/to/beam/include''')
    optCtx.add_option('--beam-libpath', type='string',
	    default='', dest='beam_libpath',
	    help='''absolute path to the beam libraries
	    e.g. /path/to/beam/lib''')

def prepare(prepCtx):
    if not prepCtx.env.dep_directory.contains('beam'):
	return
    product = prepCtx.env.dep_directory.find('beam')
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
    prepCtx.msg('Preparing Beam dependency in', strap.getPath())
    if strap.boot('--prefix=%s' % productPath, 'prepare', 'configure', 'build', 'install'):
	inclPath = os.path.join(strap.getPath(), 'include')
	libPath = os.path.join(strap.getPath(), 'lib')
	if os.path.isdir(inclPath) and os.path.isdir(libPath):
	    prepCtx.msg('Setting Beam option beam_incpath to', inclPath)
	    prepCtx.options.beam_incpath = inclPath
	    prepCtx.msg('Setting Beam option beam_libpath to', libPath)
	    prepCtx.options.beam_libpath = libPath
	else:
	    prepCtx.fatal('Beam preparation failed: %s and %s not found' % (inclPath, libPath))

    else:
	prepCtx.fatal('Beam preparation failed')

@conf
def check_beam(self):
    self.start_msg('Checking Beam headers')
    headerPath = os.path.join(self.env['INCLUDES_BEAM_SHLIB'], 'beam', 'queue', 'unordered_mixed.hpp')
    if not os.access(headerPath, os.R_OK):
	self.fatal('%s is not readable' % headerPath)
    self.end_msg('ok')
    self.start_msg('Checking Beam libraries')
    for lib in self.env['LIB_BEAM_SHLIB']: 
	libPath = os.path.join(self.env['LIBPATH_BEAM_SHLIB'], "lib%s.so" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
    for lib in self.env['STLIB_BEAM_STLIB']: 
	libPath = os.path.join(self.env['STLIBPATH_BEAM_STLIB'], "lib%s.a" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
	self.env['BEAM_STLIB_PATH'].append(libPath)
    self.end_msg('ok')

def configure(confCtx):
    platform = Utils.unversioned_sys_platform()
    if not confCtx.env['CXX']:
	confCtx.fatal('load a c++ compiler first, conf.load("compiler_cxx")')

    if confCtx.options.beam_incpath is not None and confCtx.options.beam_incpath != '':
	incpath = confCtx.options.beam_incpath
    elif platform == 'win32':
	incpath = 'C:\beam\include'
    else:
	incpath = '/usr/local/include'

    if confCtx.options.beam_libpath is not None and confCtx.options.beam_libpath != '':
	libpath = confCtx.options.beam_libpath 
    elif platform == 'win32':
	libpath = 'C:\beam\lib'
    else:
	libpath = '/usr/local/lib'

    confCtx.env['INCLUDES_BEAM_STLIB'] = incpath
    confCtx.env['INCLUDES_BEAM_SHLIB'] = incpath
    confCtx.env['LIBPATH_BEAM_SHLIB'] = libpath
    confCtx.env['STLIBPATH_BEAM_STLIB'] = libpath
    confCtx.env['LIB_BEAM_SHLIB'] = ['beam_internet', 'beam_duplex', 'beam_message']
    confCtx.env['STLIB_BEAM_STLIB'] = ['beam_internet', 'beam_duplex', 'beam_message']
    confCtx.env['BEAM_STLIB_PATH'] = []

    confCtx.check_beam()

