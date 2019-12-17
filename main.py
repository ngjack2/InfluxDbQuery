#!/usr/bin/env python
import os
import pdb
import time
import ctypes
import xlwt
import math
import json
import datetime

# custome module
import mda
import influxDb
import log

import matplotlib.pyplot as plt
import numpy as np

from multiprocessing import Process
from xlwt import Workbook
from influxdb import InfluxDBClient
from random import randint

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
        if(value > 0):
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
        i+= 1;

    return (totalPower);

#
# Use matplot to plot the query data
#
def MatplotQueryData(xData, yData, modData, mda_thres, queryItem):

    plt.figure();
    totalMDA = np.add(np.add(yData[0][0], yData[1][0]), np.add(yData[2][0], yData[3][0]));
    totalMDA1 = np.add(np.add(modData[0], modData[1]), np.add(modData[2], modData[3]));
    plt.plot(xData[0][0], totalMDA, '-x', color = 'b', label='Original');
    plt.plot(xData[0][0], totalMDA1, '-d', color = 'g', label='MdaResult');

    mda_threshold = [mda_thres for _ in range(len(xData[0][0]))];
    plt.plot(xData[0][0], mda_threshold, '-d', color = 'r', label ='MDA Threshold');

    plt.grid(True);
    plt.xlabel('time(30mins)');
    plt.ylabel('KWH');
    plt.title('MDA Used in Day');
    plt.legend();

    ## form the color map for the data
    cmap = plt.get_cmap('gnuplot');
    colors = [cmap(i) for i in np.linspace(0, 1, len(xData[0]))];
    
    ## plot the total power per day for all machine
    #plt.figure();
    #for x in range(len(xData[0])):
    #    totalMDA = np.add(np.add(yData[0][x], yData[1][x]), np.add(yData[2][x], yData[3][x]));
    #    pltproperty = plt.plot(xData[0][x], totalMDA, '-x', label='day' + str(x + 1));
    #    plt.setp(pltproperty, 'color', colors[x]);

    #plt.grid(True);
    #plt.xlabel('time(30mins)');
    #plt.ylabel('KWH');
    #plt.title('MDA Used in Day');
    #plt.legend();

    # plot the individual power usage per day
    #for y in range(4):
    #    plt.figure();
    #    for x in range(len(xData[y])):
    #        pltproperty = plt.plot(xData[y][x], yData[y][x], '-x', label='day' + str(x + 1));
    #        plt.setp(pltproperty, 'color', colors[x]);
    #    plt.grid(True);
    #    plt.xlabel('time(30mins)');
    #    plt.ylabel('KWH');
    #    plt.title(queryItem['tag'][y]);
    #    plt.legend();

    # Plot average power usage per day per machine per day
    plt.figure();
    colors1 = ['r', 'b', 'y', 'c'];
    for x in range(4):
        pltproperty = plt.plot(xData[x][0], yData[x][0], '-x', label=queryItem['tag'][x] +str(x + 1));
        plt.setp(pltproperty, 'color', colors1[x]);
    plt.grid(True);
    plt.xlabel('day');
    plt.ylabel('powerperhour');
    plt.title('original power usage');
    plt.legend();

    plt.figure();
    colors1 = ['r', 'b', 'y', 'c'];
    for x in range(4):
        pltproperty = plt.plot(xData[x][0], modData[x], '-x', label=queryItem['tag'][x] +str(x + 1));
        plt.setp(pltproperty, 'color', colors1[x]);
    plt.grid(True);
    plt.xlabel('day');
    plt.ylabel('powerperhour');
    plt.title('suggested power usage');
    plt.legend()
    # plot the MDA per day
    #plt.figure();
    #for x in range(len(xData[0])): 
    #    mda_per_day = [np.add(np.add(yData[0][x], yData[1][x]), np.add(yData[2][x], yData[3][x]))];
    #    pltproperty = plt.plot(xData[0][x], mda_per_day[0], '-x', label='day' + str(x + 1));
    #    plt.setp(pltproperty, 'color', colors[x]);

    #pltproperty = plt.plot(mean_mda, '-o', color = 'b', label='mean');

    #plt.grid(True);
    #plt.xlabel('time(30m)');
    #plt.ylabel('KWH');
    #plt.title('MDA/Day Usage, mean = ' + str(mean_mda[0]) + ', stdDev = ' + str(np.std(usage_month)));
    #plt.legend();
    #plt.show();
    plt.draw();
    plt.show();

#
# Main program start
#
def main(argv1, argv2):

    # User Guide to enter date
    #ctypes.windll.user32.MessageBoxW(0, "Please key in the date follow the format given " + queryItem['date'][0], 'Warning', 1);
    #time.sleep(3);
    path = os.path.abspath(os.path.dirname(os.sys.argv[0]));

    # Query setup
    #queryItem = {'hostIp':'10.200.32.12', 'hostPort': 8086, 'user':'mimos', 'passwrd':'mimosian', 'db':"kami", 'item':"deltaPower", 
    #     'tag':["kami_machine_Hammer_Mill1_reading", "kami_machine_Hammer_Mill2_reading", "kami_machine_Pellet_Mill1_reading", "kami_machine_Pellet_Mill2_reading"],
    #     'date':['2019-10-02T16:00:00Z','2019-10-03T15:59:00Z']};
    db_param_path = path + '/kami_prod.json';
    
    with open(db_param_path) as pFile:
        queryItem = json.load(pFile);
    # log down the process
    obj = log.Log();

   # Check any user input
    queryItem['date'][0] = argv1;
    queryItem['date'][1] = argv2;
    obj.WriteBuffer("Query input %s %s\n" %(queryItem['date'][0], queryItem['date'][1]));

    try:
        # Init database handler
        readHandler = influxDb.QueryDataBaseInit(queryItem);

        # Query the database
        points = influxDb.QueryDatabase(readHandler, queryItem);
        obj.WriteBuffer("Query start\n");

        # Close the http connection
        influxDb.CloseConnection(readHandler);
        obj.WriteBuffer("Connection close\n");

        # save it to excel
        dbtime, rtime, data = influxDb.SaveQueryDataInExcel(points, queryItem, False);

        # Extract data accordingly
        xData, yData, avgPowerPerMachine, totalPowerPerMachine = influxDb.ExtractData(rtime, data, points);

        # Change the MDA demand base on user request
        mdaThreshold = 1000000;
        #modified_total_power = MdaAnalysisDistributePower(xData, yData, mdaThreshold);

        # method 2: Calculate minimum MDA usage per day
        modData, count = mda.ShuffleDataForMda(yData, mdaThreshold);
        obj.WriteBuffer("ShuffleDataForMda %s\n" %count);

        # plot the data
        #MatplotQueryData(xData, yData, modData, mdaThreshold, queryItem);

        # Init MDA database handler
        #test= { 'measurement':"kami_machine_Hammer_Mill1_reading", 'time':'2019-10-02T16:00:00Z', 'field': { "deltaPower":127 } };
        db_param_path = path + '/kami_mda.json';
        with open(db_param_path) as pFile:
            writeItem = json.load(pFile);

        # Init database handler
        writeHandler = influxDb.QueryDataBaseInit(writeItem);

        for i in range(len(modData)):
            for j in range(len(modData[0])):
                wData = [{'measurement': writeItem['tag'][i], 'time':dbtime[i][j], 'fields': {'systime': time.strftime('%Y-%m-%dT%H:%M:%SZ'), 'deltaPower': float(modData[i][j])}}];
                writeHandler.write_points(wData);

        # Close the http connection
        influxDb.CloseConnection(writeHandler);

    except Exception as e:
        exc_type, exc_value, exc_traceback = os.sys.exc_info();
        obj.WriteBuffer("error %s, file: %s, line: %s\n" 
                        %(type(e).__name__, exc_traceback.tb_frame.f_code.co_filename, exc_traceback.tb_lineno));
    # Close the file handler
    obj.Close();

if __name__ == "__main__":

    # format time for one day query
    queryHourStart = 'T16:00:00Z'
    queryHourEnd = 'T15:59:00Z';

    # get today calendar format
    yesterday = datetime.date.today() - datetime.timedelta(days=1);
    today = datetime.date.today();
    startQuery = yesterday.strftime("%Y-%m-%d") + queryHourStart;
    endQuery = today.strftime("%Y-%m-%d") + queryHourEnd;
   
    # run query, MDA and write back to influxDB
    main(startQuery, endQuery);
