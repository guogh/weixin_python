#!/usr/bin/python

import time

print ("time.time(): %f " %  time.time())
print (time.localtime( time.time() ))
print (time.asctime( time.localtime(time.time()) ))
print ("int time.time(): %d " %  int(time.time()*1000))