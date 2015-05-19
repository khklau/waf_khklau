#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2015

'''
This is an extra tool, not bundled with the default waf binary.
To add the Capn Proto tool to the waf file:
    $ ./waf-light --tools=capnproto
or, if you have waf >= 1.6.2
    $ ./waf update --files=capnproto

When using this tool, the wscript will look like:

    def options(opt):
	opt.load('compiler_cxx cxx capnproto')

    def configure(conf):
	conf.load('compiler_cxx cxx capnproto')

    def build(bld):
	bld(source='msg.capnp', target='app', features = 'cxx', use='CAPNPROTO')

Options available are:
    --capnproto-binpath : the directory containing the compiler
    --capnproto-incpath : the directory containing the header files
    --capnproto-libpath : the directory containing the library files
'''

import os
import sys
import subprocess
import tempfile
import zipfile
from waflib import Utils, Context
from waflib.Configure import conf
from waflib.extras.bootstrap import BootStrap

BOOTSTRAP_URL = 'https://github.com/khklau/capnproto_bootstrap/archive/%s'
BOOTSTRAP_FILE = 'capnproto_bootstrap-%s.zip'

def define_task_gen(context, **keywords):
    context(name=keywords['name'],
	    rule='${CAPNP} compile --output=c++:%s ${CAPNP_FLAGS} -I%s -I${INCLUDES_CAPNPROTO} --src-prefix=%s ${SRC[0].abspath()}' % (
                        context.path.get_bld().abspath(),
                        context.path.get_src().abspath(),
                        context.path.get_src().abspath()),
	    source=keywords['source'],
	    target=keywords['target'],
	    includes=keywords['includes'])

def options(optCtx):
    optCtx.add_option('--capnproto-binpath', type='string',
	    default='', dest='capnproto_binpath',
	    help='''absolute path to the capnproto compiler
	    e.g. /path/to/capnproto/bin''')
    optCtx.add_option('--capnproto-incpath', type='string',
	    default='', dest='capnproto_incpath',
	    help='''absolute path to the capnproto headers
	    e.g. /path/to/capnproto/include''')
    optCtx.add_option('--capnproto-libpath', type='string',
	    default='', dest='capnproto_libpath',
	    help='''absolute path to the capnproto libraries
	    e.g. /path/to/capnproto/lib''')

def prepare(prepCtx):
    if not prepCtx.env.dep_directory.contains('capnproto'):
	return
    product = prepCtx.env.dep_directory.find('capnproto')
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
    prepCtx.msg('Preparing Capn Proto dependency in', strap.getPath())
    if strap.boot('prepare', 'configure', 'build'):
	binPath = os.path.join(strap.getPath(), 'bin')
	inclPath = os.path.join(strap.getPath(), 'include')
	libPath = os.path.join(strap.getPath(), 'lib')
	if os.path.isdir(binPath) and os.path.isdir(inclPath) and os.path.isdir(libPath):
	    prepCtx.msg('Setting Capn Proto option capnproto_binpath to', binPath)
	    prepCtx.options.capnproto_binpath = binPath
	    prepCtx.msg('Setting Capn Proto option capnproto_incpath to', inclPath)
	    prepCtx.options.capnproto_incpath = inclPath
	    prepCtx.msg('Setting Capn Proto option capnproto_libpath to', libPath)
	    prepCtx.options.capnproto_libpath = libPath
	else:
	    prepCtx.fatal('Capn Proto preparation failed: %s, %s and %s not found' % (binPath, inclPath, libPath))

    else:
	prepCtx.fatal('Capn Proto preparation failed')

@conf
def check_capnproto(self):
    self.start_msg('Checking Capn Proto compiler')
    if not os.access(self.env['CAPNP'], os.X_OK):
	self.fatal('%s is not executable' % self.env['CAPNP'])
    self.end_msg('ok')
    self.start_msg('Checking Capn Proto headers')
    headerPath = os.path.join(self.env['INCLUDES_CAPNPROTO'], 'capnp', 'message.h')
    if not os.access(headerPath, os.R_OK):
	self.fatal('%s is not readable' % headerPath)
    self.end_msg('ok')
    self.start_msg('Checking Capn Proto libraries')
    for lib in self.env['STLIB_CAPNPROTO']: 
	libPath = os.path.join(self.env['LIBPATH_CAPNPROTO'], "lib%s.a" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
    self.end_msg('ok')

def configure(confCtx):
    platform = Utils.unversioned_sys_platform()
    if not confCtx.env['CXX']:
	confCtx.fatal('load a c++ compiler first, conf.load("compiler_cxx")')

    if confCtx.options.capnproto_binpath is not None and confCtx.options.capnproto_binpath != '':
	binpath = confCtx.options.capnproto_binpath
    elif platform == 'win32':
	binpath = 'C:\capnproto\bin'
    else:
	binpath = '/usr/local/bin'

    if platform == 'win32':
	capnppath = os.path.join(binpath, 'capnp.exe')
	pathsep = ';'
    else:
	capnppath = os.path.join(binpath, 'capnp')
	pathsep = ':'

    if confCtx.options.capnproto_incpath is not None and confCtx.options.capnproto_incpath != '':
	incpath = confCtx.options.capnproto_incpath
    elif platform == 'win32':
	incpath = 'C:\capnproto\include'
    else:
	incpath = '/usr/local/include'

    if confCtx.options.capnproto_libpath is not None and confCtx.options.capnproto_libpath != '':
	libpath = confCtx.options.capnproto_libpath 
    elif platform == 'win32':
	libpath = 'C:\capnproto\lib'
    else:
	libpath = '/usr/local/lib'

    os.putenv('PATH', os.getenv('PATH', '') + pathsep + binpath)
    os.environ['PATH'] = os.environ['PATH'] + pathsep + binpath

    confCtx.env['CAPNP'] = capnppath
    confCtx.env['CAPNP_FLAGS'] = '--no-standard-import'
    confCtx.env['INCLUDES_CAPNPROTO'] = incpath
    confCtx.env['LIBPATH_CAPNPROTO'] = libpath
    confCtx.env['STLIB_CAPNPROTO'] = ['capnp', 'kj']
    confCtx.env['CAPNP_ST'] = '-I%s'

    confCtx.check_capnproto()

