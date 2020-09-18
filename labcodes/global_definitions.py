# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 14:16:19 2020

@author: nanospin
"""

import os
from qcodes.instrument.base import Instrument
import qcodes as qc

# -- set the path where the raw data should be saved to (pngs, txts)
def get_raw_data_root_path(cooldown_date: str,  # [yy/mm/dd], 
                           sample_name: str):
    return ('C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\Data' + 
            '\\' + cooldown_date + '_' + sample_name + '\\' + 'raw')


# set the default path of the .db database
def get_db_default_path(): 
    return os.path.join(
            'C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\Data', 
            'experiments.db')


def get_instruments_file_default_path(): 
    return os.path.join(
            'C:\\Users\\nanospin\\Nextcloud\\Lab-Shared\\measurements\\', 
            'chris\\labcodes\\conf\\instruments.json')