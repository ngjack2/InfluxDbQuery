#!/usr/bin/env python
import os
import pdb
import time
import ctypes
import xlwt
import math


import numpy as np

from xlwt import Workbook
from influxdb import InfluxDBClient

#
# Init the database for query
#
def QueryDataBaseInit(queryItem):
    handler = InfluxDBClient(host = queryItem['hostIp'],
                              port = queryItem['hostPort'],
                              username = queryItem['user'],
                              password = queryItem['passwrd']);
    return handler;

#
# Check database existance and create database
#
def CheckDataBase(handler, queryItem, create_db, obj):

    db_list = handler.get_list_database();
   
    for db in db_list:
        if queryItem['db'] == db['name']:
            handler.switch_database(db['name']);
            print(db['name']);
            obj.WriteBuffer("Log %s database\n" %db['name']);
            return handler;

    # Create the MDA database if can't find it
    if create_db == True:
        handler.create_database(queryItem['db']);
        handler.switch_database(queryItem['db']);
        obj.WriteBuffer("Create %s database\n" %queryItem['db']); 

    return (handler);

#
# Close the http connection created
#
def CloseConnection(connection):
    InfluxDBClient.close(connection);

#
# Query the item from list
#
def QueryDatabase(handler, queryItem):
    points = [];
    for x in range(4):
        queryStatement = ('SELECT sum(%s) FROM %s '
                          'WHERE time > \'%s\' AND time < \'%s\' GROUP BY time(30m) fill(0) tz(\'Asia/Singapore\')'
                          % (queryItem['item'], queryItem['tag'][x], queryItem['date'][0], queryItem['date'][1]));

        result = handler.query(queryStatement);
        points.append(result.get_points(queryItem['tag'][x]));
        print('Query now# %s' % queryItem['tag'][x]);
    return points;

#
# Save all query data into excel
#
def SaveQueryDataInExcel(points, queryItem, save_excel):
    # extract info out from query
    data = [];
    rtime = [];
    dbtime = [];
    temp1 = [];
    temp2 = [];
    temp3 = [];
    for x in range(len(points)):
        for j in points[x]:   
            var = j['time'];
            var1 = var[11:16];
            hh, mm = map(int,var1.split(':'));
            temp1.append(j['sum']);
            temp2.append((hh * 100) + mm);
            temp3.append(var);
        data.append(temp1);
        rtime.append(temp2);
        dbtime.append(temp3);
        temp1 = [];
        temp2 = [];
        temp3 = [];

    # Save when requested
    if save_excel == True:
        sheet = [];
        wb = Workbook();
        for i in range(len(dbtime)):
            cmp, name, machine, type, process = map(str,queryItem['tag'][i].split('_'));
            sheet.append(wb.add_sheet(machine + type));
            for j in range(len(dbtime[i])):
                sheet[i].write(j, 0, dbtime[i][j]);
                sheet[i].write(j, 1, data[i][j]);

        wb.save('query.xls');

    return (dbtime, rtime, data);

#
# Extract data in days series for plotting purpose
#
def ExtractData(rtime, data, points):
    # split the data set by 24 hours
    xData = [];
    yData = [];
    avgPowerPerMachine = [];
    totalPowerPerMachine = [];
    temp1 = [];
    temp2 = [];
    temp3 = [];
    temp4 = [];
    for x in range(len(points)):
        for i in range(int(len(rtime[0]) / 48)):
            start = i * 48;
            end = start + 48;
            temp1.append(rtime[x][start:end]);
            temp2.append(data[x][start:end]);
            a = data[x][start:end];
            # compute average power usage per hour per day
            if sum(a) == 0:
                temp3.append(0);
            else:
                temp3.append(sum(a) / (48 - temp2[0].count(0)) / 2);
            temp4.append(sum(a));
        xData.append(temp1);
        yData.append(temp2);
        avgPowerPerMachine.append(temp3);
        totalPowerPerMachine.append(temp4);
        temp1 = [];
        temp2 = [];
        temp3 = [];
        temp4 = [];
    return (xData, yData, avgPowerPerMachine, totalPowerPerMachine);
