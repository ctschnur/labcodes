# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 10:45:43 2020

@author: nanospin
"""

import numpy as np
import lmfit

from plottr import QtWidgets
from plottr.data.datadict import DataDictBase, MeshgridDataDict
from plottr.gui.widgets import makeFlowchartWithPlotWindow
from plottr.node.dim_reducer import XYSelector
from plottr.node.autonode import autonode

from plottr import QtGui, QtCore, Flowchart

app = QtGui.QApplication([])