To use this package from within a conda python environment `qcodes_sandbox`, install it in editable mode from within the package's root directory (`.`).
```
conda activate qcodes_sandbox
pip install -e .
```
Then you can import drivers from any jupyter notebook that runs in this environment.

# Content
In the `drivers` directory, there are the drivers for the Anritsu and the Keysight.
In the `misc_scripts` directory, there are different qcodes routines (e.g. take all traces from the Anritsu device). 
In the `sample_notebooks` directory, there are some notebooks for quick data acquisition. 

# Taking basic measurements
1. Open an instance of Jupyter Notebook running/editing measurement scripts: 
  open up an anaconda powershell prompt and type
  ```
  conda activate qcodes_sandbox
  cd ~
  jupyter notebook
  ```
  Navigate to the data-acquisition notebooks and run them.
  
2. Open an instance of plottr (inspectr) to plot the data arriving in the database: 
  open up an anaconda powershell prompt and type
  ```
  conda activate qcodes_sandbox
  plottr-inspectr
  ```
  then select the database file you want to monitor
  Or pass the database file path as an argument:
  ```
  plottr-inspectr --dbpath "[...]/experiments.db"
  ```

# qcodes
## Installation
Make sure Anaconda is installed (https://docs.anaconda.com/anaconda/install/) and up-to-date. 
Setup a conda environment tuned for qcodes: follow the `Installing QCoDeS from GitHub` section 
(https://qcodes.github.io/Qcodes/start/index.html#installing-qcodes-from-github).
Make sure you install the correct python version (the lastest github release is probably behind 
the latest python, look it up in qcodes' yml file). 
The qcodes drivers often have pyvisa (https://github.com/pyvisa/pyvisa) as a dependency. 
pyvisa depends again on a backend like pyvisa-py (https://github.com/pyvisa/pyvisa-py) or 
specific proprietary software from NI, Keysight, etc.

- install pyvisa: 
```
pip install pyvisa
```

- install pyvisa-py: 
```
pip install pyvisa-py
```

## Usage
### Qcodes config file
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
This tool makes it easy to inspect qcodes databases (.db) and it even reloads new incoming data for quasi-live viewing.
From python, you can run the the inspectr tool (for qcodes db files) 
```
import plottr.apps.inspectr as ir
ir.script()
```
There are other modules named `monitr` and `autoplot` as well, the usefulness of which is not yet clear to me as I am writing this.

## using pyvisa without the qcodes layer
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