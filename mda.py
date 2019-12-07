#!/usr/bin/env python
import os
import pdb
import time
import ctypes
import xlwt
import math
import itertools

import numpy as np

from multiprocessing import Process
from xlwt import Workbook


def RotateList(data, n):
    return data[n:] + data[:n];

def ShuffleDataAndCalculate(data, MdaThreshold):
    temp = data;
    threshold = MdaThreshold;

    count = 0;
    while(1):
        temp[0][0] = RotateList(data[0][0], randint(0, 4));
        temp[1][0] = RotateList(data[1][0], randint(0, 4));
        temp[2][0] = RotateList(data[2][0], randint(0, 4));
        temp[3][0] = RotateList(data[3][0], randint(0, 4));

        count += 1;
        var = np.add(np.add(temp[0][0], temp[1][0]), np.add(temp[2][0], temp[3][0]));
        totalPower = var.tolist();
        if (max(totalPower) < threshold):
            threshold = max(totalPower);
            data = temp;

        if count == 200:
            break;
    return data;
