"""
Program to perform measurements on VNA Anritsu (after having started initialisation_new to connect the device)
1. Before running, change the parameter under PARAMETER FOR MEASUREMENT
2. Change sample_name (this will be the name of the new folder created to save the raw data in the raw data folder) 
3. Change exp_name (the name of the experiment (the saved filename will start with the exp_counter (a unique ID for each experiment), contain the type of sweep performed and the exp_name)
4. When running the program you have four options: This helps to choose between the three functions you can execute. Usually option 3 is best if you want to take all data at once. If you want to try something else then use option 4 to skip the rest of code without executing one of the functions.
5. At the end of the measurement the power of the VNA should be automatically set to -30dBm
comments from 24/05/19
"""
#############################
#needed if run in external console
#import qcodes.instrument_drivers.Anritsu_test.MS46522B as VNA
#vna= VNA.VNABase('VNA', 'TCPIP0::169.254.235.118::5001::SOCKET', 3e9, 9e9, -30,30,2)
############################################################################################

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
######################################

"""
Comments (if deeper changes required):
#auto_sweep= false takes what is directly on the screen
#auto_sweep=true runs a sweep for each parameter
if running a new sweep; the sweep is not live plotted
new sample name will also change exp.last.counter
self._traces.clear() may cause problems
in power sweep: only one sweep for all parameter does not return last power point, therefore individual sweep for phase and magnitude
"""

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


#######################################
#Old school data labelling:
exp_name = 'keysight_debugging'

CooldownDate = '20-09-17'
sample_name = 'no_sample'

#######################################
#PARAMETER FOR MEASUREMENT

numberofpoints=2001          #number of measurement points
vnapower=13                #applied power
start_frequency=300e3  #3.387015e9#6.608e9-3.5e6         #start frequency of sweep
stop_frequency=14e9  #3.387065e9#6.611e9 +3.5e6        #stop frequency of sweep
frequency_span=stop_frequency-start_frequency
center_frequency=(stop_frequency-start_frequency)/2+start_frequency			#just used for power sweep
measuredtrace='S21'         #spectral density measured between port 1 and 2
ifbandwidth=100             #IF Bandwidth, must be in (10,30,50,70,100,300,500,700,1000,3000,5000,7000,10000)Hz
powersweepstart=-30        #start for power sweep
powersweepstop=20            #stop for powersweep
powersweepnum=6            #number of power sweeps (perhaps +/-1) MUST BE AN EVEN NUMBER AT LEAST 6
#groupdelayref=0.0000000225
#vna.groupdelay.set(groupdelayref)#resets to 0 instead of working -> rounding to 0
#print(vna.groupdelay.get())


#######################################

# path = 'C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\Data\\'+CooldownDate+'_'+sample_name+"\\raw\\"


# -- set the path where the raw data should be saved to (pngs, txts)
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

if os.path.isdir(path+date.today().strftime("%y-%m-%d"))==False:
    os.makedirs(path+date.today().strftime("%y-%m-%d"), exist_ok=True)
os.chdir(path+date.today().strftime("%y-%m-%d"))



def simple_measurement(): 
    vna.power(-5)
    vna.start(300e3)
    vna.stop(14e9)
    vna.points(IF BW)
    vna.trace("S11")
    
    vna.if_bandwidth(100e3)
    vna.averages_enabled(True)
    vna.averages(2)
    
    meas = Measurement()
    meas.register_parameter(pna.magnitude)
    
    with meas.run() as datasaver: 
        mag = vna.magnitude()
        datasaver.add_result((vna.magnitude, mag))
        
    plot_by_id(datasaver.run_id)
    
    
    
def take_screen():
    numberofpoints = vna.points.get()
    vna.active_trace.set(False)
    meas = Measurement()
    meas.register_parameter(vna.magnitude)
    meas.register_parameter(vna.phase)
    # meas.register_parameter(vna.real)
    # meas.register_parameter(vna.imaginary)
    
    with meas.run() as datasaver:
        vna.active_trace.set(1)    
        #vna.traces.tr1.run_sweep()    
        imag=vna.imaginary()    
        #vna.active_trace.set(2)
        #vna.traces.tr2.run_sweep()
        phase=vna.phase()
        real=vna.real()
        mag = vna.magnitude()
        datasaver.add_result((vna.magnitude, mag), (vna.phase, phase), (vna.real, real), (vna.imaginary, imag))
        dataid1 = datasaver.run_id
    
    x=datasaver.dataset.get_parameter_data()
    export=np.zeros((numberofpoints,5))
    export[:,0]=list(x['VNA_tr1_magnitude']['VNA_tr1_frequency'])
    export[:,1]=list(x['VNA_tr1_magnitude']['VNA_tr1_magnitude'])
    export[:,2]=list(x['VNA_tr1_phase']['VNA_tr1_phase'])
    export[:,3]=list(x['VNA_tr1_real']['VNA_tr1_real'])
    export[:,4]=list(x['VNA_tr1_imaginary']['VNA_tr1_imaginary'])
    np.savetxt(str(datasaver.run_id)+'_nosweep'+'_'+str(exp_name)+'.txt', export)#"folder%i.txt"%+(int(number)+1)
    print(dataid1)
    plot_by_id(dataid1)
    plt.cla()
    plt.plot(export[:,0],export[:,1])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.savefig(str(datasaver.run_id)+'_nosweep'+'_'+str(exp_name)+'_ampl.png')
    plt.cla()
    plt.plot(export[:,0],export[:,2])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Phase (deg)')
    plt.savefig(str(datasaver.run_id)+'_nosweep'+'_'+str(exp_name)+'_phase.png')
    return (None)

#####################################
#PART 1 TAKE WHAT IS ON THE SCREEN
def function1():
    numberofpoints=vna.points.get()
    vna.active_trace.set(False)
    meas = Measurement()
    meas.register_parameter(vna.magnitude)
    meas.register_parameter(vna.phase)
    # meas.register_parameter(vna.real)
    # meas.register_parameter(vna.imaginary)
    
    with meas.run() as datasaver:
        vna.active_trace.set(1)    
        #vna.traces.tr1.run_sweep()    
        imag=vna.imaginary()    
        #vna.active_trace.set(2)
        #vna.traces.tr2.run_sweep()
        phase=vna.phase()
        real=vna.real()
        mag = vna.magnitude()
        datasaver.add_result((vna.magnitude, mag),(vna.phase, phase), (vna.real, real),(vna.imaginary, imag))
        dataid1 = datasaver.run_id
    
    x=datasaver.dataset.get_parameter_data()
    export=np.zeros((numberofpoints,5))
    export[:,0]=list(x['VNA_tr1_magnitude']['VNA_tr1_frequency'])
    export[:,1]=list(x['VNA_tr1_magnitude']['VNA_tr1_magnitude'])
    export[:,2]=list(x['VNA_tr1_phase']['VNA_tr1_phase'])
    export[:,3]=list(x['VNA_tr1_real']['VNA_tr1_real'])
    export[:,4]=list(x['VNA_tr1_imaginary']['VNA_tr1_imaginary'])
    np.savetxt(str(datasaver.run_id)+'_nosweep'+'_'+str(exp_name)+'.txt', export)#"folder%i.txt"%+(int(number)+1)
    print(dataid1)
    plot_by_id(dataid1)
    plt.cla()
    plt.plot(export[:,0],export[:,1])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.savefig(str(datasaver.run_id)+'_nosweep'+'_'+str(exp_name)+'_ampl.png')
    plt.cla()
    plt.plot(export[:,0],export[:,2])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Phase (deg)')
    plt.savefig(str(datasaver.run_id)+'_nosweep'+'_'+str(exp_name)+'_phase.png')
    return (None)

#####################################
#PART 2 RUN A SWEEP AND MEASURE PARAMETER

def function2(numberofpoints, vnapower, start_frequency, stop_frequency, measuredtrace, ifbandwidth):
    vna.sweep_mode.set('CONT')
    vna.power.set(vnapower)
    vna.start.set(start_frequency)
    vna.stop.set(stop_frequency)
    vna.points.set(numberofpoints)
    vna.if_bandwidth.set(ifbandwidth)
    vna.trace.set(measuredtrace)
    #vna.groupdelay.set(groupdelayref)#does not work yet
    #vna.auto_sweep.set(True)
    vna.active_trace.set(False)
    
    meas = Measurement()  
    meas.register_parameter(vna.magnitude)
    meas.register_parameter(vna.phase)
    meas.register_parameter(vna.real)
    meas.register_parameter(vna.imaginary)    
    with meas.run() as datasaver:
    
        vna.active_trace.set(1)
        vna.traces.tr1.run_sweep()#may run a sweep again which is not necessary
        imag=vna.imaginary() 
        #vna.auto_sweep.set(False)
    
        #vna.active_trace.set(2)
        #vna.traces.tr2.run_sweep()
        phase=vna.phase()
        real=vna.real()
        mag = vna.magnitude()
    
    
        #print(len(mag))
        datasaver.add_result((vna.magnitude, mag),(vna.phase, phase), (vna.real, real),(vna.imaginary, imag))
    
        dataid2= datasaver.run_id
    x=datasaver.dataset.get_parameter_data()
    #print(x)
    export=np.zeros((numberofpoints,5))
    export[:,0]=list(x['VNA_tr1_magnitude']['VNA_tr1_frequency'])
    export[:,1]=list(x['VNA_tr1_magnitude']['VNA_tr1_magnitude'])
    export[:,2]=list(x['VNA_tr1_phase']['VNA_tr1_phase'])
    export[:,3]=list(x['VNA_tr1_real']['VNA_tr1_real'])
    export[:,4]=list(x['VNA_tr1_imaginary']['VNA_tr1_imaginary'])
    sweeppower=int(vna.power.get())
    np.savetxt(str(datasaver.run_id)+'_sweep'+'_'+str(exp_name)+'_'+str(sweeppower)+'dB'+'.txt', export)
    plot_by_id(dataid2)
    vna.sweep_mode.set('CONT')
    plt.cla()
    plt.plot(export[:,0],export[:,1])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.savefig(str(datasaver.run_id)+'_sweep'+'_'+str(exp_name)+'_ampl.png')
    plt.cla()
    plt.plot(export[:,0],export[:,2])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Phase (deg)')
    plt.savefig(str(datasaver.run_id)+'_sweep'+'_'+str(exp_name)+'_phase.png')
    return None
    #print(export)
    #vna.sweep_mode.set('CONT')

############################################################################
#PART 3: POWER SWEEP AND 2D PLOT
#print(x)#
#plot_by_id(dataid1)
def function3(numberofpoints, vnapower, center_frequency, frequency_span, measuredtrace, ifbandwidth,powersweepstart, powersweepstop,powersweepnum):
    #vna.sweep_mode.set('CONT')
    vna.power.set(vnapower)
    vna.center.set(center_frequency)
    vna.span.set(frequency_span)
    vna.points.set(numberofpoints)
    vna.if_bandwidth.set(ifbandwidth)
    vna.trace.set(measuredtrace)
    vna.auto_sweep.set(False)
    #vna.groupdelay.set(groupdelayref)#does not work yet
    meas=Measurement()
    meas.register_parameter(vna.power)  # register the first independent parameter
    meas.register_parameter(vna.real, setpoints=(vna.power,))  # register the second independent parameter
    meas.register_parameter(vna.imaginary, setpoints=(vna.power,))  # now register the dependent one
    meas.register_parameter(vna.phase, setpoints=(vna.power,))  # now register the dependent one
    meas.register_parameter(vna.magnitude, setpoints=(vna.power,))  # now register the dependent one

    with meas.run() as datasaver:
        for v1 in np.linspace(powersweepstart, powersweepstop,powersweepnum, endpoint=True):
            vna.active_trace.set(1)
            power=vna.power.set(v1)
            print(vna.power.get())
            
            #vna.auto_sweep.set(False)
            #vna.auto_sweep.set(True)            
            vna.traces.tr1.run_sweep()#some bug not taking the last row therefore two sweeps

            #power=vna.power()
            #vna.auto_sweep.set(False)
            imag=vna.imaginary() 
            real=vna.real()
            phase=vna.phase()            
            mag = vna.magnitude()

            #vna.active_trace.set(2)
            #vna.traces.tr2.run_sweep()
            power=vna.power()
            #time.sleep(2)
            datasaver.add_result((vna.magnitude, mag),(vna.phase, phase),(vna.real, real),(vna.imaginary, imag),(vna.power,power))
            print(vna.power.get())
            
        dataid3 = datasaver.run_id
        x=datasaver.dataset.get_parameter_data()
        #time.sleep(0.1)
        #print(x)
    export=np.zeros(((numberofpoints)*(powersweepnum),6))
    export[:,0]=list(x['VNA_tr1_magnitude']['VNA_tr1_frequency'])
    export[:,1]=list(x['VNA_tr1_magnitude']['VNA_tr1_magnitude'])
    export[:,2]=list(x['VNA_tr1_phase']['VNA_tr1_phase'])
    export[:,3]=list(x['VNA_tr1_real']['VNA_tr1_real'])
    export[:,4]=list(x['VNA_tr1_imaginary']['VNA_tr1_imaginary'])
    export[:,5]=list(x['VNA_tr1_imaginary']['VNA_power'])
    table_ampl=np.zeros((numberofpoints+1,powersweepnum+1))
    table_phase=np.zeros((numberofpoints+1,powersweepnum+1))
    table_ampl[1:(numberofpoints+1),0]=export[0:(numberofpoints),0]
    table_ampl[0,1:(powersweepnum+1)]=export[0:(len(export[:,0])-1):numberofpoints,5]
    table_phase[1:(numberofpoints+1),0]=export[0:(numberofpoints),0]
    table_phase[0,1:(powersweepnum+1)]=export[0:(len(export[:,0])-1):numberofpoints,5]
    for i in range(powersweepnum):
            table_ampl[1:(numberofpoints+1),i+1]=export[(numberofpoints*i):(numberofpoints*(i+1)),1]
            ampl=table_ampl[1:(numberofpoints+1),i+1]
            table_phase[1:(numberofpoints+1),i+1]=export[(numberofpoints*i):(numberofpoints*(i+1)),2]
            phase=table_phase[1:(numberofpoints+1),i+1]
    np.savetxt(str(datasaver.run_id)+'_powersweep'+'_'+str(exp_name)+'_ampl.txt',table_ampl)
    np.savetxt(str(datasaver.run_id)+'_powersweep'+'_'+str(exp_name)+'_phase.txt',table_phase)
    print(len(export[:,0]))
    #print(export)
    np.savetxt(str(datasaver.run_id)+'_powersweep'+'_'+str(exp_name)+'_all.txt', export)
    fig=plot_by_id(dataid3)
    plt.show()
    #time.sleep(1)
    #plt.pcolormesh(table_ampl[1:,1:])
    #plt.colorbar()
    #plt.cla()
    #plt.imshow(table_ampl[1:,1:])
    #plt.show()
    #plt.savefig('fig.png',fig)
    return None

###############################################################################
    ##########################################################################
    #########################################################################
#PROGRAM START
#print(vna.power.get())
#program_part=int(input("Choose your sequence: 1. Take what is displayed, 2. Do a sweep with measurement parameters, 3. Do a power sweep\n 4. Continue without measurement\n"))
#time.sleep(1)
#if program_part==1:
#    print('test1')
#    function1()
#elif program_part==2:
#    print('test2')
#    function2(numberofpoints, vnapower, start_frequency, stop_frequency, measuredtrace, ifbandwidth)
#    #vna.power.set(-30)
#elif program_part==3:
#    print('test3')
#    function3(numberofpoints, vnapower, center_frequency, frequency_span, measuredtrace, ifbandwidth,powersweepstart, powersweepstop,powersweepnum)
#    vna.power.set(-30)
#elif program_part==4:
#    # print(vna.groupdelay.get())
#    #vna.power.set(-15)
#    #vna.sweep_mode.set('HOLD')
#else:
#    print("Type in number between 1 and 4")

# print(vna.groupdelay.get())
#
#print(vna.power.get())
#print(vna.points.get())
#vna.sweep_mode.set('CONT')

###############################################
#Restoring old data
#print(experiments())#returns list of all experiments stored in dataset
#ex=load_experiment(1)#loads experiment name
#print(ex)
#ds=load_by_id(339)#loads by exp_id
#print(ds)
#print(ds.get_data('VNA_tr1_phase'))#gets data for stored parameter 
#plot_by_id(ds)
#input('done')
#get_data_by_id
# To inspect the config file, use
##################################################
#Change database directory
#configuration = qc.config
#print(f'Using config file from {configuration.current_config_path}')
#print(f'Database location: {configuration["core"]["db_location"]}')
#configuration['core']['db_location'] = 'C:/Users/nanospin/Nextcloud/Shared/measurements/raw_data/experiments.db'
#configuration.save_to_home()
