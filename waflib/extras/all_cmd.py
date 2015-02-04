#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2015

'''
This is an extra tool, not bundled with the default waf binary.
To add the All Command tool to the waf file:
    $ ./waf-light --tools=all_cmd
or, if you have waf >= 1.6.2
    $ ./waf update --files=all_cmd

When using this tool, the wscript will look like:

    from waflib.extras.all_cmd import AllContext

    def all(allCtx):
	allCtx.msg('my option = ', allCtx.options.my)
'''

from waflib.Configure import ConfigurationContext

class AllContext(ConfigurationContext):
    cmd = 'all'
    fun = 'all'
