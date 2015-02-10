#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2014

'''
This is an extra tool, not bundled with the default waf binary.
To add the Dependency Resolver tool to the waf file:
    $ ./waf-light --tools=dep_resolver
or, if you have waf >= 1.6.2
    $ ./waf update --files=dep_resolver

When using this tool, the wscript will look like:

    import waflib.extras.dep_resolver

    def options(opt):
	opt.load('cxx_env dep_resolver')

    def prepare(ctx):
	dep_resolver.prepare()

    def configure(conf):
	conf.load('cxx_env dep_resolver')
	conf.recurse('src')

Options available are:
    --dep-base-dir : the base directory that will contain the build dependencies
'''

import os
import json
import pprint
from waflib.extras.layout import Solution
from waflib.extras.envconf import process

class Product:

    __slots__ = ("dep_list")

    def __init__(self, name, version, dep_list):
	self.name = name
	self.version = version
	self.dep_list = dep_list

    def getName(self):
	return self.name

    def getVersion(self):
	return self.version

def parse_hook(dictionary):
    if 'dependencies' in dictionary:
	return Product(dictionary['product'].encode('ascii', 'ignore'),
		dictionary['version'].encode('ascii', 'ignore'),
		dictionary['dependencies'])
    else:
	return Product(dictionary['product'].encode('ascii', 'ignore'),
		dictionary['version'].encode('ascii', 'ignore'),
		[])

def parse(ctx, filenode):
    if filenode is None or not os.path.exists(filenode.abspath()):
	ctx.fatal('dependency.json not found')
    handle = open(filenode.abspath(), 'r')
    contents = ''
    try:
	for line in handle:
	    contents += line
    finally:
	handle.close()
    return json.loads(contents, encoding='ascii', object_hook=parse_hook)

def getJsonNode(ctx):
    return ctx.path.find_node('dependency.json')

def options(optCtx):
    optCtx.add_option('--dep-base-dir', type='string',
	    default='%s' % optCtx.path.abspath(), dest='dep_base_dir',
	    help='absolute path to the directory that will contain the build dependencies e.g. /path/to/deps')
    for dep in parse(optCtx, getJsonNode(optCtx)).dep_list:
	optCtx.load(dep.getName())

def prepare(prepCtx):
    prepCtx.msg('Preparing dependencies specified in', getJsonNode(prepCtx).abspath())
    for dep in parse(prepCtx, getJsonNode(prepCtx)).dep_list:
	prepCtx.load(dep.getName())

def configure(confCtx):
    for dep in parse(confCtx, getJsonNode(confCtx)).dep_list:
	confCtx.load(dep.getName())
