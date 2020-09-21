# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 10:30:05 2019

@author: nanospin
"""

from labcodes.drivers.Keysight_P9373A import Keysight_P9373A

from qcodes.instrument.base import Instrument

import qcodes as qc
import os
import time
from datetime import date
import logging
from qcodes.dataset.measurements import Measurement, DataSaver
from qcodes.dataset.plotting import plot_by_id
# from qcodes.dataset.database import initialise_database
from qcodes.dataset.data_set import new_data_set, ParamSpec, DataSet, load_by_id
from qcodes.dataset.data_export import get_data_by_id
#from qcodes.dataset.data_set.DataSet import get_parameter_data
from qcodes.dataset.experiment_container import new_experiment, load_experiment_by_name, experiments, load_experiment
import matplotlib.pyplot as plt
import numpy as np
import pyvisa

# -- init of measurement device
vna_name = "VNA"
vna_class = Keysight_P9373A  # this is a qcodes VisaInstrument (interface between visa and qcodes)
vna_address = "TCPIP0::maip-franck::hislip0,4880::INSTR"

# import pdb; pdb.set_trace()  # noqa BREAKPOINT

# print("hey")

# Keysight_P9373A("VNA2", "TCPIP0::maip-franck::hislip0,4880::INSTR", 300e3, 14e9, -43, +12, 2)

vna = None

if Instrument.exist(vna_name, vna_class):
    # an instrument is created by qcodes in a global context,
    # from which it can be retrieved manually using find_instrument
    vna = Instrument.find_instrument(vna_name, vna_class)
else:
    vna = vna_class(vna_name, vna_address,
                    300e3, 14e9, -43,
                    +12,  # after +12, frequency and power are not independent any more
                    2)  # init with standard parameters

# -- measurement name and parameters
exp_name = 'keysight_and_qcodes_debugging'
CooldownDate = '20-09-21'
sample_name = 'no_sample'


numberofpoints=200          #number of measurement points
vnapower=0                #applied power
start_frequency=300e3  #3.387015e9#6.608e9-3.5e6         #start frequency of sweep
stop_frequency=14e9  #3.387065e9#6.611e9 +3.5e6        #stop frequency of sweep
frequency_span=stop_frequency-start_frequency
center_frequency=(stop_frequency-start_frequency)/2+start_frequency			#just used for power sweep
measuredtrace='S11'         #spectral density measured between port 1 and 2
ifbandwidth=100             #IF Bandwidth, must be in (10,30,50,70,100,300,500,700,1000,3000,5000,7000,10000)Hz

# for the keysight: must be between -10 and 0 inclusive
powersweepstart=-10        #start for power sweep
powersweepstop=0            #stop for powersweep
powersweepnum=2


# -- storage of all experiment data into database (automatically)
path = ('C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\chris\\keysight_tests_data' +
                 '\\' + CooldownDate + '_' + sample_name + '\\'
                 'raw')
# set the .db path
qc.config["core"]["db_location"] = (
        os.path.join('C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\chris\\keysight_tests_data',
                     'keysight_tests.db'))
# store a qcodesrc file with the loaded .db path to the measurements folder
qc.config.save_config(
        os.path.join("C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\chris\\keysight_tests_data",
                     ".qcodesrc"))
try:
    exp = load_experiment_by_name(exp_name, sample=sample_name)
    print('Experiment loaded. Last ID no:', exp.last_counter)
except ValueError:
    exp = new_experiment(exp_name, sample_name)
    print('Starting new experiment.')
    os.makedirs(path, exist_ok=True)

# -- storage of raw data into png's and txt files (manually later)
if os.path.isdir(path+date.today().strftime("%y-%m-%d")) == False:
    os.makedirs(path+date.today().strftime("%y-%m-%d"), exist_ok=True)
os.chdir(path+date.today().strftime("%y-%m-%d"))

# # import qcodes.instrument_drivers.Anritsu_test.MS46522B as VNA
# # vna= VNA.VNABase('VNA', 'TCPIP0::169.254.235.118::5001::SOCKET', 50e6, 20e9, -30,30,2)
# # import qcodes.instrument_drivers.rohde_schwarz.SGS100A as SG
# # #sg= SG.RohdeSchwarz_SGS100A('SG', 'TCPIP::169.254.206.154::INSTR')
# # #.pna=PNABase.PNATrace('PNABase', 'pna', 'trace_name', 1)
