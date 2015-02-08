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

class PreparationContext(ConfigurationContext):
    cmd = 'prepare'
    fun = 'prepare'
