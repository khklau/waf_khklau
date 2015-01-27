#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2014

'''
This is an extra tool, not bundled with the default waf binary.
To add the Cxx Environment tool to the waf file:
    $ ./waf-light --tools=cxx_env
or, if you have waf >= 1.6.2
    $ ./waf update --files=cxx_env

When using this tool, the wscript will look like:

    def options(opt):
	opt.load('cxx_env')

    def configure(conf):
	conf.load('cxx_env')

    def build(bld):
	bld(source='main.cpp', target='app')

Options available are:
    --mode : the build mode
    --platform : the target build platform
    --env-conf-dir : the directory containing the build environment configuration
    --deps-base-dir : the base directory that will contain the build dependencies
'''

from waflib.extras.layout import Solution
from waflib.extras.envconf import process

def options(optCtx):
    optCtx.load('compiler_cxx')
    optCtx.add_option('--env-conf-dir', type='string',
	    default='%s' % optCtx.path.abspath(), dest='env_conf_dir',
	    help='absolute path to the directory containing the build environment configuration e.g. /path/to/myproject/env')
    optCtx.add_option('--dep-base-dir', type='string',
	    default='%s' % optCtx.path.abspath(), dest='dep_base_dir',
	    help='absolute path to the directory that will contain the build dependencies e.g. /path/to/deps')

def configure(confCtx):
    confCtx.load('compiler_cxx')
    confCtx.env.solution = Solution.fromContext(confCtx)
    confCtx.start_msg('Setting env_conf_dir to')
    confCtx.end_msg(confCtx.options.env_conf_dir)
    confCtx.start_msg('Setting dep_base_dir ')
    confCtx.end_msg(confCtx.options.dep_base_dir)
    conf_result_dir = confCtx.root.make_node(confCtx.options.env_conf_dir).find_dir(confCtx.env.CXX_NAME).get_bld()
    if conf_result_dir is None:
	confCtx.fatal('directory not found')
    else:
	conf_result_file = conf_result_dir.find_node('%s.json' % confCtx.env.CXX_NAME)
	if conf_result_file is None:
	    confCtx.fatal('file not found')
	else:
	    process(conf_result_file.abspath(), confCtx)
