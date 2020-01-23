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
# Use matplot to plot the query data
#
def MatplotQueryData(xData, yData, modData, mda_thres, queryItem):
    plt.figure();
    totalMDA = np.add(np.add(yData[0][0], yData[1][0]), np.add(yData[2][0], yData[3][0]));
    totalMDA1 = np.add(np.add(modData[0], modData[1]), np.add(modData[2], modData[3]));
    plt.plot(xData[0][0], totalMDA, '-x', color='b', label='Original');
    plt.plot(xData[0][0], totalMDA1, '-d', color='g', label='MdaResult');

    mda_threshold = [mda_thres for _ in range(len(xData[0][0]))];
    plt.plot(xData[0][0], mda_threshold, '-d', color='r', label='MDA Threshold');

    plt.grid(True);
    plt.xlabel('time(30mins)');
    plt.ylabel('KWH');
    plt.title('MDA Used in Day');
    plt.legend();

    ## form the color map for the data
    cmap = plt.get_cmap('gnuplot');
    colors = [cmap(i) for i in np.linspace(0, 1, len(xData[0]))];

    ## plot the total power per day for all machine
    # plt.figure();
    # for x in range(len(xData[0])):
    #    totalMDA = np.add(np.add(yData[0][x], yData[1][x]), np.add(yData[2][x], yData[3][x]));
    #    pltproperty = plt.plot(xData[0][x], totalMDA, '-x', label='day' + str(x + 1));
    #    plt.setp(pltproperty, 'color', colors[x]);

    # plt.grid(True);
    # plt.xlabel('time(30mins)');
    # plt.ylabel('KWH');
    # plt.title('MDA Used in Day');
    # plt.legend();

    # plot the individual power usage per day
    # for y in range(4):
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
        pltproperty = plt.plot(xData[x][0], yData[x][0], '-x', label=queryItem['tag'][x] + str(x + 1));
        plt.setp(pltproperty, 'color', colors1[x]);
    plt.grid(True);
    plt.xlabel('day');
    plt.ylabel('powerperhour');
    plt.title('original power usage');
    plt.legend();

    plt.figure();
    colors1 = ['r', 'b', 'y', 'c'];
    for x in range(4):
        pltproperty = plt.plot(xData[x][0], modData[x], '-x', label=queryItem['tag'][x] + str(x + 1));
        plt.setp(pltproperty, 'color', colors1[x]);
    plt.grid(True);
    plt.xlabel('day');
    plt.ylabel('powerperhour');
    plt.title('suggested power usage');
    plt.legend()
    # plot the MDA per day
    # plt.figure();
    # for x in range(len(xData[0])):
    #    mda_per_day = [np.add(np.add(yData[0][x], yData[1][x]), np.add(yData[2][x], yData[3][x]))];
    #    pltproperty = plt.plot(xData[0][x], mda_per_day[0], '-x', label='day' + str(x + 1));
    #    plt.setp(pltproperty, 'color', colors[x]);

    # pltproperty = plt.plot(mean_mda, '-o', color = 'b', label='mean');

    # plt.grid(True);
    # plt.xlabel('time(30m)');
    # plt.ylabel('KWH');
    # plt.title('MDA/Day Usage, mean = ' + str(mean_mda[0]) + ', stdDev = ' + str(np.std(usage_month)));
    # plt.legend();
    # plt.show();
    plt.draw();
    plt.show();


#
# Main program start
#
def main(argv1, argv2, mdaThreshold, enable_graph):

    path = os.path.abspath(os.path.dirname(os.sys.argv[0]));

    # Query setup
    db_param_path = path + '/kami_prod.json';

    with open(db_param_path) as pFile:
        queryItem = json.load(pFile);
    # log down the process
    obj = log.Log();

    # Check any user input
    queryItem['date'][0] = argv1;
    queryItem['date'][1] = argv2;
    obj.WriteBuffer("Query input %s %s\n" % (queryItem['date'][0], queryItem['date'][1]));

    try:
        # Init database handler
        readHandler = influxDb.QueryDataBaseInit(queryItem);

        # Check database existance for MDA
        readHandler = influxDb.CheckDataBase(readHandler, queryItem, False, obj);

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
        # modified_total_power = mda.MdaAnalysisDistributePower(xData, yData, mdaThreshold);

        # method 2: Calculate minimum MDA usage per day
        modData, count, success = mda.ShuffleDataForMda(yData, mdaThreshold);
        newMdaOperationHour, oldMdaOperationHour, newMdaData, oldMdaData = mda.Calculate_Operation_Hours(yData,
                                                                                                         modData);
        obj.WriteBuffer("ShuffleDataForMda %s, result %s, dbtime %s\n" % (count, success, dbtime[0][0]));

        # Init MDA database handler
        db_param_path = path + '/kami_mda.json';
        with open(db_param_path) as pFile:
            writeItem = json.load(pFile);

        # Init database handler
        writeHandler = influxDb.QueryDataBaseInit(writeItem);

        # Check database existance for MDA
        writeHandler = influxDb.CheckDataBase(writeHandler, writeItem, True, obj);

        # Write mda status into database
        var1 = np.add(np.add(yData[0][0], yData[1][0]), np.add(yData[2][0], yData[3][0]));
        mdaOrigPower = var1.tolist();
        var2 = np.add(np.add(modData[0], modData[1]), np.add(modData[2], modData[3]));
        mdaNewPower = var2.tolist();

        mdaStatus = "Failed" if success == False else "Pass";
        mdaData = [{'measurement': 'mdaTable', 'time': dbtime[0][1],
                    'fields': {'systime': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                               'threshold': float(mdaThreshold), 'mdaOrig': float(max(mdaOrigPower)),
                               'mdaNew': float(max(mdaNewPower)),
                               'currentOpHours': float(oldMdaOperationHour), 'newOpHours': float(newMdaOperationHour),
                               'mdaStatus': mdaStatus}}];
        writeHandler.write_points(mdaData);

        # Write machines data into database
        for i in range(len(modData)):
            for j in range(len(modData[0])):
                wData = [{'measurement': writeItem['tag'][i], 'time': dbtime[i][j],
                          'fields': {'systime': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                     'deltaPower': float(modData[i][j])}}];
                writeHandler.write_points(wData);

        # Close the http connection
        influxDb.CloseConnection(writeHandler);

    except Exception as e:
        exc_type, exc_value, exc_traceback = os.sys.exc_info();
        obj.WriteBuffer("error %s, file: %s, line: %s\n"
                        % (type(e).__name__, exc_traceback.tb_frame.f_code.co_filename, exc_traceback.tb_lineno));
        print("error %s, file: %s, line: %s\n"
              % (type(e).__name__, exc_traceback.tb_frame.f_code.co_filename, exc_traceback.tb_lineno));
    # Close the file handler
    obj.Close();

    # plot the data
    if enable_graph == True:
        MatplotQueryData(xData, yData, modData, mdaThreshold, queryItem);


if __name__ == "__main__":
    path = os.path.abspath(os.path.dirname(os.sys.argv[0]));
    db_param_path = path + '/kami_prod.json';

    with open(db_param_path) as pFile:
        queryItem = json.load(pFile);

    # format time for one day query
    queryHourStart = 'T16:00:00Z'
    queryHourEnd = 'T15:59:00Z';

    # get today calendar format
    yesterday = datetime.date.today() - datetime.timedelta(days=1);
    today = datetime.date.today();
    startQuery = yesterday.strftime("%Y-%m-%d") + queryHourStart;
    endQuery = today.strftime("%Y-%m-%d") + queryHourEnd;
    #startQuery = "2020-01-09" + queryHourStart;
    #endQuery = "2020-01-10" + queryHourEnd;

    # run query, MDA and write back to influxDB
    main(startQuery, endQuery, queryItem['grafana']['threshold'], enable_graph=False);
