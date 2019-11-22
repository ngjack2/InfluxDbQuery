#!/usr/bin/env python

import os
import pdb
import time
import ctypes
import xlwt

import matplotlib.pyplot as plt
import numpy as np

from xlwt import Workbook
from influxdb import InfluxDBClient
from random import randint


#
# Init the database for query
#
def QueryDataBaseInit():
    handler = InfluxDBClient (host='10.200.32.12',
                              port=8086,
                              username='mimos',
                              password='mimosian',
                              database="kami");
    return handler;

#
# Query the item from list
##result = connection.query('SELECT "deltaPower" FROM "kami_machine_Hammer_Mill1_reading" GROUP BY * ORDER BY DESC LIMIT 3');
def QueryDatabase(handler, queryItem):
    points = [];
    for x in range(4):
        queryStatement = ('SELECT sum(%s) FROM %s '
                          'WHERE time > \'%s\' AND time < \'%s\' GROUP BY time(30m) fill(0) tz(\'Asia/Singapore\')'
                          %(queryItem['item'], queryItem['tag'][x], queryItem['date'][0], queryItem['date'][1]));

        result = handler.query(queryStatement);
        points.append(result.get_points(queryItem['tag'][x]));
        print('Query now# %s' %queryItem['tag'][x]);
    return points
#
# Save all query data into excel
#
def SaveQueryDataInExcel(xData, yData):
    
    sheet = [];
    wb = Workbook();
    for i in range(len(xData)):
        cmp, name, machine, type, process = map(str,queryItem['tag'][i].split('_'));
        sheet.append(wb.add_sheet(machine+type));
        for j in range(len(xData[i])):
            sheet[i].write(j, 0, xData[i][j]);
            sheet[i].write(j, 1, yData[i][j]);

    wb.save('query.xls');

#
# Use matplot to plot the query data
#
def MatplotQueryData(time, data):

    # split the data set by 24 hours
    xData = [];
    yData = [];
    csum  = [];
    temp1 = [];
    temp2 = [];
    temp3 = [];
    for x in range(len(points)):
        for i in range(int(len(time[0]) / 48)):
            start = i * 48;
            end = start + 48;
            temp1.append(time[x][start:end]);
            temp2.append(data[x][start:end]);
            a = data[x][start:end];
            # compute average power usage per hour per day
            temp3.append(sum(a) / (48 - temp1.count(0)) / 2);
        xData.append(temp1);
        yData.append(temp2);
        csum.append(temp3);
        temp1 = [];
        temp2 = [];
        temp3 = [];
 
    # plot the data
    cmap = plt.get_cmap('gnuplot')
    colors = [cmap(i) for i in np.linspace(0, 1, len(xData[0]))]
    for y in range(4):
        plt.figure();
        for x in range(len(xData[y])):
            pltproperty = plt.plot(xData[y][x], yData[y][x], '-x', label='day' +str(x + 1));
            plt.setp(pltproperty, 'color', colors[x]);
        plt.grid(True);
        plt.xlabel('time(30mins)');
        plt.ylabel('KWH');
        plt.title(queryItem['tag'][y]);
        plt.legend();

    plt.figure();
    colors1 = ['r', 'b', 'y', 'c'];
    for x in range(4):
        pltproperty = plt.plot(csum[x], '-x', label=queryItem['tag'][x] +str(x + 1));
        plt.setp(pltproperty, 'color', colors1[x]);
        plt.grid(True);
        plt.xlabel('day');
        plt.ylabel('PowerPerHour');
        plt.title('Total Power Per Hour Per Day Usage');
        plt.legend();
    plt.show();

#
# Main program start
#
if __name__ == "__main__":

    # Query setup 
    queryItem = {'item':"deltaPower", 
         'tag':["kami_machine_Hammer_Mill1_reading", "kami_machine_Hammer_Mill2_reading", "kami_machine_Pellet_Mill1_reading", "kami_machine_Pellet_Mill2_reading"],
         'date':['2019-10-01T16:00:00Z','2019-10-31T15:59:00Z']};

    # User Guide to enter date
    ctypes.windll.user32.MessageBoxW(0, "Please key in the date follow the format given " + queryItem['date'][0], 'Warning', 1);
    #time.sleep(3);

    # Init database handler
    handler = QueryDataBaseInit();
   
   # Check any user input
    if len(os.sys.argv) > 1:
        queryItem['date'][0] = os.sys.argv[1];
        queryItem['date'][1] = os.sys.argv[2];
    else:
        print("Continue with default date in script");

    # Query the database
    points = QueryDatabase(handler, queryItem);

    # extract info out from query
    data = [];
    time = [];
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
        time.append(temp2);
        dbtime.append(temp3);
        temp1 = [];
        temp2 = [];
        temp3 = [];

    # save it to excel
    SaveQueryDataInExcel(dbtime, data);

    # plot the data
    MatplotQueryData(time, data);


