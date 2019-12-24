#!/usr/bin/env python
import os
import time
import json
import datetime
import calendar
import tkinter
import tkcalendar

# import MDA module
import main

class MdaGui:
    def __init__(self, handler):
        self.date = datetime.date.today();
        self.radioValue = 1;
        self.mdaThreshold = None;
        self.checkButton = False;
        handler.title("MDA Analysis GUI");
        handler.geometry('350x100');

        # Label the date
        self.label = tkinter.Label(window, text='Choose date');
        self.label.grid(column=0, row=1);

        # Label the main frame
        self.txt = tkinter.Label(window, text='MDA Analysis');
        self.txt.grid(column=0, row=0);

        # Run button to execute script
        self.button = tkinter.Button(window, text='Run', width=10, command=self.Run_Mda_Script);
        self.button.grid(column=3, row=3);

        # check button for graph
        self.check = tkinter.Checkbutton(window, text = "Graph", variable=checkVar, onvalue=True, offvalue=False);
        self.check.grid(column=0, row=3);

        # radio button to choose date execute or month execute
        self.rad1 = tkinter.Radiobutton(window, text="Month", variable=var, value=1);
        self.rad1.select();
        self.rad1.grid(column=0, row=2);
        self.rad2 = tkinter.Radiobutton(window, text="Date", variable=var, value=2);
        self.rad2.grid(column=1, row=2);

        # Calendar
        self.cal = tkcalendar.DateEntry(window, width=12, background='darkblue',
                        foreground='white', borderwidth=2, year=2019)
        self.cal.grid(column=1, row=1);

        # MDA Threshold
        self.label = tkinter.Label(window, text='MDA Threshold');
        self.label.grid(column=2, row=1);
        self.txt = tkinter.Entry(window, textvariable = mdaThreshold, width = 10);
        self.txt.grid(column=3, row=1);

        # Bind the calendar function
        handler.bind('<<DateEntrySelected>>', self.Get_Calendar_Date);

    #
    def Get_Calendar_Date(self, event):
        self.date = self.cal.get_date();

    #
    def Run_Mda_Script(self):
        self.radioValue = var.get();
        self.mdaThreshold = int(mdaThreshold.get());
        self.checkButton = checkVar.get();
        queryHourStart = 'T16:00:00Z'
        queryHourEnd = 'T15:59:00Z';
        if self.radioValue == 1:
            cal = calendar.Calendar();
            d1 = self.date.strftime("%Y-%m-%d");
            year, month, date = d1.split('-');
            x = [x for x in cal.itermonthdates(int(year), int(month))];

            for i in range(len(x)):
                strt = x[i].strftime("%Y-%m-%d") + queryHourStart;
                end = x[i + 1].strftime("%Y-%m-%d") + queryHourEnd;
                print(strt, end);
                self.checkButton = False;
                main.main(strt, end, self.mdaThreshold, self.checkButton);
                if i == (len(x) - 2):
                    break;
        else:
            yesterday = self.date - datetime.timedelta(days=1);
            startQuery = yesterday.strftime("%Y-%m-%d") + queryHourStart;
            endQuery = self.date.strftime("%Y-%m-%d") + queryHourEnd;

            main.main(startQuery, endQuery, self.mdaThreshold, self.checkButton);

window = tkinter.Tk();
var = tkinter.IntVar();
checkVar = tkinter.BooleanVar();
mdaThreshold = tkinter.StringVar(window, value = '1000000')
mda_gui = MdaGui(window);
window.mainloop();
