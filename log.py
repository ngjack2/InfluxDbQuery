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
        self.pFile = open("mda.log","a+");

    def WriteBuffer(self, string):
        self.pFile.write(string);

    def Close(self):
        self.pFile.close();