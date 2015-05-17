#!/usr/bin/env python
# encoding: utf-8
# Kean H Lau, 2015

'''
This is an extra tool, not bundled with the default waf binary.
To add the Envconf tool to the waf path:
    $ ./waf-light --tools=envconf
or, if you have waf >= 1.6.2
    $ ./waf update --paths=envconf

When using this tool, the wscript will look like:

    from waflib.extras.envconf import process

    def configure(conf):
	process('some_path.json', conf)
'''

import json

class AppendListToEnvVar:

    __slots__ = ('env_var', 'value_list')

    def __init__(self, env_var, value_list):
	self.env_var = env_var
	self.value_list = value_list

    def execute(self, confCtx):
	for value in self.value_list:
	    confCtx.start_msg('Appending to %s' % self.env_var)
	    confCtx.env.append_value(self.env_var, [value.encode('ascii', 'ignore')])
	    confCtx.end_msg(value)

def decode_hook(dictionary):
    if 'append_env_var' in dictionary:
	return AppendListToEnvVar(dictionary['append_env_var']['env_var'], dictionary['append_env_var']['value_list'])
    return dictionary

def decode(path):
    handle = open(path, 'r')
    contents = ''
    try:
	for line in handle:
	    contents += line
    finally:
	handle.close()
    sequence = []
    sequence.extend(json.loads(contents, object_hook=decode_hook))
    return sequence

def process(path, confCtx):
    for instruction in decode(path):
	instruction.execute(confCtx)
