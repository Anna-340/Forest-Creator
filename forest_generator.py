import os
import json
import random
import math
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide.QtGui import *
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om


class ForestCreator:

    # ui def
    # create window for user 
    #add multiple tabs in window for user
    # - tab for tree, rock and mushrom generation and amt for both
    # - tab for sapcing and orientation of objects in the scene
    # - tab for colors, user can also pick colors 
    # at the bottom there will be a create forest button and a clear scene option


    #def for creating trees, mushrooms, and rocks using simple geometry,
    #  but just the bare assets

    

