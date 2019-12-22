#!/usr/bin/env python
import os
import pdb
import time
import ctypes
import xlwt
import math
import json
import calendar
import main

# format time for one day query
queryEnd = 'T16:00:00Z'
queryStart = 'T15:59:00Z';

cal= calendar.Calendar()
x = [x for x in cal.itermonthdates(2019, 10)];

for i in range(len(x)):
    strt = x[i].strftime("%Y-%m-%d") + queryEnd;
    end = x[i + 1].strftime("%Y-%m-%d") + queryStart;
    print(strt, end);
    main.main(strt, end);
    if i == (len(x) - 2):
        break;

