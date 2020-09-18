# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 11:48:16 2020

@author: nanospin

inspired by qcodes/instrument_drivers/Keysight/N5230C.py

"""

import MS46522B

class Anritsu_MS46522B(MS46522B.VNABase):
    def __init__(self,
                 name: str,
                 address: str,
                 *args, 
                 **kwargs):
        super().__init__(
                name,
                address,
                *args, 
                **kwargs)