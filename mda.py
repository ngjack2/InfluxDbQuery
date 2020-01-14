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
# MDA data analysis to reshuffle the MDA according to threshold
#
def MdaAnalysisDistributePower(xData, yData, mdaThreshold):
    adjWrkTime = 48 - yData[0][0].count(0);
    var1 = np.add(np.add(yData[0][0], yData[1][0]), np.add(yData[2][0], yData[3][0]));
    totalPower = var1.tolist();
    avgPower = sum(totalPower) / adjWrkTime;

    if mdaThreshold > max(totalPower):
        return (totalPower);

    # pop out the list that exceeded threshold
    aboveThresholdValues = [];
    while mdaThreshold < max(totalPower):
        aboveThresholdValues.append(max(totalPower));
        totalPower.remove(max(totalPower));

    # find the last value index
    lastIndex = len(totalPower);
    for value in totalPower[::-1]:
        if (value > 0):
            break;
        lastIndex -= 1;

    # calculate and push back the value at the last index
    totalAboveThresholdValue = sum(aboveThresholdValues);
    loop = math.ceil(totalAboveThresholdValue / avgPower);
    for i in range(loop):

        if avgPower < totalAboveThresholdValue:
            totalAboveThresholdValue -= avgPower;
            totalPower[lastIndex + i] = avgPower;
        else:
            totalPower[lastIndex + i] = totalAboveThresholdValue;
        totalPower.append(0);

    # Shift the working hours
    i = 0;
    while (len(totalPower) - 48) > 0:
        if totalPower[i] == 0:
            totalPower.pop(i);
        i += 1;

    return (totalPower);

#
# Rotate the list to left by n
#
def RotateList(data, n):
    return data[n:] + data[:n];


#
#
#
def ComputePermutation(bestData, MdaThreshold):

    for idx in range(len(bestData)):
        if max(bestData[idx]) > MdaThreshold:
            return [[0, 0, 0, 0]];

    sumData = np.add(np.add(bestData[0], bestData[1]), np.add(bestData[2], bestData[3]));
    indx = np.where(sumData > 0);

    totalHours = indx[0].max() - indx[0].min();

    overTime = list(range(0, 48 - totalHours));
    permutate = list(itertools.permutations(overTime, 4));
    return permutate;
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
    success = False;
    bestData = [machine1, machine2, machine3, machine4];
    permutate = ComputePermutation(bestData, MdaThreshold);
    for x in permutate:
  
        var = np.add(np.add(machine1, machine2), np.add(machine3, machine4));
        totalPower = var.tolist();

        if (max(totalPower) < threshold):
            print(x);
            threshold = max(totalPower);
            bestData = [machine1, machine2, machine3, machine4];
            success = True;
            # initial MDA lower than threshold don't need any improvement
            if (count == 0):
                return (bestData, count, success);
            break;

        count += 1;
        machine1 = tuple(RotateList(data[0][0], x[0]));
        machine2 = tuple(RotateList(data[1][0], x[1]));
        machine3 = tuple(RotateList(data[2][0], x[2]));
        machine4 = tuple(RotateList(data[3][0], x[3]));

    return (bestData, count, success);


#
# Calculate operation hours
#
def Calculate_Operation_Hours(oldMda, newMda):

    # Calculate sum of all machine MDA
    var1 = np.add(np.add(oldMda[0][0], oldMda[1][0]), np.add(oldMda[2][0], oldMda[3][0]));
    mdaOrigPower = var1.tolist();

    # Calculate sum of all machine MDA
    var2 = np.add(np.add(newMda[0], newMda[1]), np.add(newMda[2], newMda[3]));
    mdaNewPower = var2.tolist();

    # Calculate operating hours
    oldMdaPoint = np.where(var1 > 0);
    newMdaPoint = np.where(var2 > 0);

    currentOperationHours = oldMdaPoint[0].max() - oldMdaPoint[0].min();
    newOperationHours = newMdaPoint[0].max() - newMdaPoint[0].min();

    return (newOperationHours / 2, currentOperationHours / 2, mdaNewPower, mdaOrigPower);