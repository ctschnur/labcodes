# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 11:22:09 2020

@author: nanospin
"""


import time
import numpy as np
from qcodes import load_or_create_experiment, Measurement, Parameter

xvals = np.linspace(0, 10, 101)
yvals = np.sin(xvals)
y2vals = np.cos(xvals)

def simple_1d_sweep():
    for x, y, y2 in zip(xvals, yvals, y2vals):
        yield x, y, y2
        
x = Parameter('x')
y = Parameter('y')
y2 = Parameter('y2')

station = qc.Station(x, y, y2)

exp = load_or_create_experiment('very_simple_1d_sweep', sample_name='no sample')

meas = Measurement(exp, station)
meas.register_parameter(x)
meas.register_parameter(y, setpoints=(x,))
meas.register_parameter(y2, setpoints=(x,))
meas.write_period = 2

with meas.run() as datasaver:
    for xval, yval, y2val in simple_1d_sweep():
        datasaver.add_result(
            (x, xval),
            (y, yval),
            (y2, y2val),
        )
        time.sleep(0.2)