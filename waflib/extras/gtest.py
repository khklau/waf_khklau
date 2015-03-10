#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2014

'''
This is an extra tool, not bundled with the default waf binary.
To add the Gtest tool to the waf file:
    $ ./waf-light --tools=gtest
or, if you have waf >= 1.6.2
    $ ./waf update --files=gtest

When using this tool, the wscript will look like:

    def options(opt):
	opt.load('compiler_cxx gtest')

    def configure(conf):
	conf.load('compiler_cxx gtest')

    def build(bld):
	bld(source='main.cpp', target='app', use='GTEST')

Options available are:
    --gtest-binpath : the directory containing the gtest-config script
    --gtest-incpath : the directory containing the header files
    --gtest-libpath : the directory containing the library files
'''

import os
import sys
import subprocess
import tempfile
import zipfile
from waflib import Utils, Context
from waflib.Configure import conf
from waflib.extras.url_utils import extractRemoteZip

BOOTSTRAP_URL = 'https://github.com/khklau/gtest_bootstrap/archive/%s'
BOOTSTRAP_FILE = 'gtest_bootstrap-%s.zip'

def options(optCtx):
    optCtx.add_option('--gtest-binpath', type='string',
	    default='', dest='gtest_binpath',
	    help='''absolute path to the gtest headers
	    e.g. /path/to/gtest/bin''')
    optCtx.add_option('--gtest-incpath', type='string',
	    default='', dest='gtest_incpath',
	    help='''absolute path to the gtest headers
	    e.g. /path/to/gtest/include''')
    optCtx.add_option('--gtest-libpath', type='string',
	    default='', dest='gtest_libpath',
	    help='''absolute path to the gtest libraries
	    e.g. /path/to/gtest/lib''')

def prepare(prepCtx):
    if not prepCtx.env.dep_directory.contains('gtest'):
	return
    productPath = ''
    product = prepCtx.env.dep_directory.find('gtest')
    if len(product.dep_file_path) > 0:
	productPath = os.path.dirname(product.dep_file_path)
    else:
	productPath = os.path.join(prepCtx.options.dep_base_dir,
		'%s-%s' % (product.getName(), product.getVersion()))
    topWscript = os.path.join(productPath, Context.WSCRIPT_FILE)
    if not os.path.exists(topWscript) or not os.access(topWscript, os.R_OK):
	if os.path.isdir(productPath):
	    shutil.rmtree(productPath)
	else:
	    os.remove(productPath)
	os.mkdir(productPath)
	if product.getVersion().lower() == 'master':
	    sourceFile = 'master.zip'
	else:
	    sourceFile = BOOTSTRAP_FILE % product.getVersion()
	url = BOOTSTRAP_URL % sourceFile
	prepCtx.start_msg('Downloading and extracting %s to' % url)
	if extractRemoteZip(url, productPath):
	    prepCtx.end_msg(productPath)
	else:
	    prepCtx.fatal('Could not download and extract %s' % url)
    wafExe = os.path.abspath(sys.argv[0])
    cwd = os.getcwd()
    try:
	os.chdir(productPath)
	prepCtx.msg('Preparing Google Test dependency in', productPath)
	returnCode = subprocess.call([
		wafExe,
		'prepare',
		'configure',
		'build'])
	if returnCode != 0:
	    prepCtx.fatal('Google Test preparation failed: %d' % returnCode)
	else:
	    binPath = os.path.join(productPath, 'bin')
	    inclPath = os.path.join(productPath, 'include')
	    libPath = os.path.join(productPath, 'lib')
	    if os.path.isdir(binPath) and os.path.isdir(inclPath) and os.path.isdir(libPath):
		prepCtx.msg('Setting Google Test option gtest_binpath to', binPath)
		prepCtx.options.gtest_binpath = binPath
		prepCtx.msg('Setting Google Test option gtest_incpath to', inclPath)
		prepCtx.options.gtest_incpath = inclPath
		prepCtx.msg('Setting Google Test option gtest_libpath to', libPath)
		prepCtx.options.gtest_libpath = libPath
	    else:
		prepCtx.fatal('Google Test preparation failed: %s and %s not found' % (inclPath, libPath))
    finally:
	os.chdir(cwd)

@conf
def check_gtest(self):
    self.start_msg('Checking Gtest headers')
    headerPath = os.path.join(self.env['INCLUDES_GTEST'], 'gtest', 'gtest.h')
    if not os.access(headerPath, os.R_OK):
	self.fatal('%s is not readable' % headerPath)
    self.end_msg('ok')
    self.start_msg('Checking Gtest libraries')
    for lib in self.env['STLIB_GTEST']: 
	libPath = os.path.join(self.env['STLIBPATH_GTEST'], "lib%s.a" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
    self.end_msg('ok')

def configure(confCtx):
    platform = Utils.unversioned_sys_platform()
    if not confCtx.env['CXX']:
	confCtx.fatal('load a c++ compiler first, conf.load("compiler_cxx")')

    if confCtx.options.gtest_incpath is not None and confCtx.options.gtest_incpath != '':
	incpath = confCtx.options.gtest_incpath
    elif platform == 'win32':
	incpath = 'C:\gtest\include'
    else:
	incpath = '/usr/local/include'

    if confCtx.options.gtest_libpath is not None and confCtx.options.gtest_libpath != '':
	libpath = confCtx.options.gtest_libpath 
    elif platform == 'win32':
	libpath = 'C:\gtest\lib'
    else:
	libpath = '/usr/local/lib'

    confCtx.env['INCLUDES_GTEST'] = incpath
    confCtx.env['STLIBPATH_GTEST'] = libpath
    confCtx.env['STLIB_GTEST'] = ['gtest', 'gtest_main']

    confCtx.check_gtest()
