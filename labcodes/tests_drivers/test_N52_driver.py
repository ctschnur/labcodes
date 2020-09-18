# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 11:45:43 2020

@author: nanospin
"""

# from . import N52xx

import qcodes.instrument_drivers.Keysight.N52xx as N52xx


from qcodes.dataset.measurements import Measurement, DataSaver

from qcodes.instrument.base import Instrument

class N5230C(N52xx.PNABase):
    def __init__(self, name, address, **kwargs):
        super().__init__(name, address,
                         min_freq=300e3, max_freq=13.5e9,
                         min_power=-90, max_power=13,
                         nports=2,
                         **kwargs)


# vna = VNA.VNABase('VNA', 'TCPIP0::169.254.235.118::5001::SOCKET', 50e6, 20e9, -30,30,2)
        
vna_name = 'VNA'
vna_class = N5230C  # this is a qcodes VisaInstrument (interface between visa and qcodes)

# -- check if instrument 'VNA' already exists. If not, create it
if Instrument.exist(vna_name, vna_class): 
    # an instrument is created by qcodes in a global context, 
    # from which it can be retrieved manually using find_instrument
    vna = Instrument.find_instrument(vna_name, vna_class)
else:
    vna = N5230C(vna_name, "TCPIP0::maip-franck::hislip0,4880::INSTR", 
                           # 50e6, 20e9, -30, 30, 2
                           )

#vna = N5230C('VNA', # 
#             # 'PXI10::0-0.0::INSTR'
#             
#             # , 50e6, 20e9, -30, 30, 2
#             )

#numberofpoints=vna.points.get()
## vna.active_trace.set(False)
#meas = Measurement()
#meas.register_parameter(vna.magnitude)
#meas.register_parameter(vna.phase)
#meas.register_parameter(vna.real)
#meas.register_parameter(vna.imaginary)
#
#with meas.run() as datasaver:
#    vna.active_trace.set(1)    
#    #vna.traces.tr1.run_sweep()    
#    imag=vna.imaginary()    
#    #vna.active_trace.set(2)
#    #vna.traces.tr2.run_sweep()
#    phase=vna.phase()
#    real=vna.real()
#    mag = vna.magnitude()
#    datasaver.add_result((vna.magnitude, mag),(vna.phase, phase), (vna.real, real),(vna.imaginary, imag))
#    dataid1 = datasaver.run_id
#    
#x=datasaver.dataset.get_parameter_data()


#
#
#export=np.zeros((numberofpoints,5))
#export[:,0]=list(x['VNA_tr1_magnitude']['VNA_tr1_frequency'])
#export[:,1]=list(x['VNA_tr1_magnitude']['VNA_tr1_magnitude'])
#export[:,2]=list(x['VNA_tr1_phase']['VNA_tr1_phase'])
#export[:,3]=list(x['VNA_tr1_real']['VNA_tr1_real'])
#export[:,4]=list(x['VNA_tr1_imaginary']['VNA_tr1_imaginary'])
#np.savetxt(str(datasaver.run_id)+'_nosweep'+'_'+str(exp_name)+'.txt', export)#"folder%i.txt"%+(int(number)+1)
#print(dataid1)
#plot_by_id(dataid1)
#plt.cla()
#plt.plot(export[:,0],export[:,1])
#plt.xlabel('Frequency (Hz)')
#plt.ylabel('Magnitude (dB)')
#plt.savefig(str(datasaver.run_id)+'_nosweep'+'_'+str(exp_name)+'_ampl.png')
#plt.cla()
#plt.plot(export[:,0],export[:,2])
#plt.xlabel('Frequency (Hz)')
#plt.ylabel('Phase (deg)')
#plt.savefig(str(datasaver.run_id)+'_nosweep'+'_'+str(exp_name)+'_phase.png')