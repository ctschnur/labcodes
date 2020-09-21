# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 14:38:16 2020

@author: nanospin
"""


import qcodes as qc
import os
import time
from datetime import date
import logging
from qcodes.dataset.measurements import Measurement, DataSaver
from qcodes.dataset.plotting import plot_by_id
from qcodes.dataset.data_set import new_data_set, ParamSpec, DataSet, load_by_id 
from qcodes.dataset.data_export import get_data_by_id
#from qcodes.dataset.data_set.DataSet import get_parameter_data
from qcodes.dataset.experiment_container import new_experiment, load_experiment_by_name, experiments, load_experiment
import matplotlib.pyplot as plt
import numpy as np
import pyvisa


vna.power(-5)
vna.start(300e3)
vna.stop(14e9)
vna.points(100e3)
vna.trace("S11")

vna.if_bandwidth(100e3)
vna.averages_enabled(True)
vna.averages(2)

meas = Measurement()
meas.register_parameter(vna.magnitude)

with meas.run() as datasaver: 
    mag = vna.magnitude()
    datasaver.add_result((vna.magnitude, mag))
    
plot_by_id(datasaver.run_id)

vna.sweep_mode.set('CONT')
