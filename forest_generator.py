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
        self.collision_spheres = []
        self.managed_groups = []

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

    def create_asset_tab(self):

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
                             name="rock")[0]
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

    def find_valid_pos(self, width, depth, center_x, 
                       center_z, min_spacing, max_attempts):
        
    def get_distributed_pos(self, width, depth, center_x, center_z):
        falloff_type = self.density_falloff.currentText()

        if falloff_type == "Uniform":
            x = random.uniform(center_x - width/2, center_x + width/2)
            z = random.uniform(center_z - depth/2, center_z + depth/2)
        elif falloff_type == "Center":
            radius = min(width, depth) / 2
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, radius) * random.uniform(0, 1)
            x = center_x + math.cos(angle) * dist
            z = center_z + math.sin(angle) * dist
        elif falloff_type == "Edges":
            if random.choice([True, False]):
                x = random.choice([center_x - width/2, center_x + width/2])
                z = random.uniform([center_z - depth/2, center_z + depth/2])
            else:
                x = random.uniform([center_x - width/2, center_x + width/2])
                z = random.choice([center_z - depth/2, center_z + depth/2])
        else:
            x = center_x + random.gauss(0, width/4)
            z = center_z + random.gauss(0, depth/4)
            x = max(center_x - width/2, min(center_x + width/2, x))
            z = max(center_z - depth/2, min(center_z + depth/2, z))
        return x, z
    
    def check_collision(self, x, z, min_spacing):

    def add_collision_sph(self, asset, position):

    def apply_asset_trans(self, asset, position):

    def snap_to_ground(self, asset):
            cmds.makeIdentity(asset, apply=True, translate=True, rotate=True, 
                            scale=True)
            bbox = cmds.exactWorldBoundingBox(asset)
            lowest_point = bbox[1]
            move_amount = -lowest_point
            cmds.move(move_amount, asset, moveY=True, relative=True)

    def clear_previous_scatter(self):
        self.collision_spheres = []

        if self.scatter_objects:
            try:
                existing_objects = [
                    obj for obj in self.scatter_objects if cmds.objExists(obj)]
                if existing_objects:
                    cmds.delete(existing_objects)
                self.scatter_objects = []
            except Exception as err:
                cmds.warning(f"Error clearing previous scatter: {str(err)}")

        for group in self.managed_groups[:]:
            if cmds.objExists(group):
                try:
                    cmds.delete(group)
                    self.managed_groups.remove(group)
                except:
                    pass    

    def clear_scene_dialog(self):
        reply = QMessageBox.question(self, "Confirm Clear Scene",
        "Are you sure you want to clear the forest? You can't undo this.",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
        self.clear_scene()

    def clear_scene(self):
        try:
            self.clear_previous_scatter()
            for asset_name, asset in self.generated_assets.items():
                if cmds.objExists(asset):
                    try:
                        cmds.delete(asset)
                    except:
                        pass

            self.generate_base_assets()
            forest_objects = cmds.ls("Forest_*", "tree_*", "rock_*", "mushroom_*")
            for obj in forest_objects:  
                if cmds.objExists(obj) and obj not in self.generated_assets.values():
                    try:
                        cmds.delete(obj)
                    except:
                        pass
            self.status_label.setTExt("Scene cleared")
        except Exception as e:
            self.status_label.setText(f"Error clearing scene: {str(e)}")
            cmds.warning(f"Scene clearing error: {str(e)}")



if __name__ == "__main__":
    creator = ForestCreator()



