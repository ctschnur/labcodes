# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 11:48:16 2020

@author: nanospin

inspired by qcodes\instrument_drivers\Keysight\N5230C.py
"""

from qcodes.instrument.base import Instrument

from N52xx_modified_for_Keysight_P9373A import N52xx

class Keysight_P9373A(N52xx.PNABase):
    def __init__(self, name, address, **kwargs):
        super().__init__(name, address,
                         min_freq=300e3, max_freq=13.5e9,
                         min_power=-90, max_power=13,
                         nports=2,
                         **kwargs)