Notes on data-taking tools, hardware and troubleshooting them in VNA+Fridge experiments. 


The data-taking computer runs windows 10. 

# Sets of software tools
1. A setup *everyone* should be able to use: 
  - Spyder for editing measurement scripts and navigating code
  <!-- - Juyter Notebooks (or jupyter qtconsole REPL) for running the commands to take data -->
  - jupyter console repl (with autocomplete) and activated conda environment from anaconda powershell prompt. 
  - plottr (inspectr) to view the incoming data directly after the data has been written to the database. 
  
  Workflow: 
  1. Make a folder where raw data (`.txt` and `.png`) of each measurement call is stored, in addition to the jupyter notebooks (`.ipynb`) file and possibly other quick data-analysis files; folder should be labelled by date
  2. Open a terminal, activate the desired python virutal environment (e.g. `qcodes_sandbox`) using `conda activate qcodes_sandbox` and start juypter notebook 
  3. Debugging of python code: in a terminal, run `python` and then sequentially run the commands that produce an error. Then, go to where the error occured and insert a breakpoint `import ipdb; ipdb.set_trace();`. Then, run the command again and step through the code with `n`, `s` or `c`. 

2. A setup that *hackers* could use (if it works) and can keep streamlining
  - Emacs as a general editing environment and for navigating code (lsp, c/g/etags)
  - [ ] Juyter Notebooks (server called from within emacs, with selectable virtual environment)
  - [ ] plottr (inspectr) called from within emacs
  - [ ] snapshotting the measurement run (i.e. generate a snapshot string and print it in jupyter (containing hardware settings (qcodes station) and commit hash of the script +indicator if it has been modified after the commit, +info about the python virtual environment (versions of installed packages)))

## Spyder
It should come pre-installed with each conda environment. If not, install it from the conda repos into the environment, not just using pip. Using 
`pip install spyder` resulted in an installation where 
- `where spyder` didn't show the spyder package in the conda environment
- spyder didn't access the python command of it's environment 

From within Spyder, to check which environment is active, run `import sys; print(sys.executable)`. To list all environments on the computer, type `conda env list` in the Anaconda Prompt (not the standard `cmd.exe`). This will also show the currently active conda virtual environment of the opened Anaconda Prompt (marked by *). 

### usage
#### opening up a new instance of spyder with a new indepdentent ipython kernel
Go to a cmd, activate the desired conda virtual environment, then run `where spyder`to check that it will be launched from the desired environment. Then run `spyder --new-instance` to open up spyder in a new instance. If you close that terminal, the spyder window will also close! When relaunching the spyder kernel and having a file open, spyder seems to guess the working directory to be the same as the file. You can check the working directory by typing `import os; os.getcwd()`.

#### debugging code
I prefer interactive debugging in a normal `cmd` or anaconda prompt `cmd`, but it *can* also be done from within Spyder. 
However, in Spyder, the usual approach of simply writing `import ipdb; ipdb.set_trace()` wherever one wants to interact with the code is not well supported. Instead, spyder has it's own way of calling `ipdb`, through it's own debug functions: 
- Setting a breakpoint: double click on the left side of a line of code. 
- Then, press `Ctrl+F5` to debug until that point. 
- From that point on, one can actually use the usual ipdb commands in the console window (like `n` for next line, `s` for step into and `c` for continue). 
That way, Spyder will even highlight the current line that is being debugged, in it's editor window.

## Jupyter notebooks
I found that the autocompletion on windows with jupyter notebook 6.1.1 and conda 4.8.4 worked (surprisingly) reliably. Also, jupyter notebooks are being widely used in practice (just copy-pasting data-acquisition code). At the end you always have a file (consider it a scratchpad) that you would save and re-open if the same data acquisition needs to be run again. Also, jupyter notebooks support breakpoints (`(i)pdb.set_trace()`) surprisingly well (useful for quick-and-dirty debugging of scripts), unlike spyder.

## qcodes
### Installation
Make sure Anaconda is installed (https://docs.anaconda.com/anaconda/install/) and up-to-date. 
Setup a conda environment tuned for qcodes: follow the `Installing QCoDeS from GitHub` section 
(https://qcodes.github.io/Qcodes/start/index.html#installing-qcodes-from-github).
Make sure you install the correct python version (the lastest github release is probably behind 
the latest python, look it up in qcodes' yml file). 
The qcodes drivers often have pyvisa (https://github.com/pyvisa/pyvisa) as a dependency. 
pyvisa depends again on a backend like pyvisa-py (https://github.com/pyvisa/pyvisa-py) or 
specific proprietary software from NI, Keysight, etc..
(? This package can only be download by national instruments with registering, but for free. 
Copy the downloaded pyvisa module as pyvisa-py in C:\Users\nanospin\AppData\Local\Continuum\anaconda3\envs\qcodes\Lib\site-packages)

- install pyvisa: 
```
pip install pyvisa
```

- install pyvisa-py: 
```
pip install pyvisa-py
```

### Usage 
#### Qcodes config file
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

#### snapshots
A snapshot is a json data structure stored alongside the data of a measurement run. To save a snapshot, just add a `Station` and your instruments and outside parameters using `add_component`. Then, add the station to the measurement. 
```
+
+        from qcodes import Station
+
+        station = Station()
+        station.add_component(self.vna)
+
         # import pdb; pdb.set_trace()
-        meas = Measurement()  # qcodes measurement
```
The snapshot will be able to be seen from inside plottr inspectr. 

## Plottr
### inspectr
This tool makes it easy to inspect plottr databases (.db) and even reloads new incoming data for quasi-live viewing.
run the inspectr tool (for qcodes db files) 
```
import plottr.apps.inspectr as ir
ir.script()
```
There are other modules named `monitr` and `autoplot` as well, the usefulness of which is not yet clear to me as I am writing this.

## VISA/Pyvisa (lower-level, required by qcodes)
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

### using pyvisa without the qcodes layer
Some manufacturers provide in their programming manual an example of how to connect hardware to 
the visa library (lower-level than qcodes), e.g. here for a keysight device
```
http://na.support.keysight.com/fieldfox/help/Programming/webhelp/Examples/Python_Example.htm
```
or for an anritsu vna: 
```
https://dl.cdn-anritsu.com/en-us/test-measurement/files/Manuals/Programming-Manual/10410-00746V.pdf#page=36
```

Each manufacturer can have it's own specific visa libraries, e.g. Keysight might have it at a path
```
 Open a VISA resource manager pointing to the installation folder for the Keysight Visa libraries.

rm = visa.ResourceManager('C:\\Program Files (x86)\\IVI Foundation\\VISA\\WinNT\\agvisa\\agbin\\visa32.dll') 
```

but actually, the `visa32.dll` supplied by windows (`C:\\WINDOWS\\system32\\visa32.dll`) worked for me as well. 



## hlab
A collection of tools for data-taking (wrapper around qcodes), fitting and plotting. 

### Installation
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

### Making sense of the hlab environment
- Preliminary knowledge
  The core functions that would be useful are: 
  - do1d, do2d, ...
  they run a set of sweeps, characterized by a set of parameters 

A good-enough workflow would enable the following:
Make a text file with unique names for measurement routines; specify only the 
necessary physics in that text file, then automatically execute 
the measurement and write the data to text and jpg files, so that an 
experimentalist can focus on the experiment, not on the data acquisiton code.

- A config object is created when importing hlab
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


# Data formats based on plain text
## arbitrary parameter/data tensors as a 2d matrix
If a set of parameters are varied independently and measurement values are
acquired, the data (in general a n x m x o x p x... tuple) can be represented 
in a text file as a 2d matrix (by relentless copying of the unchanging parameter
values for every changed parameter value), i.e. each unique combination of 
parameters (or data) is represented by one row in the file (matrix). 

## 3d data as a 2d-image and two other columns
In addition to that, for 3d data (x,y,z), sometimes z-values are stored like 
this in one file (e.g. `z.txt`): 
```
1   3   2
3   5   9
1   9   3
5   3   2
```
with e.g. three columns (number of y-values) and four rows (number of x-values). 
To specify the corresponding x and y values, they have their own files, 
in which there is only one column (or row). The text file `z.txt` is in general better 
human-readable than a flattened (to 2d) tensor, but it only really makes sense 
for 3d data. 


# Hardware 
## Keysight P9373A VNA  (Streamlined ENA VNA)
Qcodes has a driver for a higher-specs Keysight VNA (PNA) in it's library: 
`N52xx.py`. A specific instantiation is e.g. the `N5230C` VisaInstrument. 

To communicate with the Keysight, connect it's 'usb-c to host pc' port to the data-taking computer. 
In the 'Network Analyzer' software, go to Utility -> System -> System Setup -> Remote Interface and 
enable HiSLIP, then click `Show SCPI Parser Console` and test out some SCPI commands like `*IDN?` and 
see if the device receives them. If they are received, the device's address can be found under `Status` 
in the `SCPI Parser Console`.
### setting up a view of both LogM and Phase in the Network Analyzer
Right-click on the trace's heading and select the desired S-Matrix element (S11 will show a signal if nothing is connected to the ports). 
To show the Magnitude/Phase/Im/Re parts: right click trace heading -> Format -> [x]. 
To add a window below with the phase: Instrument -> Window -> Add Window -> New Trace + Window. Then Format -> Phase. 

## Anritsu VNA MS46522B
This device is not immediately recognized by pyvisa when following the 
instructions at 
https://dl.cdn-anritsu.com/en-us/test-measurement/files/Manuals/Programming-Manual/10410-00746V.pdf#page=36

### connecting to the local network via ethernet
When connecting the Anritsu to Ethernet, use the leftmost Ethernet plug (seen from the back). 
There is another one, but this one doesn't seem to work immediately. 

### regaining a responsive on-device GUI
When and after steering this VNA using VISA, the on-device GUI will be greyed out. 
Parallel to that, the `REMOTE` LED next to the on/off button will be on.
Press escape to regain the on-device GUI.

# Troubleshooting
## code stopped working when run after upgrading spyder from version 3 to 4
In Spyder 3, in file `fa.py` one could write:
```
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 14:13:00 2020
"""
a = 1
```

run this using `runfile(...)` (play button in spyder 3)
and when running another file `fb.py`, 

```
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 14:21:10 2020
"""

print(a)
```

it would actually print on the value of `a` (in the jupyter
console). However, in Spyder 4 (with more recent python version),
running `fb.py` with `runfile` will produce a `NameError: name 'a' is
not defined`. Running `print(a)` interactively in the jupyter console
still works, if `a` has been defined in a file ran before. This
behaviour could suggest that it is in general not good style to write
a file like the above `fb.py`, in which something is accessed without
it having been imported or defined at the top of the file. 

## autoload magic in jupyter notebooks
The `%autoload` magic seems tricky. For example, after having already run a cell containing 
```
%load_ext autoreload
%autoreload
```
a second run will actually only give me an error message that the extension has already been loaded, but then it won't run the `%autoload` in my experience! In the particular situation, I received an error about how a VNA parameter actually had not been declared (in QCODES). I was hunting down this error, but then realized that `%autoload` just didn't run. 

## Keysight does not show anything on screen after qcodes initialziation
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

## installing updated qcodes version
Both drivers (Anritsu and Keysight) give a `TypeError` in their drivers during initialization of the instrument. 
This didn't occur in the older qcodes conda environment (which is broken). 

TODO list: 
- backup the old qcodes version
- backup the old pyvisa and pyvisa-py versions
- copy the old pyvisa-py directory (copied from NI?, proprietary?) to the new environment and try again
- go and debug the driver and find the root cause of the TypeError (requires a console and a text editor, one can't debug properly in spyder). 
## reason for updating anaconda
hlab has some functions which need a newer python version than our current qcodes/python setup. 
## debugging qcodes internals: TypeError on initialization of the keysight
After updating qcodes to the following version,
```
$ pip show qcodes
Name: qcodes
Version: 0.17.0+139.g11417d944
Summary: Python-based data acquisition framework developed by the Copenhagen / Delft / Sydney / Microsoft quantum computing consortium
Home-page: https://github.com/QCoDeS/Qcodes
[...]
```
I was not able to initialize a keysight device any more (using the driver in `qcodes/instrument_drivers/Keysight/N52xx.py`), 
since it gave me a `TypeError`, more specifically: 

```
Traceback (most recent call last):
  File "qcodes_keysight_example.py", line 43, in <module>
    pna = N5245A("VNA2", "TCPIP0::maip-franck::hislip0,4880::INSTR",
  File "qcodes_keysight_example.py", line 32, in __init__
    super().__init__(name, address,
  File "c:\users\nanospin\misc\qcodes\qcodes\instrument_drivers\Keysight\N52xx.py", line 422, in __init__
    trace1 = self.traces[0]
  File "c:\users\nanospin\misc\qcodes\qcodes\instrument_drivers\Keysight\N52xx.py", line 471, in traces
    trace_num = self.select_trace_by_name(trace_name)
  File "c:\users\nanospin\misc\qcodes\qcodes\instrument_drivers\Keysight\N52xx.py", line 504, in select_trace_by_name
    self.write(f"CALC:PAR:SEL '{trace_name}'")
  File "c:\users\nanospin\misc\qcodes\qcodes\instrument\base.py", line 712, in write
    raise e
  File "c:\users\nanospin\misc\qcodes\qcodes\instrument\base.py", line 708, in write
    self.write_raw(cmd)
  File "c:\users\nanospin\misc\qcodes\qcodes\instrument\visa.py", line 212, in write_raw
    nr_bytes_written, ret_code = self.visa_handle.write(cmd)
TypeError: ('cannot unpack non-iterable int object', 'writing "CALC:PAR:SEL \'CH1_S11_1\'" to <N5245A: VNA2>')
```

So I tracked it down and indeed, in my case `self.visa_handle.write(cmd)` returned only an `int`, not a tuple!
```
> c:\users\nanospin\appdata\local\continuum\anaconda3\envs\qcodes_sandbox\lib\site-packages\pyvisa\ctwrapper\functions.py(2797)write()
-> return return_count.value, ret
(Pdb) ll
2772    def write(library, session, data):
2773        """Write data to device or interface synchronously.
2774
2775        Corresponds to viWrite function of the VISA library.
2776
2777        Parameters
2778        ----------
2779        library : ctypes.WinDLL or ctypes.CDLL
2780            ctypes wrapped library.
2781        session : VISASession
2782            Unique logical identifier to a session.
2783        data : bytes
2784            Data to be written.
2785
2786        Returns
2787        -------
2788        int
2789            Number of bytes actually transferred
2790        constants.StatusCode
2791            Return value of the library call.
2792
2793        """
2794        return_count = ViUInt32()
2795        # [ViSession, ViBuf, ViUInt32, ViPUInt32]
2796        ret = library.viWrite(session, data, len(data), byref(return_count))
2797 ->     return return_count.value, ret
(Pdb) return_count.value
25
```
I then edited `write_raw` in `qcodes/instrument/visa.py` to account for this case (and not break): 
```
 def write_raw(self, cmd: str) -> None:
        """
        Low-level interface to ``visa_handle.write``.

        Args:
            cmd: The command to send to the instrument.
        """
        with DelayedKeyboardInterrupt():
            self.visa_log.debug(f"Writing: {cmd}")
            response = self.visa_handle.write(cmd)
            nr_bytes_written = None

            if type(response) is tuple and len(response) == 2:
                nr_bytes_written = response[0]
                ret_code = response[1]
                self.check_error(ret_code)
            else:
                nr_bytes_written = response
```
I minimally altered the code to circumvent this error. Now the connection to the device works again.

Trying to make a pull request: 
1. The Qcodes commit that was working was `11417d94437bf37569fc4aa144c7c2ca900411fa`. 
(2. pull latest changes from Github.)
3. create a fork of the current Github repo
4. clone your fork onto your computer
5. create a branch
6. make the change (respect coding guidelines)
7. on github, press the pull request button and comment on why the change should be made

As it turns out, I had a version of pyvisa installed that was too new. Reverting it 
should make things work fine. 

## Rolling back to the most basic Data-Taking Workflow for the Keysight
Open up a text editor to `c:/Users/nanospin/misc/labcodes/labcodes/keysight/keysight_measurement.py`. 
Make changes to setup name, parameters and database files. 
Launch a terminal and run `conda activate qcodes_sandbox`, then run `juypter qtconsole`. 
In the qtconsole, run `%run c:/Users/nanospin/misc/labcodes/labcodes/keysight/keysight_measurement.py`, 
which will always reload the changes made to that file. Sometimes, the `autoreload` magic doesn't work I have found
and in this case, I switch to just `%run`. 

## jupyter console prints characters multiple times in the cmd -> unusable
Solution: just use the anaconda prompt (or even better: the anaconda powershell) instead of the normal cmd. It even comes with autocompletion in the jupyter session!
