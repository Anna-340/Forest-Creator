import os
import json
import random
import math
import re
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om


class ForestCreator(QtWidgets.QDialog):

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
                                QTabWidget::pane { border: 1px solid #C4C4C4; }
                                QTabBar::tab {background: #F0F0F0; 
                                padding: 8px 12px; 
                                margin-right: 2px;}
                                QTabBar::tab:selected {background: #2e8b57; 
                                color: white;}""")
        
        self.asset_tab = self.create_asset_tab()
        self.scatter_tab = self.create_scatter_tab()
        self.coloring_tab = self.create_coloring_tab()

        tab_widget.addTab(self.asset_tab, "Asset Generation")
        tab_widget.addTab(self.scatter_tab, "Scattering Controls")
        tab_widget.addTab(self.coloring_tab, "Coloring")

        main_layout.addWidget(tab_widget)
        self.add_action_btns(main_layout)
        self.status_bar(main_layout)
        
    def add_action_btns(self, layout):
        action_layout = QHBoxLayout()

        generate_btn = QPushButton("Create Forest!")
        generate_btn.setStyleSheet("QPushButton { background-color: #8b4513; " \
        "color: white; padding: 8px; }")
        generate_btn.clicked.connect(self.generate_forest)
        action_layout.addWidget(generate_btn)

        clear_btn = QPushButton("Clear Scene")
        clear_btn.setStyleSheet(
            "QPushButton { backgound-color: #8B4513; color: " \
            "white; padding: 8px;}")
        clear_btn.clicked.connect(self.clear_scene_dialog)
        action_layout.addWidget(clear_btn)

        layout.addLayout(action_layout)

    def status_bar(self, layout):
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready to generate forest assets")
        self.status_label.setStyleSheet(
            "padding: 5px; background-color: #F5F5F5; border: 1px solid #DDD;")
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)

    def create_asset_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        controls_group = QGroupBox("Asset Generation Controls")
        controls_layout = QGridLayout(controls_group)

        tree_group = self.create_tree_controls()
        rock_group = self.create_rock_controls()
        mushroom_group = self.create_mushroom_controls()
        controls_layout.addWidget(tree_group, 0, 0)
        controls_layout.addWidget(rock_group, 0, 1)
        controls_layout.addWidget(mushroom_group, 1, 0)

        layout.addWidget(controls_group)
        layout.addStretch()
        return tab

    def create_tree_controls(self):
        group = QGroupBox("Trees")
        layout = QGridLayout(group)
        self.tree_enabled = QCheckBox("Generate Trees")
        self.tree_enabled.setChecked(True)
        layout.addWidget(self.tree_enabled, 0, 0, 1, 2)
        
        layout.addWidget(QLabel("Tree Count:"), 1, 0)
        self.tree_count = QSpinBox()
        self.tree_count.setRange(1, 100)
        self.tree_count.setValue(15)
        layout.addWidget(self.tree_count, 1, 1)

        layout.addWidget(QLabel("Height Variation:"), 2, 0)
        self.tree_height_var = QDoubleSpinBox()
        self.tree_height_var.setRange(0.0, 1.0)
        self.tree_height_var.setValue(0.4)
        self.tree_height_var.setSingleStep(0.1)
        layout.addWidget(self.tree_height_var, 2, 1)

        return group

    def create_rock_controls(self):
        group = QGroupBox("Rocks")
        layout = QGridLayout(group)
        self.rock_enabled = QCheckBox("Generate Rocks")
        self.rock_enabled.setChecked(True)
        layout.addWidget(self.rock_enabled, 0, 0, 1, 2)
        
        layout.addWidget(QLabel("Rock Count:"), 1, 0)
        self.rock_count = QSpinBox()
        self.rock_count.setRange(1, 50)
        self.rock_count.setValue(10)
        layout.addWidget(self.rock_count, 1, 1)

        layout.addWidget(QLabel("Height Variation:"), 2, 0)
        self.rock_size_var = QDoubleSpinBox()
        self.rock_size_var.setRange(0.0, 2.0)
        self.rock_size_var.setValue(0.5)
        layout.addWidget(self.rock_size_var, 2, 1)

        return group

    def create_mushroom_controls(self):
        group = QGroupBox("Mushrooms")
        layout = QGridLayout(group)
        self.mushroom_enabled = QCheckBox("Generate Mushrooms")
        self.mushroom_enabled.setChecked(True)
        layout.addWidget(self.mushroom_enabled, 0, 0, 1, 2)
        
        layout.addWidget(QLabel("Mushroom Count:"), 1, 0)
        self.mushroom_count = QSpinBox()
        self.mushroom_count.setRange(1, 30)
        self.mushroom_count.setValue(8)
        layout.addWidget(self.mushroom_count, 1, 1)

        return group

    def create_scatter_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        dist_group = QGroupBox("Distribution Settings")
        dist_layout = QGridLayout(dist_group)

        dist_layout.addWidget(QLabel("Min Spacing:"), 0, 0)
        self.min_spacing = QDoubleSpinBox()
        self.min_spacing.setRange(0.1, 10.0)
        self.min_spacing.setSuffix(" units")
        dist_layout.addWidget(self.min_spacing, 0, 1)

        dist_layout.addWidget(QLabel("Placement Attempts:"), 1, 0)
        self.placement_attempts = QSpinBox()
        self.placement_attempts.setRange(1, 200)
        self.placement_attempts.setValue(50)
        dist_layout.addWidget(self.placement_attempts, 1, 1)

        dist_layout.addWidget(QLabel("Density Falloff:"), 2, 0)
        self.density_falloff = QComboBox()
        self.density_falloff.addItems(["Uniform", "Center", "Edges", "Random"])
        dist_layout.addWidget(self.density_falloff, 2, 1)
        layout.addWidget(dist_group)

        collision_group = self.create_collision_controls()
        layout.addWidget(collision_group)
        scale_group = self.create_scale_controls()
        layout.addWidget(scale_group)
        layout.addStretch()

        return tab

    def create_collision_controls(self):
        group = QGroupBox("Collision Avoidance")
        layout = QGridLayout(group)

        self.collision_enabled = QCheckBox("Enable Collision Detection")
        self.collision_enabled.setChecked(True)
        layout.addWidget(self.collision_enabled, 0, 0, 1, 2)
        layout.addWidget(QLabel("Collision Radius Multiplier:"), 1, 0)
        self.collision_multiplier = QDoubleSpinBox()
        self.collision_multiplier.setRange(0.5, 3.0)
        self.collision_multiplier.setValue(1.2)
        layout.addWidget(self.collision_multiplier, 1, 1)

        return group

    def create_scale_controls(self):
        group = QGroupBox("Scale & Rotation Variation")
        layout = QGridLayout(group)
        layout.addWidget(QLabel("Global Scale Min:"), 0, 0)
        self.scale_min = QDoubleSpinBox()
        self.scale_min.setRange(0.1, 2.0)
        self.scale_min.setValue(0.7)
        layout.addWidget(self.scale_min, 0, 1)

        layout.addWidget(QLabel("Global Scale Max:"), 1, 0)
        self.scale_max = QDoubleSpinBox()
        self.scale_max.setRange(0.1, 3.0)
        self.scale_max.setValue(1.3)
        layout.addWidget(self.scale_max, 1, 1)

        self.random_rotation = QCheckBox("Random Rotation")
        self.random_rotation.setChecked(True)
        layout.addWidget(self.random_rotation, 2, 0, 1, 2)

        return group
    
    def create_coloring_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        tree_group = self.create_tree_color_controls()
        rock_group = self.create_rock_color_controls()
        mushroom_group = self.create_mushroom_color_controls()
        global_group = self.create_global_color_controls()

        layout.addWidget(tree_group)
        layout.addWidget(rock_group)
        layout.addWidget(mushroom_group)
        layout.addWidget(global_group)
        layout.addStretch()
        return tab

    def create_tree_color_controls(self):
        group = QGroupBox("Tree Coloring")
        layout = QGridLayout(group)

        layout.addWidget(QLabel("Tree Trunk Color:"), 0, 0)
        self.tree_trunk_color_btn = self.create_color_btn("#8B4513", 
                                                          "tree_trunk")
        layout.addWidget(self.tree_trunk_color_btn, 0, 1)

        layout.addWidget(QLabel("Tree Leaves Color:"), 0, 0)
        self.tree_leaves_color_btn = self.create_color_btn("#0E912A", 
                                                           "tree_leaves")
        layout.addWidget(self.tree_leaves_color_btn, 0, 1)

        apply_btn = QPushButton("Apply Tree Colors")
        apply_btn.clicked.connect(self.apply_tree_colors)
        layout.addWidget(apply_btn, 2, 0, 1, 2)
        
        return group

    def create_rock_color_controls(self):
        group = QGroupBox("Rock Coloring")
        layout = QGridLayout(group)

        layout.addWidget(QLabel("Rock Base Color:"), 0, 0)
        self.rock_color_btn = self.create_color_btn("#696969", "rock")
        layout.addWidget(self.rock_color_btn, 0, 1)

        apply_btn = QPushButton("Apply Rock Colors")
        apply_btn.clicked.connect(self.apply_rock_color)
        layout.addWidget(apply_btn, 1, 0, 1, 2)

        return group

    def create_mushroom_color_controls(self):
        group = QGroupBox("Mushroom Coloring:")
        layout = QGridLayout(group)

        layout.addWidget(QLabel("Mushroom Stem Color:"), 0, 0)
        self.mushroom_stem_color_btn = self.create_color_btn("#F5F5CD", 
                                                             "mushroom_stem")
        layout.addWidget(self.mushroom_stem_color_btn, 0, 1)

        layout.addWidget(QLabel("Mushroom Cap Color:"), 1, 0)
        self.mushroom_cap_color_btn = self.create_color_btn("#FF6B6B", 
                                                            "mushroom_cap")
        layout.addWidget(self.mushroom_cap_color_btn, 1, 1)

        apply_btn = QPushButton("Apply Mushroom Colors")
        apply_btn.clicked.connect(self.apply_mushroom_colors)
        layout.addWidget(apply_btn, 2, 0, 1, 2)

        return group

    def create_global_color_controls(self):
        group = QGroupBox("Global Color Controls")
        layout = QVBoxLayout(group)

        apply_all_btn = QPushButton("Apply All Colors to Forest Assets")
        apply_all_btn.setStyleSheet("QPushButton { background-color: #4CAF50; " \
        "color: white; font-weight: bold; padding: 8px; }")
        apply_all_btn.clicked.connect(self.apply_all_colors)
        layout.addWidget(apply_all_btn)

        randomize_btn = QPushButton("Randomize All Colors")
        randomize_btn.setStyleSheet("QPushButton { background-color: #9C27B0; " \
        "color: white; padding: 8px; }")
        randomize_btn.clicked.connect(self.randomize_all_colors)
        layout.addWidget(randomize_btn)

        return group

    def create_color_btn(self, default_color, color_type):
        button = QPushButton()
        button.setStyleSheet(f"background-color {default_color}; border: 1px solid #666;")
        button.setFixedSize(60, 25)
        button.clicked.connect(lambda: self.choose_color(color_type))
        return button

    def choose_color(self, color_type):
        current_color = self.get_current_color(color_type)
        color = QColorDialog.getColor(current_color, self, 
                    f"Choose {color_type.replace('_', ' ').title()} Color")
        if color.isValid():
            self.set_color_btn(color_type, color)

    def get_current_color(self, color_type):
        color_map = {'tree_trunk': '#8B4513',
                     'tree_leaves': '#0E912A',
                     'rock': '#696969', 'mushroom_stem': '#F5F5CD',
                     'mushroom_cap': '#FF6B6B'
                     }
        return QColor(color_map.get(color_type, '#FFFFFF'))

    def set_color_btn(self, color_type, color):
        button_map = {'tree_trunk': self.tree_trunk_color_btn,
                      'tree_leaves': self.tree_leaves_color_btn,
                      'rock': self.rock_color_btn, 
                      'mushroom_stem': self.mushroom_stem_color_btn,
                      'mushroom_cap': self.mushroom_cap_color_btn
                      }
        button = button_map.get(color_type)
        if button:
            button.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #666;")

    def get_btn_color(self, button):
        style = button.styleSheet()
        match = re.search(r'background-color:\s*([^;]+);', style)
        if match:
            color_str = match.group(1)
            return QColor(color_str)
        return QColor('#FFFFFF')

    def apply_tree_colors(self):
        trunk_color = self.get_btn_color(self.tree_trunk_color_btn)
        leaves_color = self.get_btn_color(self.tree_leaves_color_btn)

        trees = cmds.ls("tree_*", "Forest_Trees", type="transform")
        valid_trees = [
        t for t in trees if cmds.objExists(t) and t not in self.generated_assets.values()
        ]

        for tree in valid_trees:
            self.color_tree(tree, trunk_color, leaves_color)
        self.status_label.setText(f"Applied colors to {len(valid_trees)} trees")

    def color_tree(self, tree, trunk_color, leaves_color):
        children = cmds.listRelatives(tree, children=True, fullPath=True) or []
        for child in children:
            child_name = child.split('|')[-1]
            if 'trunk' in child_name.lower():
                self.apply_color_to_obj(child, trunk_color)
            elif 'leaves' in child_name.lower():
                self.apply_color_to_obj(child, leaves_color)

    def apply_rock_color(self):
        base_color = self.get_btn_color(self.rock_color_btn)
        rocks = cmds.ls("rock_*", "Forest_Rocks", type="transform")
        valid_rocks = [
        r for r in rocks if cmds.objExists(r) and r not in self.generated_assets.values()
            ]
        for rock in valid_rocks:
            self.apply_color_to_obj(rock, base_color)
        self.status_label.setText(f"Applied colors to {len(valid_rocks)} rocks")

    def apply_mushroom_colors(self):
        stem_color = self.get_btn_color(self.mushroom_stem_color_btn)
        cap_color = self.get_btn_color(self.mushroom_cap_color_btn)
        mushrooms = cmds.ls("mushroom_*", "Forest_Mushrooms", type="transform")
        valid_mushrooms = [
        m for m in mushrooms if cmds.objExists(m) and m not in self.generated_assets.values()
        ]
        for mushroom in valid_mushrooms:
            self.color_mushroom(mushroom, stem_color, cap_color)
        self.status_label.setText(
        f"Applied colors to {len(valid_mushrooms)} mushrooms")

    def color_mushroom(self, mushroom, stem_color, cap_color):
        children = cmds.listRelatives(mushroom, children=True, fullPath=True) or []
        for child in children:
            child_name = child.split('|')[-1]
            if 'stem' in child_name.lower():
                self.apply_color_to_obj(child, stem_color)
            elif 'cap' in child_name.lower():
                self.apply_color_to_obj(child, cap_color)

    def apply_all_colors(self):
        self.apply_tree_colors()
        self.apply_rock_color()
        self.apply_mushroom_colors()
        self.status_label.setText("Applied all colors to entire forest!")

    def randomize_all_colors(self):
        self.set_color_btn('tree_trunk', QColor(random.randint(50, 150), 
        random.randint(30, 80), random.randint(10, 50)))
        self.set_color_btn('tree_leaves', QColor(random.randint(0, 100), 
        random.randint(100, 200), random.randint(0, 100)))

        gray_val = random.randint(50, 150)
        self.set_color_btn('rock', QColor(gray_val, gray_val, gray_val))

        self.set_color_btn('mushroom_stem', QColor(random.randint(200, 255), 
        random.randint(200, 255), random.randint(180, 220)))
        self.set_color_btn('mushroom_cap', QColor(random.randint(150, 255), 
        random.randint(50, 200), random.randint(50, 200)))

        self.status_label.setText("Randomized all color settings!")

    def apply_color_to_obj(self, obj, color):
        red = color.red() / 255.0
        green = color.green() / 255.0
        blue = color.blue() / 255.0

        shader_name = f"{obj}_shader"
        if not cmds.objExists(shader_name):
            shader = cmds.shadingNode('lambert', asShader=True, name=shader_name)
            shading_group = cmds.sets(renderable=True, noSurfaceShader=True, 
                                      empty=True, name=f"{shader_name}SGH")
            cmds.connectAttr(f'{shader}.outColor', f'{shading_group}.surfaceShader')
        else:
            shader = shader_name

        cmds.setAttr(f'{shader}.color', red, green, blue, type='double3')
        cmds.select(obj)
        cmds.hyperShade(assign=shader)

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

    def create_tree(self):
        trunk = cmds.polyCylinder(radius=0.3, height=4, sx=8, sy=4, sz=1,
                                  name="tree_trunk")[0]
        cmds.move(0, 2, 0, trunk)

        foliage = cmds.polySphere(radius=1.5, sx=8, sy=6, name="tree_leaves")[0]
        cmds.move(0, 5, 0, foliage)

        tree_group = cmds.group([trunk, foliage], name="base_tree")
        return tree_group

    def create_rock(self):
        rock = cmds.polyCube(width=1.5, height=0.8, depth=1.2, sx=3, sy=2, 
                             sz=3, name="rock")[0]
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
    
    def generate_forest(self):
        self.status_label.setText("Starting forest generation!")
        try:
            self.clear_previous_scatter()
            for asset_type, asset in self.generated_assets.items():
                if not cmds.objExists(asset):
                    self.generate_base_assets()
                    break
                cmds.showHidden(asset)

            assets_to_scatter = []
            if self.tree_enabled.isChecked():
                assets_to_scatter.extend(['tree'] * self.tree_count.value())
            if self.rock_enabled.isChecked():
                assets_to_scatter.extend(['rock'] * self.rock_count.value())
            if self.mushroom_enabled.isChecked():
                assets_to_scatter.extend(
                    ['mushroom'] * self.mushroom_count.value())
                
            random.shuffle(assets_to_scatter)

            area_width = 20.0
            aread_depth = 20.0
            center_x = 0.0
            center_z = 0.0

            forest_group = cmds.group(empty=True, name="Forest_Scatter")
            self.managed_groups.append(forest_group)

            asset_groups = {}
            for asset_type in ['tree', 'rock', 'mushroom']:
                group_name = f"Forest_{asset_type.capitalize()}s"
                asset_groups[asset_type] = cmds.group(empty=True, 
                                                      name=group_name)
                cmds.parent(asset_groups[asset_type], forest_group)
                self.managed_groups.append(asset_groups[asset_type])

            total_assets = len(assets_to_scatter)
            placed_count = 0

            for ast, asset_type in enumerate(assets_to_scatter):
                if ast % 10 == 0:
                    self.status_label.setText(
                        f"Placing {asset_type}s... ({ast}/{total_assets})")
                    QtCore.QCoreApplication.processEvents()

                    position = self.find_valid_pos(area_width, 
                    aread_depth, center_x, center_z, self.min_spacing.value(), 
                    self.placement_attempts.value())
                
                if position:
                    base_asset = self.generated_assets[asset_type]
                    cmds.showHidden(base_asset)

                    new_asset = cmds.duplicate(
                        base_asset, name=f"{asset_type}_{placed_count}")[0]
                    self.apply_asset_trans(new_asset, position, asset_type)

                    if self.collision_enabled.isChecked():
                        self.add_collision_sph(new_asset, position)

                    cmds.parent(new_asset, asset_groups[asset_type])
                    self.scatter_objects.append(new_asset)
                    placed_count += 1

            for asset in self.generated_assets.values():
                if cmds.objExists(asset):
                    cmds.hide(asset)
            
            self.apply_all_colors()
            self.finalize_scene()
            self.status_label.setText(
            f"Forest generation complete!!! Placed {placed_count} assets! :D")
        
        except Exception as e:
            self.status_label.setText(f"Error during generation: {str(e)}")
            cmds.warning(f"Forest generation error: {str(e)}")


    def find_valid_pos(self, width, depth, center_x, 
                       center_z, min_spacing, max_attempts):
        for attempt in range(max_attempts):
            x, z = self.get_distributed_pos(width, depth, center_x, center_z)
            if not self.collision_enabled.isChecked() or not self.check_collision(
                x, z, min_spacing):
                return (x, 0, z)
        return None

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
                z = random.uniform(center_z - depth/2, center_z + depth/2)
            else:
                x = random.uniform(center_x - width/2, center_x + width/2)
                z = random.choice([center_z - depth/2, center_z + depth/2])
        else:
            x = center_x + random.gauss(0, width/4)
            z = center_z + random.gauss(0, depth/4)
            x = max(center_x - width/2, min(center_x + width/2, x))
            z = max(center_z - depth/2, min(center_z + depth/2, z))
        return x, z
    
    def check_collision(self, x, z, min_spacing):
        for sphere in self.collision_spheres:
            pos, radius = sphere
            distance = math.sqrt((x - pos[0])**2 + (z -pos[2])**2)
            if distance < (radius + min_spacing) * self.collision_multiplier.value():
                return True
        return False

    def add_collision_sph(self, asset, position):
        bbox = cmds.exactWorldBoundingBox(asset)
        width = bbox[3] - bbox[0]
        depth = bbox[5] - bbox[2]
        radius = max(width, depth) / 2
        self.collision_spheres.append((position, radius))

    def apply_asset_trans(self, asset, position, asset_type):
        x, y, z = position
        cmds.move(x, y, z, asset)
        scale = random.uniform(self.scale_min.value(), self.scale_max.value())

        if asset_type == 'tree':
            height_scale = scale * random.uniform(
                1 - self.tree_height_var.value(), 
                1 + self.tree_height_var.value())
            cmds.scale(scale, height_scale, scale, asset)
        elif asset_type == 'rock':
            rock_scale = scale * random.uniform(1 - self.rock_size_var.value(), 
                                                1 + self.rock_size_var.value())
            cmds.scale(rock_scale, 
                    rock_scale * random.uniform(0.8, 1.2), rock_scale, asset)
        else:
            cmds.scale(scale, scale, scale, asset)

        if self.random_rotation.isChecked():
            cmds.rotate(0, random.uniform(0, 360), 0, asset)

        self.snap_to_ground(asset)            

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
            self.status_label.setText("Scene cleared")
        except Exception as e:
            self.status_label.setText(f"Error clearing scene: {str(e)}")
            cmds.warning(f"Scene clearing error: {str(e)}")

    def finalize_scene(self):
        cmds.refresh()

def show_forest_creator():
    global forest_creator_window

    try:
        forest_creator_window.close()
    except:
        pass

    forest_creator_window = ForestCreator()
    forest_creator_window.show()

if __name__ == "__main__":
    show_forest_creator()
