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
    # add status bar at bottom for user

    #def for creating trees, mushrooms, and rocks using simple geometry,
    #  but just the bare assets for duplicating later
    # tree = cylinder for trunk and editted sphere for leaves
    # rock = editted cube shape
    # mushroom = cylinder for stem and upsidedown cone for cap
    def create_tree(self):

    #def for creating forest, 
    # duplicate assets for scattering around area from user settings
    # add random shuffle too
    # for each of the assets find a place on the plane where they wont overlap
    # if there is an area that is free copy and place the asset there
    # organize assets by groups to keep it organized 

    #def for finding a place on the grid where no other asset is placed
    # to avoid overlapping,



