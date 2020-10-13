# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 11:48:16 2020

@author: nanospin

inspired by qcodes/instrument_drivers/Keysight/N5230C.py

"""

from qcodes.instrument.base import Instrument

from qcodes.instrument_drivers.Keysight.N52xx import PNABase

class Keysight_P9373A(PNABase):
    def __init__(self, name, address, 
                 min_freq, max_freq,
                 min_power, max_power,
                 nports, 
                 **kwargs):
        super().__init__(name, address,
                         min_freq=min_freq, max_freq=max_freq,
                         min_power=min_power, max_power=max_power,
                         nports=nports,
                         **kwargs)