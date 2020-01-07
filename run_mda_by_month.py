#!/usr/bin/env python
import os
import pdb
import time
import ctypes
import xlwt
import math
import json
import calendar
import datetime
import main
import threading


#
# Check json file on threshold, threshold change run MDA analysis
#
def Scheduler_MDA():
    # Read old threshold
    path = os.path.abspath(os.path.dirname(os.sys.argv[0]));
    db_param_path = path + '/kami_prod.json';
    with open(db_param_path) as pFile:
        queryItem = json.load(pFile);

    # Read new threshold
    with open("D:\Work\grafana_source\grafana\data\grafana.db", "rb") as pFile:
        temp = pFile.read();
        data = str(temp);

    strtIndx = 0;
    while (True):
        strtIndx = data.find("\"thresholds\":[{\"colorMode\"", strtIndx + 1);

        endIndx = data.find("]", strtIndx);
        buffer = "{" + data[strtIndx:endIndx + 1] + "}";

        titleIndx = data.find("\"title\"", endIndx);
        titleEnd = data.find(",", titleIndx);
        if strtIndx == -1:
            break;
        jsonTemp = json.loads(buffer);

        title = "{" + data[titleIndx:titleEnd] + "}";
        jsonTitle = json.loads(title);
        if (jsonTitle['title'] == "Analysis MDA"):
            mdaThreshold = jsonTemp['thresholds'][0]['value'];

    # Compare old and new threshold, difference will run MDA analysis
    if (mdaThreshold != queryItem['threshold']):
        queryItem['threshold'] = mdaThreshold;
        with open(db_param_path, "r+") as pFile:
            json.dump(queryItem, pFile);

        # format time for one day query
        queryEnd = 'T16:00:00Z'
        queryStart = 'T15:59:00Z';

        for i in range(1, 30):
            past = datetime.date.today() - datetime.timedelta(days=i + 1);
            present = datetime.date.today() - datetime.timedelta(days=i);
            strt = past.strftime("%Y-%m-%d") + queryStart;
            end = present.strftime("%Y-%m-%d") + queryEnd;
            print(strt, end);
            main.main(strt, end, mdaThreshold, enable_graph=False);


if __name__ == "__main__":
    WAIT_TIME_SECONDS = 20

    ticker = threading.Event()
    while not ticker.wait(WAIT_TIME_SECONDS):
        Scheduler_MDA();
