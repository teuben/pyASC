#! /usr/bin/env python
#

from __future__ import print_function

import time
import numpy as np
import logging

#  For some variations on this theme, e.g.  time.time vs. time.clock, see
#  http://stackoverflow.com/questions/7370801/measure-time-elapsed-in-python
#

class Dtime(object):
    """ Class to help measuring the wall clock time between tagged events
        Typical usage:
    
        dt = Dtime('some_label')
        ...
        dt.tag('a')
        ...
        dt.tag('b')
        dt.end()
    """
    def __init__(self, label=".", report=True):
        self.start = self.time()
        self.init = self.start
        self.label = label
        self.report = report
        self.dtimes = []
        dt = self.init - self.init
        if self.report:
            #logging.info("Dtime: %s ADMIT " % (self.label + self.start)) #here took out a '
            logging.info("Dtime: %s BEGIN " % self.label + str(dt))

    def reset(self, report=True):
        self.start = self.time()
        self.report = report
        self.dtimes = []

    def tag(self, mytag):
        t0 = self.start
        t1 = self.time()
        dt = t1 - t0
        self.dtimes.append((mytag, dt))
        self.start = t1
        if self.report:
            logging.info("Dtime: %s " % self.label + mytag + "  " + str(dt))
        return dt

    def show(self):
        if self.report:
            for r in self.dtimes:
                logging.info("Dtime: %s " % self.label + str(r[0]) + "  " + str(r[1]))
        return self.dtimes

    def end(self):
        t0 = self.init
        t1 = self.time()
        dt = t1 - t0
        if self.report:
            logging.info("Dtime: %s END " % self.label + str(dt))
        return dt

    def time(self):
        """ pick the actual OS routine that returns some kind of timer
        time.time   :    wall clock time (include I/O and multitasking overhead)
        time.clock  :    cpu clock time
        """
        return np.array([time.clock(), time.time()])

    def get_mem(self):
        """ Read memory usage info from /proc/pid/status
            Return Virtual and Resident memory size in MBytes.

            NOTE: not implemented here, see the ADMIT version if you need this.
        """
        return np.array([])       # NA yet

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    dt = Dtime("testingDtime")
    dt.tag('one')
    # print("Hello Dtime World")
    print("Hello Dtime World")
    dt.tag('two')
    dt.end()
       
