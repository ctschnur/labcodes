# -*- coding: utf-8 -*-
"""
In this setup, the VNA generates a signal and measures S21 (phase and magnitude) as a function of frequency. 
The fridge is empty and warm, measurement is just noise. 

Procedure: 
    - turn on hardware VNA and check if the program Anritsu Shockline MS4522B registers a signal.
    - Setup an instrument in QCODES
    - run commands from QCODES (over the driver) to the machine: 
        - capture the data which is displayed on the Anritsu's screen
"""

from Keysight_P9373A import Keysight_P9373A

import qcodes as qc
import os
from datetime import date

from qcodes.dataset.measurements import Measurement  #, DataSaver
from qcodes.dataset.plotting import plot_by_id
# from qcodes.dataset.database import initialise_database
# from qcodes.dataset.data_set import new_data_set, ParamSpec, DataSet, load_by_id 
# from qcodes.dataset.data_export import get_data_by_id
# from qcodes.dataset.data_set.DataSet import get_parameter_data
from qcodes.dataset.experiment_container import load_experiment_by_name, new_experiment  #, experiments, load_experiment
import matplotlib.pyplot as plt
import numpy as np
# import pyvisa  # package which allows to control masurement devices independent of interface (USB, Ethernet, ...)

import logging  # general logging package
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

from qcodes.instrument.base import Instrument
# from pathlib import Path


class MeasurementClass:
    """ Module for the whole measurement """
    
    def __init__(self): 
        """ 1. setup the VNA as an instrument (if it's not already setup) 
            2. specify experimental parameters 
            3. specify paths of the target files: 
               database file and a new folder with raw (txt, png) files """
        
        self.vna_name = 'VNA'
        self.vna_class = Keysight_P9373A  # this is a qcodes VisaInstrument (interface between visa and qcodes)
        self.vna_address = "TCPIP0::maip-franck::hislip0,4880::INSTR"
        
        # -- check if instrument 'VNA' already exists. If not, create it
        if Instrument.exist(self.vna_name, self.vna_class): 
            # an instrument is created by qcodes in a global context, 
            # from which it can be retrieved manually using find_instrument
            self.vna = Instrument.find_instrument(self.vna_name, self.vna_class)
        else:
            self.vna = self.vna_class(self.vna_name, self.vna_address, 
                                      50e6, 20e9, -30, 30, 2)
        
        # -- name the experiment -> automatic file names
        self.exp_name = 'Keysight_Noise'  # name used by qcodes
        self.cooldown_date = '15-09-08'
        self.sample_name = 'no_sample'
        
        # -- set experiment parameters (global constants, used in different measurement functions)
        self.numberofpoints = 20 # 2001  # number of measurement points
        self.vnapower = -10  # applied power
        self.start_frequency = 3.7e9  #3.387015e9 #6.608e9-3.5e6  # start frequency of sweep
        self.stop_frequency = 5.7e9  #3.387065e9 #6.611e9 +3.5e6  # stop frequency of sweep
        self.frequency_span = self.stop_frequency - self.start_frequency
        self.center_frequency = (self.stop_frequency - self.start_frequency)/2. + self.start_frequency  # just used for power sweep
        self.measuredtrace='S21'  # spectral density measured between port 1 and 2
        self.ifbandwidth=10  # IF Bandwidth, must be in (10,30,50,70,100,300,500,700,1000,3000,5000,7000,10000)Hz
        self.powersweepstart=-30  # start for power sweep
        self.powersweepstop=20  # stop for powersweep
        self.powersweepnum=6  # number of power sweeps (perhaps +/-1) MUST BE AN EVEN NUMBER AT LEAST 6
        # groupdelayref=0.0000000225
        # vna.groupdelay.set(groupdelayref)#resets to 0 instead of working -> rounding to 0
        # print(vna.groupdelay.get())
        
        
        # -- set the path where the raw data should be saved to (pngs, txts)
        self.raw_path = ('C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\Data' + 
                         '\\' + self.cooldown_date + '_' + self.sample_name + '\\'
                         'raw')
        
        # set the .db path
        qc.config["core"]["db_location"] = (
                os.path.join('C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\Data',
                             'experiments.db'))
        
        # store a qcodesrc file with the loaded .db path to the measurements folder
        qc.config.save_config(
                os.path.join("C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements", ".qcodesrc"))
        
        # -- check if in the standard folder -see qcodes config file- an experiment with exp_name already exists
        #    if not, create a new folder at path
        #    if so, just print the last exp. ID and go on
        try:
            # qcodes interface of loading an experiment: 
            # -- tries to connect to a database (specificed in config data structure) and searches for the exp_name
            self.exp = load_experiment_by_name(self.exp_name, sample=self.sample_name)
            print('Experiment loaded. Last ID no: ', self.exp.last_counter)  # keep track of the experiment number
        except ValueError:
            print("Experiment name ", self.exp_name, " with sample name ", self.sample_name, " not found in ", 
                  qc.config["core"]["db_location"])
            
            print('Starting new experiment.')
            self.exp = new_experiment(self.exp_name, self.sample_name)
            
            os.makedirs(self.raw_path, exist_ok=True)
            
            
        # ---- always create a new folder for each day of taking measurements
        self.raw_path_with_date = os.path.join(self.raw_path, date.today().strftime("%y-%m-%d"))
        
        if not os.path.isdir(self.raw_path_with_date):
            os.makedirs(self.raw_path_with_date, exist_ok=True)  # force-create the directory
        
        # # change working directory to be inside the 
        # os.chdir(raw_path_with_date)

    def record_vna_screen(self):
        numberofpoints = self.vna.points.get()  # get current number of points from VNA settings
        
        # control the vna from inside qcodes -> set a parameter
        self.vna.active_trace.set(False)  # ? is the trace just the screen shown in the ShockLine program?
        
        # -- Get the measurable values from the intrument, through the driver/Qcodes interface, 
        #    which provides access to current parameter and measurement values through methods
        #    of the instrument's instance (-> pretty easy from the user's perspective)
        
        meas = Measurement()  # qcodes measurement
        
        # if S21 is a complex number (? it must be calculated from something real which is actually measured)
        # get it's data (? whole array that is showing at runtime in the window, or last complete sweep (buffered))
        meas.register_parameter(self.vna.real)
        meas.register_parameter(self.vna.imaginary)
        
        # ? aren't these redundant and are just calculated from real and imaginary parts?
        meas.register_parameter(self.vna.magnitude)
        meas.register_parameter(self.vna.phase)
        
        # actually get the data
        
        print("before taking data")
        with meas.run() as datasaver:  # try to run the measurement (? but this doesn't yet write to the database)
            self.vna.active_trace.set(1)  # there are Tr1 and Tr2
            # vna.traces.tr1.run_sweep()
            imag = self.vna.imaginary()
            # vna.active_trace.set(2)
            # vna.traces.tr2.run_sweep()
            
            # call the vna driver's methods to get measurement values
            # parameters, after saving them in a 'runner' (returned from run()), have unique names
            # which can be explored by printing the keys of the runner's dataset (get_parameter_data(...))
            phase = self.vna.phase()
            real = self.vna.real()
            mag = self.vna.magnitude()
            
            # pass pairs of (function, acquired value) to the datasaver (for later saving into the database)
            datasaver.add_result((self.vna.magnitude, mag), 
                                 (self.vna.phase, phase), 
                                 (self.vna.real, real),
                                 (self.vna.imaginary, imag))
            # dataid1 = datasaver.run_id
        
        print("after taking data")
        
        # -- extract data from datasaver
        # datasaver object has been declared in the head of the with block
        # but is still accessible here
        x = datasaver.dataset.get_parameter_data()
        self.export = np.zeros((numberofpoints, 5))
        
        # in the anritsu vna, there are several S21 vs freq graph windows (tr1 and tr2)
        # here, presumably, only tr1 is listened to
        
        # the database keys (below) can be explored by e.g. 
        # just printing the dictionary on the jupyter console
        # these key names are generated in the Anritsu's driver's `traces` function
        self.export[:,0] = list(x['VNA_tr1_magnitude']['VNA_tr1_frequency'])
        self.export[:,1] = list(x['VNA_tr1_magnitude']['VNA_tr1_magnitude'])
        self.export[:,2] = list(x['VNA_tr1_phase']['VNA_tr1_phase'])
        self.export[:,3] = list(x['VNA_tr1_real']['VNA_tr1_real'])
        self.export[:,4] = list(x['VNA_tr1_imaginary']['VNA_tr1_imaginary'])
        
        np.savetxt(
            os.path.join(self.raw_path_with_date,
                                str(datasaver.run_id) + '_nosweep' + '_' + str(self.exp_name) + '.txt'), 
            self.export)  # "folder%i.txt"%+(int(number)+1)
        
        # -- plotting -> qcodes' plotting routine + matplotlib
        plot_by_id(datasaver.run_id)  # qcodes can plot the datasaver data
        
        plt.cla()
        plt.plot(self.export[:,0], self.export[:,1])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude (dB)')
        plt.savefig(os.path.join(self.raw_path_with_date, 
                                 str(datasaver.run_id) + '_nosweep' + '_' + str(self.exp_name) + '_ampl.png'))
        plt.cla()
        
        plt.plot(self.export[:,0], self.export[:,2])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Phase (deg)')
        plt.savefig(os.path.join(self.raw_path_with_date, 
                                 str(datasaver.run_id) + '_nosweep' + '_' + str(self.exp_name) + '_phase.png'))
        
        print("txt and plots written to", self.raw_path_with_date)
        
    
    def measure_frequency_sweep(self
#                                , numberofpoints, 
#                                vnapower, start_frequency, 
#                                stop_frequency, measuredtrace, 
#                                ifbandwidth
                                ):
        """ run a sweep and measure parameters 
            (apparently, record_vna_screen merely takes a momentary capture of the screen. The device itself might 
            be already sweeping automatically (mode of operation would be set by the device itself, not remotely via qcodes), 
            so that record_vna_screen records a part of the last sweep in addition to a part of the current sweep) """
        
        self.vna.sweep_mode.set('CONT')  # look this command up in the anritsu's manual
        
        
        # settting parameters (which are regsitered in a VisaInstrument 
        # class via e.g. add_parameter('power'))
        self.vna.power.set(self.vnapower)
        self.vna.start.set(self.start_frequency)
        self.vna.stop.set(self.stop_frequency)
        self.vna.points.set(self.numberofpoints)
        self.vna.if_bandwidth.set(self.ifbandwidth)
        self.vna.trace.set(self.measuredtrace)
        #self.vna.groupdelay.set(groupdelayref)#does not work yet
        #self.vna.auto_sweep.set(True)
        self.vna.active_trace.set(False)
        
        meas = Measurement()
        meas.register_parameter(self.vna.magnitude)
        meas.register_parameter(self.vna.phase)
        meas.register_parameter(self.vna.real)
        meas.register_parameter(self.vna.imaginary)    
        
        with meas.run() as datasaver:
            self.vna.active_trace.set(1)
            
            # expore the traces object by debugging
            self.vna.traces.tr1.run_sweep()  # may run a sweep again which is not necessary
            imag = self.vna.imaginary() 
            #self.vna.auto_sweep.set(False)
        
            #self.vna.active_trace.set(2)
            #self.vna.traces.tr2.run_sweep()
            phase = self.vna.phase()
            real = self.vna.real()
            mag = self.vna.magnitude()
        
            # print(len(mag))
            datasaver.add_result((self.vna.magnitude, mag),
                                 (self.vna.phase, phase), 
                                 (self.vna.real, real),
                                 (self.vna.imaginary, imag))
        
        x = datasaver.dataset.get_parameter_data()
        
        #print(x)
        self.export = np.zeros((self.numberofpoints, 5))
        self.export[:,0]=list(x['VNA_tr1_magnitude']['VNA_tr1_frequency'])
        self.export[:,1]=list(x['VNA_tr1_magnitude']['VNA_tr1_magnitude'])
        self.export[:,2]=list(x['VNA_tr1_phase']['VNA_tr1_phase'])
        self.export[:,3]=list(x['VNA_tr1_real']['VNA_tr1_real'])
        self.export[:,4]=list(x['VNA_tr1_imaginary']['VNA_tr1_imaginary'])
        
        sweeppower = int(self.vna.power.get())
        
        np.savetxt(os.path.join(self.raw_path_with_date, 
                                (str(datasaver.run_id) + '_sweep' + '_' + 
                                 str(self.exp_name) + '_' + str(sweeppower) + 
                                 'dB' + '.txt')), self.export)
        
        plot_by_id(datasaver.run_id)  # qcodes
        
        self.vna.sweep_mode.set('CONT')  # why setting it here again?
        
        plt.cla()
        plt.plot(self.export[:,0], self.export[:,1])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude (dB)')
        plt.savefig(os.path.join(self.raw_path_with_date,
                     str(datasaver.run_id) + '_sweep' + '_' + 
                     str(self.exp_name) + '_ampl.png'))
        plt.cla()
        
        plt.plot(self.export[:,0], self.export[:,2])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Phase (deg)')
        plt.savefig(os.path.join(self.raw_path_with_date,
                     str(datasaver.run_id) + '_sweep' + '_' + 
                     str(self.exp_name) + '_phase.png'))
        
        print("txt and plots written to", self.raw_path_with_date)
        
        # return None
        #print(export)
        #self.vna.sweep_mode.set('CONT')
        
        
    def measure_power_sweep_and_2d_plot(self, 
#                                 numberofpoints, 
# vnapower, 
#                                center_frequency, frequency_span, 
#                                measuredtrace, ifbandwidth, 
#                                powersweepstart, powersweepstop, 
#                                powersweepnum
                                ): 
        
        # -- setting vna parameters 
        # vna.sweep_mode.set('CONT')
        self.vna.power.set(self.vnapower)
        self.vna.center.set(self.center_frequency)
        self.vna.span.set(self.frequency_span)
        self.vna.points.set(self.numberofpoints)
        self.vna.if_bandwidth.set(self.ifbandwidth)
        self.vna.trace.set(self.measuredtrace)
        self.vna.auto_sweep.set(False)
        
        #vna.groupdelay.set(groupdelayref) #does not work yet
        meas = Measurement()
        meas.register_parameter(self.vna.power)  # register the first independent parameter
        meas.register_parameter(self.vna.real, setpoints=(self.vna.power,))  # register the second independent parameter
        # ^ (? Why would vna.real be an independent parameter?) Does it not get measured (dependent) as a function of freq?
        meas.register_parameter(self.vna.imaginary, setpoints=(self.vna.power,))  # now register the dependent one
        meas.register_parameter(self.vna.phase, setpoints=(self.vna.power,))  # now register the dependent one
        meas.register_parameter(self.vna.magnitude, setpoints=(self.vna.power,))  # now register the dependent one
    
        # -- taking data
        with meas.run() as datasaver:
            for v1 in np.linspace(self.powersweepstart, self.powersweepstop, self.powersweepnum, endpoint=True):
                self.vna.active_trace.set(1)
                
                power = self.vna.power.set(v1)
                
                print(self.vna.power.get())  # check
                
                #vna.auto_sweep.set(False)
                #vna.auto_sweep.set(True)            
                self.vna.traces.tr1.run_sweep()#some bug not taking the last row therefore two sweeps
    
                #power=vna.power()
                #vna.auto_sweep.set(False)
                imag = self.vna.imaginary() 
                real = self.vna.real()
                phase = self.vna.phase()            
                mag = self.vna.magnitude()
    
                #vna.active_trace.set(2)
                #vna.traces.tr2.run_sweep()
                power = self.vna.power()  # should still be the same as a few lines above
                
                #time.sleep(2)
                datasaver.add_result((self.vna.magnitude, mag),
                                     (self.vna.phase, phase),
                                     (self.vna.real, real),
                                     (self.vna.imaginary, imag),
                                     (self.vna.power, power))
                
                print(self.vna.power.get())
                
            
            #time.sleep(0.1)
            #print(x)
            
        x = datasaver.dataset.get_parameter_data()
            
        self.export = np.zeros(((self.numberofpoints)*(self.powersweepnum), 6))
        self.export[:,0] = list(x['VNA_tr1_magnitude']['VNA_tr1_frequency'])
        self.export[:,1] = list(x['VNA_tr1_magnitude']['VNA_tr1_magnitude'])
        self.export[:,2] = list(x['VNA_tr1_phase']['VNA_tr1_phase'])
        self.export[:,3] = list(x['VNA_tr1_real']['VNA_tr1_real'])
        self.export[:,4] = list(x['VNA_tr1_imaginary']['VNA_tr1_imaginary'])
        self.export[:,5] = list(x['VNA_tr1_imaginary']['VNA_power'])
        
        table_ampl = np.zeros((self.numberofpoints + 1, self.powersweepnum+1))
        table_phase = np.zeros((self.numberofpoints + 1, self.powersweepnum+1))
        table_ampl[1:(self.numberofpoints + 1), 0] = self.export[0:(self.numberofpoints), 0]
        table_ampl[0, 1:(self.powersweepnum + 1)] = self.export[0:(len(self.export[:,0]) - 1):self.numberofpoints, 5]
        table_phase[1:(self.numberofpoints + 1), 0] = self.export[0:(self.numberofpoints), 0]
        table_phase[0, 1:(self.powersweepnum + 1)] = self.export[0:(len(self.export[:,0]) - 1):self.numberofpoints, 5]
        
        for i in range(self.powersweepnum):
            table_ampl[1:(self.numberofpoints + 1), i + 1] = self.export[(self.numberofpoints*i):(self.numberofpoints*(i + 1)), 1]
            ampl = table_ampl[1:(self.numberofpoints + 1), i + 1]
            table_phase[1:(self.numberofpoints + 1), i + 1] = self.export[(self.numberofpoints*i):(self.numberofpoints*(i + 1)), 2]
            phase=table_phase[1:(self.numberofpoints + 1), i + 1]
            
        np.savetxt(os.path.join(self.raw_path_with_date,
                     str(datasaver.run_id) + '_powersweep' + '_' + 
                     str(self.exp_name) + '_phase.txt'), self.export)
        
        print(len(self.export[:, 0]))
        #print(self.export)
        
        np.savetxt(os.path.join(self.raw_path_with_date,
                     str(datasaver.run_id) + '_powersweep' + '_' + 
                     str(self.exp_name) + '_all.txt'), self.export)
        
        
        plot_by_id(datasaver.run_id)
        plt.show()
        
        #time.sleep(1)
        #plt.pcolormesh(table_ampl[1:,1:])
        #plt.colorbar()
        #plt.cla()
        #plt.imshow(table_ampl[1:,1:])
        #plt.show()
        #plt.savefig('fig.png',fig)
    

if __name__ == '__main__':
    m = MeasurementClass()
    m.record_vna_screen()
    
    