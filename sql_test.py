import os
from influxdb import InfluxDBClient
import matplotlib.pyplot as plt
import numpy as np
import xlwt
from xlwt import Workbook
import pdb

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
                          'WHERE time > \'%s\' AND time < \'%s\' GROUP BY time(30m) tz(\'Asia/Singapore\')'
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
    temp1 = [];
    temp2 = [];
    for x in range(len(points)):
        for i in range(int(len(time[0]) / 48)):
            start = i * 48;
            end = start + 48;
            temp1.append(time[x][start:end]);
            temp2.append(data[x][start:end]);
        xData.append(temp1);
        yData.append(temp2);
        temp1 = [];
        temp2 = [];

    # plot the data
    cmap = plt.get_cmap('gnuplot')
    colors = [cmap(i) for i in np.linspace(0, 1, len(xData[0]))]
    for y in range(4):
        plt.figure();
        for x in range(len(xData[y])):
            pltproperty = plt.plot(xData[y][x], yData[y][x], '-x', label='day' +str(x + 1));
            plt.setp(pltproperty, 'color', colors[x]);
        plt.grid(True);
        plt.xlabel('time');
        plt.ylabel('KWH');
        plt.title(queryItem['tag'][y]);
        plt.legend();
    plt.show();


#
# Main program start
#
if __name__ == "__main__":

    # Init database handler
    handler = QueryDataBaseInit();

    # Query setup 
    queryItem = {'item':"deltaPower", 
         'tag':["kami_machine_Hammer_Mill1_reading", "kami_machine_Hammer_Mill2_reading", "kami_machine_Pellet_Mill1_reading", "kami_machine_Pellet_Mill2_reading"],
         'date':['2019-10-20T16:00:00Z','2019-11-12T15:59:00Z']};
    
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


