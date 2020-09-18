# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 14:51:48 2020

@author: nanospin
"""

import global_definitions


def qcodes_config_set_test_database(): 
    # set the .db path
    qc.config["core"]["db_location"] = (
            os.path.join('C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\chris\\keysight_tests_data',
                         'keysight_tests.db'))
    
    
def qcodes_config_set_measurement_database(): 
    # set the .db path
    qc.config["core"]["db_location"] = (
            os.path.join("C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\Data\\", 
                         "experiments.db"))
    
    # store a qcodesrc file with the loaded .db path to the measurements folder
    # qc.config.save_config(
    #     os.path.join("C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\chris\\keysight_tests_data", 
    #                  ".qcodesrc"))
    


# -- there is a json file with a list of known instruments and their addresses
import json

def get_known_instruments(known_instruments_file_path=None): 
    """ read from a json file the known instruments with their usual names and
    addresses """
    file_path = None
    
    if known_instruments_file_path: 
        file_path = known_instruments_file_path
    else: 
        file_path = global_definitions.get_instruments_file_default_path()
        
    with open(file_path) as json_file:
        json_data = json.load(json_file)
    
    for instrument in json_data['instruments']:
        print(instrument)
        # print('driver_filepath: ' + instrument['driver_filepath'])

from qcodes.instrument.base import Instrument
from qcodes import VisaInstrument

_active_instruments = []

def get_instrument(qcodes_instrument_driver_class: VisaInstrument, 
                   name: str,
                   address: str): 
    """ this loads the qcodes driver for an instrument. 
        The path of this driver has to be specified. """
    # -- check if instrument 'VNA' already exists. If not, create it
    if Instrument.exist(name, qcodes_instrument_driver_class): 
        # an instrument is created by qcodes in a global context, 
        # from which it can be retrieved manually using find_instrument
        return Instrument.find_instrument(name, qcodes_instrument_driver_class)
    else:
        instrument = qcodes_instrument_driver_class(
                name, address
                # min_freq=300e3, max_freq=13.5e9,
                # min_power=-90, max_power=13,
                # nports=2
                )
        _active_instruments.append(instrument)
        return instrument
    
def remove_instrument(instrument: VisaInstrument): 
    _active_instruments.remove(instrument)
        
def get_instrument_parameters(instrument: VisaInstrument):
    return list(instrument.parameters.keys())

def get_active_instruments(): 
    """ get a list of all active instruments loaded by qcodes """
    return _active_instruments


class Parameter: 
    """  """
    def __init__(self): 

class SettingInstruction:
""" one settingInstruction is e.g. 
- parameter to be set as a function of time
- be able to set these from an 'experiment' file
"""
    def __init__(self, parameter):
        self.parameter = parameter
        

class MeasuringInstruction: 
""" 
- instrument to be used
- several SettingInstructions
- dependent parameter to be measured (as a function of the SettingInstruction
Parameters, or just time !?)
"""

# -- doing a measurement: 
def capture_data_1d(setting_instructions,  
                    measuring_instructions):
    """ capture data from a device where we have one independent variable (1d)
        potentially several dependent variables 
        (like real and imaginary parts of S21)
    """
    