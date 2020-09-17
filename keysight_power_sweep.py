# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 15:28:59 2020

@author: nanospin
"""

import qcodes as qc
import os
import time
from datetime import date
import logging
from qcodes.dataset.measurements import Measurement, DataSaver
from qcodes.dataset.plotting import plot_by_id
from qcodes.dataset.database import initialise_database
from qcodes.dataset.data_set import new_data_set, ParamSpec, DataSet, load_by_id 
from qcodes.dataset.data_export import get_data_by_id
#from qcodes.dataset.data_set.DataSet import get_parameter_data
from qcodes.dataset.experiment_container import new_experiment, load_experiment_by_name, experiments, load_experiment
import matplotlib.pyplot as plt
import numpy as np
import pyvisa

#vna.sweep_mode.set('CONT')
vna.power(vnapower)
vna.center(center_frequency)
vna.span(frequency_span)
vna.points(numberofpoints)
vna.if_bandwidth(ifbandwidth)
vna.trace(measuredtrace)
vna.auto_sweep(False)
#vna.groupdelay.set(groupdelayref)#does not work yet

meas=Measurement()
meas.register_parameter(vna.power)  # register the first independent parameter
meas.register_parameter(vna.real, setpoints=(vna.power,))  # register the second independent parameter
meas.register_parameter(vna.imaginary, setpoints=(vna.power,))  # now register the dependent one
meas.register_parameter(vna.phase, setpoints=(vna.power,))  # now register the dependent one
meas.register_parameter(vna.magnitude, setpoints=(vna.power,))  # now register the dependent one

with meas.run() as datasaver:
    for v1 in np.linspace(powersweepstart, powersweepstop, powersweepnum, endpoint=True):
        vna.active_trace.set(1)
        power = vna.power.set(v1)
        print(vna.power.get())
        
        #vna.auto_sweep.set(False)
        #vna.auto_sweep.set(True)            
        vna.traces.tr1.run_sweep()

        #power=vna.power()
        #vna.auto_sweep.set(False)
        imag = vna.imaginary()
        real = vna.real()
        phase = vna.phase()            
        mag = vna.magnitude()

        #vna.active_trace.set(2)
        #vna.traces.tr2.run_sweep()
        power=vna.power()
        #time.sleep(2)
        datasaver.add_result(
                (vna.imaginary, imag), 
                (vna.real, real), 
                (vna.magnitude, mag),
                (vna.phase, phase),
                (vna.power, power))
        print(vna.power.get())
        
plot_by_id(datasaver.run_id)

# vna.sweep_mode.set('CONT')