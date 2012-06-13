# -*- coding: utf-8 -*-
"""
Docstring here

"""
import json
import urllib
import urllib2

def query(text):
    """
    """
    params = urllib.urlencode({'text': '%s' % text}) 
    f = urllib2.urlopen("http://localhost:9906/do_process", 
                                                params)
    f_response = f.read()
    results = json.loads(f_response)
    return results["postgrammar"]
        

fd = open( "corpus.txt" )
content = fd.readline()

# Data for accuracy
c_p_p = 0
c_p_ne = 0
c_p_n = 0

c_ne_p = 0
c_ne_ne = 0
c_ne_n = 0

c_n_p = 0
c_n_ne = 0
c_n_n = 0

cont_tot = 0
while (content != "" ):
    content = content.replace( "\n", "" )
    # trained data
    a1 = content.count("positive")
    b1 = content.count("negative")
    r1 = a1-b1
    # tested data
    aux = query(content)
    a2 = aux.count("POSITIVE")
    b2 = aux.count("NEGATIVE")
    r2 = a2-b2
    
    # compute statistics
    if r1 > 0 and r2 > 0:
        c_p_p += 1
    elif r1 > 0 and r2 == 0:
        c_p_ne += 1
    elif r1 > 0 and r2 < 0:
        c_p_n += 1
        
    elif r1 == 0 and r2 > 0:
        c_ne_p += 1
    elif r1 == 0 and r2 == 0:
        c_ne_ne += 1
    elif r1 == 0 and r2 < 0:
        c_ne_n += 1
        
    elif r1 < 0 and r2 > 0:
        c_n_p += 1
    elif r1 < 0 and r2 == 0:
        c_n_ne += 1
    elif r1 < 0 and r2 < 0:
        c_n_n += 1
            
    cont_tot += 1
    content = fd.readline()
    
print "c_p_p: %s" % c_p_p
print "c_p_ne: %s" % c_p_ne
print "c_p_n: %s\n" % c_p_n

print "c_ne_p: %s" % c_ne_p
print "c_ne_ne: %s" % c_ne_ne
print "c_ne_n: %s\n" % c_ne_n

print "c_n_p: %s" % c_n_p
print "c_n_ne: %s" % c_n_ne
print "c_n_n: %s\n" % c_n_n


print "+[%s] / %s" % (c_p_p + c_ne_ne + c_n_n, cont_tot)