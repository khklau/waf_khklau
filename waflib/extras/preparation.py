#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2015

'''
This is an extra tool, not bundled with the default waf binary.
To add the Preparation tool to the waf file:
    $ ./waf-light --tools=preparation
or, if you have waf >= 1.6.2
    $ ./waf update --files=preparation

When using this tool, the wscript will look like:

    from waflib.extras.preparation import PreparationContext

    def prepare(prepCtx):
	prepCtx.msg('my option = ', prepCtx.options.my)
'''

from waflib.Configure import ConfigurationContext
from waflib import Utils, Options, Context

class PreparationContext(ConfigurationContext):

    cmd = 'prepare'
    fun = 'prepare'

    def __init__(self, **kw):
	super(PreparationContext, self).__init__(**kw)

    def load(self, input, tooldir=None, funs=None, download=False):
	"""
	Load Waf tools, which will be imported whenever a build is started.

	:param input: waf tools to import
	:type input: list of string
	:param tooldir: paths for the imports
	:type tooldir: list of string
	:param funs: functions to execute from the waf tools
	:type funs: list of string
	:param download: whether to download the tool from the waf repository
	:type download: bool
	"""
	# ConfigurationContext.load isn't reusable, so it ends up being nostly duplicated here
	tools = Utils.to_list(input)
	if tooldir: tooldir = Utils.to_list(tooldir)
	for tool in tools:
	    # avoid loading the same tool more than once with the same functions
	    # used by composite projects

	    mag = (tool, id(self.env), funs)
	    if mag in self.tool_cache:
		self.to_log('(tool %s is already loaded, skipping)' % tool)
		continue
	    self.tool_cache.append(mag)

	    module = None
	    try:
		module = Context.load_tool(tool, tooldir)
	    except ImportError as e:
		if Options.options.download:
		    module = download_tool(tool, ctx=self)
		    if not module:
			self.fatal('Could not load the Waf tool %r or download a suitable replacement from the repository (sys.path %r)\n%s' % (tool, sys.path, e))
		else:
		    self.fatal('Could not load the Waf tool %r from %r (try the --download option?):\n%s' % (tool, sys.path, e))
	    except Exception as e:
		self.to_log('imp %r (%r & %r)' % (tool, tooldir, funs))
		self.to_log(Utils.ex_stack())
		raise

	    if funs is not None:
		self.eval_rules(funs)
	    else:
		func = getattr(module, 'prepare', None)
		if func:
		    if type(func) is type(Utils.readf): func(self)
		    else: self.eval_rules(func)

		self.tools.append({'tool':tool, 'tooldir':tooldir, 'funs':funs})
