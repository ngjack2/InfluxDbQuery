#!/usr/bin/env python
import os
import pdb
import xlwt
import math
import itertools

import numpy as np

from multiprocessing import Process
from xlwt import Workbook

#
# Rotate the list to left by n
#
def RotateList(data, n):
    return data[n:] + data[:n];

#
# Shuffle the data and calcuate the optimun MDA
#
def ShuffleDataForMda(data, MdaThreshold):

    threshold = MdaThreshold;
    machine1 = data[0][0];
    machine2 = data[1][0];
    machine3 = data[2][0];
    machine4 = data[3][0];
    
    count = 0;
    permutate = list(itertools.permutations([0,1,2,3,4], 4));
    bestData = [machine1, machine2, machine3, machine4];
    for x in permutate:
  
        var = np.add(np.add(machine1, machine2), np.add(machine3, machine4));
        totalPower = var.tolist();

        if (max(totalPower) < threshold):
            print(x);
            threshold = max(totalPower);
            bestData = [machine1, machine2, machine3, machine4];
            
            # initial MDA lower than threshold don't need any improvement
            if (count == 0):
                return (bestData, count);

        count += 1;
        machine1 = tuple(RotateList(data[0][0], x[0]));
        machine2 = tuple(RotateList(data[1][0], x[1]));
        machine3 = tuple(RotateList(data[2][0], x[2]));
        machine4 = tuple(RotateList(data[3][0], x[3]));

    return (bestData, count);
