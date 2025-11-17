import os
import json
import random
import math
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om


class ForestCreator(QtWidgets.QDialog):

    # ui def
    # create window for user 
    #add multiple tabs in window for user
    # - tab for tree, rock and mushrom generation and amt for both
    # - tab for sapcing and orientation of objects in the scene
    # - tab for colors, user can also pick colors 
    # at the bottom there will be a create forest button and a clear scene option
    # add status bar at bottom for user

     #def for creating forest, 
    # duplicate assets for scattering around area from user settings
    # add random shuffle too
    # for each of the assets find a place on the plane where they wont overlap
    # if there is an area that is free copy and place the asset there
    # organize assets by groups to keep it organized 

    #def for finding a place on the grid where no other asset is placed
    # to avoid overlapping,


    def __init__(self, parent=None):
        super(ForestCreator, self).__init__(parent)
        self.setWindowTitle("Forest Creator! :D")
        self.setMinimumSize(900, 700)
        self.setObjectName("ForestCreator")

        self.generated_assets = {}
        self.scatter_objects = []

        self.setup_ui()
        self.generate_base_assets()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel("Forest Creator!")
        title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2E8B57;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
                                 QtabWidget::pane { border: 1px solid #C4C4C4; }
                                 QTabBar::tab {background: #F0F0F0; 
                                 padding: 8px 12px; 
                                 margin-right: 2px;}
                                 QTabBar::tab:selected {background: #2e8b57; 
                                 color: white;}""")
        
        self.status_bar(main_layout)
        
    def status_bar(self, layout):
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready to generate forest assets")
        self.status_label.setStyleSheet("padding: 5px; background-color: #F5F5F5; border: 1px solid #DDD;")
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)

    def create_tree(self):
        trunk = cmds.polyCylinder(radius=0.3, height=4, sx=8, sy=4, sz=1,
                                  name="tree_trunk")[0]
        cmds.move(0, 2, 0, trunk)

        foliage = cmds.polySphere(radius=1.5, sx=8, sy=6, name="tree_leaves")[0]
        cmds.move(0, 5, 0, foliage)

        tree_group = cmds.group([trunk, foliage], name="base_tree")
        return tree_group

    def create_rock(self):
        rock = cmds.polyCube(width=1.5, height=0.8, depth=1.2, sx=3, sy=2, sz=3,
                             name="rock")
        cmds.select(rock + ".vtx[0:25]")
        cmds.polyMoveVertex(random=0.3)
        cmds.select(clear=True)

        return rock
    
    def create_mushroom(self):
        stem = cmds.polyCylinder(radius=0.1, height=0.8, sx=6, 
                                 name="mushroom_stem")[0]
        cmds.move(0, 0.4, 0, stem)
        cap = cmds.polyCone(radius=0.4, height=0.2, sx=8, name="mushroom_cap")[0]
        cmds.move(0, 0.9, 0, cap)
        cmds.rotate(180, 0, 0, cap)

        mushroom_group = cmds.group([stem, cap], name="full_mushroom")
        return mushroom_group
    
    def generate_base_assets(self):
        self.status_label.setText("Generating base assets...")
        self.clean_base_assets()

        self.generated_assets['tree'] = self.create_tree()
        self.generated_assets['rock'] = self.create_rock()
        self.generated_assets['mushroom'] = self.create_mushroom()
        self.status_label.setText("Base assets generated!")

    def clean_base_assets(self):
        for asset_name, asset in list(self.generated_assets.items()):
            if cmds.objExists(asset):
                try:
                    cmds.delete(asset)
                except:
                    pass
        self.generated_assets = {}

if __name__ == "__main__":
    creator = ForestCreator()

    tree = creator.create_tree()
    rock = creator.create_rock()
    mushroom = creator.create_mushroom()
    user = creator.setup_ui()
    window = creator.__init__()

