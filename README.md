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

## Qcodes config file
A file called `qcodesrc.json` can potentially be found in many places, e.g.: 
- in the home folder `C:\Users\[username]` 
- in python's current working directory `import os; print(os.get_cwd())`
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

# Installing git on windows
This code will be managed inside a git repository. In Windows 10, installing 
git is very easy (https://git-scm.com/download/win). This will install a 
shell called `Git Bash`, which is useful as it provides many unix shell commands.

# Dealing with conda environments on windows
Anaconda should install the `Anaconda Prompt`. Inside there, the conda commands
work out-of-the-box: checking out different environments, installing things, etc..
