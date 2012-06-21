# -*- coding: utf-8 -*-
"""
Docstring here

"""
from __future__ import division
import json
import urllib
import urllib2
import time

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

a = time.time()
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
        print content,"\n"
        print aux,"\n"
        c_n_p += 1
    elif r1 < 0 and r2 == 0:
        c_n_ne += 1
    elif r1 < 0 and r2 < 0:
        c_n_n += 1
            
    cont_tot += 1
    content = fd.readline()
    

print "Leyenda:"
print "x_y / donde x=entrenado e y=servicio"
print "p  = positivo"
print "ne = neutro"
print "n  = negativo"

print "p_p: %s" % c_p_p
print "p_ne: %s" % c_p_ne
print "p_n: %s\n" % c_p_n

print "ne_p: %s" % c_ne_p
print "ne_ne: %s" % c_ne_ne
print "ne_n: %s\n" % c_ne_n

print "n_p: %s" % c_n_p
print "n_ne: %s" % c_n_ne
print "n_n: %s\n" % c_n_n


p = (c_p_p / (c_p_p + c_p_n + c_p_ne))
print "P+ = %s " % p
c = (c_p_p / (c_p_p + c_n_p + c_ne_p))
f_pos = (2.0*((p*c)/(p+c)))
print "C+ = %s " % c
print "F+ = %s\n" % f_pos


p = (c_n_n / (c_n_n + c_n_p + c_n_ne))
print "P- = %s " % p
c = (c_n_n / (c_n_n + c_p_n + c_ne_n))
f_neg = (2.0*((p*c)/(p+c)))
print "C- = %s " % c
print "F- = %s\n" % f_neg


p = (c_ne_ne / (c_ne_ne + c_ne_p + c_ne_n))
print "Po = %s" % p
c = (c_ne_ne / (c_ne_ne + c_p_ne + c_n_ne))
f_neu = (2.0*((p*c)/(p+c)))
print "Co = %s " % c
print "Fo = %s " % f_neu

print "\nPrecision total = %s / %s (%s%%)" % (c_p_p + c_ne_ne + c_n_n, cont_tot, ((100*(c_p_p + c_ne_ne + c_n_n))/cont_tot))
print "Medias de F = %s" % ((f_pos+f_neg+f_neu)/3)
print "Tiempo total %s" % (time.time() - a)










