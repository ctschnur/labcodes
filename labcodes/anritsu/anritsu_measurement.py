from labcodes.drivers.Anritsu_MS46522B import Anritsu_MS46522B

import qcodes as qc
import os
import time
from datetime import date

from qcodes.dataset.measurements import Measurement  #, DataSaver
from qcodes.dataset.plotting import plot_by_id
from qcodes.dataset.experiment_container import load_experiment_by_name, new_experiment  #, experiments, load_experiment
import matplotlib.pyplot as plt
import numpy as np

import logging  # general logging package
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

from qcodes.instrument.base import Instrument


class AnritsuMeasurement:
    """ Module for the whole measurement """
    
    def __init__(self): 
        """ 1. setup the VNA as an instrument (if it's not already setup) 
            2. specify experimental parameters 
            3. specify paths of the target files: 
               database file and a new folder with raw (txt, png) files """

        self.vna_name = "VNA_Anritsu"
        self.vna_class = Anritsu_MS46522B  # this is a qcodes VisaInstrument (interface between visa and qcodes)
        self.vna_address = "TCPIP0::169.254.235.118::5001::SOCKET"
        # "TCPIP0::169.254.81.17::5001::SOCKET"
        # "TCPIP0::169.254.235.118::5001::SOCKET"  # "TCPIP0::maip-franck::hislip0,4880::INSTR"

        # (# 'VNA', 'TCPIP0::169.254.235.118::5001::SOCKET',
        # 50e6, 20e9, -30, 30, 2  # )

        # -- check if instrument 'VNA' already exists. If not, create it
        if Instrument.exist(self.vna_name, self.vna_class): 
            # an instrument is created by qcodes in a global context, 
            # from which it can be retrieved manually using find_instrument
            self.vna = Instrument.find_instrument(self.vna_name, self.vna_class)
        else:
            if self.vna_class == Anritsu_MS46522B:
                self.vna = self.vna_class(self.vna_name, self.vna_address,
                                          50e6, 20e9, -30, 30, 2)
            else:
                exit(1)
        
        # -- name the experiment -> automatic file names
        self.exp_name = 'Anritsu_Something'  # name used by qcodes
        self.cooldown_date = '20-09-21'
        self.sample_name = 'sample_not_important'

        self.numberofpoints=2001  #number of measurement points
        self.vnapower=13   #applied power
        self.start_frequency=3.4e9   #3.387015e9#6.608e9-3.5e6    #start frequency of sweep
        self.stop_frequency=7.4e9  #3.387065e9#6.611e9 +3.5e6    #stop frequency of sweep
        self.frequency_span=self.stop_frequency-self.start_frequency
        self.center_frequency=(self.stop_frequency-self.start_frequency)/2. + self.start_frequency			#just used for power sweep
        self.measuredtrace='S21'   #spectral density measured between port 1 and 2
        self.ifbandwidth=100   #IF Bandwidth, must be in (10,30,50,70,100,300,500,700,1000,3000,5000,7000,10000)Hz
        self.powersweepstart=-30    #start for power sweep
        self.powersweepstop=20    #stop for powersweep
        self.powersweepnum=6    #number of power sweeps (perhaps +/-1) MUST BE AN EVEN NUMBER AT LEAST 6

        # # -- set experiment parameters (global constants, used in different measurement functions)
        # self.numberofpoints = 50 # 2001  # number of measurement points
        # self.vnapower = -10  # applied power
        # self.start_frequency = 300e3  # 3.7e9  #3.387015e9 #6.608e9-3.5e6  # start frequency of sweep
        # self.stop_frequency = 13.5e9  # 5.7e9  #3.387065e9 #6.611e9 +3.5e6  # stop frequency of sweep
        # self.frequency_span = self.stop_frequency - self.start_frequency
        # self.center_frequency = (self.stop_frequency - self.start_frequency)/2. + self.start_frequency  # just used for power sweep
        # self.measuredtrace='S21'  # spectral density measured between port 1 and 2
        # self.ifbandwidth=10  # IF Bandwidth, must be in (10,30,50,70,100,300,500,700,1000,3000,5000,7000,10000)Hz
        # self.powersweepstart=-30  # start for power sweep
        # self.powersweepstop=13  # stop for powersweep
        # self.powersweepnum=3  # number of power sweeps (perhaps +/-1) MUST BE AN EVEN NUMBER AT LEAST 6
        # # groupdelayref=0.0000000225
        # # vna.groupdelay.set(groupdelayref)#resets to 0 instead of working -> rounding to 0
        # # print(vna.groupdelay.get())
        
        self.create_database_experiment_and_folders()
        
        # self.ask_what_to_do()
        
    def get_smatrix_elem_str_from_active_trace_number(self): 
        """ merely a convention to stick by """
        traces_and_smatrix_elems = [(1, "S11"), 
                                    (2, "S12"), 
                                    (3, "S21"), 
                                    (4, "S22")]
        for key, val in traces_and_smatrix_elems: 
            if key == self.vna.active_trace.get(): 
                return val
            
        print("not a vaild trace number")
        exit(1)
        

    def take_screen_anritsu_four_traces(self):   
        # self.vna.active_trace.set(False)  # is this needed at all?
    
        meas = Measurement()  # qcodes measurement
        
        # self.vna.auto_sweep(False)

        # from qcodes import Parameter
        # smatrix_elem_str = Parameter("smatrix_elem", self.vna)
        
        traces = self.vna.traces
        
        for trace in traces:
            meas.register_parameter(trace.trace, paramtype="text")  # this is actually the label "S11, S12, ..." of the trace
            
            meas.register_parameter(trace.real)
            meas.register_parameter(trace.imaginary)
        
            meas.register_parameter(trace.magnitude)
            meas.register_parameter(trace.phase)
        
        # actually get the data
        with meas.run() as datasaver:  # try to run the measurement (? but this doesn't yet write to the database)
        
            data = []
            for trace in traces:
                # self.vna.active_trace.set(n)  # there may be even 4 traces (S-matrix elements)
                # self.vna.traces.tr1.run_sweep()
                
                # smatrix_elem = self.vna.smatrix_elem()
                
                tr = trace.trace()
                
                imag = trace.imaginary()
                real = trace.real()
        
                mag = trace.magnitude()
                phase = trace.phase()
                
                data.append((trace.trace, tr))
                data.append((trace.imaginary, imag))
                data.append((trace.real, real))
                data.append((trace.magnitude, mag))
                data.append((trace.phase, phase))
            
            # import pdb; pdb.set_trace()
            
            datasaver.add_result(*data)
            dataid = datasaver.run_id

        plot_by_id(dataid)


    def record_S21_sweep_power_sweep_frequency(self):
        
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
                
        plot_by_id(datasaver.run_id)

        self.set_of_parameter_data = datasaver.dataset.get_parameter_data()


    def ask_what_to_do(self):
        print("self.vna.power.get(): ", self.vna.power.get())
        program_part = int( input("Choose your sequence: \n  1. take_screen_tim_anritsu\n  2. record S21, sweep power and frequency\n"))
        time.sleep(1)

        if program_part==1:
            self.take_screen_tim_anritsu()
        elif program_part==2:
            self.record_S21_sweep_power_sweep_frequency()
        else:
            print("wrong choice")
            exit(1)

        # print(self.vna.groupdelay.get())
        print("self.vna.power.get(): ", self.vna.power.get())
        print("self.vna.points.get(): ", self.vna.points.get())

        self.vna.sweep_mode.set('CONT')


    def create_database_experiment_and_folders(self):
        # -- set the path where the raw data should be saved to (pngs, txts)
        # self.raw_path = ('C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\chris\\keysight_tests_data' +
        #                  '\\' + self.cooldown_date + '_' + self.sample_name + '\\'
        #                  'raw')

        # qc.config["core"]["db_location"] = (
        #         os.path.join('C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\chris\\keysight_tests_data',
        #                      'keysight_tests.db'))

        # self.raw_path = 'C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\Data\\'+self.cooldown_date+'_'+self.sample_name+"\\raw\\"

        # qc.config["core"]["db_location"] = (
        #     os.path.join('C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\Data', 'experiments.db'))
        
        # set the .db path
        qc.config["core"]["db_location"] = (
            os.path.join('C:\\Users\\nanospin\\Desktop\\test.db'))


        # store a qcodesrc file with the loaded .db path to the measurements folder
        # qc.config.save_config(
        #         os.path.join("C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements", ".qcodesrc"))

        # -- check if in the standard folder -see qcodes config file- an experiment with exp_name already exists
        #    if not, create a new folder at path
        #    if so, just print the last exp. ID and go on
        try:
            # qcodes interface of loading an experiment:
            # -- tries to connect to a database (specificed in config data structure) and searches for the exp_name
            self.exp = load_experiment_by_name(self.exp_name, sample=self.sample_name)
            print('Experiment loaded. Last ID no: ', self.exp.last_counter)  # keep track of the experiment number
        except ValueError:
            print("Experiment name `", self.exp_name, "` with sample name `", self.sample_name, "` not found in ",
                  qc.config["core"]["db_location"])

            print('Starting new experiment.')
            self.exp = new_experiment(self.exp_name, self.sample_name)

        #     os.makedirs(self.raw_path, exist_ok=True)

        # # ---- always create a new folder for each day of taking measurements
        # self.raw_path_with_date = os.path.join(self.raw_path, date.today().strftime("%y-%m-%d"))

        # if not os.path.isdir(self.raw_path_with_date):
        #     os.makedirs(self.raw_path_with_date, exist_ok=True)  # force-create the directory

if __name__ == '__main__':
    am = AnritsuMeasurement()
    print("m created")
    # m.record_vna_screen()
