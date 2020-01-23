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
import log
import threading

#
# Check json file on threshold, threshold change run MDA analysis
#
def Scheduler_Mda():

    try:
        # Read old threshold
        path = os.path.abspath(os.path.dirname(os.sys.argv[0]));
        db_param_path = path + '/kami_prod.json';
        with open(db_param_path) as pFile:
            queryItem = json.load(pFile);

        # Read new threshold
        #path = os.path.expanduser('~') + '/grafana-storage/grafana.db';
        with open(queryItem['grafana']['grafana_db_path'], "rb") as pFile:
            temp = pFile.read();
            data = str(temp);

        strtIndx = 0;
        while (True):
            # find the threshold sentence
            strtIndx = data.find("\"thresholds\":[{\"colorMode\"", strtIndx + 1);
            if strtIndx == -1:
                break;
            endIndx = data.find("]", strtIndx);

            # find the MDA tile
            titleIndx = data.find("\"title\"", endIndx);
            titleEnd = data.find(",", titleIndx);
            mdaThresholdJson = json.loads("{" + data[strtIndx:endIndx+1] + "," + data[titleIndx:titleEnd] + "}");

            # find the version of the MDA panel
            verIndx = data.find("\"time\":{", titleEnd);
            verEnd = data.find("\"version\"", verIndx);
            verEnd = data.find("}", verEnd);

            # load all the buffer into json format
            mdaVersionJson = json.loads("{" + data[verIndx:verEnd+1]);

            # check the panel title, and version to update the latest threshold
            if (mdaThresholdJson['title'] == "Analysis MDA"):
                if (mdaVersionJson['version'] > queryItem['grafana']['version']):
                    mdaThreshold = mdaThresholdJson['thresholds'][0]['value'];
                    queryItem['grafana']['version'] = mdaVersionJson['version'];

        # Compare old and new threshold, difference will run MDA analysis
        if (mdaThreshold != queryItem['grafana']['threshold']):

            queryItem['grafana']['threshold'] = mdaThreshold;
            queryItem['grafana']['version'] = mdaVersionJson['version'];

            with open(db_param_path, "w") as pFile:
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

    except Exception as e:
        # log down the process
        obj = log.Log();

        exc_type, exc_value, exc_traceback = os.sys.exc_info();
        obj.WriteBuffer("error %s, file: %s, line: %s\n"
                        %(type(e).__name__, exc_traceback.tb_frame.f_code.co_filename, exc_traceback.tb_lineno));
        print("error %s, file: %s, line: %s\n"
                        %(type(e).__name__, exc_traceback.tb_frame.f_code.co_filename, exc_traceback.tb_lineno));

        # Close the file handler
        obj.Close();


if __name__ == "__main__":
    WAIT_TIME_SECONDS = 5

    ticker = threading.Event()
    while not ticker.wait(WAIT_TIME_SECONDS):
        Scheduler_Mda();
