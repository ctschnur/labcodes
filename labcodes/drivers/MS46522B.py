from typing import Sequence, Union, Any, Tuple, List
import time
import re
import logging

import numpy as np
from pyvisa import VisaIOError, errors
from qcodes import (VisaInstrument, InstrumentChannel, ArrayParameter,
                    ChannelList)
from qcodes.utils.validators import Ints, Numbers, Enum, Bool

logger = logging.getLogger()


class VNASweep(ArrayParameter):
    def __init__(self,
                 name: str,
                 instrument: 'VNABase',
                 **kwargs: Any) -> None:

        super().__init__(name,
                         instrument=instrument,
                         shape=(0,),
                         setpoints=((0,),),
                         **kwargs)

    @property # type: ignore
    def shape(self) -> Sequence[int]: # type: ignore
        if self._instrument is None:
            return (0,)
        return (self._instrument.root_instrument.points(),)
    @shape.setter
    def shape(self, val: Sequence[int]) -> None:
        pass

    @property # type: ignore
    def setpoints(self) -> Sequence: # type: ignore
        if self._instrument is None:
            raise RuntimeError("Cannot return setpoints if not attached "
                               "to instrument")
        start = self._instrument.root_instrument.start()
        stop = self._instrument.root_instrument.stop()
        return (np.linspace(start, stop, self.shape[0]),)
    @setpoints.setter
    def setpoints(self, val: Sequence[int]) -> None:
        pass



class FormattedSweep(VNASweep):
    """
    Mag will run a sweep, including averaging, before returning data.
    As such, wait time in a loop is not needed.
    """
    def __init__(self,
                 name: str,
                 instrument: 'VNABase',
                 sweep_format: str,
                 label: str,
                 unit: str,
                 memory: bool = False) -> None:
        super().__init__(name,
                         instrument=instrument,
                         label=label,
                         unit=unit,
                         setpoint_names=('frequency',),
                         setpoint_labels=('Frequency',),
                         setpoint_units=('Hz',)
                         )
        self.sweep_format = sweep_format
        self.memory = memory


    def get_raw(self) -> Sequence[float]:
        if self._instrument is None:
            raise RuntimeError("Cannot get data without instrument")
        root_instr = self._instrument.root_instrument
        # Check if we should run a new sweep
        if root_instr.auto_sweep():
            print('try new sweep')
            prev_mode = self._instrument.run_sweep()
            print('new sweep complete')
        # Ask for data, setting the format to the requested form
        self._instrument.format(self.sweep_format)
        print('data taken')
        data = root_instr.visa_handle.query_binary_values('CALC:DATA:FDAT?',
                                                          datatype='f',
                                                          is_big_endian=False)
        #data = np.array(data)
        #data1=[]
        #data1.append(data)
        # Restore previous state if it was changed
        if root_instr.auto_sweep():
            root_instr.sweep_mode(prev_mode)
        print('success')
        return data



class VNAPort(InstrumentChannel):
    """
    Allow operations on individual VNA ports.
    Note: This can be expanded to include a large number of extra parameters...
    """

    def __init__(self,
                 parent: 'VNABase',
                 name: str,
                 port: int,
                 min_power: Union[int, float],
                 max_power: Union[int, float]) -> None:
        super().__init__(parent, name)

        self.port = int(port)
        if self.port < 1 or self.port > 2:
            raise ValueError("Port must be between 1 and 2.")
        """
        pow_cmd = f"SOUR:POW{self.port}"
        self.add_parameter("source_power",
                           label="power",
                           unit="dBm",
                           get_cmd=f"{pow_cmd}?",
                           set_cmd=f"{pow_cmd} {{}}",
                           get_parser=float,
                           vals=Numbers(min_value=min_power,
                                        max_value=max_power))
        """
        """

    def _set_power_limits(self,
                          min_power: Union[int, float],
                          max_power: Union[int, float]) -> None:
        """
        #Set port power limits
        """
        self.source_power.vals = Numbers(min_value=min_power,
                                         max_value=max_power)
        """


class VNATrace(InstrumentChannel):
    """
    Allow operations on individual VNA traces.
    """

    def __init__(self,
                 parent: 'VNABase',
                 name: str,
                 trace_name: str,
                 trace_num: int) -> None:
        super().__init__(parent, name)
        self.trace_name = trace_name
        self.trace_num = trace_num

        # Name of parameter (i.e. S11, S21 ...)
        self.add_parameter('trace',
                           label='Trace',
                           get_cmd=':CALC1:PAR:DEF?',
                           set_cmd=':CALC1:PAR:DEF {}')
        # Format
        # Note: Currently parameters that return complex values are not
        # supported as there isn't really a good way of saving them into the
        # dataset
        print("parameters loaded")
        self.add_parameter('Formatoutput',
                           label='Format of Output',
                           get_cmd="FORM:DATA?",
                           get_parser=str,
                           set_cmd="FORM:DATA {}",
                           vals=Enum('REAL', 'ASC', 'REAL32'))
        self.Formatoutput.set('REAL32')
        self.add_parameter('format',
                           label='Format',
                           get_cmd=':CALC:FORM?',
                           set_cmd=':CALC:FORM {}',
                           vals=Enum('MLIN', 'MLOG', 'PHAS','GDEL',
                                     'IMAG', 'REAL'))

        # And a list of individual formats
        self.add_parameter('magnitude',
                           sweep_format='MLOG',
                           label='Magnitude',
                           unit='dB',
                           parameter_class=FormattedSweep)
        self.add_parameter('linear_magnitude',
                           sweep_format='MLIN',
                           label='Magnitude',
                           unit='ratio',
                           parameter_class=FormattedSweep)
        self.add_parameter('phase',
                           sweep_format='PHAS',
                           label='Phase',
                           unit='deg',
                           parameter_class=FormattedSweep)
        self.add_parameter("group_delay",
                           sweep_format='GDEL',
                           label='Group Delay',
                           unit='s',
                           parameter_class=FormattedSweep)
        self.add_parameter('real',
                           sweep_format='REAL',
                           label='Real',
                           unit='Real',
                           parameter_class=FormattedSweep)
        self.add_parameter('imaginary',
                           sweep_format='IMAG',
                           label='Imaginary',
                           unit='Imag',
                           parameter_class=FormattedSweep)


    def run_sweep(self) -> str:
        """
        Run a set of sweeps on the network analyzer.
        Note that this will run all traces on the current channel.
        """
        print('sweep')
        root_instr = self.root_instrument
        # Store previous mode
        prev_mode = root_instr.sweep_mode()
        # Take instrument out of continuous mode, and send triggers equal to
        # the number of averages
        """
        if root_instr.averages_enabled():
            avg = root_instr.averages()
            root_instr.reset_averages()
            root_instr.group_trigger_count(avg)
            root_instr.sweep_mode('SING')#was on GRO
        else:
            root_instr.sweep_mode('SING')
        """
        root_instr.sweep_mode('SING')
        print('single')
        # Once the sweep mode is in hold, we know we're done
        try:
            while root_instr.sweep_mode() =='SING':#!= 'HOLD':
                time.sleep(0.1)
        except KeyboardInterrupt:
            # If the user aborts because (s)he is stuck in the infinite loop
            # mentioned above, provide a hint of what can be wrong.
            msg = "User abort detected. "
            source = root_instr.trigger_source()
            if source == "MAN":
                msg += "The trigger source is manual. Are you sure this is " \
                       "correct? Please set the correct source with the " \
                       "'trigger_source' parameter"
            elif source == "EXT":
                msg += "The trigger source is external. Is the trigger " \
                       "source functional?"
            logger.warning(msg)

        # Return previous mode, incase we want to restore this
        return prev_mode


    """
    def write(self, cmd: str) -> None:
        
        #Select correct trace before querying
        
        self.root_instrument.active_trace(self.trace_num)
        super().write(cmd)



    def ask(self, cmd: str) -> str:
        
        #Select correct trace before querying
        
        self.root_instrument.active_trace(self.trace_num)
        return super().ask(cmd)
    """
    """
    def _Sparam(self) -> str:
        #Extrace S_parameter from returned VNA format
        paramspec = self.root_instrument.get_trace_catalog()
        specs = paramspec.split(',')
        for spec_ind in range(len(specs)//2):
            name, param = specs[spec_ind*2:(spec_ind+1)*2]
            if name == self.trace_name:
                return param
        raise RuntimeError("Can't find selected trace on the VNA")
    

    def _set_Sparam(self, val: str) -> None:
        
        #Set an S-parameter, in the format S<a><b>, where a and b
        #can range from 1-4
        
        if not re.match("S[1-2][1-2]", val):
            raise ValueError("Invalid S parameter spec")
        self.write(f"CALC:PAR:DEF \"{val}\"")
    """


class VNABase(VisaInstrument):
    """

    Note: Currently this driver only expects a single channel on the VNA. We
          can handle multiple traces, but using traces across multiple channels
          may have unexpected results.
    """

    def __init__(self,
                 name: str,
                 address: str,
                 # Set frequency ranges
                 min_freq: Union[int, float], max_freq: Union[int, float],
                 # Set power ranges
                 min_power: Union[int, float], max_power: Union[int, float],
                 nports: int, # Number of ports on the VNA
                 **kwargs: Any) -> None:
        super().__init__(name, address, terminator='\n', **kwargs)
        self.min_freq = min_freq
        self.max_freq = max_freq

        #Ports
        ports = ChannelList(self, "VNAPorts", VNAPort)
        for port_num in range(1, nports+1):
            port = VNAPort(self, f"port{port_num}", port_num,
                           min_power, max_power)
            ports.append(port)
            self.add_submodule(f"port{port_num}", port)
        ports.lock()
        self.add_submodule("ports", ports)
        
        # Drive power#only low and high
        self.add_parameter('power',
                           label='Power',
                           get_cmd=':SOUR:POW:PORT?',
                           get_parser=float,
                           set_parser=float,
                           set_cmd='SOUR:POW:PORT {:.2f}',
                           unit='dBm',
                           vals=Numbers(-30,30))
        """
        self.add_parameter(name='power',
                           label='Power',
                           unit='dBm',
                           get_cmd=':SENS:FSEGM:POW:PORT1?',
                           set_cmd=':SENS:FSEGM:POW:PORT1 {:.4f}',
                           get_parser=float,
                           set_parser=float,
                           vals=Numbers(-30, 30))
        """
        self.add_parameter(name='frequencyList',
                           label='Frequency list',
                           unit='Hz',
                           get_cmd=':SENS:FREQ:DATA?',
                           set_cmd=':SENS:FREQ:DATA {:.4f}',
                           get_parser=float,
                           set_parser=float,
                           vals=Numbers(300e3, 20e9))
        # IF bandwidth
        
        self.add_parameter(name='if_bandwidth',
                           label='Intermediate Frequency Bandwidth',
                           unit='Hz',
                           get_cmd=':SENS:BWID?',
                           set_cmd=':SENS:BWID {}',
                           get_parser=float,
                           set_parser=float,
                           vals=Enum(10,20,30,50,70,100,200,300,500,700,1000,3000,5000,7000,10000))
        """
        # Number of averages (also resets averages)
        self.add_parameter('averages_enabled',
                           label='Averages Enabled',
                           get_cmd="SENS:AVER?",
                           set_cmd="SENS:AVER {}",
                           val_mapping={True: '1', False: '0'})
        self.add_parameter('averages',
                           label='Averages',
                           get_cmd='SENS:AVER:COUN?',
                           get_parser=int,
                           set_cmd='SENS:AVER:COUN {:d}',
                           unit='',
                           vals=Numbers(min_value=1, max_value=65536))
        """

        # Setting frequency range
       
        self.add_parameter(name='start',
                           label='Start frequency',
                           unit='Hz',
                           get_cmd=':SENS:FREQ:STAR?',
                           set_cmd=':SENS:FREQ:STAR {:.4f}',
                           get_parser=float,
                           set_parser=float,
                           vals=Numbers(min_value=min_freq,
                                        max_value=max_freq))
        
        self.add_parameter(name='stop',
                           label='Stop frequency',
                           unit='Hz',
                           get_cmd=':SENS:FREQ:STOP?',
                           set_cmd=':SENS:FREQ:STOP {:.4f}',
                           get_parser=float,
                           set_parser=float,
                           vals=Numbers(min_value=min_freq,
                                        max_value=max_freq))
        
        self.add_parameter(name='center',
                           label='Center frequency',
                           unit='Hz',
                           get_cmd=':SENS:FREQ:CENT?',
                           set_cmd=':SENS:FREQ:CENT {:.4f}',
                           get_parser=float,
                           set_parser=float,
                           vals=Numbers(min_value=min_freq,
                                        max_value=max_freq))
        self.add_parameter(name='span',
                           label='Frequency span',
                           unit='Hz',
                           get_cmd=':SENS:FREQ:SPAN?',
                           set_cmd=':SENS:FREQ:SPAN {:.4f}',
                           get_parser=float,
                           set_parser=float,
                           vals=Numbers(min_value=100,
                                        max_value=20e9))
        self.add_parameter(name='groupdelay',
                           label='group delay in reference plane subsystem',
                           unit='s',
                           get_cmd=':SENS:CORR:EXT:PORT1?',
                           set_cmd=':SENS:CORR:EXT:PORT1 {:.4f}',
                           get_parser=float,
                           set_parser=float,
                           )
       

        # Number of points in a sweep
        
        self.add_parameter(name='points',
                           label='Number of measurement points',
                           unit='',
                           get_cmd=':SENS:SWE:POIN?',
                           set_cmd=':SENS:SWE:POIN {}',
                           get_parser=int,
                           set_parser=int,
                           vals=Numbers(2, 20001))

        # Sweep Time
        self.add_parameter('sweep_time',
                           label='Time',
                           get_cmd='SENS:SWE:TIME?',
                           get_parser=float,
                           unit='s',
                           vals=Numbers(0, 1e6))
        
        # Sweep Mode
        
        self.add_parameter(name = 'sweep_mode',
                           label = 'Hold_Function',
                           get_cmd=':SENS:HOLD:FUNC?',
                           set_cmd=':SENS:HOLD:FUNC {}',
                           get_parser=str,
                           vals=Enum('HOLD', 'hold', 'CONT','continuous', 'SING', 'single'))
        """
        # Group trigger count
        self.add_parameter('group_trigger_count',
                           get_cmd="SENS:SWE:GRO:COUN?",
                           get_parser=int,
                           set_cmd="SENS:SWE:GRO:COUN {}",
                           vals=Ints(1, 2000000))
        # Trigger Source
        self.add_parameter('trigger_source',
                           get_cmd="TRIG:SOUR?",
                           set_cmd="TRIG:SOUR {}",
                           vals=Enum("EXT", "IMM", "MAN"))
        """

        # Traces
        self.add_parameter('active_trace',
                           label='Active Trace',
                           get_cmd="CALC1:PAR:SEL?",
                           get_parser=int,
                           set_cmd="CALC1:PAR{}:SEL")
        """
        self.add_parameter('active_trace',
                           label='Active Trace',
                           get_cmd="CALC1:PAR:MNUM?",
                           get_parser=int,
                           set_cmd="CALC1:PAR:MNUM {}",
                           vals=Numbers(min_value=1, max_value=24))
        """
        self.add_parameter('Number_Traces',
                           label='Number Traces',
                           get_cmd="CALC1:PAR:COUN?",
                           get_parser=int,
                           set_cmd="CALC1:PAR:COUN {}")
        # Note: Traces will be accessed through the traces property which
        # updates the channellist to include only active trace numbers

        self._traces = ChannelList(self, "VNATraces", VNATrace)
        self.add_submodule("traces", self._traces)
        #print(self._traces)
        #ChannelList.__getitem__(self, 0)
        # Add shortcuts to first trace
        trace1 = self.traces[0]
        
        for param in trace1.parameters.values():
            self.parameters[param.name] = param
            #print(param)
        # And also add a link to run sweep
        print('in sweep')
        self.run_sweep = trace1.run_sweep
        # Set this trace to be the default (it's possible to end up in a
        # situation where no traces are selected, causing parameter snapshots
        # to fail)
        self.active_trace(trace1.trace_num)
        """
        for i in range(2):
            trace1 = self.traces[i]
            for param in trace1.parameters.values():
                self.parameters[param.name] = param
                print(param)
        # And also add a link to run sweep
            self.run_sweep = trace1.run_sweep
        # Set this trace to be the default (it's possible to end up in a
        # situation where no traces are selected, causing parameter snapshots
        # to fail)
            self.active_trace(trace1.trace_num)
        """
        # Set this trace to be the default (it's possible to end up in a
        # situation where no traces are selected, causing parameter snapshots
        # to fail)


        # Set auto_sweep parameter
        # If we want to return multiple traces per setpoint without sweeping
        # multiple times, we should set this to false
        self.add_parameter('auto_sweep',
                           label='Auto Sweep',
                           set_cmd=None,
                           get_cmd=None,
                           vals=Bool(),
                           initial_value=False)
        

        self.connect_message()

    @property
    def traces(self) -> ChannelList:
        """
        Update channel list with active traces and return the new list
        """
        # Keep track of which trace was active before. This command may fail
        # if no traces were selected.
        """
        try:
            active_trace = self.active_trace()
        except VisaIOError as e:
            if e.error_code == errors.StatusCode.error_timeout:
                active_trace = None
            else:
                raise
        """

        # Get a list of traces from the instrument and fill in the traces list
        parlist = self.Number_Traces.get()
        #print(parlist)
        #self_traces.clear() may cause problems when channellist empty
        self._traces.clear()
        for trace_num in range(1,parlist+1):
            trace_name = str(trace_num)
            #print(trace_name)
            vna_trace = VNATrace(self, "tr{}".format(trace_num),
                                 trace_name, trace_num)
            #print(vna_trace)
            self._traces.append(vna_trace)
        #print(self._traces)

        # Restore the active trace if there was one
        """
        if active_trace:
            self.active_trace(active_trace)
        """

        # Return the list of traces on the instrument
        return self._traces

    """
    def get_options(self) -> List[str]:
        # Query the instrument for what options are installed
        return self.ask('*OPT?').strip('"').split(',')
    """

    """
    def get_trace_catalog(self):
        Get the trace catalog, that is a list of trace and sweep types
        from the VNA.

        The format of the returned trace is:
            trace_name,trace_type,trace_name,trace_type...
        num=self.Number_Traces.get()
        
        return self.ask("CALC:PAR:CAT:EXT?").strip('"')
    """


    """
    def select_trace_by_name(self, trace_name: str) -> int:
       
        #Select a trace on the VNA by name.

       # Returns:
          #  The trace number of the selected trace
        
        self.write(f"CALC:PAR:SEL '{trace_name}'")
        return self.active_trace()
    """



