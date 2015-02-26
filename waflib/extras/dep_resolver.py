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
import waflib.Context
from waflib.extras.layout import Solution
from waflib.extras.envconf import process

class Product:

    __slots__ = ("dep_file_path", "dep_list")

    def __init__(self, name, version, dep_file_path, dep_list):
	self.name = name
	self.version = version
	self.dep_file_path = dep_file_path
	self.dep_list = dep_list

    def __repr__(self):
	return "__import__('waflib').extras.dep_resolver.%s(%s, %s, %s, %s)" % (
		self.__class__.__name__,
		self.name.__repr__(),
		self.version.__repr__(),
		self.dep_file_path.__repr__(),
		self.dep_list.__repr__())

    def getName(self):
	return self.name

    def getVersion(self):
	return self.version

class Directory:

    def __init__(self, root, directory = {}):
	self.root = root
	self.directory = directory

    def __repr__(self):
	return "__import__('waflib').extras.dep_resolver.%s(%s, %s)" % (
		self.__class__.__name__,
		self.root.__repr__(),
		self.directory.__repr__())

    def getRoot(self):
	return self.root

    def add(self, product):
	self.directory[product.getName()] = product

    def contains(self, name):
	return name in self.directory

    def find(self, name):
	return self.directory[name]

    @classmethod
    def __assemble(cls, context, directory, productList):
	if len(productList) == 0:
	    return directory
	else:
	    product = productList[0]
	    if directory.contains(product.getName()):
		existingVer = directory.find(product.getName()).getVersion()
		if product.getVersion() != existingVer:
		    context.fatal('Version mismatch for %s: %s vs %s' % (
			    product.getName(),
			    product.getVersion(),
			    existingVer))
		    return directory
		else:
		    context.fatal('Cyclic dependency detected for %s' % product.getName())
		    return directory
	    else:
		directory.add(product)
	    productList.pop(0)
	    productList.extend(product.dep_list)
	    return Directory.__assemble(context, directory, productList)

    @classmethod
    def assemble(cls, context, product):
	return Directory.__assemble(context, Directory(product), [] + product.dep_list)

def parse_hook(dictionary):
    if 'dependencies' in dictionary:
	return Product(
		dictionary['product'].encode('ascii', 'ignore'),
		dictionary['version'].encode('ascii', 'ignore'),
		'',
		dictionary['dependencies'])
    else:
	return Product(
		dictionary['product'].encode('ascii', 'ignore'),
		dictionary['version'].encode('ascii', 'ignore'),
		'',
		[])

def parse(ctx, filepath):
    if not os.path.exists(filepath):
	ctx.fatal('%s not found' % filepath)
    handle = open(filepath, 'r')
    contents = ''
    try:
	for line in handle:
	    contents += line
    finally:
	handle.close()
    product = json.loads(contents, encoding='ascii', object_hook=parse_hook)
    product.dep_file_path = filepath
    return product

__JSON_FILENAME = 'dependency.json'

def findDependencyJson(baseDir):
    jsonList = []
    for dirPath, subDirList, fileList in os.walk(baseDir, followlinks=True):
	for file in fileList:
	    if file.lower() == __JSON_FILENAME:
		jsonList.append(os.path.join(dirPath, file))
    return jsonList

def findWhichDepsExistLocally(ctx, directory, baseDir):
    ctx.start_msg('Searching dependency base directory')
    existingProducts = dict()
    for json in findDependencyJson(ctx.options.dep_base_dir):
	product = parse(ctx, json)
	existingProducts[product.getName()] = product
    for dep in directory.getRoot().dep_list:
	if dep.getName() in existingProducts and dep.getVersion() == existingProducts[dep.getName()].getVersion():
	    dep.dep_file_path = existingProducts[dep.getName()].dep_file_path
    ctx.end_msg('ok')

def getThisJsonPath(ctx):
    path = os.path.join(waflib.Context.top_dir, __JSON_FILENAME)
    if os.access(path, os.R_OK):
	return path
    else:
	return __JSON_FILENAME

def options(optCtx):
    optCtx.add_option('--dep-base-dir', type='string',
	    default='%s' % optCtx.path.abspath(), dest='dep_base_dir',
	    help='absolute path to the directory that will contain the build dependencies e.g. /path/to/deps')
    for dep in parse(optCtx, getThisJsonPath(optCtx)).dep_list:
	optCtx.load(dep.getName())

def prepare(prepCtx):
    prepCtx.msg('Preparing dependencies specified in', getThisJsonPath(prepCtx))
    prepCtx.env.dep_directory = Directory.assemble(prepCtx, parse(prepCtx, getThisJsonPath(prepCtx)))
    prepCtx.msg('Specified dependency base directory', prepCtx.options.dep_base_dir)
    findWhichDepsExistLocally(prepCtx, prepCtx.env.dep_directory, prepCtx.options.dep_base_dir)
    for dep in prepCtx.env.dep_directory.getRoot().dep_list:
	prepCtx.load(dep.getName())

def configure(confCtx):
    for dep in parse(confCtx, getThisJsonPath(confCtx)).dep_list:
	confCtx.load(dep.getName())
