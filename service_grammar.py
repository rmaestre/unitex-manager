#!/usr/bin/env python2.7-32
# -*- coding: utf-8 -*-
"""
Something here
"""
import cherrypy
import sys
import re
import json
import time
from unitex_manager import UnitexManager

class Form(object):
    """
    Something here
    """
    
    def index(self):
        """
        Something here
        """
        str_aux = """
        <form action="do_process" method="get">
            Text:<textarea name="text"></textarea><br>
            <input type="submit">
        </form>
        """
        return str_aux
    index.exposed = True
               
    def do_process(self , text):
        """
        Something here
        """
        time_start = time.time()
        # Encode input text
        text = text.encode('utf-8')
        # Set response
        response = {}
        response['text'] = text
        # Process grammar
        unitexManager = UnitexManager()
        # Get tokens
        tokens_result = unitexManager.tokenizer(text, "es")
        print 'TOKENS: %s' % tokens_result
        # Apply POSTtagging
        pos_tagging = unitexManager.postagger(tokens_result, "es")
        print 'POSTTAGG: %s' % pos_tagging
        # Apply Grammar
        grammar = unitexManager.grammar(tokens_result, pos_tagging, "es")   
        
        print "OUTPUT (%s)" % grammar
        response['postgrammar'] = grammar          
        # Time debug info
        response['time'] = (time.time() - time_start)    
        
        # Return response
        return json.dumps(response)
    do_process.exposed = True
        

def main(argv):
    """
    Something here
    """
    conf = {
            'global': {
                'server.socket_host': '0.0.0.0',
                'server.socket_port': 9906,
                'server.thread_pool': 100,
                'tools.encode.on': True,
                'tools.encode.encoding':'utf8'
                }
            }
    cherrypy.config.update(conf)
    cherrypy.quickstart(Form())


if __name__ == '__main__':
    main(sys.argv[1:])
