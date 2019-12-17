#!/usr/bin/env python
import os
import pdb
import time
import ctypes
import math
    
#
# Class for logging 
#
class Log():
    def __init__(self):
        path = os.path.abspath(os.path.dirname(os.sys.argv[0])) + '/mda.log';
        self.pFile = open(path,"a+");

    def WriteBuffer(self, string):
        buffer = ("[%s]: " %(time.strftime('%Y-%m-%dT%H:%M:%SZ')));
        self.pFile.write(buffer + string);

    def Close(self):
        self.pFile.close();