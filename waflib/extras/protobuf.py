#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2014

'''
This is an extra tool, not bundled with the default waf binary.
To add the Protocol Buffer tool to the waf file:
    $ ./waf-light --tools=protobuf
or, if you have waf >= 1.6.2
    $ ./waf update --files=protobuf

When using this tool, the wscript will look like:

    def options(opt):
	opt.load('compiler_cxx cxx protobuf')

    def configure(conf):
	conf.load('compiler_cxx cxx protobuf')

    def build(bld):
	bld(source='msg.proto', target='app', features = 'cxx', use='PROTOBUF')

Options available are:
    --protobuf-binpath : the directory containing the compiler
    --protobuf-incpath : the directory containing the header files
    --protobuf-libpath : the directory containing the library files
'''

import os
import sys
import subprocess
import tempfile
import urllib
import zipfile
from waflib import Utils, Context
from waflib.Configure import conf

BOOTSTRAP_URL = 'https://github.com/khklau/protobuf_bootstrap/archive/%s'
BOOTSTRAP_FILE = 'protobuf_bootstrap-%s.zip'

def define_task_gen(context, **keywords):
    context(name=keywords['name'],
	    rule='${PROTOC} --cpp_out=%s ${PROTOC_FLAGS} -I%s ${SRC[0].abspath()}' % (
                        context.path.get_bld().abspath(),
                        context.path.get_src().abspath()),
	    source=keywords['source'],
	    target=keywords['target'],
	    includes=keywords['includes'])

def options(optCtx):
    optCtx.add_option('--protobuf-binpath', type='string',
	    default='', dest='protobuf_binpath',
	    help='''absolute path to the protobuf compiler
	    e.g. /path/to/protobuf/bin''')
    optCtx.add_option('--protobuf-incpath', type='string',
	    default='', dest='protobuf_incpath',
	    help='''absolute path to the protobuf headers
	    e.g. /path/to/protobuf/include''')
    optCtx.add_option('--protobuf-libpath', type='string',
	    default='', dest='protobuf_libpath',
	    help='''absolute path to the protobuf libraries
	    e.g. /path/to/protobuf/lib''')

def prepare(prepCtx):
    if not prepCtx.env.dep_directory.contains('protobuf'):
	return
    productPath = ''
    product = prepCtx.env.dep_directory.find('protobuf')
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
	tempDir = tempfile.mkdtemp(prefix='protobuf_prepare-')
	try:
	    if product.getVersion().lower() == 'master':
		sourceFile = 'master.zip'
	    else:
		sourceFile = BOOTSTRAP_FILE % product.getVersion()
	    url = BOOTSTRAP_URL % sourceFile
	    filePath = os.path.join(tempDir, sourceFile)
	    prepCtx.start_msg('Downloading %s' % url)
	    triesRemaining = 10
	    while triesRemaining > 1:
		try:
		    urllib.urlretrieve(url, filePath)
		    break
		except urllib.ContentTooShortError:
		    triesRemaining -= 1
		if os.path.exists(filePath):
		    os.remove(filePath)
		else:
		    prepCtx.fatal('Could not download %s' % url)
	    handle = zipfile.Zipfile(filePath, 'r')
	    handle.extractall(productPath)
	finally:
	    shutil.rmtree(tempDir)
    wafExe = os.path.abspath(sys.argv[0])
    cwd = os.getcwd()
    try:
	os.chdir(productPath)
	prepCtx.msg('Preparing Protocol Buffers dependency in', productPath)
	returnCode = subprocess.call([
		wafExe,
		'prepare',
		'configure',
		'build'])
	if returnCode != 0:
	    prepCtx.fatal('Protocol Buffers preparation failed: %d' % returnCode)
	else:
	    binPath = os.path.join(productPath, 'bin')
	    inclPath = os.path.join(productPath, 'include')
	    libPath = os.path.join(productPath, 'lib')
	    if os.path.isdir(binPath) and os.path.isdir(inclPath) and os.path.isdir(libPath):
		prepCtx.msg('Setting Protocol Buffers option protobuf_binpath to', binPath)
		prepCtx.options.protobuf_binpath = binPath
		prepCtx.msg('Setting Protocol Buffers option protobuf_incpath to', inclPath)
		prepCtx.options.protobuf_incpath = inclPath
		prepCtx.msg('Setting Protocol Buffers option protobuf_libpath to', libPath)
		prepCtx.options.protobuf_libpath = libPath
	    else:
		prepCtx.fatal('Protocol Buffers preparation failed: %s and %s not found' % (inclPath, libPath))
    finally:
	os.chdir(cwd)

@conf
def check_protobuf(self):
    self.start_msg('Checking Protocol Buffer compiler')
    if not os.access(self.env['PROTOC'], os.X_OK):
	self.fatal('%s is not executable' % self.env['PROTOC'])
    self.end_msg('ok')
    self.start_msg('Checking Protocol Buffer headers')
    headerPath = os.path.join(self.env['INCLUDES_PROTOBUF'], 'google', 'protobuf', 'message.h')
    if not os.access(headerPath, os.R_OK):
	self.fatal('%s is not readable' % headerPath)
    self.end_msg('ok')
    self.start_msg('Checking Protocol Buffer libraries')
    for lib in self.env['LIB_PROTOBUF']: 
	libPath = os.path.join(self.env['LIBPATH_PROTOBUF'], "lib%s.so" % lib)
	if not os.access(libPath, os.R_OK):
	    self.fatal('%s is not readable' % libPath)
    self.end_msg('ok')

def configure(confCtx):
    platform = Utils.unversioned_sys_platform()
    if not confCtx.env['CXX']:
	confCtx.fatal('load a c++ compiler first, conf.load("compiler_cxx")')

    if confCtx.options.protobuf_binpath is not None and confCtx.options.protobuf_binpath != '':
	binpath = confCtx.options.protobuf_binpath
    elif platform == 'win32':
	binpath = 'C:\protobuf\bin'
    else:
	binpath = '/usr/local/bin'

    if platform == 'win32':
	protocpath = os.path.join(binpath, 'protoc.exe')
    else:
	protocpath = os.path.join(binpath, 'protoc')

    if confCtx.options.protobuf_incpath is not None and confCtx.options.protobuf_incpath != '':
	incpath = confCtx.options.protobuf_incpath
    elif platform == 'win32':
	incpath = 'C:\protobuf\include'
    else:
	incpath = '/usr/local/include'

    if confCtx.options.protobuf_libpath is not None and confCtx.options.protobuf_libpath != '':
	libpath = confCtx.options.protobuf_libpath 
    elif platform == 'win32':
	libpath = 'C:\protobuf\lib'
    else:
	libpath = '/usr/local/lib'

    confCtx.env['PROTOC'] = protocpath
    confCtx.env['INCLUDES_PROTOBUF'] = incpath
    confCtx.env['LIBPATH_PROTOBUF'] = libpath
    confCtx.env['LIB_PROTOBUF'] = ['protobuf']
    confCtx.env['PROTOC_ST'] = '-I%s'

    confCtx.check_protobuf()

