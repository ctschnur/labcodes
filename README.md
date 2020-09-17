# QCODES files for running an experiment in the VNA+SG+Fridge setup

## Typical setup on windows: 
Open Spyder (which is installed in a specific virtual environment called 'qcodes' using `pip install spyder`). 
```
C:\Users\nanospin\AppData\Local\Continuum\anaconda3\envs\qcodes\pythonw.exe
```
To check which environment is active, run
```
import sys; print(sys.executable)
```

To list all environments on the computer, type 
```
conda env list 
``` 
in the Anaconda Prompt (not the standard `cmd.exe`). 
This will also show the currently active conda virtual environment of the opened Anaconda Prompt (marked by *). 

## installing spyder 
Spyder needs to be installed with the command
```
conda install -c anaconda spyder
```
Using 
```
pip install spyder
```
resulted in an installation where 
- `where spyder` didn't show the spyder package in the conda environment
- spyder didn't access the python command of it's environment 

## opening up a new instance of spyder with a new indepdentent ipython kernel
Go to a cmd, activate the desired conda virtual environment, then run
```
where spyder
``` 
to check that it will be launched from the desired environment. Then run
```
spyder --new-instance
```
to open up spyder in a new instance. If you close that terminal, the spyder window will also close!

When relaunching the spyder kernel and having a file open, spyder seems to guess the working directory to 
be the same as the file. You can check the working directory by typing
```
import os; os.getcwd()
```


## Debugging workflow
In Spyder, the usual approach of simply writing 
```
import ipdb; ipdb.set_trace()
```
wherever one wants to interact with the code is not well supported. Instead, spyder has it's own way of calling 
`ipdb`, through it's debug functions. 
Setting a breakpoint: double click on the left side of a line of code. 
Then, press `Ctrl+F5` to debug until that point. 
From that point on, one can actually use the usual ipdb commands in the console window 
(like n for next line, s for step into and c for continue). 
That way, Spyder will even highlight the current line that is being debugged, in it's editor window.


## installing qcodes
Make sure Anaconda is installed (https://docs.anaconda.com/anaconda/install/). 
Setup a conda environment tuned for qcodes: follow the `Installing QCoDeS from GitHub` section 
(https://qcodes.github.io/Qcodes/start/index.html#installing-qcodes-from-github).
The qcodes drivers often have pyvisa (https://github.com/pyvisa/pyvisa) as a dependency. 
pyvisa depends again on a backend like pyvisa-py (https://github.com/pyvisa/pyvisa-py) or 
specific proprietary software from NI, Keysight, etc..
(? This package can only be download by national instruments with registering, but for free. 
Copy the downloaded pyvisa module as pyvisa-py in C:\Users\nanospin\AppData\Local\Continuum\anaconda3\envs\qcodes\Lib\site-packages)

### try to setup the Keysight in the old qcodes environment
(without modifying any software, since the old qcodes environment is key, to take data)
- initialization works: 
```
vna = Keysight_P9373A("VNA", "TCPIP0::maip-franck::hislip0,4880::INSTR", 
                      50e6, 20e9, -30, 30, 2)
```
However, nothing shows up on the screen of the VNA. Reason: choose a valid range of frequency and power values. 
They are automatically set when restarting the VNA and opening the `Network Analyzer` software and can be looked up 
under Stimulus -> Sweep Setup. Accordingly,
```
vna = Keysight_P9373A("VNA", "TCPIP0::maip-franck::hislip0,4880::INSTR", 
                      300e3, 14e9, -43, +12, 2)
```
shows something on the screen. 

## setting up a view of both LogM and Phase in the Network Analyzer
Right-click on the trace's heading and select the desired S-Matrix element (S11 will show a signal if nothing is connected to the ports). 
To show the Magnitude/Phase/Im/Re parts: right click trace heading -> Format -> [x]. 
To add a window below with the phase: Instrument -> Window -> Add Window -> New Trace + Window. Then Format -> Phase. 

## taking data from the Keysight


## Qcodes config file
A file called `qcodesrc.json` can potentially be found in many places, e.g.: 
- in the home folder `C:\Users\[username]` 
- in python's current working directory `import os; print(os.getcwd())`
or somewhere else. To check which configuration file qcodes has loaded, call
```
qc.config
```
There might even be a list of many `qcodesrc.json` files in several locations. 
If two of them have an entry for e.g. `db_location`, the file occuring first 
in the list will be prevalent. 

## VISA/Pyvisa
This package should allow to find names and addresses of connected hardware 
devices, which must be known for qcodes to initialize the device like e.g.
```
VNA.VNABase(self.vna_name, 'TCPIP0::169.254.235.118::5001::SOCKET', 
                                   50e6, 20e9, -30, 30, 2)
```
The above command creates a `VisaInstrument` (interface betweeen qcodes and
any instrument recognized by visa). (? Internally, all VISA should be doing 
in the above case of the VNA is to communicate via the usual tcp/ip sockets 
to the connected device. If the device is connected via USB, VISA generalizes the set of 
commands for communication, which would be the real utility of the VISA interface.)
For a particular device, there should be instructions on it's website of 
how to connect it to a programming interface, through additional layers, 
like pyvisa. 

To get the ip address of a particular device, either look in the settings of 
the device itself or determine it from what ip address has been added to 
the network, using the command (in windows)
```
arp -a
```

### Anritsu VNA MS46522B
This device is not immediately recognized by pyvisa when following the 
instructions at 
https://dl.cdn-anritsu.com/en-us/test-measurement/files/Manuals/Programming-Manual/10410-00746V.pdf#page=36


### Keysight P9373A VNA  (Streamlined ENA VNA)
Qcodes has a driver for a higher-specs Keysight VNA (PNA) in it's library: 
`N52xx.py`. A specific instantiation is e.g. the `N5230C` VisaInstrument. 

To communicate with the Keysight, connect it's 'usb-c to host pc' port to the data-taking computer. 
In the 'Network Analyzer' software, go to Utility -> System -> System Setup -> Remote Interface and 
enable HiSLIP, then click `Show SCPI Parser Console` and test out some SCPI commands like `*IDN?` and 
see if the device receives them. If they are received, the device's address can be found under `Status` 
in the `SCPI Parser Console`.


# Install `hlab` to a python virtual environment
Activate the virtual environment
```
conda activate qcodes
```
Then point `pip` to the folder of the `setup.py` of the hlab package, 
which can be located anywhere on the system. 
```
pip install -e hlab\environment
```

In `git bash` on windows, after having done
```
source C:/Users/nanospin/AppData/Local/Continuum/anaconda3/etc/profile.d/conda.sh
```
to get the conda command, to view the current conda virtual environment, do
```
conda info --envs
```
and the one marked with the astrisk is the current one. 


# Making sense of the hlab environment

## Preliminary knowledge
The core functions are: 
- do1d, do2d, ...
they run a set of sweeps, characterized by a set of parameters 

The principle should be the following: 
make a text file with unique names for measurement routines; specify only the 
necessary physics in that text file, then automatically execute 
the measurement and write the data to text and jpg files, so that an 
experimentalist can focus on the experiment, not on the data acquisiton code.

## exploring the code
- A config object is created when import
ing hlab

- until 12 Feb 2020: 
  ./analysis: 
  - model fitting functions (for vector networks)
  ./config: 
  - a class that loads a json config file, containing folder paths for scripts and data
  ./data_io: 
  - different files containing helper functions to read in data from different file types (output from e.g. simulation software (sonnet), VNA s2p files (?), 
    downloading things from a seafile server, dealing with csv files, ...)
    -  qc_sweeps.py: 
       abstraction of measurement.run() routine, for an arbitrary amount of parameters
    - dstruct.py: 
      - class data1d, which holds x, y data of a trace, has a function .fit(f) accepting the fit model function, ...
      - class data1d_cmplx, plotting phase and magnitude
  ./plotting
  - customized version of the plottrs inspector, plotting utils
  
  
- Additions until latest release: 

  ./plotting
  - adding capabilities to take horizontal and vertical cut out of 2d data
  
  
## conda_envs
To roll back to working conda environments, yml files are stored here. 

  

