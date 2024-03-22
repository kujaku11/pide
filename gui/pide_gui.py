#!/usr/bin/env python3

import os

core_path_ext = os.path.join(os.path.dirname(os.path.abspath(__file__)) , 'SEEL', 'seel_src')

import sys, csv, platform, warnings
import numpy as np
import iapws
import matplotlib.pyplot as plt
from matplotlib.pyplot import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *

try:
	import pyperclip
	clipbool = True
except ModuleNotFoundError:
	pass
	clipbool = False

#Importing external functions

sys.path.append(core_path_ext)

#importing odd melt/fluid functions
from cond_models.melt_odd import * 
from cond_models.fluids_odd import * 
#importing odd rock functions
from cond_models.rocks.granite_odd import * 
from cond_models.rocks.granulite_odd import *
from cond_models.rocks.sandstone_odd import *
from cond_models.rocks.gneiss_odd import *
from cond_models.rocks.amphibolite_odd import *
from cond_models.rocks.basalt_odd import *
from cond_models.rocks.mud_odd import *
from cond_models.rocks.gabbro_odd import *
from cond_models.rocks.other_rocks_odd import *
#importing odd mineral functions
from cond_models.minerals.quartz_odd import *
from cond_models.minerals.plag_odd import *
from cond_models.minerals.amp_odd import *
from cond_models.minerals.kfelds_odd import *
from cond_models.minerals.opx_odd import *
from cond_models.minerals.cpx_odd import *
from cond_models.minerals.mica_odd import *
from cond_models.minerals.garnet_odd import *
from cond_models.minerals.ol_odd import *
from cond_models.minerals.mixtures_odd import *
from cond_models.minerals.other_odd import *

warnings.filterwarnings("ignore", category=RuntimeWarning) #ignoring many RuntimeWarning printouts that are utterly useless

#Color coding class for fancy-colored print-outs.
class bcolors:
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	RED = '\033[91m'
	B = '\033[0m'
	NC ='\x1b[0m'
	
#Version 0.1, June. 2023.
#SEEL - (S)ynthetic (E)lectrical (E)arth (L)ibrary
#Program written by Sinan Ozaydin (University of Sydney, School of Geosciences, Australia).

#Indentation method: hard tabs ('\t')

#Works with Python3
#Required libraries: numpy,matplotlib,PyQt5
#optional libraries: pyperclip

print(bcolors.GREEN + '#############################################')
print(' ')
print(' ')
print(' ')
print(bcolors.GREEN + '                  SEEL_GUI 0.1')
print(' ')
print(bcolors.BLUE + '        Synthetic Electrical Earth Library')
print(bcolors.RED + '            Graphical User Interface')
print(' ')
print(' ')
print(' ')
print(bcolors.GREEN + '#############################################')
print(bcolors.BLUE + 'developed by Sinan Ozaydin,' + bcolors.RED +  ' School of Geosciences, University of Sydney')
print(' ')
print(' ')
print(bcolors.NC + 'for questions, email: sinan.ozaydin@protonmail.com or sinan.ozaydin@sydney.edu.au')
print('Initializing the software...')

class SEEL(QMainWindow):

	def __init__(self, core_path = core_path_ext, clipping = clipbool, parent = None):

		super(SEEL,self).__init__(parent)

		self.core_path = core_path
		self.working_path = os.getcwd()

		self.clipping = clipping
		
		if platform.system() == 'Windows':
			self.commandmv = 'move'
		else:
			self.commandmv = 'mv'

		args_input = sys.argv
		if len(args_input) == 1:
			SEEL.arguments_load = False
			SEEL.composition_args_path = False
		else:
			SEEL.arguments_load = True
			try:
				SEEL.composition_args_path = args_input[1]
			except IndexError:
				pass
		
		self.setMinimumSize(1800,1000)
		self.setStyleSheet("QMainWindow{background-color: #ebfaeb;border: 1px solid black}")
		self.setWindowTitle("SEEL - Synthetic Electrical Earth Library")
		
		#Defining Menubar items
		mainMenu = self.menuBar()
		mainMenu.setNativeMenuBar(False)
		mainMenu.setStyleSheet("QMenuBar{background-color: #ccffcc;border: 1px solid black}")
		fileMenu = mainMenu.addMenu('Main')
		mainMenu.setStyleSheet("QMenuBar{background-color: #ccffcc;border: 1px solid black}")
		fugMenu = mainMenu.addMenu('Oxygen Fugacity')
		fugMenu.setStyleSheet("QMenu{background-color: #ccffcc;border: 1px solid black}")
		watercalibMenu = mainMenu.addMenu('Water Calibration Correction')
		watercalibMenu.setStyleSheet("QMenu{background-color: #9098a3;border: 1px solid black}")
		
		#ENV FILE BUTTON
		infoMain = QAction("&Info", self)
		infoMain.setShortcut("Ctrl+I")
		infoMain.triggered.connect(self.info_main)
		fileMenu.addAction(infoMain)
		
		paramreadMain = QAction("&Read Parameter File", self)
		paramreadMain.setShortcut("Ctrl+O")
		paramreadMain.triggered.connect(self.read_parameter_file_batch)
		fileMenu.addAction(paramreadMain)
		
		paramwriteMain = QAction("&Write Parameter File", self)
		paramwriteMain.setShortcut("Ctrl+S")
		paramwriteMain.triggered.connect(self.write_parameter_file_batch)
		fileMenu.addAction(paramwriteMain)
		
		openFugButton = QAction("&Oxygen Fugacity Selection", self)
		openFugButton.triggered.connect(self.fo2_properties_popup)
		fugMenu.addAction(openFugButton)
		self.fo2_pop = None
		
		#WATER CALIBRATIONS MENU

		watercalibButton = QAction("&Water/Hydroxyl Calibration Setup",self)
		watercalibButton.triggered.connect(self.water_calib_popup)
		self.water_calib_pop = None

		watercalibMenu.addAction(watercalibButton)

		self.home()
		
	def home(self):
		
		#Setting up initial variables.

		SEEL.loaded_file = False
		self.cond_calculated = False

		SEEL.plot_style_list = ['ggplot', 'default', 'classic','bmh', 'fast', 'seaborn', 'seaborn-colorblind',
		'seaborn-deep','seaborn-pastel', 'seaborn-dark','fivethirtyeight','grayscale']
		SEEL.plot_style_selection = 0

		self.init_params = self.read_csv(filename = os.path.join(self.core_path,'init_param.csv'),delim = ',') #loading the blueprint parameter file.
		
		if SEEL.arguments_load == False:

			SEEL.fluid_cond_selection = 0
			SEEL.melt_cond_selection = 0

			SEEL.fluid_or_melt_method = 0
			SEEL.solid_phase_method = 2

			SEEL.granite_cond_selection = 0
			SEEL.granulite_cond_selection = 0
			SEEL.sandstone_cond_selection = 0
			SEEL.gneiss_cond_selection = 0
			SEEL.amphibolite_cond_selection = 0
			SEEL.basalt_cond_selection = 0
			SEEL.mud_cond_selection = 0
			SEEL.gabbro_cond_selection = 0
			SEEL.other_rock_cond_selection = 0

			SEEL.quartz_cond_selection = 0
			SEEL.plag_cond_selection = 0
			SEEL.amp_cond_selection = 0
			SEEL.kfelds_cond_selection = 0
			SEEL.opx_cond_selection = 0
			SEEL.cpx_cond_selection = 0
			SEEL.mica_cond_selection = 0
			SEEL.garnet_cond_selection = 0
			SEEL.sulphide_cond_selection = 0
			SEEL.graphite_cond_selection = 0
			SEEL.ol_cond_selection = 0
			SEEL.mixture_cond_selection = 0
			SEEL.other_cond_selection = 0
			
			SEEL.ol_calib = 3
			SEEL.px_gt_calib = 2
			SEEL.feldspar_calib = 2

			self.salinity_fluid = np.zeros(1)
			self.k2o_melt = np.zeros(1)
			self.co2_melt = np.zeros(1)
			self.h2o_melt = np.zeros(1)
			self.na2o_melt = np.zeros(1)
			
			self.granite_frac = np.ones(1) * 0.8
			self.granulite_frac = np.ones(1) * 0.2
			self.sandstone_frac = np.zeros(1)
			self.gneiss_frac = np.zeros(1)
			self.amphibolite_frac = np.zeros(1)
			self.basalt_frac = np.zeros(1)
			self.mud_frac = np.zeros(1)
			self.gabbro_frac = np.zeros(1)
			self.other_rock_frac = np.zeros(1)

			SEEL.granite_water = np.zeros(1)
			SEEL.granulite_water = np.zeros(1)
			SEEL.sandstone_water = np.zeros(1)
			SEEL.gneiss_water = np.zeros(1)
			SEEL.amphibolite_water = np.zeros(1)
			SEEL.basalt_water = np.zeros(1)
			SEEL.mud_water = np.zeros(1)
			SEEL.gabbro_water = np.zeros(1)
			SEEL.other_rock_water = np.zeros(1)
			
			SEEL.rock_water_list = [SEEL.granite_water, SEEL.granulite_water,
			SEEL.sandstone_water, SEEL.gneiss_water, SEEL.amphibolite_water, SEEL.basalt_water,
			SEEL.mud_water, SEEL.gabbro_water, SEEL.other_rock_water]
			
			self.quartz_frac = np.zeros(1)
			self.plag_frac = np.zeros(1)
			self.amp_frac = np.zeros(1)
			self.kfelds_frac = np.zeros(1)
			self.opx_frac = np.zeros(1)
			self.cpx_frac = np.zeros(1)
			self.mica_frac = np.zeros(1)
			self.garnet_frac = np.zeros(1)
			self.sulphide_frac = np.zeros(1)
			self.graphite_frac = np.zeros(1)
			self.ol_frac = np.zeros(1)
			self.mixture_frac = np.zeros(1)
			self.other_frac = np.zeros(1)

			SEEL.quartz_water = np.zeros(1)
			SEEL.plag_water = np.zeros(1)
			SEEL.amp_water = np.zeros(1)
			SEEL.kfelds_water = np.zeros(1)
			SEEL.garnet_water = np.zeros(1)
			SEEL.opx_water = np.zeros(1)
			SEEL.cpx_water = np.zeros(1)
			SEEL.mica_water = np.zeros(1)
			SEEL.sulphide_water = np.zeros(1)
			SEEL.graphite_water = np.zeros(1)
			SEEL.ol_water = np.zeros(1)
			SEEL.mixture_water = np.zeros(1)
			SEEL.other_water = np.zeros(1)
			
			SEEL.mineral_water_list = [SEEL.quartz_water, SEEL.plag_water, SEEL.amp_water, SEEL.kfelds_water,
			SEEL.opx_water, SEEL.cpx_water, SEEL.mica_water, SEEL.garnet_water, SEEL.sulphide_water,
				   SEEL.graphite_water, SEEL.ol_water, SEEL.mixture_water, SEEL.other_water]
				   
			SEEL.granite_param1 = np.zeros(1)
			SEEL.granulite_param1 = np.zeros(1)
			SEEL.sandstone_param1 = np.zeros(1)
			SEEL.gneiss_param1 = np.zeros(1)
			SEEL.amphibolite_param1 = np.zeros(1)
			SEEL.basalt_param1 = np.zeros(1)
			SEEL.mud_param1 = np.zeros(1)
			SEEL.gabbro_param1 = np.zeros(1)
			SEEL.other_rock_param1 = np.zeros(1)
			
			SEEL.param1_rock_list = [SEEL.granite_param1, SEEL.granulite_param1, SEEL.sandstone_param1, SEEL.gneiss_param1, SEEL.amphibolite_param1,
			SEEL.basalt_param1, SEEL.mud_param1, SEEL.gabbro_param1, SEEL.other_rock_param1]
			
			SEEL.quartz_param1 = np.zeros(1)
			SEEL.plag_param1 = np.zeros(1)
			SEEL.amp_param1 = np.zeros(1)
			SEEL.kfelds_param1 = np.zeros(1)
			SEEL.garnet_param1 = np.zeros(1)
			SEEL.opx_param1 = np.zeros(1)
			SEEL.cpx_param1 = np.zeros(1)
			SEEL.mica_param1 = np.zeros(1)
			SEEL.sulphide_param1 = np.zeros(1)
			SEEL.graphite_param1 = np.zeros(1)
			SEEL.ol_param1 = np.zeros(1)
			SEEL.mixture_param1 = np.zeros(1)
			SEEL.other_param1 = np.zeros(1)
			
			SEEL.param1_mineral_list = [SEEL.quartz_param1,SEEL.plag_param1,SEEL.amp_param1,SEEL.kfelds_param1,SEEL.opx_param1,SEEL.cpx_param1,SEEL.mica_param1,SEEL.garnet_param1,
			SEEL.sulphide_param1,SEEL.graphite_param1,SEEL.ol_param1,SEEL.mixture_param1,SEEL.other_param1]			
			
			SEEL.granite_param2 = np.zeros(1)
			SEEL.granulite_param2 = np.zeros(1)
			SEEL.sandstone_param2 = np.zeros(1)
			SEEL.gneiss_param2 = np.zeros(1)
			SEEL.amphibolite_param2 = np.zeros(1)
			SEEL.basalt_param2 = np.zeros(1)
			SEEL.mud_param2 = np.zeros(1)
			SEEL.gabbro_param2 = np.zeros(1)
			SEEL.other_rock_param2 = np.zeros(1)
			
			SEEL.param2_rock_list = [SEEL.granite_param2, SEEL.granulite_param2, SEEL.sandstone_param2, SEEL.gneiss_param2, SEEL.amphibolite_param2,
			SEEL.basalt_param2, SEEL.mud_param2, SEEL.gabbro_param2, SEEL.other_rock_param2]
			
			SEEL.quartz_param2 = np.zeros(1)
			SEEL.plag_param2 = np.zeros(1)
			SEEL.amp_param2 = np.zeros(1)
			SEEL.kfelds_param2 = np.zeros(1)
			SEEL.garnet_param2 = np.zeros(1)
			SEEL.opx_param2 = np.zeros(1)
			SEEL.cpx_param2 = np.zeros(1)
			SEEL.mica_param2 = np.zeros(1)
			SEEL.sulphide_param2 = np.zeros(1)
			SEEL.graphite_param2 = np.zeros(1)
			SEEL.ol_param2 = np.zeros(1)
			SEEL.mixture_param2 = np.zeros(1)
			SEEL.other_param2 = np.zeros(1)
			
			SEEL.param2_mineral_list = [SEEL.quartz_param2,SEEL.plag_param2,SEEL.amp_param2,SEEL.kfelds_param2,SEEL.opx_param2,SEEL.cpx_param2,SEEL.mica_param2,SEEL.garnet_param2,
			SEEL.sulphide_param2,SEEL.graphite_param2,SEEL.ol_param2,SEEL.mixture_param2,SEEL.other_param2]		
			
			self.melt_fluid_mass_frac = np.zeros(1)

			self.bckgr_res = np.zeros(1)
			
			SEEL.phs_mix_method = 0
			SEEL.phs_melt_mix_method = 0
			
			SEEL.melt_fluid_m = np.ones(1) * 5
			
			SEEL.granite_m = np.ones(1) * 4
			SEEL.granulite_m = np.ones(1) * 4
			SEEL.sandstone_m = np.ones(1) * 4
			SEEL.gneiss_m = np.ones(1) * 4
			SEEL.amphibolite_m = np.ones(1) * 4
			SEEL.basalt_m = np.ones(1) * 4
			SEEL.mud_m = np.ones(1) * 4
			SEEL.gabbro_m = np.ones(1) * 4
			SEEL.other_rock_m = np.ones(1) * 4
			
			SEEL.quartz_m = np.ones(1) * 1
			SEEL.plag_m = np.ones(1) * 2.5
			SEEL.amp_m = np.ones(1) * 4
			SEEL.kfelds_m = np.ones(1) * 2.5
			SEEL.opx_m = np.ones(1) * 4
			SEEL.cpx_m = np.ones(1) * 4
			SEEL.mica_m = np.ones(1) * 4
			SEEL.garnet_m = np.ones(1) * 4
			SEEL.sulphide_m = np.ones(1) * 6
			SEEL.graphite_m = np.ones(1) * 6
			SEEL.ol_m = np.ones(1) * 6
			SEEL.mixture_m = np.ones(1) * 6
			SEEL.other_m = np.ones(1) * 6
			
			self.depth = np.array([26.0])
			self.p = np.array([1])
			self.T = np.array([500.0])
			
			SEEL.o2_buffer = 0

		elif SEEL.arguments_load == True:

			data_comp_file = self.read_csv(filename = self.composition_args_path, delim = ',')

			for i in range(1,len(data_comp_file)):

				if data_comp_file[i][2] == 'SEEL':
					if data_comp_file[i][3] == 'float':
						setattr(SEEL, data_comp_file[i][0], np.array([float(data_comp_file[i][1])]))
					elif data_comp_file[i][3] == 'int':
						setattr(SEEL, data_comp_file[i][0], int(data_comp_file[i][1]))

				elif data_comp_file[i][2] == 'self':
					if data_comp_file[i][3] == 'float':
						if ('frac' in data_comp_file[i][0]) == True:
							setattr(self, data_comp_file[i][0], np.array([float(data_comp_file[i][1])/1e2]))
						else:
							if data_comp_file[i][0] == 'p':
								setattr(self, data_comp_file[i][0], np.array([float(data_comp_file[i+1][1]) / 26.0]))
							else:
								setattr(self, data_comp_file[i][0], np.array([float(data_comp_file[i][1])]))
					elif data_comp_file[i][3] == 'int':
						setattr(self, data_comp_file[i][0], int(data_comp_file[i][1]))


		SEEL.rock_cond_selections = [SEEL.granite_cond_selection, SEEL.granulite_cond_selection, SEEL.sandstone_cond_selection, SEEL.gneiss_cond_selection,
				   SEEL.amphibolite_cond_selection, SEEL.basalt_cond_selection, SEEL.mud_cond_selection, SEEL.gabbro_cond_selection, SEEL.other_rock_cond_selection]

		SEEL.minerals_cond_selections = [SEEL.quartz_cond_selection, SEEL.plag_cond_selection, SEEL.amp_cond_selection, SEEL.kfelds_cond_selection, SEEL.opx_cond_selection,
				   SEEL.cpx_cond_selection, SEEL.mica_cond_selection, SEEL.garnet_cond_selection, SEEL.sulphide_cond_selection,
				   SEEL.graphite_cond_selection, SEEL.ol_cond_selection, SEEL.mixture_cond_selection, SEEL.other_cond_selection]

		self.composition_set = False

		#Setting up the blank canvas on the main page.

		self.canvas_widget = QFrame(self)
		self.canvas_widget.setGeometry(750,50,1000,925)
		self.canvas_widget.setStyleSheet("border:1.25px solid #768795")
		self.canvaslayout = QVBoxLayout(self.canvas_widget)

		#Using the internal matplotlib style ggplot
		plt.style.use('ggplot')
		self.fig = Figure()
		self.fig.patch.set_facecolor('#EFF0F1')

		self.canvas = FigureCanvas(self.fig)
		self.toolbar = NavigationToolbar(self.canvas, self)
		self.toolbar.setStyleSheet("QToolBar { border: 0px ; : #889DAE}")
		self.canvaslayout.addWidget(self.toolbar)
		self.canvaslayout.addWidget(self.canvas)

		#Reading parameter files...

		self.read_cond_models()
		self.read_params()

		#Defining buttons on the MainWindow
		properties_mark = QLabel(self)
		properties_mark.setText('Setup')
		properties_mark.setStyleSheet("QLabel {font:bold};fontsize: 10pt;color: red")
		properties_mark.move(65,35)

		#conductivity button

		cond_btn = QPushButton('Conductivity Models', self)
		cond_btn.move(10,65)
		cond_btn.setStyleSheet("QPushButton {min-width: 10em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		cond_btn.clicked.connect(self.conductivity_popup)
		self.cond_pop = None

		mix_btn = QPushButton('Phase Mixing', self)
		mix_btn.move(10,100)
		mix_btn.setStyleSheet("QPushButton {min-width: 10em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		mix_btn.clicked.connect(self.phase_mixing_popup)
		self.phs_mix_popup = None
		
		int_btn = QPushButton('Phase Interconnectivity', self)
		int_btn.move(10,135)
		int_btn.setStyleSheet("QPushButton {min-width: 10em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		int_btn.clicked.connect(self.phase_intercon_popup)
		self.phs_intercon_popup = None
		
		water_btn = QPushButton('Solid Phase Water Contents', self)
		water_btn.move(10,170)
		water_btn.setStyleSheet("QPushButton {min-width: 10em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		water_btn.clicked.connect(self.water_content_popup)
		self.water_phase_popup = None
		
		param_btn = QPushButton('Optional Parameters', self)
		param_btn.move(10,205)
		param_btn.setStyleSheet("QPushButton {min-width: 10em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		param_btn.clicked.connect(self.optional_param_popup)
		self.param_phase_popup = None
				
		pt_mark = QLabel(self)
		pt_mark.setText('P-T')
		pt_mark.setStyleSheet("QLabel {font:bold};fontsize: 10pt;color: red")
		pt_mark.move(225,310)
		
		SEEL.btn_pressure = QPushButton("Pressure (GPa)", self)
		SEEL.btn_pressure.clicked.connect(self.get_pressure)
		SEEL.btn_pressure.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.pressure_textbox = QLineEdit(str(self.depth[0] / 26.0), self)
		self.pressure_textbox.setEnabled(False)
		self.pressure_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_pressure.move(100,345)
		self.pressure_textbox.move(280,345)
		
		SEEL.btn_depth = QPushButton("Depth (Km)", self)
		SEEL.btn_depth.clicked.connect(self.get_depth)
		SEEL.btn_depth.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.depth_textbox = QLineEdit(str(self.depth[0]), self)
		self.depth_textbox.setEnabled(False)
		self.depth_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_depth.move(100,380)
		self.depth_textbox.move(280,380)		
		
		SEEL.btn_temp = QPushButton("Temperature (C)", self)
		SEEL.btn_temp.clicked.connect(self.get_temp)
		SEEL.btn_temp.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.temp_textbox = QLineEdit(str(self.T[0]), self)
		self.temp_textbox.setEnabled(False)
		self.temp_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_temp.move(100,415)
		self.temp_textbox.move(280,415)

		#radiobutton melt or fluid

		fluid_phases_mark = QLabel(self)
		fluid_phases_mark.setText('Fluid Phases')
		fluid_phases_mark.setStyleSheet("QLabel {font:bold};fontsize: 10pt;color: red")
		fluid_phases_mark.move(290,35)

		btn_fluid_phase_setup = QPushButton("Fluid Phase Setup", self)
		btn_fluid_phase_setup.clicked.connect(self.fluid_phase_popup)
		btn_fluid_phase_setup.setStyleSheet("QPushButton {min-width: 18em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		btn_fluid_phase_setup.move(200,65)
		self.fluid_melt_pop = None

		btn_melt_content= QPushButton("Fluid-Melt Content (%)", self)
		btn_melt_content.clicked.connect(self.get_fluid_melt_content)
		btn_melt_content.setStyleSheet("QPushButton {min-width: 10em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.melt_content_textbox = QLineEdit(str(self.melt_fluid_mass_frac[0]*1e2), self)
		self.melt_content_textbox.setEnabled(False)
		self.melt_content_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		btn_melt_content.move(200,100)
		self.melt_content_textbox.move(370,100)

		SEEL.btn_salinity_fluid= QPushButton("Fluid Salinity (%wt)", self)
		SEEL.btn_salinity_fluid.clicked.connect(self.get_salinity)
		if SEEL.fluid_or_melt_method == 0:
			SEEL.btn_salinity_fluid.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.fluid_or_melt_method == 1:
			SEEL.btn_salinity_fluid.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		SEEL.btn_salinity_fluid.setStyleSheet("QPushButton {min-width: 10em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.salinity_textbox = QLineEdit(str(self.salinity_fluid[0]), self)
		self.salinity_textbox.setEnabled(False)
		self.salinity_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_salinity_fluid.move(200,135)
		self.salinity_textbox.move(370,135)

		SEEL.btn_co2_melt = QPushButton("Melt CO2 (ppm)", self)
		SEEL.btn_co2_melt.clicked.connect(self.get_co2_melt)
		if SEEL.fluid_or_melt_method == 1:
			SEEL.btn_co2_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.fluid_or_melt_method == 0:
			SEEL.btn_co2_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		self.co2_melt_textbox = QLineEdit(str(self.co2_melt[0]), self)
		self.co2_melt_textbox.setEnabled(False)
		self.co2_melt_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_co2_melt.move(200,170)
		self.co2_melt_textbox.move(370,170)

		SEEL.btn_h2o_melt = QPushButton("Melt H2O (ppm)", self)
		SEEL.btn_h2o_melt.clicked.connect(self.get_h2o_melt)
		if SEEL.fluid_or_melt_method == 1:
			SEEL.btn_h2o_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.fluid_or_melt_method == 0:
			SEEL.btn_h2o_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		self.h2o_melt_textbox = QLineEdit(str(self.h2o_melt[0]), self)
		self.h2o_melt_textbox.setEnabled(False)
		self.h2o_melt_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_h2o_melt.move(200,205)
		self.h2o_melt_textbox.move(370,205)
		
		SEEL.btn_nao_melt = QPushButton("Melt NaO (%wt)", self)
		SEEL.btn_nao_melt.clicked.connect(self.get_nao_melt)
		if SEEL.fluid_or_melt_method == 1:
			SEEL.btn_nao_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.fluid_or_melt_method == 0:
			SEEL.btn_nao_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		self.na2o_melt_textbox = QLineEdit(str(self.na2o_melt[0]), self)
		self.na2o_melt_textbox.setEnabled(False)
		self.na2o_melt_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_nao_melt.move(200,240)
		self.na2o_melt_textbox.move(370,240)

		SEEL.btn_k2o_melt = QPushButton("Melt K2O (%wt)", self)
		SEEL.btn_k2o_melt.clicked.connect(self.get_k2o_melt)
		if SEEL.fluid_or_melt_method == 1:
			SEEL.btn_k2o_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.fluid_or_melt_method == 0:
			SEEL.btn_k2o_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		self.k2o_melt_textbox = QLineEdit(str(self.k2o_melt[0]), self)
		self.k2o_melt_textbox.setEnabled(False)
		self.k2o_melt_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_k2o_melt.move(200,275)
		self.k2o_melt_textbox.move(370,275)
		
		solid_phases_mark = QLabel(self)
		solid_phases_mark.setText('Solid Phases')
		solid_phases_mark.setStyleSheet("QLabel {font:bold}; min-width: 12em ; fontsize: 10pt;color: red")
		solid_phases_mark.move(200,440)

		btn_solid_phase_setup = QPushButton("Solid Phase Setup", self)
		btn_solid_phase_setup.clicked.connect(self.solid_phase_popup)
		btn_solid_phase_setup.setStyleSheet("QPushButton {min-width: 18em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		btn_solid_phase_setup.move(110,475)
		self.solid_phase_pop = None

		SEEL.btn_bckgr_res = QPushButton("Backgr. Resistivity", self)
		SEEL.btn_bckgr_res.clicked.connect(self.get_bckgr_res)
		if SEEL.solid_phase_method == 0:
			SEEL.btn_bckgr_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.solid_phase_method == 1:
			SEEL.btn_bckgr_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_bckgr_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		self.bckgr_res_textbox = QLineEdit(str(self.bckgr_res[0]), self)
		self.bckgr_res_textbox.setEnabled(False)
		self.bckgr_res_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_bckgr_res.move(10,510)
		self.bckgr_res_textbox.move(140,510)

		line_mark = QLabel(self)
		line_mark.setText('------------------------------------------')
		line_mark.setStyleSheet("QLabel {font:bold}; min-width: 100em ; fontsize: 10pt;color: red")
		line_mark.move(20,545)

		SEEL.btn_granite_res = QPushButton("Granite", self)
		SEEL.btn_granite_res.clicked.connect(lambda: self.get_rock_value(textbox_obj=self.granite_frac_textbox, param = "granite_frac", rock = "Granite"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_granite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_granite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_granite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		self.granite_frac_textbox = QLineEdit(str(self.granite_frac[0]*1e2), self)
		self.granite_frac_textbox.setEnabled(False)
		self.granite_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_granite_res.move(10,580)
		self.granite_frac_textbox.move(140,580)

		SEEL.btn_granulite_res = QPushButton("Granulite", self)
		SEEL.btn_granulite_res.clicked.connect(lambda: self.get_rock_value(textbox_obj=self.granulite_frac_textbox, param = "granulite_frac", rock = "Granulite"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_granulite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_granulite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_granulite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		self.granulite_frac_textbox = QLineEdit(str(self.granulite_frac[0]*1e2), self)
		self.granulite_frac_textbox.setEnabled(False)
		self.granulite_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_granulite_res.move(10,615)
		self.granulite_frac_textbox.move(140,615)

		SEEL.btn_sandstone_res = QPushButton("Sandstone", self)
		SEEL.btn_sandstone_res.clicked.connect(lambda: self.get_rock_value(textbox_obj=self.sandstone_frac_textbox, param = "sandstone_frac", rock = "Sandstone"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_sandstone_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_sandstone_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_sandstone_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		self.sandstone_frac_textbox = QLineEdit(str(self.sandstone_frac[0]*1e2), self)
		self.sandstone_frac_textbox.setEnabled(False)
		self.sandstone_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_sandstone_res.move(10,650)
		self.sandstone_frac_textbox.move(140,650)

		SEEL.btn_gneiss_res = QPushButton("Gneiss", self)
		SEEL.btn_gneiss_res.clicked.connect(lambda: self.get_rock_value(textbox_obj=self.gneiss_frac_textbox, param = "gneiss_frac", rock = "Gneiss"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_gneiss_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_gneiss_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_gneiss_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		self.gneiss_frac_textbox = QLineEdit(str(self.gneiss_frac[0]*1e2), self)
		self.gneiss_frac_textbox.setEnabled(False)
		self.gneiss_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_gneiss_res.move(250,580)
		self.gneiss_frac_textbox.move(380,580)

		SEEL.btn_amphibolite_res = QPushButton("Amphibolite", self)
		SEEL.btn_amphibolite_res.clicked.connect(lambda: self.get_rock_value(textbox_obj=self.amphibolite_frac_textbox, param = "amphibolite_frac", rock = "Amphibolite"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_amphibolite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_amphibolite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_gneiss_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		self.amphibolite_frac_textbox = QLineEdit(str(self.amphibolite_frac[0]*1e2), self)
		self.amphibolite_frac_textbox.setEnabled(False)
		self.amphibolite_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_amphibolite_res.move(250,615)
		self.amphibolite_frac_textbox.move(380,615)
		
		SEEL.btn_basalt_res = QPushButton("Basalt", self)
		SEEL.btn_basalt_res.clicked.connect(lambda: self.get_rock_value(textbox_obj=self.basalt_frac_textbox, param = "basalt_frac", rock = "Basalt"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_basalt_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_basalt_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_basalt_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")

		self.basalt_frac_textbox = QLineEdit(str(self.basalt_frac[0]*1e2), self)
		self.basalt_frac_textbox.setEnabled(False)
		self.basalt_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_basalt_res.move(250,650)
		self.basalt_frac_textbox.move(380,650)

		SEEL.btn_mud_res = QPushButton("Mudstone/Shale", self)
		SEEL.btn_mud_res.clicked.connect(lambda: self.get_rock_value(textbox_obj=self.mud_frac_textbox, param = "mud_frac", rock = "Mudstone/Shale"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_mud_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_mud_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_mud_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")

		self.mud_frac_textbox = QLineEdit(str(self.mud_frac[0]*1e2), self)
		self.mud_frac_textbox.setEnabled(False)
		self.mud_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_mud_res.move(490,580)
		self.mud_frac_textbox.move(620,580)

		SEEL.btn_gabbro_res = QPushButton("Gabbro", self)
		SEEL.btn_gabbro_res.clicked.connect(lambda: self.get_rock_value(textbox_obj=self.gabbro_frac_textbox, param = "gabbro_frac", rock = "Gabbro"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_gabbro_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_gabbro_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_gabbro_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")

		self.gabbro_frac_textbox = QLineEdit(str(self.gabbro_frac[0]*1e2), self)
		self.gabbro_frac_textbox.setEnabled(False)
		self.gabbro_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_gabbro_res.move(490,615)
		self.gabbro_frac_textbox.move(620,615)

		SEEL.btn_other_rock_res = QPushButton("Other Rock", self)
		SEEL.btn_other_rock_res.clicked.connect(lambda: self.get_rock_value(textbox_obj=self.other_rock_frac_textbox, param = "other_rock_frac", rock = "Other Rock"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_other_rock_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_other_rock_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_other_rock_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")

		self.other_rock_frac_textbox = QLineEdit(str(self.other_rock_frac[0]*1e2), self)
		self.other_rock_frac_textbox.setEnabled(False)
		self.other_rock_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_other_rock_res.move(490,650)
		self.other_rock_frac_textbox.move(620,650)
		
		total_label_1 = QLabel(self)
		total_label_1.setText('Total:')
		total_label_1.setStyleSheet("QLabel {font:bold}; min-width: 100em ; fontsize: 10pt;color: red")
		total_label_1.move(490,685)
		
		self.total_rock_textbox = QLineEdit(str(self.granite_frac[0]*1e2 + self.granulite_frac[0]*1e2 +\
							self.sandstone_frac[0]*1e2 + self.gneiss_frac[0]*1e2 + self.amphibolite_frac[0]*1e2 +\
							self.basalt_frac[0]*1e2 + self.mud_frac[0]*1e2 + self.gabbro_frac[0]*1e2 +\
								self.other_rock_frac[0]*1e2), self)
		self.total_rock_textbox.setEnabled(False)
		self.total_rock_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		self.total_rock_textbox.move(620,685)


		line_mark_2 = QLabel(self)
		line_mark_2.setText('------------------------------------------')
		line_mark_2.setStyleSheet("QLabel {font:bold}; min-width: 100em ; fontsize: 10pt;color: red")
		line_mark_2.move(20,685)

		SEEL.btn_quartz_res = QPushButton("Quartz", self)
		SEEL.btn_quartz_res.clicked.connect(lambda: self.get_mineral_value(textbox_obj=self.quartz_frac_textbox, param = "quartz_frac", mineral = "Quartz"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_quartz_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_quartz_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_quartz_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.quartz_frac_textbox = QLineEdit(str(self.quartz_frac[0]*1e2), self)
		self.quartz_frac_textbox.setEnabled(False)
		self.quartz_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_quartz_res.move(10,720)
		self.quartz_frac_textbox.move(140,720)

		SEEL.btn_plag_res = QPushButton("Plagioclase", self)
		SEEL.btn_plag_res.clicked.connect(lambda: self.get_mineral_value(textbox_obj=self.plag_frac_textbox, param = "plag_frac", mineral = "Plagioclase"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_plag_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_plag_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_plag_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.plag_frac_textbox = QLineEdit(str(self.plag_frac[0]*1e2), self)
		self.plag_frac_textbox.setEnabled(False)
		self.plag_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_plag_res.move(10,755)
		self.plag_frac_textbox.move(140,755)

		SEEL.btn_amp_res = QPushButton("Amphibole", self)
		SEEL.btn_amp_res.clicked.connect(lambda: self.get_mineral_value(textbox_obj=self.amp_frac_textbox, param = "amp_frac", mineral = "Amphibole"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_amp_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_amp_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_amp_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.amp_frac_textbox = QLineEdit(str(self.amp_frac[0]*1e2), self)
		self.amp_frac_textbox.setEnabled(False)
		self.amp_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_amp_res.move(10,790)
		self.amp_frac_textbox.move(140,790)
		
		SEEL.btn_kfelds_res = QPushButton("K-Feldspar", self)
		SEEL.btn_kfelds_res.clicked.connect(lambda: self.get_mineral_value(textbox_obj=self.kfelds_frac_textbox, param = "kfelds_frac", mineral = "K-Feldspar"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_kfelds_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_kfelds_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_kfelds_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.kfelds_frac_textbox = QLineEdit(str(self.kfelds_frac[0]*1e2), self)
		self.kfelds_frac_textbox.setEnabled(False)
		self.kfelds_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_kfelds_res.move(10,825)
		self.kfelds_frac_textbox.move(140,825)
		
		SEEL.btn_garnet_res = QPushButton("Garnet", self)
		SEEL.btn_garnet_res.clicked.connect(lambda: self.get_mineral_value(textbox_obj=self.garnet_frac_textbox, param = "garnet_frac", mineral = "Garnet"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_garnet_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_garnet_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_garnet_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.garnet_frac_textbox = QLineEdit(str(self.garnet_frac[0]*1e2), self)
		self.garnet_frac_textbox.setEnabled(False)
		self.garnet_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_garnet_res.move(10,860)
		self.garnet_frac_textbox.move(140,860)

		SEEL.btn_ol_res = QPushButton("Olivine", self)
		SEEL.btn_ol_res.clicked.connect(lambda: self.get_mineral_value(textbox_obj=self.ol_frac_textbox, param = "ol_frac", mineral = "Olivine"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_ol_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_ol_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_ol_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.ol_frac_textbox = QLineEdit(str(self.ol_frac[0]*1e2), self)
		self.ol_frac_textbox.setEnabled(False)
		self.ol_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_ol_res.move(10,895)
		self.ol_frac_textbox.move(140,895)
		
		SEEL.btn_opx_res = QPushButton("Orthopyroxene", self)
		SEEL.btn_opx_res.clicked.connect(lambda: self.get_mineral_value(textbox_obj=self.opx_frac_textbox, param = "opx_frac", mineral = "Orthopyroxene"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_opx_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_opx_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_opx_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.opx_frac_textbox = QLineEdit(str(self.opx_frac[0]*1e2), self)
		self.opx_frac_textbox.setEnabled(False)
		self.opx_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_opx_res.move(250,720)
		self.opx_frac_textbox.move(380,720)
		
		SEEL.btn_cpx_res = QPushButton("Clinopyroxene", self)
		SEEL.btn_cpx_res.clicked.connect(lambda: self.get_mineral_value(textbox_obj=self.cpx_frac_textbox, param = "cpx_frac", mineral = "Clinopyroxene"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_cpx_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_cpx_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_cpx_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.cpx_frac_textbox = QLineEdit(str(self.cpx_frac[0]*1e2), self)
		self.cpx_frac_textbox.setEnabled(False)
		self.cpx_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_cpx_res.move(250,755)
		self.cpx_frac_textbox.move(380,755)
		
		SEEL.btn_mica_res = QPushButton("Mica", self)
		SEEL.btn_mica_res.clicked.connect(lambda: self.get_mineral_value(textbox_obj=self.mica_frac_textbox, param = "mica_frac", mineral = "Mica"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_mica_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_mica_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_mica_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.mica_frac_textbox = QLineEdit(str(self.mica_frac[0]*1e2), self)
		self.mica_frac_textbox.setEnabled(False)
		self.mica_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_mica_res.move(250,790)
		self.mica_frac_textbox.move(380,790)
		
		SEEL.btn_graphite_res = QPushButton("Graphite", self)
		SEEL.btn_graphite_res.clicked.connect(lambda: self.get_mineral_value(textbox_obj=self.graphite_frac_textbox, param = "graphite_frac", mineral = "Graphite"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_graphite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_graphite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_graphite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.graphite_frac_textbox = QLineEdit(str(self.graphite_frac[0]*1e2), self)
		self.graphite_frac_textbox.setEnabled(False)
		self.graphite_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_graphite_res.move(250,825)
		self.graphite_frac_textbox.move(380,825)

		SEEL.btn_sulphides_res = QPushButton("Sulphides", self)
		SEEL.btn_sulphides_res.clicked.connect(lambda: self.get_mineral_value(textbox_obj=self.sulphides_frac_textbox, param = "sulphide_frac", mineral = "Sulphides"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_sulphides_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_sulphides_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_sulphides_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.sulphides_frac_textbox = QLineEdit(str(self.sulphide_frac[0]*1e2), self)
		self.sulphides_frac_textbox.setEnabled(False)
		self.sulphides_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_sulphides_res.move(250,860)
		self.sulphides_frac_textbox.move(380,860)
		
		SEEL.btn_mixture_res = QPushButton("Mixtures", self)
		SEEL.btn_mixture_res.clicked.connect(lambda: self.get_mineral_value(textbox_obj=self.mixture_frac_textbox, param = "mixture_frac", mineral = "Mixtures"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_mixture_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_mixture_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_mixture_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.mixture_frac_textbox = QLineEdit(str(self.mixture_frac[0]*1e2), self)
		self.mixture_frac_textbox.setEnabled(False)
		self.mixture_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_mixture_res.move(250,895)
		self.mixture_frac_textbox.move(380,895)

		SEEL.btn_other_res = QPushButton("Other", self)
		SEEL.btn_other_res.clicked.connect(lambda: self.get_mineral_value(textbox_obj=self.other_frac_textbox, param = "other_frac", mineral = "Other"))
		if SEEL.solid_phase_method == 1:
			SEEL.btn_other_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 0:
			SEEL.btn_other_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		elif SEEL.solid_phase_method == 2:
			SEEL.btn_other_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
		self.other_frac_textbox = QLineEdit(str(self.other_frac[0]*1e2), self)
		self.other_frac_textbox.setEnabled(False)
		self.other_frac_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		SEEL.btn_other_res.move(490,720)
		self.other_frac_textbox.move(620,720)
		
		total_label_2 = QLabel(self)
		total_label_2.setText('Total:')
		total_label_2.setStyleSheet("QLabel {font:bold}; min-width: 100em ; fontsize: 10pt;color: red")
		total_label_2.move(490,930)
		
		self.total_min_textbox = QLineEdit(str(self.quartz_frac[0]*1e2 + self.plag_frac[0]*1e2 + self.kfelds_frac[0]*1e2 +\
						self.amp_frac[0]*1e2 + self.opx_frac[0]*1e2 + self.cpx_frac[0]*1e2 + self.mica_frac[0]*1e2 +\
						self.garnet_frac[0]*1e2 + self.sulphide_frac[0]*1e2 + self.graphite_frac[0]*1e2 + self.ol_frac[0]*1e2 + self.mixture_frac[0]*1e2 + self.other_frac[0]*1e2), self)
		self.total_min_textbox.setEnabled(False)
		self.total_min_textbox.setStyleSheet("QlineEdit {min-width: 4em}")
		self.total_min_textbox.move(620,930)

		self.act_comp_btn = QPushButton('Plot Composition',self)
		self.act_comp_btn.move(550,65)
		self.act_comp_btn.setStyleSheet("QPushButton {min-width: 10em; font: bold; font-size: 9pt;background-color: #93db88}")
		self.act_comp_btn.clicked.connect(self.plot_composition_button)
		
		self.calc_cond_btn = QPushButton('Calculate Conductivity',self)
		self.calc_cond_btn.move(550,100)
		self.calc_cond_btn.setStyleSheet("QPushButton {min-width: 10em; font: bold; font-size: 9pt;background-color: #93db88}")
		self.calc_cond_btn.clicked.connect(self.calculate_conductivity_button)

		self.cp_solid_val_btn = QPushButton('Copy Solid Cond. Clipboard', self)
		self.cp_solid_val_btn.move(550,170)
		self.cp_solid_val_btn.setStyleSheet("QPushButton {min-width: 10em; font: bold; font-size: 9pt;background-color: #3248a8}")
		self.cp_solid_val_btn.clicked.connect(lambda: self.cp_val_to_clipboard(param = 'solid'))

		self.cp_melt_fluid_val_btn = QPushButton('Copy Melt Cond. Clipboard', self)
		self.cp_melt_fluid_val_btn.move(550,205)
		self.cp_melt_fluid_val_btn.setStyleSheet("QPushButton {min-width: 10em; font: bold; font-size: 9pt;background-color: #3248a8}")
		self.cp_melt_fluid_val_btn.clicked.connect(lambda: self.cp_val_to_clipboard(param = 'melt_fluid'))

		self.cp_bulk_val_btn = QPushButton('Copy Bulk Cond. Clipboard', self)
		self.cp_bulk_val_btn.move(550,240)
		self.cp_bulk_val_btn.setStyleSheet("QPushButton {min-width: 10em; font: bold; font-size: 9pt;background-color: #3248a8}")
		self.cp_bulk_val_btn.clicked.connect(lambda: self.cp_val_to_clipboard(param = 'bulk'))
		
		self.show()
		
	def fill_lineEdit_values(self):
	
		self.depth_textbox.setText(str(self.depth[0]))
		self.temp_textbox.setText(str(self.T[0]))
		self.melt_content_textbox.setText(str(self.melt_fluid_mass_frac[0] * 1e2)) 
		self.salinity_textbox.setText(str(self.salinity_fluid[0]))
		self.co2_melt_textbox.setText(str(self.co2_melt[0]))
		self.h2o_melt_textbox.setText(str(self.h2o_melt[0]))
		self.na2o_melt_textbox.setText(str(self.na2o_melt[0]))
		self.k2o_melt_textbox.setText(str(self.k2o_melt[0]))
		self.bckgr_res_textbox.setText(str(self.bckgr_res[0]))
		
		self.granite_frac_textbox.setText(str(self.granite_frac[0])*1e2)
		self.granulite_frac_textbox.setText(str(self.granulite_frac[0]*1e2))
		self.sandstone_frac_textbox.setText(str(self.sandstone_frac[0]*1e2))
		self.gneiss_frac_textbox.setText(str(self.gneiss_frac[0]*1e2))
		self.amphibolite_frac_textbox.setText(str(self.amphibolite_frac[0]*1e2))
		self.basalt_frac_textbox.setText(str(self.basalt_frac[0]*1e2))
		self.mud_frac_textbox.setText(str(self.mud_frac[0]*1e2))
		self.gabbro_frac_textbox.setText(str(self.gabbro_frac[0]*1e2))
		self.other_rock_frac_textbox.setText(str(self.other_rock_frac[0]*1e2))
		
		self.total_rock_textbox.setText(str(self.granite_frac[0]*1e2 + self.granulite_frac[0]*1e2 +\
							self.sandstone_frac[0]*1e2 + self.gneiss_frac[0]*1e2 + self.amphibolite_frac[0]*1e2 +\
							self.basalt_frac[0]*1e2 + self.mud_frac[0]*1e2 + self.gabbro_frac[0]*1e2 +\
								self.other_rock_frac[0]*1e2))
		
		self.quartz_frac_textbox.setText(str(self.quartz_frac[0]*1e2))
		self.plag_frac_textbox.setText(str(self.plag_frac[0]*1e2))
		self.amp_frac_textbox.setText(str(self.amp_frac[0]*1e2))
		self.kfelds_frac_textbox.setText(str(self.kfelds_frac[0]*1e2))
		self.garnet_frac_textbox.setText(str(self.garnet_frac[0]*1e2))
		self.ol_frac_textbox.setText(str(self.ol_frac[0]*1e2))
		self.opx_frac_textbox.setText(str(self.opx_frac[0]*1e2))
		self.cpx_frac_textbox.setText(str(self.cpx_frac[0]*1e2))
		self.mica_frac_textbox.setText(str(self.mica_frac[0]*1e2))
		self.graphite_frac_textbox.setText(str(self.graphite_frac[0]*1e2))
		self.sulphides_frac_textbox.setText(str(self.sulphide_frac[0]*1e2))
		self.mixture_frac_textbox.setText(str(self.mixture_frac[0]*1e2))
		self.other_frac_textbox.setText(str(self.other_frac[0]*1e2))
		
		self.total_min_textbox.setText(str(self.quartz_frac[0]*1e2 + self.plag_frac[0]*1e2 + self.kfelds_frac[0]*1e2 +\
						self.amp_frac[0]*1e2 + self.opx_frac[0]*1e2 + self.cpx_frac[0]*1e2 + self.mica_frac[0]*1e2 +\
						self.garnet_frac[0]*1e2 + self.sulphide_frac[0]*1e2 + self.graphite_frac[0]*1e2 + self.ol_frac[0]*1e2 + self.mixture_frac[0]*1e2 + self.other_frac[0]*1e2))
		
		
	def get_pressure(self):
		
		text, ok = QInputDialog.getText(self, 'Pressure Dialogue', 'Enter the value in (GPa):')
		if ok:
			try:
				float(text)
				if (float(text) > 0.0):
					self.pressure_textbox.setText(str(text))
					self.p = np.array([float(text)])
					self.depth = np.array([float(text) * 26.0]) #assuming a density of crust of 2.6 g/cm^3
					self.depth_textbox.setText(str(float(text) * 26.0))
				else:
					QMessageBox.about(self,"Warning!","Enter a value larger than 0")
			except ValueError:
				QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")
				
	def get_depth(self):
		
		text, ok = QInputDialog.getText(self, 'Depth Dialogue', 'Enter the value in (km):')
		if ok:
			try:
				float(text)
				if (float(text) > 0.0):
					self.depth_textbox.setText(str(text))
					self.depth = np.array([float(text)])
					self.p = np.array([float(text) / 26.0]) #assuming a density of crust of 2.6 g/cm^3
					self.pressure_textbox.setText(str(float(text) / 26.0))
				else:
					QMessageBox.about(self,"Warning!","Enter a value larger than 0")
			except ValueError:
				QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")
		
	def get_temp(self):
	
		text, ok = QInputDialog.getText(self, 'Temperature Dialogue', 'Enter the value in (C):')
		if ok:
			try:
				float(text)
				if (float(text) > 0.0):
					self.temp_textbox.setText(str(text))
					self.T = np.array([float(text)])
				else:
					QMessageBox.about(self,"Warning!","Enter a value larger than 0")
			except ValueError:
				QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")

	def get_fluid_melt_content(self):

		text, ok = QInputDialog.getText(self, 'Melt Content Dialogue', 'Enter the value in (%):')
		if ok:
			try:
				float(text)
				if (float(text) <= 100.0) and (float(text) > 0.0):
					self.melt_content_textbox.setText(str(text))
					self.melt_fluid_mass_frac = np.array([float(text) / 1e2])
				else:
					QMessageBox.about(self,"Warning!","Enter a value between 0 and 100")
			except ValueError:
				QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")
		
	def get_salinity(self):

		if SEEL.fluid_or_melt_method == 0:
			text, ok = QInputDialog.getText(self, 'Salinity Content Dialogue', 'Enter the value in (%):')
			if ok:
				try:
					float(text)
					self.salinity_textbox.setText(str(text))
					self.salinity_fluid = np.array([float(text)])
				except ValueError:
					QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")
		else:
			QMessageBox.about(self,"Warning!","Only fluids can have salinity. Now, the fluid phase is selected to be melt.")
		
	def get_co2_melt(self):

		if SEEL.fluid_or_melt_method == 1:
			text, ok = QInputDialog.getText(self, 'CO2 Melt Dialogue', 'Enter the value in (ppm):')
			if ok:
				try:
					float(text)
					self.co2_melt_textbox.setText(str(text))
					self.co2_melt = np.array([float(text)])
				except ValueError:
					QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")
		else:
			QMessageBox.about(self,"Warning!","Only melts can have co2. Now, the phase is selected to be fluid.")
		
	def get_h2o_melt(self):

		if SEEL.fluid_or_melt_method == 1:
			text, ok = QInputDialog.getText(self, 'H2O Melt Dialogue', 'Enter the value in (ppm):')
			if ok:
				try:
					float(text)
					self.h2o_melt_textbox.setText(str(text))
					self.h2o_melt = np.array([float(text)])
				except ValueError:
					QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")
		else:
			QMessageBox.about(self,"Warning!","Only melts can have strcutrally bounded h2o. Now, the phase is selected to be fluid.")
		
	def get_nao_melt(self):

		if SEEL.fluid_or_melt_method == 1:
			text, ok = QInputDialog.getText(self, 'NaO Melt Dialogue', 'Enter the value in (%wt):')
			if ok:
				try:
					float(text)
					self.na2o_melt_textbox.setText(str(text))
					self.na2o_melt = np.array([float(text)])
				except ValueError:
					QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")
		else:
			QMessageBox.about(self,"Warning!","Only melts can have NaO in this software. Now, the phase is selected to be fluid.")

	def get_k2o_melt(self):

		if SEEL.fluid_or_melt_method == 1:
			text, ok = QInputDialog.getText(self, 'K2O Melt Dialogue', 'Enter the value in (wt%):')
			if ok:
				try:
					float(text)
					self.k2o_melt_textbox.setText(str(text))
					self.k2o_melt = np.array([float(text)])
				except ValueError:
					QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")
		else:
			QMessageBox.about(self,"Warning!","Only melts can have K2O in this software. Now, the phase is selected to be fluid.")

	def get_bckgr_res(self):

		if SEEL.solid_phase_method == 0:
			text, ok = QInputDialog.getText(self, 'Background Resistivity Dialogue', 'Enter the value in (ohm m):')
			if ok:
				try:
					float(text)
					self.bckgr_res_textbox.setText(str(text))
					self.bckgr_res = np.array([float(text)])
				except ValueError:
					QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")
		else:
			QMessageBox.about(self,"Warning!","You selected to use experimental conductivity measurements to build the solid phases. Choose the other option ot use this method.")
	
	def get_rock_value(self, textbox_obj,param,rock):

		if SEEL.solid_phase_method == 1:
			text, ok = QInputDialog.getText(self, rock + 'volume dialogue', 'Enter the value in (%)')
			if ok:
				try:
					float(text)
					if (float(text) <= 100.0) and (float(text) >= 0.0):

						textbox_obj.setText(str(text))
						setattr(self, param, np.array([float(text) / 1e2]))
						self.total_rock_textbox.setText(str(self.granite_frac[0]*1e2 + self.granulite_frac[0]*1e2 +\
							self.sandstone_frac[0]*1e2 + self.gneiss_frac[0]*1e2 + self.amphibolite_frac[0]*1e2 +\
							self.basalt_frac[0]*1e2 + self.mud_frac[0]*1e2 + self.gabbro_frac[0]*1e2 +\
								self.other_rock_frac[0]*1e2))
								
						self.composition_set = False

					else:
						QMessageBox.about(self,"Warning!","Enter a value between 0 and 100")
				except ValueError:
					QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")
		else:
			QMessageBox.about(self,"Warning!","You selected to use the background resistivity mode. Choose the other option ot use experimental conductivity measurements to build a mixing model..")
	
	def get_mineral_value(self, textbox_obj, param, mineral):

		if SEEL.solid_phase_method == 2:
			text, ok = QInputDialog.getText(self, mineral + 'volume dialogue', 'Enter the value in (%)')
			if ok:
				try:
					float(text)
					if (float(text) <= 100.0) and (float(text) >= 0.0):

						textbox_obj.setText(str(text))
						setattr(self, param, np.array([float(text) / 1e2]))
						self.total_min_textbox.setText(str(self.quartz_frac[0]*1e2 + self.plag_frac[0]*1e2 + self.kfelds_frac[0]*1e2 +\
						self.amp_frac[0]*1e2 + self.opx_frac[0]*1e2 + self.cpx_frac[0]*1e2 + self.mica_frac[0]*1e2 +\
						self.garnet_frac[0]*1e2 + self.sulphide_frac[0]*1e2 + self.graphite_frac[0]*1e2 + self.ol_frac[0]*1e2 + self.mixture_frac[0]*1e2 + self.other_frac[0]*1e2))

						self.composition_set = False

					else:
						QMessageBox.about(self,"Warning!","Enter a value between 0 and 100")
				except ValueError:
					QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")
		else:
			QMessageBox.about(self,"Warning!","You selected to use the background resistivity or rock conductivity mode. Choose the other option ot use experimental conductivity measurements to build a mixing model..")
	
	def fluid_phase_popup(self):

		if self.fluid_melt_pop is None:
			self.fluid_melt_pop = FLUID_MELT_POP()
			self.fluid_melt_pop.setGeometry(QtCore.QRect(100, 500, 100, 100))
		self.fluid_melt_pop.show()

	def solid_phase_popup(self):

		if self.solid_phase_pop is None:
			self.solid_phase_pop = SOLID_PHASE_POP()
			self.solid_phase_pop.setGeometry(QtCore.QRect(100, 500, 400, 100))
		self.solid_phase_pop.show()
		
	def fo2_properties_popup(self):

		if self.fo2_pop is None:
			self.fo2_pop = FUG_POP()
			self.fo2_pop.setGeometry(QtCore.QRect(100, 100, 100, 100))
		self.fo2_pop.show()
		
	def water_calib_popup(self):

		if self.water_calib_pop is None:
			self.water_calib_pop = WATER_CALIB_POP()
			self.water_calib_pop.setGeometry(QtCore.QRect(100, 100, 100, 100))
		self.water_calib_pop.show()


	def read_csv(self,filename,delim):

		#Simple function for reading csv files and give out filtered output for given delimiter (delim)

		file_obj = open(filename,'rt',encoding = "utf8") #Creating file object
		file_csv = csv.reader(file_obj,delimiter = delim) #Reading the file object with csv module, delimiter assigned to ','
		data = [] #Creating empty array to append data

		#Appending data from csb object
		for row in file_csv:
			data.append(row)

		#Filtering data for None elements read.
		for j in range(0,len(data)):
			data[j] = list(filter(None,data[j]))
		data = list(filter(None,data))

		return data

	def read_cond_models(self):

		#A function that reads conductivity model files and get the data.

		self.fluid_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'fluids.csv'),delim = ',') 
		self.melt_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'melt.csv'),delim = ',')

		#reading rocks
		self.granite_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'rocks', 'granite.csv'),delim = ',')
		self.granulite_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'rocks', 'granulite.csv'),delim = ',')
		self.sandstone_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'rocks', 'sandstone.csv'),delim = ',')
		self.gneiss_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'rocks', 'gneiss.csv'),delim = ',')
		self.amphibolite_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'rocks', 'amphibolite.csv'),delim = ',')
		self.basalt_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'rocks', 'basalt.csv'),delim = ',')
		self.mud_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'rocks', 'mud.csv'),delim = ',')
		self.gabbro_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'rocks', 'gabbro.csv'),delim = ',')
		self.other_rock_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'rocks', 'other_rock.csv'),delim = ',')

		#reading minerals
		self.quartz_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'quartz.csv'),delim = ',')
		self.plag_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'plag.csv'),delim = ',')
		self.amp_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'amp.csv'),delim = ',')
		self.kfelds_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'kfelds.csv'),delim = ',')
		self.opx_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'opx.csv'),delim = ',')
		self.cpx_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'cpx.csv'),delim = ',')
		self.mica_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'mica.csv'),delim = ',')
		self.garnet_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'garnet.csv'),delim = ',')
		self.sulphides_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'sulphides.csv'),delim = ',')
		self.graphite_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'graphite.csv'),delim = ',')
		self.ol_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'ol.csv'),delim = ',')
		self.mixture_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'mixtures.csv'),delim = ',')
		self.other_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'other.csv'),delim = ',')
		

		self.cond_data_array = [self.fluid_cond_data, self.melt_cond_data, self.granite_cond_data, self.granulite_cond_data,
			  self.sandstone_cond_data, self.gneiss_cond_data, self.amphibolite_cond_data, self.basalt_cond_data, self.mud_cond_data,
			   self.gabbro_cond_data, self.other_rock_cond_data, self.quartz_cond_data, self.plag_cond_data,
			  self.amp_cond_data, self.kfelds_cond_data, self.opx_cond_data, self.cpx_cond_data, self.mica_cond_data,
			  self.garnet_cond_data, self.sulphides_cond_data, self.graphite_cond_data, self.ol_cond_data, self.mixture_cond_data,
			  self.other_cond_data]

		len_fluid = len(self.fluid_cond_data) - 1 
		len_melt = len(self.melt_cond_data) - 1

		self.fluid_num = 2

		len_granite = len(self.granite_cond_data) - 1
		len_granulite = len(self.granulite_cond_data) - 1
		len_sandstone = len(self.sandstone_cond_data) - 1
		len_gneiss = len(self.gneiss_cond_data) - 1
		len_amphibolite = len(self.amphibolite_cond_data) - 1
		len_basalt = len(self.basalt_cond_data) - 1
		len_mud = len(self.mud_cond_data) - 1
		len_gabbro = len(self.gabbro_cond_data) - 1
		len_other_rock = len(self.other_rock_cond_data) - 1
		
		self.rock_num = 9

		len_quartz = len(self.quartz_cond_data) - 1
		len_plag = len(self.plag_cond_data) - 1
		len_amp = len(self.amp_cond_data) - 1
		len_kfelds = len(self.kfelds_cond_data) - 1
		len_opx = len(self.opx_cond_data) - 1
		len_cpx = len(self.cpx_cond_data) - 1
		len_mica = len(self.mica_cond_data) - 1
		len_garnet = len(self.garnet_cond_data) - 1
		len_sulphides = len(self.sulphides_cond_data) - 1
		len_graphite = len(self.graphite_cond_data) - 1
		len_ol = len(self.ol_cond_data) - 1
		len_mixture = len(self.mixture_cond_data) - 1
		len_other = len(self.other_cond_data) - 1

		self.mineral_num = 15

		#Creating empty arrays for appending new data.
		SEEL.name = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		SEEL.type = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		SEEL.t_min = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		SEEL.t_max = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.p_min = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.p_max = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.w_calib = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.mg_cond = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.sigma_i =  [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.sigma_i_err =  [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.h_i =  [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.h_i_err =  [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.sigma_pol = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.sigma_pol_err = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.h_pol = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.h_pol_err = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.sigma_p = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.sigma_p_err = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.h_p = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.h_p_err = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.r = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.r_err = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.alpha_p = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.alpha_p_err = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.wtype = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]
		self.dens_mat = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
		   [None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_mixture, [None] * len_other]

		#Filling up the arrays.
		for i in range(0,len(SEEL.type)):
			count = 1
			for j in range(0,len(SEEL.type[i])):
				SEEL.name[i][count-1] = self.cond_data_array[i][count][0]
				SEEL.type[i][count-1] = self.cond_data_array[i][count][1]
				SEEL.t_min[i][count-1] = float(self.cond_data_array[i][count][2])
				SEEL.t_max[i][count-1] = float(self.cond_data_array[i][count][3])
				self.p_min[i][count-1] = float(self.cond_data_array[i][count][4])
				self.p_max[i][count-1] = float(self.cond_data_array[i][count][5])
				self.w_calib[i][count-1] = int(self.cond_data_array[i][count][6])
				self.mg_cond[i][count-1] = float(self.cond_data_array[i][count][7])
				self.sigma_i[i][count-1] = float(self.cond_data_array[i][count][8])
				self.sigma_i_err[i][count-1] = float(self.cond_data_array[i][count][9])
				self.h_i[i][count-1] = float(self.cond_data_array[i][count][10])
				self.h_i_err[i][count-1] = float(self.cond_data_array[i][count][11])
				self.sigma_pol[i][count-1] = float(self.cond_data_array[i][count][12])
				self.sigma_pol_err[i][count-1] = float(self.cond_data_array[i][count][13])
				self.h_pol[i][count-1] = float(self.cond_data_array[i][count][14])
				self.h_pol_err[i][count-1] = float(self.cond_data_array[i][count][15])
				self.sigma_p[i][count-1] = float(self.cond_data_array[i][count][16])
				self.sigma_p_err[i][count-1] = float(self.cond_data_array[i][count][17])
				self.h_p[i][count-1] = float(self.cond_data_array[i][count][18])
				self.h_p_err[i][count-1] = float(self.cond_data_array[i][count][19])
				self.r[i][count-1] = float(self.cond_data_array[i][count][20])
				self.r_err[i][count-1] = float(self.cond_data_array[i][count][21])
				self.alpha_p[i][count-1] = float(self.cond_data_array[i][count][22])
				self.alpha_p_err[i][count-1] = float(self.cond_data_array[i][count][23])
				self.wtype[i][count-1] = int(self.cond_data_array[i][count][24])
				self.dens_mat[i][count-1] = float(self.cond_data_array[i][count][25])
			
				count += 1

	def read_params(self):

		#READING THE PARAMETERS IN PARAMS.CSV WHICH ARE GENERAL PHYSICAL CONSTANTS
		#AND PROPERTIES OF MATERIALS

		params_dat = self.read_csv(os.path.join(self.core_path, 'params.csv'), delim = ',')

		self.g = float(params_dat[0][1]) # in kg/
		self.R = float(params_dat[1][1])
		self.avog = float(params_dat[2][1])
		self.boltz = float(params_dat[3][1])
		self.el_q = float(params_dat[4][1])
		SEEL.spreadsheet = str(params_dat[5][1])
		self.mu = 4.0 * np.pi * 10**(-7)
		
		correction_factor_dat = self.read_csv(os.path.join(self.core_path, 'water_calib.csv'), delim = ',')

		#olivines
		self.pat2with = float(correction_factor_dat[0][1])
		self.bell2with = float(correction_factor_dat[1][1])
		self.pat2bell = float(correction_factor_dat[2][1])
		self.with2bell = 1.0/self.bell2with
		self.bell2path = 1.0/self.pat2bell
		self.with2pat = 1.0/self.pat2with
		
		#pyroxene and gt
		self.pat2bell95 = float(correction_factor_dat[3][1])
		self.bell952pat = 1.0/self.pat2bell95
		
		#feldspars
		self.john2mosen = float(correction_factor_dat[4][1])
		self.mosen2john = 1.0 / self.john2mosen

	def check_composition(self):

		continue_adjusting = True

		if SEEL.solid_phase_method == 0:

			pass

		elif SEEL.solid_phase_method == 1:

			tot = self.granite_frac[0] + self.granulite_frac[0] + self.sandstone_frac[0] +\
			self.gneiss_frac[0] + self.amphibolite_frac[0] + self.basalt_frac[0] + self.mud_frac[0] +\
				 self.gabbro_frac[0] + self.other_rock_frac[0]
				 
			if (tot <= 0.99) or (tot >= 1.01):
				QMessageBox.about(self, "Warning!", "The total number of does not add up to 100%. Currently it is:  " + str(tot*1e2))
				continue_adjusting = False
				
		elif SEEL.solid_phase_method == 2:

			tot = self.quartz_frac[0] + self.plag_frac[0] + self.amp_frac[0] + self.kfelds_frac[0] +\
			self.opx_frac[0] + self.cpx_frac[0] + self.mica_frac[0] + self.garnet_frac[0] + self.sulphide_frac[0] + self.graphite_frac[0] +\
			self.ol_frac[0] + self.mixture_frac[0] + self.other_frac[0]

			if (tot <= 0.99) or (tot > 1.01):
				QMessageBox.about(self, "Warning!", "The total number of does not add up to 100%. Currently it is:  " + str(tot*1e2))
				continue_adjusting = False

		return continue_adjusting
	
	def calculate_arrhenian_single(self, T, sigma, E, r, alpha, water):

		if (sigma == 0.0) and (E == 0.0):
			cond = 0.0
		else:
			cond = (10.0**sigma) * (water**r) * np.exp(-(E + (alpha * water)**(1.0/3.0)) / (self.R * T))

		return cond
	
	def calculate_fluids_conductivity(self, method, sol_idx = None):

		if method == 'array':
			idx_node = None
		elif method == 'index':
			idx_node = sol_idx

		cond_fluids = np.zeros(len(self.T))

		if SEEL.type[0][SEEL.fluid_cond_selection] == '0':

			self.melt_fluid_cond[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[0][SEEL.fluid_cond_selection],
								   E = self.h_i[0][SEEL.fluid_cond_selection],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[0][SEEL.fluid_cond_selection],
								   E = self.h_pol[0][SEEL.fluid_cond_selection],r = 0, alpha = 0, water = 0)
			
		elif SEEL.type[0][SEEL.fluid_cond_selection] == '1':

			self.melt_fluid_cond[idx_node] =  self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[0][SEEL.fluid_cond_selection],
								   E = self.h_i[0][SEEL.fluid_cond_selection],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[0][SEEL.fluid_cond_selection],
								   E = self.h_pol[0][SEEL.fluid_cond_selection],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_p[0][SEEL.fluid_cond_selection],
								   E = self.h_p[0][SEEL.fluid_cond_selection],r = 0, alpha = 0, water = 0)
			
		elif SEEL.type[0][SEEL.fluid_cond_selection] == '3':

			if ('*' in SEEL.name[0][SEEL.fluid_cond_selection]) == True:

				fluids_odd_function = SEEL.name[0][SEEL.fluid_cond_selection].replace('*','')

			else:

				fluids_odd_function = SEEL.name[0][SEEL.fluid_cond_selection]

			cond_fluids[idx_node] = eval(fluids_odd_function + '(T = self.T[idx_node], P = self.p[idx_node], salinity = self.salinity_fluid[idx_node], method = method)')
	
		return cond_fluids

	def calculate_melt_conductivity(self, method, sol_idx = None):

		if method == 'array':
			idx_node = None
		elif method == 'index':
			idx_node = sol_idx

		cond_melt = np.zeros(len(self.T))
		
		if ("Wet" in self.name[1][SEEL.melt_cond_selection]) == True:
					
			if self.wtype[1][SEEL.melt_cond_selection] == "0":
				water_corr_factor = 1e4 #converting to wt % if the model requires
			else:
				water_corr_factor = 1.0
			
		else:
			
			water_corr_factor = 1.0

		if SEEL.type[1][SEEL.melt_cond_selection] == '0':

			cond_melt[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[1][SEEL.melt_cond_selection],
								   E = self.h_i[1][SEEL.melt_cond_selection],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[1][SEEL.melt_cond_selection],
								   E = self.h_pol[1][SEEL.melt_cond_selection],r = 0, alpha = 0, water = 0)
			
		elif SEEL.type[1][SEEL.melt_cond_selection] == '1':

			cond_melt[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[1][SEEL.melt_cond_selection],
								   E = self.h_i[1][SEEL.melt_cond_selection],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[1][SEEL.melt_cond_selection],
								   E = self.h_pol[1][SEEL.melt_cond_selection],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_p[1][SEEL.melt_cond_selection],
								   E = self.h_p[1][SEEL.melt_cond_selection], r = self.r[1][SEEL.melt_cond_selection], alpha = self.alpha_p[1][SEEL.melt_cond_selection],
								   water = self.h2o_melt/water_corr_factor)
			
		elif SEEL.type[1][SEEL.melt_cond_selection] == '3':

			if ('*' in SEEL.name[1][SEEL.melt_cond_selection]) == True:

				melt_odd_function = SEEL.name[1][SEEL.melt_cond_selection].replace('*','')

			else:

				melt_odd_function = SEEL.name[1][SEEL.melt_cond_selection]

			cond_melt[idx_node] = eval(melt_odd_function + '(T = self.T[idx_node], P = self.p[idx_node], Melt_H2O = self.h2o_melt[idx_node]/water_corr_factor,' +
			'Melt_CO2 = self.co2_melt, Melt_Na2O = self.na2o_melt[idx_node], Melt_K2O = self.k2o_melt[idx_node], method = method)')
		
		return cond_melt

	def calculate_rock_conductivity(self, method, rock_idx = None, sol_idx = None):

		if method == 'array':
			idx_node = None
		elif method == 'index':
			idx_node = sol_idx

		cond = np.zeros(len(self.T))

		rock_sub_idx = rock_idx - self.fluid_num
		
		if ("Wet" in self.name[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]]) == True:
					
			if self.wtype[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]] == "0":
				water_corr_factor = water_corr_factor * 1e4 #converting to wt % if the model requires
			else:
				water_corr_factor = 1.0
			
		else:
			
			water_corr_factor = 1.0

		if SEEL.type[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]] == '0':

			cond[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]],
								   E = self.h_i[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]],
								   E = self.h_pol[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]],r = 0, alpha = 0, water = 0)
			
		elif SEEL.type[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]] == '1':

			cond[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]],
								   E = self.h_i[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]],
								   E = self.h_pol[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_p[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]],
								   E = self.h_p[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]], r = self.r[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]],
								   alpha = self.alpha_p[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]], water = SEEL.rock_water_list[rock_sub_idx][idx_node] / water_corr_factor)
			
		elif SEEL.type[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]] == '3':

			if ('*' in SEEL.name[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]]) == True:

				odd_function = SEEL.name[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]].replace('*','')

			else:

				odd_function = SEEL.name[rock_idx][SEEL.rock_cond_selections[rock_sub_idx]]

			if ('fo2' in odd_function) == True:
				cond[idx_node] = eval(odd_function + '(T = self.T[idx_node], P = self.p[idx_node], water = SEEL.rock_water_list[SEEL.rock_cond_selections[rock_sub_idx]][idx_node] / water_corr_factor, param1 = SEEL.param1_rock_list[SEEL.rock_cond_selections[rock_sub_idx]][idx_node], param2 = SEEL.param2_rock_list[SEEL.rock_cond_selections[rock_sub_idx]][idx_node], fo2 = self.calculate_fugacity(SEEL.o2_buffer),fo2_ref = self.calculate_fugacity(3), method = method)')
			else:
				cond[idx_node] = eval(odd_function + '(T = self.T[idx_node], P = self.p[idx_node], water = SEEL.rock_water_list[SEEL.rock_cond_selections[rock_sub_idx]][idx_node] / water_corr_factor, param1 = SEEL.param1_rock_list[SEEL.rock_cond_selections[rock_sub_idx]][idx_node], param2 = SEEL.param2_rock_list[SEEL.rock_cond_selections[rock_sub_idx]][idx_node], method = method)')
		
		return cond
	
	def calculate_mineral_conductivity(self, method, min_idx = None, sol_idx = None):
	
		if method == 'array':
			idx_node = None
		elif method == 'index':
			idx_node = sol_idx

		cond = np.zeros(len(self.T))

		min_sub_idx = min_idx - self.fluid_num - self.rock_num
		
		if ("Wet" in self.name[min_idx][SEEL.minerals_cond_selections[min_sub_idx]]) == True:
		
			water_corr_factor = self.Water_correction(min_idx = min_idx)
			
			if self.wtype[min_idx][SEEL.minerals_cond_selections[min_sub_idx]] == "0":
				water_corr_factor = water_corr_factor * 1e4 #converting to wt % if the model requires
			else:
				pass
			
		else:
			
			water_corr_factor = 1.0


		if SEEL.type[min_idx][SEEL.minerals_cond_selections[min_sub_idx]] == '0':

			cond[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[min_idx][SEEL.minerals_cond_selections[min_sub_idx]],
								   E = self.h_i[min_idx][SEEL.minerals_cond_selections[min_sub_idx]],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[min_idx][SEEL.minerals_cond_selections[min_sub_idx]],
								   E = self.h_pol[min_idx][SEEL.minerals_cond_selections[min_sub_idx]],r = 0, alpha = 0, water = 0)
			
		elif SEEL.type[min_idx][SEEL.minerals_cond_selections[min_sub_idx]] == '1':
		

			cond[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[min_idx][SEEL.minerals_cond_selections[min_sub_idx]],
								   E = self.h_i[min_idx][SEEL.minerals_cond_selections[min_sub_idx]],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[min_idx][SEEL.minerals_cond_selections[min_sub_idx]],
								   E = self.h_pol[min_idx][SEEL.minerals_cond_selections[min_sub_idx]],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_p[min_idx][SEEL.minerals_cond_selections[min_sub_idx]],
								   E = self.h_p[min_idx][SEEL.minerals_cond_selections[min_sub_idx]], r = self.r[min_idx][SEEL.minerals_cond_selections[min_sub_idx]],
								   alpha = self.alpha_p[min_idx][SEEL.minerals_cond_selections[min_sub_idx]], water = SEEL.mineral_water_list[min_sub_idx][idx_node] / water_corr_factor)
			
		elif SEEL.type[min_idx][SEEL.minerals_cond_selections[min_sub_idx]] == '3':

			if ('*' in SEEL.name[min_idx][SEEL.minerals_cond_selections[min_sub_idx]]) == True:

				odd_function = SEEL.name[min_idx][SEEL.minerals_cond_selections[min_sub_idx]].replace('*','')

			else:

				odd_function = SEEL.name[min_idx][SEEL.minerals_cond_selections[min_sub_idx]]

			if ('fo2' in odd_function) == True:

				cond[idx_node] = eval(odd_function + '(T = self.T[idx_node], P = self.p[idx_node], water = SEEL.mineral_water_list[min_sub_idx][idx_node] / water_corr_factor, param1 = SEEL.param1_mineral_list[min_sub_idx][idx_node], param2 = SEEL.param2_mineral_list[min_sub_idx][idx_node], fo2 = self.calculate_fugacity(SEEL.o2_buffer),fo2_ref = self.calculate_fugacity(3), method = method)')

			else:

				cond[idx_node] = eval(odd_function + '(T = self.T[idx_node], P = self.p[idx_node], water = SEEL.mineral_water_list[min_sub_idx][idx_node] / water_corr_factor, param1 = SEEL.param1_mineral_list[min_sub_idx][idx_node], param2 = SEEL.param2_mineral_list[min_sub_idx][idx_node], method = method)')

		return cond
		
	def Water_correction(self, min_idx = None):

		#A function that corrects the water content to desired calibration. Numbers are taken from Demouchy and Bolfan-Casanova (2016, Lithos) for olivine, pyroxene and garnet.
		#For feldspars, the correction number is taken from Mosenfelder et al. (2015, Am. Min.)

		if min_idx == 21:
		#olivine

			calib_object = self.w_calib[min_idx][SEEL.ol_cond_selection]
			calib_object_2 = SEEL.ol_calib

			if calib_object_2 == 0:

				if calib_object == 0:
					
					CORR_Factor = self.pat2with #Paterson to Withers

				elif calib_object == 1:

					CORR_Factor = self.bell2with #Bell to Withers from Demouchy and Bolfan Casanova

				else:

					CORR_Factor= 1.0 #Withers to Withers

			elif calib_object_2 == 1:

				if calib_object == 0:

					CORR_Factor = self.pat2bell #Paterson to Bell

				elif calib_object == 1:

					CORR_Factor = 1.0 #Bell to Bell

				else:

					CORR_Factor = self.with2bell #Withers to Bell


			elif calib_object_2 == 2:

				if calib_object == 0:


					CORR_Factor = 1.0 #Paterson to paterson

				elif calib_object == 1:

					CORR_Factor = self.bell2path #Bell to Paterson

				else:

					CORR_Factor = self.with2pat #Withers to Paterson
					
			else:
			
				CORR_Factor = 1.0

		elif (min_idx == 15) or (min_idx == 16) or (min_idx == 18): #opx, cpx and garnet

			calib_object = self.w_calib[min_idx][SEEL.minerals_cond_selections[min_idx - self.rock_num - self.fluid_num]]
			calib_object_2 = SEEL.px_gt_calib

			if calib_object_2 == 0:

				if calib_object == 0:

					CORR_Factor = self.pat2bell95

				else:

					CORR_Factor = 1.0

			elif calib_object_2 == 1:

				if calib_object == 1:

					CORR_Factor = self.bell952pat

				else:

					CORR_Factor = 1.0
			
			else:
			
				CORR_Factor = 1.0

		elif (min_idx == 12) or (min_idx == 14): #Plagioclase and k-feldspar
			
			calib_object = self.w_calib[min_idx][SEEL.minerals_cond_selections[min_idx - self.rock_num - self.fluid_num]]
			calib_object_2 = SEEL.feldspar_calib
				
			if calib_object_2 == 0:

				if calib_object == 0:

					CORR_Factor = self.john2mosen

				else:

					CORR_Factor = 1.0

			elif calib_object_2 == 1:

				if calib_object_2 == 1:

					CORR_Factor = self.mosen2john

				else:

					CORR_Factor = 1.0
					
			else:
			
				CORR_Factor == 1.0
					
		else:
		
			CORR_Factor = 1.0
		
		return CORR_Factor
		
		
	def phase_mixing_function(self, method = None, melt_method = None, indexing_method = None, sol_idx = None):

		self.bulk_cond = np.zeros(len(self.T)) #setting up an empty bulk conductivity array for all methods
		self.dens_melt_fluid = np.zeros(len(self.T))

		if indexing_method == 'array':
			idx_node = None
		elif indexing_method == 'index':
			idx_node = sol_idx
			
		if method == 0:

			#Calculating phase exponent of the abundant mineral to make connectedness equal to unity.
			#From Glover (2010, Geophysics), analytic solution.

			#creating search limits for different indexing methods.
			if indexing_method == 'array':
				start_idx = 0
				end_idx = len(self.T)
			elif indexing_method == 'index':
				start_idx = sol_idx
				end_idx = sol_idx + 1
				
			for i in range(start_idx,end_idx):
			
				if SEEL.solid_phase_method == 1:
					phase_list = [self.granite_frac[i],self.granulite_frac[i],self.sandstone_frac[i],
					self.gneiss_frac[i], self.amphibolite_frac[i], self.basalt_frac[i], self.mud_frac[i],
					 self.gabbro_frac[i], self.other_rock_frac[i]]
					m_list = [SEEL.granite_m[i],SEEL.granulite_m[i],SEEL.sandstone_m[i],
					SEEL.gneiss_m[i], SEEL.amphibolite_m[i], SEEL.basalt_m[i], self.mud_m[i],
					 self.gabbro_m[i], SEEL.other_rock_m[i]]
				elif SEEL.solid_phase_method == 2:
					phase_list = [self.quartz_frac[i], self.plag_frac[i], self.amp_frac[i], self.kfelds_frac[i],
					self.opx_frac[i], self.cpx_frac[0], self.mica_frac[i], self.garnet_frac[i],
					self.sulphide_frac[i], self.graphite_frac[i], self.ol_frac[i], self.mixture_frac[i], self.other_frac[i]]
					m_list = [SEEL.quartz_m[i], SEEL.plag_m[i], SEEL.amp_m[i], SEEL.kfelds_m[i],
					SEEL.opx_m[i], SEEL.cpx_m[i], SEEL.mica_m[i], SEEL.garnet_m[i],
					SEEL.sulphide_m[i], SEEL.graphite_m[i], SEEL.ol_m[i], SEEL.mixture_m[i], SEEL.other_m[i]]
					
				frac_abundant = max(phase_list) #fraction of abundant mineral
				idx_max_ph = phase_list.index(frac_abundant) #index of the abundant mineral
				del phase_list[idx_max_ph] #deleting the abundant mineral form local list
				del m_list[idx_max_ph] #deleting the exponent of the abundant mineral from local list
				connectedness = np.asarray(phase_list)**np.asarray(m_list) #calculating the connectedness of the rest

				if sum(phase_list) != 0.0:
					m_abundant = np.log(1.0 - np.sum(connectedness)) / np.log(frac_abundant) #analytic solution to the problem
				else:
					m_abundant = 1

				if SEEL.solid_phase_method == 1:
					
					if idx_max_ph == 0:
						SEEL.granite_m[idx_node] = m_abundant
					elif idx_max_ph == 1:
						SEEL.granulite_m[idx_node] = m_abundant
					elif idx_max_ph == 2:
						SEEL.sandstone_m[idx_node] = m_abundant
					elif idx_max_ph == 3:
						SEEL.gneiss_m[idx_node] = m_abundant
					elif idx_max_ph == 4:
						SEEL.amphibolite_m[idx_node] = m_abundant
					elif idx_max_ph == 5:
						SEEL.basalt_m[idx_node] = m_abundant
					elif idx_max_ph == 6:
						SEEL.mud_m[idx_node] = m_abundant
					elif idx_max_ph == 7:
						SEEL.gabbro_m[idx_node] = m_abundant
					elif idx_max_ph == 8:
						SEEL.other_rock_m[idx_node] = m_abundant
					
					self.bulk_cond[idx_node] = (self.granite_cond[idx_node]*(self.granite_frac[idx_node]**SEEL.granite_m[idx_node])) +\
					(self.granulite_cond[idx_node]*(self.granulite_frac[idx_node]**SEEL.granulite_m[idx_node])) +\
					(self.sandstone_cond[idx_node]*(self.sandstone_frac[idx_node]**SEEL.sandstone_m[idx_node])) +\
					(self.gneiss_cond[idx_node]*(self.gneiss_frac[idx_node]**SEEL.gneiss_m[idx_node])) +\
					(self.amphibolite_cond[idx_node]*(self.amphibolite_frac[idx_node]**SEEL.amphibolite_m[idx_node])) +\
					(self.basalt_cond[idx_node]*(self.basalt_frac[idx_node]**SEEL.basalt_m[idx_node])) +\
					(self.mud_cond[idx_node]*(self.mud_frac[idx_node]**SEEL.mud_m[idx_node])) +\
					(self.gabbro_cond[idx_node]*(self.gabbro_frac[idx_node]**SEEL.gabbro_m[idx_node])) +\
					(self.other_rock_cond[idx_node]*(self.other_rock_frac[idx_node]**SEEL.other_rock_m[idx_node]))
				
				elif SEEL.solid_phase_method == 2:
					if idx_max_ph == 0:
						SEEL.quartz_m[idx_node] = m_abundant
					elif idx_max_ph == 1:
						SEEL.plag_m[idx_node] = m_abundant
					elif idx_max_ph == 2:
						SEEL.amp_m[idx_node] = m_abundant
					elif idx_max_ph == 3:
						SEEL.kfelds_m[idx_node] = m_abundant
					elif idx_max_ph == 4:
						SEEL.opx_m[idx_node] = m_abundant
					elif idx_max_ph == 5:
						SEEL.cpx_m[idx_node] = m_abundant
					elif idx_max_ph == 6:
						SEEL.mica_m[idx_node] = m_abundant
					elif idx_max_ph == 7:
						SEEL.garnet_m[idx_node] = m_abundant
					elif idx_max_ph == 8:
						SEEL.sulphide_m[idx_node] = m_abundant
					elif idx_max_ph == 9:
						SEEL.graphite_m[idx_node] = m_abundant
					elif idx_max_ph == 10:
						SEEL.ol_m[idx_node] = m_abundant
					elif idx_max_ph == 11:
						SEEL.mixture_m[idx_node] = m_abundant
					elif idx_max_ph == 12:
						SEEL.other_m[idx_node] = m_abundant
						
					self.bulk_cond[idx_node] = (self.quartz_cond[idx_node]*(self.quartz_frac[idx_node]**SEEL.quartz_m[idx_node])) +\
					(self.plag_cond[idx_node]*(self.plag_frac[idx_node]**SEEL.plag_m[idx_node])) +\
					(self.amp_cond[idx_node]*(self.amp_frac[idx_node]**SEEL.amp_m[idx_node])) +\
					(self.kfelds_cond[idx_node]*(self.kfelds_frac[idx_node]**SEEL.kfelds_m[idx_node])) +\
					(self.opx_cond[idx_node]*(self.opx_frac[idx_node]**SEEL.opx_m[idx_node])) +\
					(self.cpx_cond[idx_node]*(self.cpx_frac[idx_node]**SEEL.cpx_m[idx_node])) +\
					(self.mica_cond[idx_node]*(self.mica_frac[idx_node]**SEEL.mica_m[idx_node])) +\
					(self.garnet_cond[idx_node]*(self.garnet_frac[idx_node]**SEEL.garnet_m[idx_node])) +\
					(self.sulphide_cond[idx_node]*(self.sulphide_frac[idx_node]**SEEL.sulphide_m[idx_node])) +\
					(self.graphite_cond[idx_node]*(self.graphite_frac[idx_node]**SEEL.graphite_m[idx_node])) +\
					(self.ol_cond[idx_node]*(self.ol_frac[idx_node]**SEEL.ol_m[idx_node])) +\
					(self.mixture_cond[idx_node]*(self.mixture_frac[idx_node]**SEEL.mixture_m[idx_node])) +\
					(self.other_cond[idx_node]*(self.other_frac[idx_node]**SEEL.other_m[idx_node]))
					
		elif method == 1:
			
			if indexing_method == 'array':
				
				self.bulk_cond = np.zeros(len(self.ol_cond))
				start_idx = 0
				end_idx = len(self.T)
			elif indexing_method == 'index':
				start_idx = sol_idx
				end_idx = sol_idx + 1
				
			for i in range(start_idx,end_idx):
				
				if SEEL.solid_phase_method == 1:
					list_i = [self.granite_cond[i], self.granulite_cond[i], self.sandstone_cond[i],
					self.gneiss_cond[i],self.amphibolite_cond[i], self.basalt_cond[i], self.mud_cond[i],
					  self.gabbro_cond, self.other_rock_cond[i]]
				elif SEEL.solid_phase_method == 2:
					list_i = [self.quartz_cond[i], self.plag_cond[i], self.amp_cond[i],
					self.kfelds_cond[i],self.opx_cond[i],self.cpx_cond[i],self.mica_cond[i],
					self.garnet_cond[i],self.sulphide_cond[i],self.graphite_cond[i],self.ol_cond[i], self.mixture_cond[i], self.other_cond[i]]				
					
				while True:
				
					#while loop for deleting the zero arrays that could be encountered due to non-existence of the mineral.
					
					min_local = np.amin(np.asarray(list_i))
				
					if (min_local != 0.0):
						
						break
					
					else:
					
						list_i = np.delete(list_i, np.argwhere(list_i == 0))
						
				if SEEL.solid_phase_method == 1:
				
					self.bulk_cond[i] = (((self.granite_frac[i] / (self.granite_cond[i] + (2*min_local))) +\
					(self.granulite_frac[i] / (self.granulite_cond[i] + (2*min_local))) +\
					(self.sandstone_frac[i] / (self.sandstone_cond[i] + (2*min_local))) +\
					(self.gneiss_frac[i] / (self.gneiss_cond[i] + (2*min_local))) +\
					(self.amphibolite_frac[i] / (self.amphibolite_cond[i] + (2*min_local))) +\
					(self.basalt_frac[i] / (self.basalt_cond[i] + (2*min_local))) +\
					(self.mud_frac[i] / (self.mud_cond[i] + (2*min_local))) +\
					(self.gabbro_frac[i] / (self.gabbro_cond[i] + (2*min_local))) +\
					(self.other_rock_frac[i] / (self.other_rock_cond[i] + (2*min_local))))**(-1.0)) -\
					2.0*min_local
						
				elif SEEL.solid_phase_method == 2:
				
					self.bulk_cond[i] = (((self.quartz_frac[i] / (self.quartz_cond[i] + (2*min_local))) +\
					(self.plag_frac[i] / (self.plag_cond[i] + (2*min_local))) +\
					(self.amp_frac[i] / (self.amp_cond[i] + (2*min_local))) +\
					(self.kfelds_frac[i] / (self.kfelds_cond[i] + (2*min_local))) +\
					(self.opx_frac[i] / (self.opx_cond[i] + (2*min_local))) +\
					(self.cpx_frac[i] / (self.cpx_cond[i] + (2*min_local))) +\
					(self.mica_frac[i] / (self.mica_cond[i] + (2*min_local))) +\
					(self.garnet_frac[i] / (self.garnet_cond[i] + (2*min_local))) +\
					(self.sulphide_frac[i] / (self.sulphide_cond[i] + (2*min_local))) +\
					(self.graphite_frac[i] / (self.graphite_cond[i] + (2*min_local))) +\
					(self.ol_frac[i] / (self.ol_cond[i] + (2*min_local))) +\
					(self.mixture_frac[i] / (self.mixture_cond[i] + (2*min_local))) +\
					(self.other_frac[i] / (self.other_cond[i] + (2*min_local)))
					)**(-1.0)) -\
					2.0*min_local
					
		elif method == 2:
		
			if indexing_method == 'array':
				
				self.bulk_cond = np.zeros(len(self.ol_cond))
				start_idx = 0
				end_idx = len(self.T)
			elif indexing_method == 'index':
				start_idx = sol_idx
				end_idx = sol_idx + 1
				
			for i in range(start_idx,end_idx):
				
				if SEEL.solid_phase_method == 1:
					list_i = [self.granite_cond[i], self.granulite_cond[i], self.sandstone_cond[i],
					self.gneiss_cond[i],self.amphibolite_cond[i], self.basalt_cond[i], self.mud_cond[i],
					  self.gabbro_cond, self.other_rock_cond[i]]
				elif SEEL.solid_phase_method == 2:
					list_i = [self.quartz_cond[i], self.plag_cond[i], self.amp_cond[i],
					self.kfelds_cond[i],self.opx_cond[i],self.cpx_cond[i],self.mica_cond[i],
					self.garnet_cond[i],self.sulphide_cond[i],
					self.graphite_cond[i],self.ol_cond[i], self.mixture_cond[i], self.other_cond[i]]				
					
				while True:
				
					#while loop for deleting the zero arrays that could be encountered due to non-existence of the mineral.
					
					max_local = np.amax(np.asarray(list_i))
				
					if (max_local != 0.0):
						
						break
					
					else:
					
						list_i = np.delete(list_i, np.argwhere(list_i == 0))
						
				if SEEL.solid_phase_method == 1:
				
					self.bulk_cond[i] = (((self.granite_frac[i] / (self.granite_cond[i] + (2*max_local))) +\
					(self.granulite_frac[i] / (self.granulite_cond[i] + (2*max_local))) +\
					(self.sandstone_frac[i] / (self.sandstone_cond[i] + (2*max_local))) +\
					(self.gneiss_frac[i] / (self.gneiss_cond[i] + (2*max_local))) +\
					(self.amphibolite_frac[i] / (self.amphibolite_cond[i] + (2*max_local))) +\
					(self.basalt_frac[i] / (self.basalt_cond[i] + (2*max_local))) +\
					(self.mud_frac[i] / (self.mud_cond[i] + (2*max_local))) +\
					(self.gabbro_frac[i] / (self.gabbro_cond[i] + (2*max_local))) +\
					(self.other_rock_frac[i] / (self.other_rock_cond[i] + (2*max_local))))**(-1.0)) -\
					2.0*max_local
						
				elif SEEL.solid_phase_method == 2:
				
					self.bulk_cond[i] = (((self.quartz_frac[i] / (self.quartz_cond[i] + (2*max_local))) +\
					(self.plag_frac[i] / (self.plag_cond[i] + (2*max_local))) +\
					(self.amp_frac[i] / (self.amp_cond[i] + (2*max_local))) +\
					(self.kfelds_frac[i] / (self.kfelds_cond[i] + (2*max_local))) +\
					(self.opx_frac[i] / (self.opx_cond[i] + (2*max_local))) +\
					(self.cpx_frac[i] / (self.cpx_cond[i] + (2*max_local))) +\
					(self.mica_frac[i] / (self.mica_cond[i] + (2*max_local))) +\
					(self.garnet_frac[i] / (self.garnet_cond[i] + (2*max_local))) +\
					(self.sulphide_frac[i] / (self.sulphide_cond[i] + (2*max_local))) +\
					(self.graphite_frac[i] / (self.graphite_cond[i] + (2*max_local))) +\
					(self.ol_frac[i] / (self.ol_cond[i] + (2*max_local))) +\
					(self.mixture_frac[i] / (self.mixture_cond[i] + (2*max_local))) +\
					(self.other_frac[i] / (self.other_cond[i] + (2*max_local)))					
					)**(-1.0)) -\
					2.0*max_local
					
		elif method == 3:
		
			#Parallel model for maximum, minimum bounds and neutral w/o errors
			
			if SEEL.solid_phase_method == 1:
				self.bulk_cond[idx_node] = (self.granite_frac[idx_node]*self.granite_cond[idx_node]) +\
				(self.granulite_frac[idx_node]*self.granulite_cond[idx_node]) +\
				(self.sandstone_frac[idx_node]*self.sandstone_cond[idx_node]) +\
				(self.gneiss_frac[idx_node]*self.gneiss_cond[idx_node]) +\
				(self.amphibolite_frac[idx_node]*self.amphibolite_cond[idx_node]) +\
				(self.basalt_frac[idx_node]*self.basalt_cond[idx_node]) +\
				(self.mud_frac[idx_node]*self.mud_cond[idx_node]) +\
				(self.gabbro_frac[idx_node]*self.gabbro_cond[idx_node]) +\
				(self.other_rock_frac[idx_node]*self.other_rock_cond[idx_node])
				
			elif SEEL.solid_phase_method == 2:
			
				self.bulk_cond[idx_node] = (self.quartz_frac[idx_node]*self.quartz_cond[idx_node]) +\
				(self.plag_frac[idx_node]*self.plag_cond[idx_node]) +\
				(self.amp_frac[idx_node]*self.amp_cond[idx_node]) +\
				(self.kfelds_frac[idx_node]*self.kfelds_cond[idx_node]) +\
				(self.opx_frac[idx_node]*self.opx_cond[idx_node]) +\
				(self.cpx_frac[idx_node]*self.cpx_cond[idx_node]) +\
				(self.mica_frac[idx_node]*self.mica_cond[idx_node]) +\
				(self.garnet_frac[idx_node]*self.garnet_cond[idx_node]) +\
				(self.sulphide_frac[idx_node]*self.sulphide_cond[idx_node]) +\
				(self.graphite_frac[idx_node]*self.graphite_cond[idx_node]) +\
				(self.ol_frac[idx_node]*self.ol_cond[idx_node]) +\
				(self.mixture_frac[idx_node]*self.mixture_cond[idx_node]) +\
				(self.other_frac[idx_node]*self.other_cond[idx_node])
				
				
		elif method == 4:
		
			if indexing_method == 'array':
				self.bulk_cond = np.zeros(len(self.ol_cond))
				start_idx = 0
				end_idx = len(self.T)
			elif indexing_method == 'index':
				start_idx = sol_idx
				end_idx = sol_idx + 1

			#Perpendicular model for maximum, minimum bounds and neutral w/o errors				
			if SEEL.solid_phase_method == 1:
				for i in range(start_idx,end_idx):
					if self.granite_frac[i] == 0.0:
						self.granite_cond[i] = -999
					if self.granulite_frac[i] == 0.0:
						self.granulite_cond[i] = -999
					if self.sandstone_frac[i] == 0.0:
						self.sandstone_cond[i] = -999
					if self.gneiss_frac[i] == 0.0:
						self.gneiss_cond[i] = -999
					if self.amphibolite_frac[i] == 0.0:
						self.amphibolite_cond[i] = -999
					if self.basalt_frac[i] == 0.0:
						self.basalt_cond[i] = -999
					if self.mud_frac[i] == 0.0:
						self.mud_cond[i] = -999
					if self.gabbro_frac[i] == 0.0:
						self.gabbro_cond[i] = -999
					if self.other_rock_frac[i] == 0.0:
						self.other_rock_cond[i] = -999
	
				self.bulk_cond[idx_node] = 1.0 / ((self.granite_frac[idx_node] / self.granite_cond[idx_node]) +\
				(self.granulite_frac[idx_node] / self.granulite_cond[idx_node]) +\
				(self.sandstone_frac[idx_node] / self.sandstone_cond[idx_node]) +\
				(self.gneiss_frac[idx_node] / self.gneiss_cond[idx_node]) +\
				(self.amphibolite_frac[idx_node] / self.amphibolite_cond[idx_node]) +\
				(self.basalt_frac[idx_node] / self.basalt_cond[idx_node]) +\
				(self.mud_frac[idx_node] / self.mud_cond[idx_node]) +\
				(self.gabbro_frac[idx_node] / self.gabbro_cond[idx_node]) +\
				(self.other_rock_frac[idx_node] / self.other_rock_cond[idx_node]))
				
			elif SEEL.solid_phase_method == 2:
			
				for i in range(start_idx,end_idx):
					if self.quartz_frac[i] == 0.0:
						self.quartz_cond[i] = -999
					if self.plag_frac[i] == 0.0:
						self.plag_cond[i] = -999
					if self.amp_frac[i] == 0.0:
						self.amp_cond[i] = -999
					if self.kfelds_frac[i] == 0.0:
						self.kfelds_cond[i] = -999
					if self.opx_frac[i] == 0.0:
						self.opx_cond[i] = -999
					if self.cpx_frac[i] == 0.0:
						self.cpx_cond[i] = -999
					if self.mica_frac[i] == 0.0:
						self.mica_cond[i] = -999
					if self.garnet_frac[i] == 0.0:
						self.garnet_cond[i] = -999
					if self.sulphide_frac[i] == 0.0:
						self.sulphide_cond[i] = -999
					if self.graphite_frac[i] == 0.0:
						self.graphite_cond[i] = -999
					if self.ol_frac[i] == 0.0:
						self.ol_cond[i] = -999
					if self.mixture_frac[i] == 0.0:
						self.mixture_cond[i] = -999
					if self.other_frac[i] == 0.0:
						self.other_cond[i] = -999
	
				self.bulk_cond[idx_node] = 1.0 / ((self.quartz_frac[idx_node] / self.quartz_cond[idx_node]) +\
				(self.plag_frac[idx_node] / self.plag_cond[idx_node]) +\
				(self.amp_frac[idx_node] / self.amp_cond[idx_node]) +\
				(self.kfelds_frac[idx_node] / self.kfelds_cond[idx_node]) +\
				(self.opx_frac[idx_node] / self.opx_cond[idx_node]) +\
				(self.cpx_frac[idx_node] / self.cpx_cond[idx_node]) +\
				(self.mica_frac[idx_node] / self.mica_cond[idx_node]) +\
				(self.garnet_frac[idx_node] / self.garnet_cond[idx_node]) +\
				(self.sulphide_frac[idx_node] / self.sulphide_cond[idx_node]) +\
				(self.graphite_frac[idx_node] / self.graphite_cond[idx_node]) +\
				(self.ol_frac[idx_node] / self.ol_cond[idx_node]) +\
				(self.mixture_frac[idx_node] / self.mixture_cond[idx_node]) +\
				(self.other_frac[idx_node] / self.other_cond[idx_node]))
				
		elif method == 5:
		
			#Random model for maximum, minimum bounds and neutral w/o errors
			
			if SEEL.solid_phase_method == 1:
				
				self.bulk_cond[idx_node] = (self.granite_cond[idx_node]**self.granite_frac[idx_node]) *\
				(self.granulite_cond[idx_node]**self.granulite_frac[idx_node]) *\
				(self.sandstone_cond[idx_node]**self.sandstone_frac[idx_node]) *\
				(self.gneiss_cond[idx_node]**self.gneiss_frac[idx_node]) *\
				(self.amphibolite_cond[idx_node]**self.amphibolite_frac[idx_node]) *\
				(self.basalt_cond[idx_node]**self.basalt_frac[idx_node]) *\
				(self.mud_cond[idx_node]**self.mud_frac[idx_node]) *\
				(self.gabbro_cond[idx_node]**self.gabbro_frac[idx_node]) *\
				(self.other_rock_cond[idx_node]**self.other_rock_frac[idx_node]) 
				
			elif SEEL.solid_phase_method == 2:

				self.bulk_cond[idx_node] = (self.quartz_cond[idx_node]**self.quartz_frac[idx_node]) *\
				(self.plag_cond[idx_node]**self.plag_frac[idx_node]) *\
				(self.amp_cond[idx_node]**self.amp_frac[idx_node]) *\
				(self.kfelds_cond[idx_node]**self.kfelds_frac[idx_node]) *\
				(self.opx_cond[idx_node]**self.opx_frac[idx_node]) *\
				(self.cpx_cond[idx_node]**self.cpx_frac[idx_node]) *\
				(self.mica_cond[idx_node]**self.mica_frac[idx_node]) *\
				(self.garnet_cond[idx_node]**self.garnet_frac[idx_node]) *\
				(self.sulphide_cond[idx_node]**self.sulphide_frac[idx_node]) *\
				(self.graphite_cond[idx_node]**self.graphite_frac[idx_node]) *\
				(self.ol_cond[idx_node]**self.ol_frac[idx_node]) *\
				(self.mixture_cond[idx_node]**self.mixture_frac[idx_node]) *\
				(self.other_cond[idx_node]**self.other_frac[idx_node])
				
		elif method == -1:
			
			#In case the bulk conductivity is determined by a solid phase conductivity entry...
			
			self.bulk_cond = self.bckgr_res

		self.solid_phase_cond = np.array(self.bulk_cond)
			
		#Calculations regarding solid phases and fluid phases mixing take place after this.
		#checking if there's any melt/fluid on the list at all.
		if np.mean(self.melt_fluid_mass_frac) != 0:
			
			if SEEL.fluid_or_melt_method == 0:
				
				dens = iapws.iapws08.SeaWater(T = self.T[idx_node], P = self.p[idx_node], S = 0)
				self.dens_melt_fluid[idx_node] = dens.rho / 1e3
				
			elif SEEL.fluid_or_melt_method == 1:
				
				self.dens_melt_dry = float(self.dens_mat[1][SEEL.melt_cond_selection]) / 1e3 #index 1 is equate to melt
				#Determining xvol, first have to calculate the density of the melt from Sifre et al. (2014)
				
				self.dens_melt_fluid[idx_node] = (((self.h2o_melt[idx_node] * 1e-4) / 1e2) * 1.4) +\
				(((self.co2_melt[idx_node] * 1e-4) / 1e2) * 2.4) + (1 - (((self.h2o_melt[idx_node] * 1e-4) +\
				(self.co2_melt[idx_node] * 1e-4)) / 1e2)) * self.dens_melt_dry #calculating how much volatiles changed its density
				
			if indexing_method == 'array':
				self.melt_fuid_frac = np.zeros(len(self.melt_fluid_mass_frac))
				start_idx = 0
				end_idx = len(self.T)
			elif indexing_method == 'index':
				start_idx = sol_idx
				end_idx = sol_idx + 1

			self.melt_fluid_frac = np.zeros(len(self.melt_fluid_mass_frac))

			for i in range(start_idx,end_idx):
				if self.melt_fluid_mass_frac[i] != 0.0:
					self.melt_fluid_frac[i] = 1.0 / (1 + (((1.0/self.melt_fluid_mass_frac[i]) - 1) * (self.dens_melt_fluid[i] / (self.density_solids[i]))))
	 
			if melt_method == 0:

				#Modified Archie's Law taken from Glover et al. (2000) from eq. 8

				for i in range(start_idx,end_idx):

					if self.melt_fluid_mass_frac[i] != 0.0:

						p = np.log10(1.0 - self.melt_fluid_frac[i]**SEEL.melt_fluid_m[i]) / np.log10(1.0 - self.melt_fluid_frac[i])

						self.bulk_cond[i] = (self.bulk_cond[i] * (1.0 - self.melt_fluid_frac[i])**p) + (self.melt_fluid_cond[i] * (self.melt_fluid_frac[i]**SEEL.melt_fluid_m[i]))
							
			elif melt_method == 1:

				#Tubes model for melt and solid mixture from ten Grotenhuis et al. (2005) eq.5

				self.bulk_cond[idx_node] = ((1.0/3.0) * self.melt_fluid_frac[idx_node] * self.melt_fluid_cond[idx_node]) + ((1.0 - self.melt_fluid_frac[idx_node]) * self.bulk_cond[idx_node])
				
			elif melt_method == 2:

				#Spheres model for melt ans solid mixture got from ten Grotenhuis et al. (2005), eq.3

				self.bulk_cond[idx_node] = self.melt_fluid_cond[idx_node] + ((1.0 - self.melt_fluid_frac[idx_node]) / ((1.0 / (self.bulk_cond[idx_node] - self.melt_fluid_cond[idx_node])) +\
				 	(self.melt_fluid_frac[idx_node] / (3.0 * self.melt_fluid_cond[idx_node]))))
			
			elif melt_method == 3:
			
				#Modified brick-layer model from Schilling et al. (1997)

				ones = (1.0 - self.melt_fluid_frac[idx_node])
				two_thirds = (1.0 - self.melt_fluid_frac[idx_node])**(2.0/3.0)

				self.bulk_cond[idx_node] = self.melt_fluid_cond[idx_node] * (((self.melt_fluid_cond[idx_node] * (two_thirds - 1.0)) - (self.bulk_cond[idx_node] * two_thirds)) /\
				((self.bulk_cond[idx_node] * (ones - two_thirds)) + (self.melt_fluid_cond[idx_node] * (two_thirds - ones - 1.0))))
				
			elif melt_method == 4:
			
				#Hashin-shtrikman upper bound from Glover et al. (2000)
				vol_matrix = 1.0 - self.melt_fluid_frac[idx_node]

				self.bulk_cond[idx_node] = self.melt_fluid_cond[idx_node] * (1 -\
				((3 * vol_matrix * (self.melt_fluid_cond[idx_node] - self.bulk_cond[idx_node])) /\
				(3 * self.melt_fluid_cond[idx_node] - (self.melt_fluid_frac[idx_node] * (self.melt_fluid_cond[idx_node] - self.bulk_cond[idx_node])))))
				
			elif melt_method == 5:
			
				#Hashin-shtrikman lower bound from Glover et al. (2000)
				vol_matrix = 1.0 - self.melt_fluid_frac[idx_node]

				self.bulk_cond[idx_node] = self.bulk_cond[idx_node] * (1 +\
				((3 * self.melt_fluid_frac[idx_node] * (self.melt_fluid_cond[idx_node] - self.bulk_cond[idx_node])) /\
				(3 * self.bulk_cond[idx_node] + (vol_matrix * (self.melt_fluid_cond[idx_node] - self.bulk_cond[idx_node])))))
				
	def calculate_fugacity(self,mode):

		#Function that calculates oxygen fugacity buffers from selection.

		self.A_list = [-999,-27489.0,-999,-24930.0,-30650.0]
		self.B_list = [-999,6.702,-999,9.36,8.92]
		self.C_list = [-999,0.055,-999,0.046,0.054]

		#OXYGEN FUGACITY BUFFER CONSTANTS in the lists above(self.A_list ...)
		#Index 0: FMQ:
		#Index 1: IW: Hirsch (1991)
		#Index 2: QIF:
		#Index 3: NNO: Li et al. (1998)
		#Index 4 MMO: Xu et al. (2000)

		self.A_FMQ_low = -26455.3
		self.A_FMQ_high = -25096.3
		self.B_FMQ_low = 10.344
		self.B_FMQ_high = 8.735
		self.C_FMQ_low = 0.092
		self.C_FMQ_high = 0.11
		self.T_crit = 846.0

		self.A_QIF_low = -29435.7
		self.A_QIF_high = -29520.8
		self.B_QIF_low = 7.391
		self.B_QIF_high = 7.492
		self.C_QIF_low = 0.044
		self.C_QIF_high = 0.05


		if (mode == 0):

			self.fo2 = np.zeros(len(self.T))

			for i in range(0,len(self.T)):

				if self.T[i] < self.T_crit:

					self.fo2[i] = 10**((self.A_FMQ_low / self.T[i]) + self.B_FMQ_low + ((self.C_FMQ_low * ((self.p[i]*1e4) - 1)) / self.T[i]))

				else:

					self.fo2[i] = 10**((self.A_FMQ_high / self.T[i]) + self.B_FMQ_high + ((self.C_FMQ_high * ((self.p[i]*1e4) - 1)) / self.T[i]))


		elif (mode == 2):

			self.fo2 = np.zeros(len(self.T))

			for i in range(0,len(self.T)):

				if self.T[i] < self.T_crit:

					self.fo2[i] = 10**((self.A_QIF_low / self.T[i]) + self.B_QIF_low + ((self.C_QIF_low * ((self.p[i]*1e4) - 1)) / self.T[i]))

				else:

					self.fo2[i] = 10**((self.A_QIF_high / self.T[i]) + self.B_QIF_high + ((self.C_QIF_high * ((self.p[i]*1e4) - 1)) / self.T[i]))

		else:

			self.fo2 = 10**((self.A_list[mode] / self.T) + self.B_list[mode] + ((self.C_list[mode] * ((self.p*1e4) - 1)) / self.T))

		#self.fo2 is in bars multiply by 1e5 for Pa and 1e-4 for GPa

		return self.fo2

	def calculate_density_solid(self):
		
		if SEEL.solid_phase_method == 1:
		
			dens_list = [float(self.dens_mat[2][SEEL.granite_cond_selection])/1e3,
			float(self.dens_mat[3][SEEL.granulite_cond_selection])/1e3,
			float(self.dens_mat[4][SEEL.sandstone_cond_selection])/1e3,
			float(self.dens_mat[5][SEEL.gneiss_cond_selection])/1e3,
			float(self.dens_mat[6][SEEL.amphibolite_cond_selection])/1e3,
			float(self.dens_mat[7][SEEL.basalt_cond_selection])/1e3,
			float(self.dens_mat[8][SEEL.mud_cond_selection])/1e3,
			float(self.dens_mat[9][SEEL.gabbro_cond_selection])/1e3,
			float(self.dens_mat[10][SEEL.other_rock_cond_selection])/1e3]
			
			self.density_solids = np.zeros(len(self.T))
			
			for i in range(0,len(self.T)):
			
				density_indv = 0.0
				
				phase_list = [self.granite_frac[i],self.granulite_frac[i],self.sandstone_frac[i],
						self.gneiss_frac[i], self.amphibolite_frac[i], self.basalt_frac[i], self.mud_frac[i],
						 self.gabbro_frac[i], self.other_rock_frac[i]]
				
				for j in range(0,len(phase_list)):
					density_indv = density_indv + (phase_list[j] * dens_list[j])
					
				self.density_solids[i] = density_indv
				
			
		elif SEEL.solid_phase_method == 2:
		
			dens_list = [float(self.dens_mat[11][SEEL.quartz_cond_selection])/1e3,
			float(self.dens_mat[12][SEEL.plag_cond_selection])/1e3,
			float(self.dens_mat[13][SEEL.amp_cond_selection])/1e3,
			float(self.dens_mat[14][SEEL.kfelds_cond_selection])/1e3,
			float(self.dens_mat[15][SEEL.opx_cond_selection])/1e3,
			float(self.dens_mat[16][SEEL.cpx_cond_selection])/1e3,
			float(self.dens_mat[17][SEEL.mica_cond_selection])/1e3,
			float(self.dens_mat[18][SEEL.garnet_cond_selection])/1e3,
			float(self.dens_mat[19][SEEL.sulphide_cond_selection])/1e3,
			float(self.dens_mat[20][SEEL.graphite_cond_selection])/1e3,
			float(self.dens_mat[21][SEEL.ol_cond_selection])/1e3,
			float(self.dens_mat[22][SEEL.mixture_cond_selection])/1e3,
			float(self.dens_mat[23][SEEL.other_cond_selection])/1e3] 
						
			self.density_solids = np.zeros(len(self.T))
			
			for i in range(0,len(self.T)):
			
				density_indv = 0.0
				
				phase_list = [self.quartz_frac[i], self.plag_frac[i], self.amp_frac[i], self.kfelds_frac[i],
					self.opx_frac[i], self.cpx_frac[i], self.mica_frac[i], self.garnet_frac[i],
					self.sulphide_frac[i], self.graphite_frac[i], self.ol_frac[i], self.mixture_frac[i], self.other_frac[i]]
				
				for j in range(0,len(phase_list)):
					density_indv = density_indv + (phase_list[j] * dens_list[j])
					
				self.density_solids[i] = density_indv
								
	def calculate_conductivity_single(self, method = None):
	
		if SEEL.fluid_or_melt_method == 0:
			self.melt_fluid_cond = self.calculate_fluids_conductivity(method= method, sol_idx = 0)
		elif SEEL.fluid_or_melt_method == 1:
			self.melt_fluid_cond = self.calculate_melt_conductivity(method = method, sol_idx = 0)
	
		if SEEL.solid_phase_method == 0:

			self.phase_mixing_function(method == -1, melt_method = SEEL.phs_melt_mix_method, indexing_method= method, sol_idx = 0)
			
		elif SEEL.solid_phase_method == 1:
		
			if self.granite_frac[0] != 0:
				self.granite_cond = self.calculate_rock_conductivity(method = method, rock_idx= 2, sol_idx = 0)
			else:
				self.granite_cond = np.array([0])
				
			if self.granulite_frac[0] != 0:
				self.granulite_cond = self.calculate_rock_conductivity(method = method, rock_idx= 3, sol_idx = 0)
			else:
				self.granulite_cond = np.array([0])
				
			if self.sandstone_frac[0] != 0:
				self.sandstone_cond = self.calculate_rock_conductivity(method = method, rock_idx= 4, sol_idx = 0)
			else:
				self.sandstone_cond = np.array([0])
				
			if self.gneiss_frac[0] != 0:
				self.gneiss_cond = self.calculate_rock_conductivity(method = method, rock_idx= 5, sol_idx = 0)
			else:
				self.gneiss_cond = np.array([0])
				
			if self.amphibolite_frac[0] != 0:
				self.amphibolite_cond = self.calculate_rock_conductivity(method = method, rock_idx= 6, sol_idx = 0)
			else:
				self.amphibolite_cond = np.array([0])

			if self.basalt_frac[0] != 0:
				self.basalt_cond = self.calculate_rock_conductivity(method = method, rock_idx= 7, sol_idx = 0)
			else:
				self.basalt_cond = np.array([0])

			if self.mud_frac[0] != 0:
				self.mud_cond = self.calculate_rock_conductivity(method = method, rock_idx= 8, sol_idx = 0)
			else:
				self.mud_cond = np.array([0])

			if self.gabbro_frac[0] != 0:
				self.gabbro_cond = self.calculate_rock_conductivity(method = method, rock_idx= 9, sol_idx = 0)
			else:
				self.gabbro_cond = np.array([0])
				
			if self.other_rock_frac[0] != 0:
				self.other_rock_cond = self.calculate_rock_conductivity(method = method, rock_idx= 10, sol_idx = 0)
			else:
				self.other_rock_cond = np.array([0])
				
		
			self.phase_mixing_function(method = SEEL.phs_mix_method, melt_method = SEEL.phs_melt_mix_method, indexing_method= method, sol_idx = 0)
			
		elif SEEL.solid_phase_method == 2:
		
			if self.quartz_frac[0] != 0:
				self.quartz_cond = self.calculate_mineral_conductivity(method = method, min_idx= 11, sol_idx = 0)
			else:
				self.quartz_cond = np.array([0])
				
			if self.plag_frac[0] != 0:
				self.plag_cond = self.calculate_mineral_conductivity(method = method, min_idx= 12, sol_idx = 0)
			else:
				self.plag_cond = np.array([0])
				
			if self.amp_frac[0] != 0:
				self.amp_cond = self.calculate_mineral_conductivity(method = method, min_idx= 13, sol_idx = 0)
			else:
				self.amp_cond = np.array([0])
				
			if self.kfelds_frac[0] != 0:
				self.kfelds_cond = self.calculate_mineral_conductivity(method = method, min_idx= 14, sol_idx = 0)
			else:
				self.kfelds_cond = np.array([0])
				
			if self.opx_frac[0] != 0:
				self.opx_cond = self.calculate_mineral_conductivity(method = method, min_idx= 15, sol_idx = 0)
			else:
				self.opx_cond = np.array([0])
				
			if self.cpx_frac[0] != 0:
				self.cpx_cond = self.calculate_mineral_conductivity(method = method, min_idx= 16, sol_idx = 0)
			else:
				self.cpx_cond = np.array([0])
				
			if self.mica_frac[0] != 0:
				self.mica_cond = self.calculate_mineral_conductivity(method = method, min_idx= 17, sol_idx = 0)
			else:
				self.mica_cond = np.array([0])
				
			if self.garnet_frac[0] != 0:
				self.garnet_cond = self.calculate_mineral_conductivity(method = method, min_idx= 18, sol_idx = 0)
			else:
				self.garnet_cond = np.array([0])

			if self.sulphide_frac[0] != 0:
				self.sulphide_cond = self.calculate_mineral_conductivity(method = method, min_idx= 19, sol_idx = 0)
			else:
				self.sulphide_cond = np.array([0])

			if self.graphite_frac[0] != 0:
				self.graphite_cond = self.calculate_mineral_conductivity(method = method, min_idx= 20, sol_idx = 0)
			else:
				self.graphite_cond = np.array([0])

			if self.ol_frac[0] != 0:
				self.ol_cond = self.calculate_mineral_conductivity(method = method, min_idx= 21, sol_idx = 0)
			else:
				self.ol_cond = np.array([0])
				
			if self.mixture_frac[0] != 0:
				self.mixture_cond = self.calculate_mineral_conductivity(method = method, min_idx= 22, sol_idx = 0)
			else:
				self.mixture_cond = np.array([0])
	
			if self.other_frac[0] != 0:
				self.other_cond = self.calculate_mineral_conductivity(method = method, min_idx= 23, sol_idx = 0)
			else:
				self.other_cond = np.array([0])
	
				
			self.phase_mixing_function(method = SEEL.phs_mix_method, melt_method = SEEL.phs_melt_mix_method, indexing_method= method, sol_idx = 0)
		
		self.cond_calculated = True
	
	def plot_composition(self, method = None):

		if method == 'draw':
			
			self.ax0 = plt.subplot2grid((16,16),(0,0), rowspan = 4,colspan = 3, fig = self.fig)
			self.ax1 = plt.subplot2grid((16,16),(0,6), rowspan = 4,colspan = 3, fig = self.fig)
			
		elif method == 'save':
		
			self.figure_comp_save = plt.figure(figsize = (2,7))
			self.ax0 = plt.subplot(111)
			
		self.label_general_rocks = ['Granite', 'Granulite', 'Sandstone', 'Gneiss', 'Amphibolite', 'Basalt', 'Mudstone/Shale', 'Gabbro', 'Other Rock']
		self.color_general_rocks = ['#e016c2',"#52081b","#f0cf6e","#cbe0c3","#41453f", "#32a852" ,"#706041", "#43205c", "#ba6e2b"]
		labels = []
		label_colors = []
		
		self.label_general_mins = ['Quartz', 'Plagioclase', 'Amphibole', 'K-Feldspar', 'Orthopyroxene', 'Clinopyroxene', 'Mica', 
				 'Garnet', 'Sulphide', 'Graphite', 'Olivine', 'Mixtures', 'Other']
		self.color_general_mins = ["#f7f7d7","#fad9a0", "#bfbab2", "#fa5f93", "#3747b0", "dbc14e", "#36cf45", "#ad0f1f", "#8810a3"
		, "#2b292b", "#0b820f", "#eb344c","#32a852"]
				
		if SEEL.solid_phase_method == 0:
			self.solid_phase_array = np.array([100])
			labels = ['Rock\n Assemblage']
			label_colors = ['#70653f']
		elif SEEL.solid_phase_method == 1:
			
			self.solid_phase_array = []
			solid_phase_array = [self.granite_frac, self.granulite_frac,self.sandstone_frac,
			self.gneiss_frac,self.amphibolite_frac,self.basalt_frac,self.mud_frac,self.gabbro_frac,self.other_rock_frac]
			
			for i in range(0,len(solid_phase_array)):
				if solid_phase_array[i][0] != 0.0:
					self.solid_phase_array.append(solid_phase_array[i][0]*1e2)
					labels.append(self.label_general_rocks[i])
					label_colors.append(self.color_general_rocks[i])
					
		elif SEEL.solid_phase_method == 2:
		
			self.solid_phase_array = []
			solid_phase_array = [self.quartz_frac, self.plag_frac, self.kfelds_frac, self.amp_frac, self.opx_frac, self.cpx_frac,
			self.mica_frac,self.garnet_frac,self.sulphide_frac,self.graphite_frac,self.ol_frac,
			self.mixture_frac, self.other_frac]
			
			for i in range(0,len(solid_phase_array)):
				if solid_phase_array[i][0] != 0.0:
					
					self.solid_phase_array.append(solid_phase_array[i][0]*1e2)
					labels.append(self.label_general_mins[i])
					label_colors.append(self.color_general_mins[i])
					
					
		solid = (1 - self.melt_fluid_mass_frac[0]) * 1e2
		liquid = self.melt_fluid_mass_frac[0] * 1e2
		
		sol_liq_array = []
		labels_fs = []
		color_fs = []
		
		if solid != 0:
			sol_liq_array.append(solid)
			labels_fs.append('Solid')
			color_fs.append('#70653f')
		
		if liquid != 0:
		
			sol_liq_array.append(liquid)
			
			if SEEL.fluid_or_melt_method == 1:
				label_f = 'Melt'
				color_f = '#912c10'
			else:
				label_f = 'Fluid'
				color_f = '#24abad'
		
			labels_fs.append(label_f)
			color_fs.append(color_f)
		
		self.ax0.pie(self.solid_phase_array, labels = labels, colors = label_colors,radius = 2,autopct='%1.1f%%')
		self.ax1.pie(sol_liq_array, labels = labels_fs, colors = color_fs,radius = 2, autopct='%1.1f%%')
		
		if method == 'draw':
		
			self.canvas.draw()

	def plot_conductivity(self, method = None):

		if method == 'draw':
			
			self.ax2 = plt.subplot2grid((16,16),(10,0), rowspan = 6,colspan = 16, fig = self.fig)
			self.ax2.grid(None)
			self.ax2.axis('off')
			
		elif method == 'save':
		
			self.figure_comp_save = plt.figure(figsize = (2,7))
			fontsize_labels = 10
			self.ax2 = plt.subplot(111)

		if (self.melt_fluid_cond[0] <= 1e-3):
			res_melt = '% .5E' % (1.0/self.melt_fluid_cond[0])
		else:
			res_melt = (1.0/self.melt_fluid_cond[0])

		if np.mean(self.melt_fluid_mass_frac != 0.0):
			self.ax2.text(0,4,'Melt/Fluid Conductivity:' + str('% .5E' % self.melt_fluid_cond[0]) + ' S/m  or ' + str(res_melt) + r' $\Omega$m', fontsize = 13, fontstyle = 'normal')
		
		if (self.solid_phase_cond[0] <= 1e-3):
			res_solid = '% .5E' % (1.0/self.solid_phase_cond[0])
		else:
			res_solid = (1.0/self.solid_phase_cond[0])
		
		self.ax2.text(0,2,'Bulk Solid Phases Conductivity:' + str('% .5E' % self.solid_phase_cond[0]) + ' S/m  or ' + str(res_solid) + r' $\Omega$m', fontsize = 13, fontstyle = 'normal')
		
		if (self.bulk_cond[0] <= 1e-3):
			res_bulk = '% .5E' % (1.0/self.bulk_cond[0])
		else:
			res_bulk = (1.0/self.bulk_cond[0])
		self.ax2.text(0,0,'Bulk Electrical Conductivity:' + str('% .5E' % self.bulk_cond[0]) + ' S/m  or ' + str(res_bulk) + r' $\Omega$m', fontsize = 13, fontstyle = 'normal')
		
		self.ax2.set_ylim(0,6)
		if method == 'draw':

			self.canvas.draw()

	def info_main(self):
		QMessageBox.about(self, "INFO GENERAL", "TBW.")

	def plot_composition_button(self):
	
		bool_comp = self.check_composition()

		if bool_comp == True:

			self.plot_composition(method = 'draw')
			self.act_comp_btn.setStyleSheet("QPushButton {min-width: 10em; font: bold; font-size: 9pt;background-color: #679c5f}")
			self.composition_set = True
			
			
	def calculate_conductivity_button(self):
	
		if self.composition_set == True:
			
			self.calculate_density_solid()
			self.calculate_conductivity_single(method = 'index')
			self.plot_conductivity(method = 'draw')
			
		else:
		
			QMessageBox.about(self, "Set composition again", "You have changed the composition. Set the composition again by clicking the Plot Composition button.")
			
	def conductivity_popup(self):

		if self.cond_pop is None:
			self.cond_pop = COND_POP()
			self.cond_pop.setGeometry(QtCore.QRect(1000, 700, 100, 100))
		self.cond_pop.show()

	def phase_mixing_popup(self):

		if self.phs_mix_popup is None:
			self.phs_mix_popup = PHS_MIX_POP()
			self.phs_mix_popup.setGeometry(QtCore.QRect(100, 100, 1000, 200))
		self.phs_mix_popup.show()
		
	def phase_intercon_popup(self):
	
		if self.phs_intercon_popup is None:
			self.phs_intercon_popup = PHS_INTER_POP()
			self.phs_intercon_popup.setGeometry(QtCore.QRect(100, 100, 300, 200))
		self.phs_intercon_popup.show()

	def water_content_popup(self):

		if self.water_phase_popup is None:
			self.water_phase_popup = WATER_PHS_POP()
			self.water_phase_popup.setGeometry(QtCore.QRect(100, 100, 300, 200))
		self.water_phase_popup.show()
		
	def optional_param_popup(self):
	
		if self.param_phase_popup is None:
			self.param_phase_popup = OPTIONAL_PARAM_POP()
			self.param_phase_popup.setGeometry(QtCore.QRect(100, 100, 300, 200))
		self.param_phase_popup.show()

	def write_parameter_file(self):

		self.write_file_save_name = QFileDialog.getSaveFileName(self, 'Save File')

		if self.write_file_save_name[0] != '':

			lines = ['Parameter,Value,Objects,Type,Description,Unit\n']

			for i in range(1,len(self.init_params)):

				if self.init_params[i][2] == 'SEEL':
					val = getattr(SEEL,self.init_params[i][0])
				elif self.init_params[i][2] == 'self':
					val = getattr(self,self.init_params[i][0])
				try:
					if ('frac' in self.init_params[i][0]) == True:
						lines.append(','.join((self.init_params[i][0],str(val[0] * 1e2),self.init_params[i][2],self.init_params[i][3],self.init_params[i][4], self.init_params[i][5] + '\n')))
					else:
						lines.append(','.join((self.init_params[i][0],str(val[0]),self.init_params[i][2],self.init_params[i][3],self.init_params[i][4], self.init_params[i][5] + '\n')))
				except TypeError:
					lines.append(','.join((self.init_params[i][0],str(int(val)),self.init_params[i][2],self.init_params[i][3],self.init_params[i][4], self.init_params[i][5] + '\n')))

			filesave_composition = open(self.write_file_save_name[0] ,'w')
			filesave_composition.writelines(lines)
			filesave_composition.close()

			QMessageBox.about(self, 'Hey sup!', "Files are saved at the chosen location ")
			
	def read_parameter_file_batch(self):
		
		self.param_input_file = QFileDialog.getOpenFileName(self, 'Open File')
		
		self.param_data = self.read_csv(self.param_input_file, delim = ',')
		
		for i in range(0,len(self.param_data[0])):
			
			if ('selection' in self.param_data[0][i] is True) or ('method' in self.param_data[0][i] is True):
				try:
					setattr(SEEL, self.param_data[0][i], int(self.param_data[1][i]))
				except AttributeError:
					setattr(self, self.param_data[0][i], int(self.param_data[1][i]))
			else:
				try:
					setattr(self, self.param_data[0][i], float(self.param_data[1][i]) * np.ones(1))
					
				except AttributeError:
					setattr(SEEL, self.param_data[0][i], float(self.param_data[1][i]) * np.ones(1))
					
		self.fill_lineEdit_values()
			
	def write_parameter_file_batch(self):
	
		self.write_file_save_name = QFileDialog.getSaveFileName(self, 'Save File')
		init_params_numpy = []
		
		
		if self.write_file_save_name[0] != '':
			vals = []
			header_vals = []
			
			for i in range(1,len(self.init_params)):
				header_vals.append(self.init_params[i][0])
				if self.init_params[i][2] == 'SEEL':
					val = getattr(SEEL,self.init_params[i][0])
				elif self.init_params[i][2] == 'self':
					val = getattr(self,self.init_params[i][0])
					
				try:
					if ('frac' in self.init_params[i][0]) == True:
						vals.append(str(val[0])*1e2)
					else:
						vals.append(str(val[0]))
				except TypeError:
					vals.append(str(int(val)))
			
			header = ','.join(header_vals) + '\n'
			lines = [header]
			lines.append(','.join(vals) + '\n')
					
			
			filesave_composition = open(self.write_file_save_name[0] ,'w')
			filesave_composition.writelines(lines)
			filesave_composition.close()

			QMessageBox.about(self, 'Hey sup!', "Files are saved at the chosen location ")
			
	def cp_val_to_clipboard(self,param):
		
		if self.cond_calculated == True:
			if self.clipping == True:
				if param == 'solid':
					pyperclip.copy(str(self.solid_phase_cond[0]))
				elif param == 'melt_fluid':
					if np.mean(self.melt_fluid_mass_frac) != 0:
						pyperclip.copy(str(self.melt_fluid_cond[0]))
					else:
						QMessageBox.about(self, 'Warning!', "There is not melt/fluid entered in the composition...")
				elif param == 'bulk':
					pyperclip.copy(str(self.bulk_cond[0]))
			else:
				QMessageBox.about(self, 'Warning!', "To use this functionality, you have to install the 'pyperclip' library first!")
		else:
			QMessageBox.about(self, 'Warning!', "You have to calculate the conductivities first!")

class FLUID_MELT_POP(QWidget):

	def __init__(self):

		QWidget.__init__(self)

		fluid_melt_layout = QVBoxLayout(self)

		fluid_melt_label = QLabel(self)
		fluid_melt_label.setText('Select the fluid phase')
		fluid_melt_label.setStyleSheet("QLabel {font:bold};fontsize: 10pt;color: red")


		fluid_melt_btg = QButtonGroup(self)

		self.btn_fom_1 = QRadioButton("Fluid")
		self.btn_fom_1.toggled.connect(lambda:self.btnstate_fluidormelt(self.btn_fom_1))
		self.btn_fom_2 = QRadioButton("Melt")
		self.btn_fom_2.toggled.connect(lambda:self.btnstate_fluidormelt(self.btn_fom_2))

		if SEEL.fluid_or_melt_method == 0:
			self.btn_fom_1.setChecked(True)
		elif SEEL.fluid_or_melt_method == 1:
			self.btn_fom_2.setChecked(True)

		fluid_melt_btg.addButton(self.btn_fom_1)
		fluid_melt_btg.addButton(self.btn_fom_2)

		fluid_melt_layout.addWidget(fluid_melt_label)
		fluid_melt_layout.addWidget(self.btn_fom_1)
		fluid_melt_layout.addWidget(self.btn_fom_2)

	def btnstate_fluidormelt(self,b):

		if b.text() == "Fluid":
			if b.isChecked() == True:
				SEEL.fluid_or_melt_method = 0
				SEEL.btn_salinity_fluid.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_co2_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_h2o_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_nao_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_k2o_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		if b.text() == "Melt":
			if b.isChecked() == True:
				SEEL.fluid_or_melt_method = 1
				SEEL.btn_salinity_fluid.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_co2_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_h2o_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_nao_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_k2o_melt.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")


class SOLID_PHASE_POP(QWidget):

	def __init__(self):

		QWidget.__init__(self)

		layout = QVBoxLayout(self)

		main_label = QLabel(self)
		main_label.setText('Select the solid phase option.')
		main_label.setStyleSheet("QLabel {font:bold};min-width: 10em; fontsize: 10pt;color: red")

		solid_phase_btg = QButtonGroup(self)

		self.btn_sphase_1 = QRadioButton("Background Resistivity Entry")
		self.btn_sphase_1.toggled.connect(lambda:self.btnstate_solid_phase_setup(self.btn_sphase_1))
		self.btn_sphase_2 = QRadioButton("Experimental Conductivity Measurements of Rocks")
		self.btn_sphase_2.toggled.connect(lambda:self.btnstate_solid_phase_setup(self.btn_sphase_2))
		self.btn_sphase_3 = QRadioButton("Experimental Conductivity Measurements of Minerals")
		self.btn_sphase_3.toggled.connect(lambda:self.btnstate_solid_phase_setup(self.btn_sphase_3))

		if SEEL.solid_phase_method == 0:
			self.btn_sphase_1.setChecked(True)
		elif SEEL.solid_phase_method == 1:
			self.btn_sphase_2.setChecked(True)
		elif SEEL.solid_phase_method == 2:
			self.btn_sphase_3.setChecked(True)

		solid_phase_btg.addButton(self.btn_sphase_1)
		solid_phase_btg.addButton(self.btn_sphase_2)
		solid_phase_btg.addButton(self.btn_sphase_3)

		layout.addWidget(main_label)
		layout.addWidget(self.btn_sphase_1)
		layout.addWidget(self.btn_sphase_2)
		layout.addWidget(self.btn_sphase_3)

	def btnstate_solid_phase_setup(self,b):

		if b.text() == "Background Resistivity Entry":
			if b.isChecked() == True:
				SEEL.solid_phase_method = 0
				SEEL.btn_bckgr_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_granite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_granulite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_sandstone_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_gneiss_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_amphibolite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_basalt_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_mud_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_gabbro_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_other_rock_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_quartz_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_plag_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_amp_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_kfelds_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_opx_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_cpx_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_mica_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_garnet_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_sulphides_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_graphite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_ol_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_mixture_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_other_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		if b.text() == "Experimental Conductivity Measurements of Rocks":
			if b.isChecked() == True:
				SEEL.solid_phase_method = 1
				SEEL.btn_bckgr_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_granite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_granulite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_sandstone_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_gneiss_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_amphibolite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_basalt_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_mud_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_gabbro_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_other_rock_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_quartz_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_plag_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_amp_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_kfelds_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_opx_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_cpx_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_mica_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_garnet_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_sulphides_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_graphite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_ol_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_mixture_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_other_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
		if b.text() == "Experimental Conductivity Measurements of Minerals":
			if b.isChecked() == True:
				SEEL.solid_phase_method = 2
				SEEL.btn_bckgr_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_granite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_granulite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_sandstone_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_gneiss_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_amphibolite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_basalt_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_mud_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_gabbro_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_other_rock_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #6b786e}")
				SEEL.btn_quartz_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_plag_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_amp_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_kfelds_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_opx_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_cpx_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_mica_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_garnet_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_sulphides_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_graphite_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_ol_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_mixture_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")
				SEEL.btn_other_res.setStyleSheet("QPushButton {min-width: 8em; font: bold; font-size: 9pt;background-color: #c8cccc}")

class COND_POP(QWidget):
	
	def __init__(self):

		QWidget.__init__(self)

		conduc_layout = QFormLayout(self)
		
		self.fluid_cond_btn = QPushButton('Fluid Model')
		self.fluid_cond_text_box = QLineEdit(SEEL.name[0][SEEL.fluid_cond_selection])
		self.fluid_cond_text_box.setEnabled(False)
		self.fluid_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.melt_cond_text_box, param = "fluid_cond_selection", name_index = 0))

		self.melt_cond_btn = QPushButton('Melt Model')
		self.melt_cond_text_box = QLineEdit(SEEL.name[1][SEEL.melt_cond_selection])
		self.melt_cond_text_box.setEnabled(False)
		self.melt_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.melt_cond_text_box, param = "melt_cond_selection", name_index = 1))

		self.granite_cond_btn = QPushButton('Granite Model')
		self.granite_cond_text_box = QLineEdit(SEEL.name[2][SEEL.granite_cond_selection])
		self.granite_cond_text_box.setEnabled(False)
		self.granite_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.granite_cond_text_box, param = "granite_cond_selection", name_index = 2))

		self.granulite_cond_btn = QPushButton('Granulite Model')
		self.granulite_cond_text_box = QLineEdit(SEEL.name[3][SEEL.granulite_cond_selection])
		self.granulite_cond_text_box.setEnabled(False)
		self.granulite_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.granulite_cond_text_box, param = "granulite_cond_selection", name_index = 3))

		self.sandstone_cond_btn = QPushButton('Sandstone Model')
		self.sandstone_cond_text_box = QLineEdit(SEEL.name[4][SEEL.sandstone_cond_selection])
		self.sandstone_cond_text_box.setEnabled(False)
		self.sandstone_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.sandstone_cond_text_box, param = "sandstone_cond_selection", name_index = 4))

		self.gneiss_cond_btn = QPushButton('Gneiss Model')
		self.gneiss_cond_text_box = QLineEdit(SEEL.name[5][SEEL.gneiss_cond_selection])
		self.gneiss_cond_text_box.setEnabled(False)
		self.gneiss_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.gneiss_cond_text_box, param = "gneiss_cond_selection", name_index =5))

		self.amphibolite_cond_btn = QPushButton('Amphibolite Model')
		self.amphibolite_cond_text_box = QLineEdit(SEEL.name[6][SEEL.amphibolite_cond_selection])
		self.amphibolite_cond_text_box.setEnabled(False)
		self.amphibolite_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.amphibolite_cond_text_box, param = "amphibolite_cond_selection", name_index = 6))

		self.basalt_cond_btn = QPushButton('Basalt Model')
		self.basalt_cond_text_box = QLineEdit(SEEL.name[7][SEEL.basalt_cond_selection])
		self.basalt_cond_text_box.setEnabled(False)
		self.basalt_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.basalt_cond_text_box, param = "basalt_cond_selection", name_index = 7))

		self.mud_cond_btn = QPushButton('Mudstone/Shale Model')
		self.mud_cond_text_box = QLineEdit(SEEL.name[8][SEEL.mud_cond_selection])
		self.mud_cond_text_box.setEnabled(False)
		self.mud_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.mud_cond_text_box, param = "mud_cond_selection", name_index = 8))

		self.gabbro_cond_btn = QPushButton('Gabbro Model')
		self.gabbro_cond_text_box = QLineEdit(SEEL.name[9][SEEL.gabbro_cond_selection])
		self.gabbro_cond_text_box.setEnabled(False)
		self.gabbro_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.gabbro_cond_text_box, param = "gabbro_cond_selection", name_index = 9))

		self.other_rock_cond_btn = QPushButton('Other Rock Model')
		self.other_rock_cond_text_box = QLineEdit(SEEL.name[10][SEEL.other_rock_cond_selection])
		self.other_rock_cond_text_box.setEnabled(False)
		self.other_rock_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.other_rock_cond_text_box, param = "other_rock_cond_selection", name_index = 10))

		self.quartz_cond_btn = QPushButton('Quartz Model')
		self.quartz_cond_text_box = QLineEdit(SEEL.name[11][SEEL.quartz_cond_selection])
		self.quartz_cond_text_box.setEnabled(False)
		self.quartz_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.quartz_cond_text_box, param = "quartz_cond_selection", name_index = 11))
		
		self.plag_cond_btn = QPushButton('Plagioclase Model')
		self.plag_cond_text_box = QLineEdit(SEEL.name[12][SEEL.plag_cond_selection])
		self.plag_cond_text_box.setEnabled(False)
		self.plag_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.plag_cond_text_box, param = "plag_cond_selection", name_index = 12))

		self.amp_cond_btn = QPushButton('Amphibole Model')
		self.amp_cond_text_box = QLineEdit(SEEL.name[13][SEEL.amp_cond_selection])
		self.amp_cond_text_box.setEnabled(False)
		self.amp_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.amp_cond_text_box, param = "amp_cond_selection", name_index = 13))

		self.kfelds_cond_btn = QPushButton('K-Feldspar Model')
		self.kfelds_cond_text_box = QLineEdit(SEEL.name[14][SEEL.kfelds_cond_selection])
		self.kfelds_cond_text_box.setEnabled(False)
		self.kfelds_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.kfelds_cond_text_box, param = "kfelds_cond_selection", name_index = 14))

		self.opx_cond_btn = QPushButton('Orthopyroxene Model')
		self.opx_cond_text_box = QLineEdit(SEEL.name[15][SEEL.opx_cond_selection])
		self.opx_cond_text_box.setEnabled(False)
		self.opx_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.opx_cond_text_box, param = "opx_cond_selection", name_index = 15))
		
		self.cpx_cond_btn = QPushButton('Clinopyroxene Model')
		self.cpx_cond_text_box = QLineEdit(SEEL.name[16][SEEL.cpx_cond_selection])
		self.cpx_cond_text_box.setEnabled(False)
		self.cpx_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.cpx_cond_text_box, param = "cpx_cond_selection", name_index = 16))

		self.mica_cond_btn = QPushButton('Mica Model')
		self.mica_cond_text_box = QLineEdit(SEEL.name[17][SEEL.mica_cond_selection])
		self.mica_cond_text_box.setEnabled(False)
		self.mica_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.mica_cond_text_box, param = "mica_cond_selection", name_index = 17))

		self.garnet_cond_btn = QPushButton('Garnet Model')
		self.garnet_cond_text_box = QLineEdit(SEEL.name[18][SEEL.garnet_cond_selection])
		self.garnet_cond_text_box.setEnabled(False)
		self.garnet_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.garnet_cond_text_box, param = "garnet_cond_selection", name_index = 18))

		self.sulphides_cond_btn = QPushButton('Sulphide Model')
		self.sulphides_cond_text_box = QLineEdit(SEEL.name[19][SEEL.sulphide_cond_selection])
		self.sulphides_cond_text_box.setEnabled(False)
		self.sulphides_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.sulphides_cond_text_box, param = "sulphide_cond_selection", name_index = 19))

		self.graphite_cond_btn = QPushButton('Graphite Model')
		self.graphite_cond_text_box = QLineEdit(SEEL.name[20][SEEL.graphite_cond_selection])
		self.graphite_cond_text_box.setEnabled(False)
		self.graphite_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.graphite_cond_text_box, param = "graphite_cond_selection", name_index = 20))

		self.olivine_cond_btn = QPushButton('Olivine Model')
		self.olivine_cond_text_box = QLineEdit(SEEL.name[21][SEEL.ol_cond_selection])
		self.olivine_cond_text_box.setEnabled(False)
		self.olivine_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.olivine_cond_text_box, param = "ol_cond_selection", name_index = 21))
		
		self.mixture_cond_btn = QPushButton('Mixture Model')
		self.mixture_cond_text_box = QLineEdit(SEEL.name[22][SEEL.mixture_cond_selection])
		self.mixture_cond_text_box.setEnabled(False)
		self.mixture_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.mixture_cond_text_box, param = "mixture_cond_selection", name_index = 22))

		self.other_cond_btn = QPushButton('Other Model')
		self.other_cond_text_box = QLineEdit(SEEL.name[23][SEEL.other_cond_selection])
		self.other_cond_text_box.setEnabled(False)
		self.other_cond_btn.clicked.connect(lambda: self.cond_get(textbox_obj=self.other_cond_text_box, param = "other_cond_selection", name_index = 23))

		label_meltfluid = QLabel(self)
		label_meltfluid.setText('--------Melt/Fluid--------')
		label_meltfluid.setStyleSheet("QLabel {font:bold};min-width: 10em; fontsize: 10pt;color: red")

		label_rocks = QLabel(self)
		label_rocks.setText('--------Rocks--------')
		label_rocks.setStyleSheet("QLabel {font:bold};min-width: 10em; fontsize: 10pt;color: red")

		label_minerals = QLabel(self)
		label_minerals.setText('--------Minerals--------')
		label_minerals.setStyleSheet("QLabel {font:bold};min-width: 10em; fontsize: 10pt;color: red")

		conduc_layout.addRow(label_meltfluid)
		conduc_layout.addRow(self.fluid_cond_btn,self.fluid_cond_text_box)
		conduc_layout.addRow(self.melt_cond_btn,self.melt_cond_text_box)
		conduc_layout.addRow(label_rocks)
		conduc_layout.addRow(self.granite_cond_btn,self.granite_cond_text_box)
		conduc_layout.addRow(self.granulite_cond_btn,self.granulite_cond_text_box)
		conduc_layout.addRow(self.sandstone_cond_btn,self.sandstone_cond_text_box)
		conduc_layout.addRow(self.gneiss_cond_btn,self.gneiss_cond_text_box)
		conduc_layout.addRow(self.amphibolite_cond_btn,self.amphibolite_cond_text_box)
		conduc_layout.addRow(self.basalt_cond_btn,self.basalt_cond_text_box)
		conduc_layout.addRow(self.mud_cond_btn,self.mud_cond_text_box)
		conduc_layout.addRow(self.gabbro_cond_btn,self.gabbro_cond_text_box)
		conduc_layout.addRow(self.other_rock_cond_btn,self.other_rock_cond_text_box)
		conduc_layout.addRow(label_minerals)
		conduc_layout.addRow(self.quartz_cond_btn,self.quartz_cond_text_box)
		conduc_layout.addRow(self.plag_cond_btn,self.plag_cond_text_box)
		conduc_layout.addRow(self.amp_cond_btn,self.amp_cond_text_box)
		conduc_layout.addRow(self.kfelds_cond_btn,self.kfelds_cond_text_box)
		conduc_layout.addRow(self.opx_cond_btn,self.opx_cond_text_box)
		conduc_layout.addRow(self.cpx_cond_btn,self.cpx_cond_text_box)
		conduc_layout.addRow(self.mica_cond_btn,self.mica_cond_text_box)
		conduc_layout.addRow(self.garnet_cond_btn,self.garnet_cond_text_box)
		conduc_layout.addRow(self.sulphides_cond_btn,self.sulphides_cond_text_box)
		conduc_layout.addRow(self.graphite_cond_btn,self.graphite_cond_text_box)
		conduc_layout.addRow(self.olivine_cond_btn,self.olivine_cond_text_box)
		conduc_layout.addRow(self.mixture_cond_btn,self.mixture_cond_text_box)
		conduc_layout.addRow(self.other_cond_btn,self.other_cond_text_box)

	def cond_get(self, textbox_obj, param, name_index):

		item, ok = QInputDialog.getItem(self, "select input dialog",
			"Conductivity model", SEEL.name[name_index], 0, False)

		if ok and item:
			textbox_obj.setText(item)
		
		setattr(SEEL, param, SEEL.name[name_index].index(item))

		SEEL.rock_cond_selections = [SEEL.granite_cond_selection, SEEL.granulite_cond_selection, SEEL.sandstone_cond_selection, SEEL.gneiss_cond_selection,
				   SEEL.amphibolite_cond_selection, SEEL.basalt_cond_selection, SEEL.mud_cond_selection, SEEL.gabbro_cond_selection, SEEL.other_rock_cond_selection]
		
		SEEL.minerals_cond_selections = [SEEL.quartz_cond_selection, SEEL.plag_cond_selection, SEEL.amp_cond_selection, SEEL.kfelds_cond_selection, SEEL.opx_cond_selection,
				   SEEL.cpx_cond_selection, SEEL.mica_cond_selection, SEEL.garnet_cond_selection, SEEL.sulphide_cond_selection,
				   SEEL.graphite_cond_selection, SEEL.ol_cond_selection, SEEL.mixture_cond_selection, SEEL.other_cond_selection]
		
				
class PHS_MIX_POP(QWidget):

	def __init__(self):

		QWidget.__init__(self)

		layout = QGridLayout(self)

		bg1 = QButtonGroup(self)
		
		label_solid_mix = QLabel(self)
		label_solid_mix.setText('--------Solid-State Mixing--------')
		label_solid_mix.setStyleSheet("QLabel {font:bold};min-width: 10em; fontsize: 10pt;color: red")
		layout.addWidget(label_solid_mix,0,0)
		
		self.btn_mix_1 = QRadioButton("Generalized Archie's Law (Glover, 2010)")
		self.btn_mix_1.toggled.connect(lambda:self.btnstate_phsmix(self.btn_mix_1))
		self.btn_mix_2 = QRadioButton("Hashin-Shtrikman Lower Bound (Berryman, 1995)")
		self.btn_mix_2.toggled.connect(lambda:self.btnstate_phsmix(self.btn_mix_2))
		self.btn_mix_3 = QRadioButton("Hashin-Shtrikman Upper Bound (Berryman, 1995)")
		self.btn_mix_3.toggled.connect(lambda:self.btnstate_phsmix(self.btn_mix_3))
		self.btn_mix_4 = QRadioButton("Parallel Model (Guegen and Palciauskas, 1994)")
		self.btn_mix_4.toggled.connect(lambda:self.btnstate_phsmix(self.btn_mix_4))
		self.btn_mix_5 = QRadioButton("Perpendicular Model (Guegen and Palciauskas, 1994)")
		self.btn_mix_5.toggled.connect(lambda:self.btnstate_phsmix(self.btn_mix_5))
		self.btn_mix_6 = QRadioButton("Random Model (Guegen and Palciauskas, 1994)")
		self.btn_mix_6.toggled.connect(lambda:self.btnstate_phsmix(self.btn_mix_6))
		
		if SEEL.phs_mix_method == 0:
			self.btn_mix_1.setChecked(True)
		elif SEEL.phs_mix_method == 1:
			self.btn_mix_2.setChecked(True)
		elif SEEL.phs_mix_method == 2:
			self.btn_mix_3.setChecked(True)
		elif SEEL.phs_mix_method == 3:
			self.btn_mix_4.setChecked(True)
		elif SEEL.phs_mix_method == 4:
			self.btn_mix_5.setChecked(True)
		elif SEEL.phs_mix_method == 5:
			self.btn_mix_6.setChecked(True)
			
		bg1.addButton(self.btn_mix_1)
		bg1.addButton(self.btn_mix_2)
		bg1.addButton(self.btn_mix_3)
		bg1.addButton(self.btn_mix_4)
		bg1.addButton(self.btn_mix_5)
		bg1.addButton(self.btn_mix_6)
		
		layout.addWidget(self.btn_mix_1,1,0)
		layout.addWidget(self.btn_mix_2,2,0)
		layout.addWidget(self.btn_mix_3,3,0)
		layout.addWidget(self.btn_mix_4,4,0)
		layout.addWidget(self.btn_mix_5,5,0)
		layout.addWidget(self.btn_mix_6,6,0)
		
		label_melt_mix = QLabel(self)
		label_melt_mix.setText('--------Melt/Fluid-Solid Mixing--------')
		label_melt_mix.setStyleSheet("QLabel {font:bold};min-width: 10em; fontsize: 10pt;color: red")
		layout.addWidget(label_melt_mix,0,1)

		self.btn_mix_melt_1 = QRadioButton("Modified Archie's Law (Glover et al., 2000)")
		self.btn_mix_melt_1.toggled.connect(lambda:self.btnstate_phsmix_melt(self.btn_mix_melt_1))
		self.btn_mix_melt_2 = QRadioButton("Tubes Model (ten Grotenhuis et al., 2005)")
		self.btn_mix_melt_2.toggled.connect(lambda:self.btnstate_phsmix_melt(self.btn_mix_melt_2))
		self.btn_mix_melt_3 = QRadioButton("Spheres Model (ten Grotenhuis et al., 2005)")
		self.btn_mix_melt_3.toggled.connect(lambda:self.btnstate_phsmix_melt(self.btn_mix_melt_3))
		self.btn_mix_melt_4 = QRadioButton("Modified Brick-layer Model (Schilling et al., 1997)")
		self.btn_mix_melt_4.toggled.connect(lambda:self.btnstate_phsmix_melt(self.btn_mix_melt_4))
		self.btn_mix_melt_5 = QRadioButton("Hashin-Shtrikman Upper-Bound (Glover et al., 2000)")
		self.btn_mix_melt_5.toggled.connect(lambda:self.btnstate_phsmix_melt(self.btn_mix_melt_5))
		self.btn_mix_melt_6 = QRadioButton("Hashin-Shtrikman Lower-Bound (Glover et al., 2000)")
		self.btn_mix_melt_6.toggled.connect(lambda:self.btnstate_phsmix_melt(self.btn_mix_melt_6))

		bg2 = QButtonGroup(self)

		bg2.addButton(self.btn_mix_melt_1)
		bg2.addButton(self.btn_mix_melt_2)
		bg2.addButton(self.btn_mix_melt_3)
		bg2.addButton(self.btn_mix_melt_4)
		bg2.addButton(self.btn_mix_melt_5)
		bg2.addButton(self.btn_mix_melt_6)

		layout.addWidget(self.btn_mix_melt_1,1,1)
		layout.addWidget(self.btn_mix_melt_2,2,1)
		layout.addWidget(self.btn_mix_melt_3,3,1)
		layout.addWidget(self.btn_mix_melt_4,4,1)
		layout.addWidget(self.btn_mix_melt_5,5,1)
		layout.addWidget(self.btn_mix_melt_6,6,1)

		if SEEL.phs_melt_mix_method == 0:
			self.btn_mix_melt_1.setChecked(True)
		elif SEEL.phs_melt_mix_method == 1:
			self.btn_mix_melt_2.setChecked(True)
		elif SEEL.phs_melt_mix_method == 2:
			self.btn_mix_melt_3.setChecked(True)
		elif SEEL.phs_melt_mix_method == 3:
			self.btn_mix_melt_4.setChecked(True)
		elif SEEL.phs_melt_mix_method == 4:
			self.btn_mix_melt_5.setChecked(True)
		elif SEEL.phs_melt_mix_method == 5:
			self.btn_mix_melt_6.setChecked(True)


	def btnstate_phsmix(self,b):

		if b.text() == "Generalized Archie's Law (Glover, 2010)":
			if b.isChecked() == True:
				SEEL.phs_mix_method = 0
		if b.text() == "Hashin-Shtrikman Lower Bound (Berryman, 1995)":
			if b.isChecked() == True:
				SEEL.phs_mix_method = 1
		if b.text() == "Hashin-Shtrikman Upper Bound (Berryman, 1995)":
			if b.isChecked() == True:
				SEEL.phs_mix_method = 2
		if b.text() == "Parallel Model (Guegen and Palciauskas, 1994)":
			if b.isChecked() == True:
				SEEL.phs_mix_method = 3
		if b.text() == "Perpendicular Model (Guegen and Palciauskas, 1994)":
			if b.isChecked() == True:
				SEEL.phs_mix_method = 4
		if b.text() == "Random Model (Guegen and Palciauskas, 1994)":
			if b.isChecked() == True:
				SEEL.phs_mix_method = 5
				
				
	def btnstate_phsmix_melt(self, b2):

		if b2.text() == "Modified Archie's Law (Glover et al., 2000)":
			if b2.isChecked() == True:
				SEEL.phs_melt_mix_method = 0
				SEEL.phs_melt_mix_type = 0
		elif b2.text() == "Tubes Model (ten Grotenhuis et al., 2005)":
			if b2.isChecked() == True:
				SEEL.phs_melt_mix_method = 1
				SEEL.phs_melt_mix_type = 1
		elif b2.text() == "Spheres Model (ten Grotenhuis et al., 2005)":
			if b2.isChecked() == True:
				SEEL.phs_melt_mix_method = 2
				SEEL.phs_melt_mix_type = 1
		elif b2.text() == "Modified Brick-layer Model (Glover et al., 2000)":
			if b2.isChecked() == True:
				SEEL.phs_melt_mix_method = 3
				SEEL.phs_melt_mix_type = 1
		elif b2.text() == "Hashin-Shtrikman Upper-Bound (Glover et al., 2000)":
			if b2.isChecked() == True:
				SEEL.phs_melt_mix_method = 4
				SEEL.phs_melt_mix_type = 1
		elif b2.text() == "Hashin-Shtrikman Lower-Bound (Glover et al., 2000)":
			if b2.isChecked() == True:
				SEEL.phs_melt_mix_method = 5
				SEEL.phs_melt_mix_type = 1
				
class PHS_INTER_POP(QWidget):

	def __init__(self):
	
		QWidget.__init__(self)

		layout = QFormLayout(self)

		desc_label = QLabel(self)
		desc_label.setText('---Enter Interconnectivity (Cementation exponent) values---')
		desc_label.setStyleSheet("QLabel {font:bold};fontsize: 10pt;color: red")
		
		self.melt_fluid_m_btn = QPushButton('Melt/Fluid m')
		self.melt_fluid_m_textbox = QLineEdit(str(SEEL.melt_fluid_m[0]))
		self.melt_fluid_m_textbox.setEnabled(False)
		self.melt_fluid_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.melt_fluid_m_textbox, param = "melt_fluid_m"))


		#rocks
		rocks_label = QLabel(self)
		rocks_label.setText('---Rocks---')
		rocks_label.setStyleSheet("QLabel {font:bold};fontsize: 10pt;color: red")

		self.granite_m_btn = QPushButton('Granite m')
		self.granite_m_textbox = QLineEdit(str(SEEL.granite_m[0]))
		self.granite_m_textbox.setEnabled(False)
		self.granite_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.granite_m_textbox, param = "granite_m"))

		self.granulite_m_btn = QPushButton('Granulite m')
		self.granulite_m_textbox = QLineEdit(str(SEEL.granulite_m[0]))
		self.granulite_m_textbox.setEnabled(False)
		self.granulite_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.granulite_m_textbox, param = "granulite_m"))

		self.sandstone_m_btn = QPushButton('Sandstone m')
		self.sandstone_m_textbox = QLineEdit(str(SEEL.sandstone_m[0]))
		self.sandstone_m_textbox.setEnabled(False)
		self.sandstone_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.sandstone_m_textbox, param = "sandstone_m"))

		self.gneiss_m_btn = QPushButton('Gneiss m')
		self.gneiss_m_textbox = QLineEdit(str(SEEL.gneiss_m[0]))
		self.gneiss_m_textbox.setEnabled(False)
		self.gneiss_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.gneiss_m_textbox, param = "gneiss_m"))

		self.amphibolite_m_btn = QPushButton('Amphibolite m')
		self.amphibolite_m_textbox = QLineEdit(str(SEEL.amphibolite_m[0]))
		self.amphibolite_m_textbox.setEnabled(False)
		self.amphibolite_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.amphibolite_m_textbox, param = "amphibolite_m"))

		self.basalt_m_btn = QPushButton('Basalt m')
		self.basalt_m_textbox = QLineEdit(str(SEEL.basalt_m[0]))
		self.basalt_m_textbox.setEnabled(False)
		self.basalt_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.basalt_m_textbox, param = "basalt_m"))

		self.mud_m_btn = QPushButton('mud m')
		self.mud_m_textbox = QLineEdit(str(SEEL.mud_m[0]))
		self.mud_m_textbox.setEnabled(False)
		self.mud_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.mud_m_textbox, param = "mud_m"))

		self.gabbro_m_btn = QPushButton('Gabbro m')
		self.gabbro_m_textbox = QLineEdit(str(SEEL.gabbro_m[0]))
		self.gabbro_m_textbox.setEnabled(False)
		self.gabbro_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.gabbro_m_textbox, param = "gabbro_m"))

		self.other_rock_m_btn = QPushButton('Other rock m')
		self.other_rock_m_textbox = QLineEdit(str(SEEL.other_rock_m[0]))
		self.other_rock_m_textbox.setEnabled(False)
		self.other_rock_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.other_rock_m_textbox, param = "other_rock_m"))
		
		#minerals
		minerals_label = QLabel(self)
		minerals_label.setText('---Mineral---')
		minerals_label.setStyleSheet("QLabel {font:bold};fontsize: 10pt;color: red")

		self.quartz_m_btn = QPushButton('Quartz m')
		self.quartz_m_textbox = QLineEdit(str(SEEL.quartz_m[0]))
		self.quartz_m_textbox.setEnabled(False)
		self.quartz_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.quartz_m_textbox, param = "quartz_m"))

		self.plag_m_btn = QPushButton('Plagioclase m')
		self.plag_m_textbox = QLineEdit(str(SEEL.plag_m[0]))
		self.plag_m_textbox.setEnabled(False)
		self.plag_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.plag_m_textbox, param = "plag_m"))

		self.amp_m_btn = QPushButton('Amphibole m')
		self.amp_m_textbox = QLineEdit(str(SEEL.amp_m[0]))
		self.amp_m_textbox.setEnabled(False)
		self.amp_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.amp_m_textbox, param = "amp_m"))

		self.kfelds_m_btn = QPushButton('K-Feldspar m')
		self.kfelds_m_textbox = QLineEdit(str(SEEL.kfelds_m[0]))
		self.kfelds_m_textbox.setEnabled(False)
		self.kfelds_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.kfelds_m_textbox, param = "kfelds_m"))

		self.garnet_m_btn = QPushButton('Garnet m')
		self.garnet_m_textbox = QLineEdit(str(SEEL.garnet_m[0]))
		self.garnet_m_textbox.setEnabled(False)
		self.garnet_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.garnet_m_textbox, param = "garnet_m"))
		
		self.ol_m_btn = QPushButton('Olivine m')
		self.ol_m_textbox = QLineEdit(str(SEEL.ol_m[0]))
		self.ol_m_textbox.setEnabled(False)
		self.ol_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.ol_m_textbox, param = "ol_m"))
		
		self.opx_m_btn = QPushButton('Orthopyroxene m')
		self.opx_m_textbox = QLineEdit(str(SEEL.opx_m[0]))
		self.opx_m_textbox.setEnabled(False)
		self.opx_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.opx_m_textbox, param = "opx_m"))
		
		self.cpx_m_btn = QPushButton('Clinopyroxene m')
		self.cpx_m_textbox = QLineEdit(str(SEEL.cpx_m[0]))
		self.cpx_m_textbox.setEnabled(False)
		self.cpx_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.cpx_m_textbox, param = "cpx_m"))

		self.sulphides_m_btn = QPushButton('Sulphides m')
		self.sulphides_m_textbox = QLineEdit(str(SEEL.sulphide_m[0]))
		self.sulphides_m_textbox.setEnabled(False)
		self.sulphides_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.sulphides_m_textbox, param = "sulphide_m"))

		self.graphite_m_btn = QPushButton('Graphite m')
		self.graphite_m_textbox = QLineEdit(str(SEEL.graphite_m[0]))
		self.graphite_m_textbox.setEnabled(False)
		self.graphite_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.graphite_m_textbox, param = "graphite_m"))

		self.mica_m_btn = QPushButton('Mica m')
		self.mica_m_textbox = QLineEdit(str(SEEL.mica_m[0]))
		self.mica_m_textbox.setEnabled(False)
		self.mica_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.mica_m_textbox, param = "mica_m"))
		
		self.mixture_m_btn = QPushButton('Mixtures m')
		self.mixture_m_textbox = QLineEdit(str(SEEL.mixture_m[0]))
		self.mixture_m_textbox.setEnabled(False)
		self.mixture_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.mixture_m_textbox, param = "mixture_m"))

		self.other_m_btn = QPushButton('Other m')
		self.other_m_textbox = QLineEdit(str(SEEL.other_m[0]))
		self.other_m_textbox.setEnabled(False)
		self.other_m_btn.clicked.connect(lambda: self.get_interconnectivity(textbox_obj=self.other_m_textbox, param = "other_m"))

	
		layout.addRow(desc_label)
		layout.addRow(self.melt_fluid_m_btn, self.melt_fluid_m_textbox)

		layout.addRow(rocks_label)

		layout.addRow(self.granite_m_btn, self.granite_m_textbox)
		layout.addRow(self.granulite_m_btn, self.granulite_m_textbox)
		layout.addRow(self.sandstone_m_btn, self.sandstone_m_textbox)
		layout.addRow(self.gneiss_m_btn, self.gneiss_m_textbox)
		layout.addRow(self.amphibolite_m_btn, self.amphibolite_m_textbox)
		layout.addRow(self.basalt_m_btn, self.basalt_m_textbox)
		layout.addRow(self.mud_m_btn, self.mud_m_textbox)
		layout.addRow(self.gabbro_m_btn, self.gabbro_m_textbox)
		layout.addRow(self.other_rock_m_btn, self.other_rock_m_textbox)

		layout.addRow(minerals_label)

		layout.addRow(self.quartz_m_btn, self.quartz_m_textbox)
		layout.addRow(self.plag_m_btn, self.plag_m_textbox)
		layout.addRow(self.amp_m_btn, self.amp_m_textbox)
		layout.addRow(self.kfelds_m_btn, self.kfelds_m_textbox)
		layout.addRow(self.garnet_m_btn, self.garnet_m_textbox)
		layout.addRow(self.ol_m_btn, self.ol_m_textbox)
		layout.addRow(self.opx_m_btn, self.opx_m_textbox)
		layout.addRow(self.cpx_m_btn, self.cpx_m_textbox)
		layout.addRow(self.mica_m_btn, self.mica_m_textbox)
		layout.addRow(self.graphite_m_btn, self.graphite_m_textbox)
		layout.addRow(self.sulphides_m_btn, self.sulphides_m_textbox)
		layout.addRow(self.mixture_m_btn, self.mixture_m_textbox)
		layout.addRow(self.other_m_btn, self.other_m_textbox)

	def get_interconnectivity(self,textbox_obj,param):

		text, ok = QInputDialog.getText(self, 'Interconnectivity dialogue', 'Enter the value (bigger than 1)')
		if ok:
			try:
				float(text)
				if (float(text) >= 1):

					textbox_obj.setText(str(text))
					setattr(SEEL, param, np.array([float(text)]))

				else:
					QMessageBox.about(self,"Warning!","Enter a value above 1")
			except ValueError:
				QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")

class WATER_PHS_POP(QWidget):

	def __init__(self):
	
		QWidget.__init__(self)

		layout = QFormLayout(self)

		desc_label = QLabel(self)
		desc_label.setText('---Enter Solid phase water contents (in ppm) values---')
		desc_label.setStyleSheet("QLabel {font:bold};fontsize: 10pt;color: red")

		#rocks
		rocks_label = QLabel(self)
		rocks_label.setText('---Rocks---')
		rocks_label.setStyleSheet("QLabel {font:bold};fontsize: 10pt;color: red")
		
		self.granite_water_btn = QPushButton('Granite water')
		self.granite_water_textbox = QLineEdit(str(SEEL.granite_water[0]))
		self.granite_water_textbox.setEnabled(False)
		self.granite_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.granite_water_textbox, param = "granite_water"))

		self.granulite_water_btn = QPushButton('Granulite water')
		self.granulite_water_textbox = QLineEdit(str(SEEL.granulite_water[0]))
		self.granulite_water_textbox.setEnabled(False)
		self.granulite_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.granulite_water_textbox, param = "granulite_water"))

		self.sandstone_water_btn = QPushButton('Sandstone water')
		self.sandstone_water_textbox = QLineEdit(str(SEEL.sandstone_water[0]))
		self.sandstone_water_textbox.setEnabled(False)
		self.sandstone_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.sandstone_water_textbox, param = "sandstone_water"))

		self.gneiss_water_btn = QPushButton('Gneiss water')
		self.gneiss_water_textbox = QLineEdit(str(SEEL.gneiss_water[0]))
		self.gneiss_water_textbox.setEnabled(False)
		self.gneiss_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.gneiss_water_textbox, param = "gneiss_water"))

		self.amphibolite_water_btn = QPushButton('Amphibolite water')
		self.amphibolite_water_textbox = QLineEdit(str(SEEL.amphibolite_water[0]))
		self.amphibolite_water_textbox.setEnabled(False)
		self.amphibolite_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.amphibolite_water_textbox, param = "amphibolite_water"))

		self.basalt_water_btn = QPushButton('Basalt water')
		self.basalt_water_textbox = QLineEdit(str(SEEL.basalt_water[0]))
		self.basalt_water_textbox.setEnabled(False)
		self.basalt_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.basalt_water_textbox, param = "basalt_water"))

		self.mud_water_btn = QPushButton('Mudstone/shale water')
		self.mud_water_textbox = QLineEdit(str(SEEL.mud_water[0]))
		self.mud_water_textbox.setEnabled(False)
		self.mud_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.mud_water_textbox, param = "mud_water"))

		self.gabbro_water_btn = QPushButton('Gabbro water')
		self.gabbro_water_textbox = QLineEdit(str(SEEL.gabbro_water[0]))
		self.gabbro_water_textbox.setEnabled(False)
		self.gabbro_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.gabbro_water_textbox, param = "gabbro_water"))

		self.other_rock_water_btn = QPushButton('Other rock water')
		self.other_rock_water_textbox = QLineEdit(str(SEEL.other_rock_water[0]))
		self.other_rock_water_textbox.setEnabled(False)
		self.other_rock_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.other_rock_water_textbox, param = "other_rock_water"))

		#minerals
		minerals_label = QLabel(self)
		minerals_label.setText('---Mineral---')
		minerals_label.setStyleSheet("QLabel {font:bold};fontsize: 10pt;color: red")

		self.quartz_water_btn = QPushButton('Quartz water')
		self.quartz_water_textbox = QLineEdit(str(SEEL.quartz_water[0]))
		self.quartz_water_textbox.setEnabled(False)
		self.quartz_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.quartz_water_textbox, param = "quartz_water"))

		self.plag_water_btn = QPushButton('Plagioclase water')
		self.plag_water_textbox = QLineEdit(str(SEEL.plag_water[0]))
		self.plag_water_textbox.setEnabled(False)
		self.plag_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.plag_water_textbox, param = "plag_water"))

		self.amp_water_btn = QPushButton('Amphibole water')
		self.amp_water_textbox = QLineEdit(str(SEEL.amp_water[0]))
		self.amp_water_textbox.setEnabled(False)
		self.amp_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.amp_water_textbox, param = "amp_water"))

		self.kfelds_water_btn = QPushButton('K-feldspar water')
		self.kfelds_water_textbox = QLineEdit(str(SEEL.kfelds_water[0]))
		self.kfelds_water_textbox.setEnabled(False)
		self.kfelds_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.kfelds_water_textbox, param = "kfelds_water"))

		self.garnet_water_btn = QPushButton('Garnet water')
		self.garnet_water_textbox = QLineEdit(str(SEEL.garnet_water[0]))
		self.garnet_water_textbox.setEnabled(False)
		self.garnet_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.garnet_water_textbox, param = "garnet_water"))

		self.opx_water_btn = QPushButton('Orthopyroxene water')
		self.opx_water_textbox = QLineEdit(str(SEEL.opx_water[0]))
		self.opx_water_textbox.setEnabled(False)
		self.opx_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.opx_water_textbox, param = "opx_water"))
		
		self.cpx_water_btn = QPushButton('Clinopyroxene water')
		self.cpx_water_textbox = QLineEdit(str(SEEL.cpx_water[0]))
		self.cpx_water_textbox.setEnabled(False)
		self.cpx_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.cpx_water_textbox, param = "cpx_water"))
		
		self.ol_water_btn = QPushButton('Olivine water')
		self.ol_water_textbox = QLineEdit(str(SEEL.ol_water[0]))
		self.ol_water_textbox.setEnabled(False)
		self.ol_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.ol_water_textbox, param = "ol_water"))

		self.mica_water_btn = QPushButton('Mica water')
		self.mica_water_textbox = QLineEdit(str(SEEL.mica_water[0]))
		self.mica_water_textbox.setEnabled(False)
		self.mica_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.mica_water_textbox, param = "mica_water"))
		
		self.mixture_water_btn = QPushButton('Mixture water')
		self.mixture_water_textbox = QLineEdit(str(SEEL.mixture_water[0]))
		self.mixture_water_textbox.setEnabled(False)
		self.mixture_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.mixture_water_textbox, param = "mixture_water"))
		
		self.other_water_btn = QPushButton('Other water')
		self.other_water_textbox = QLineEdit(str(SEEL.other_water[0]))
		self.other_water_textbox.setEnabled(False)
		self.other_water_btn.clicked.connect(lambda: self.get_water(textbox_obj=self.other_water_textbox, param = "other_water"))

		layout.addRow(desc_label)
		layout.addRow(rocks_label)

		layout.addRow(self.granite_water_btn, self.granite_water_textbox)
		layout.addRow(self.granulite_water_btn, self.granulite_water_textbox)
		layout.addRow(self.sandstone_water_btn, self.sandstone_water_textbox)
		layout.addRow(self.gneiss_water_btn, self.gneiss_water_textbox)
		layout.addRow(self.amphibolite_water_btn, self.amphibolite_water_textbox)
		layout.addRow(self.basalt_water_btn, self.basalt_water_textbox)
		layout.addRow(self.mud_water_btn, self.mud_water_textbox)
		layout.addRow(self.gabbro_water_btn, self.gabbro_water_textbox)
		layout.addRow(self.other_rock_water_btn, self.other_rock_water_textbox)

		layout.addRow(minerals_label)

		layout.addRow(self.quartz_water_btn, self.quartz_water_textbox)
		layout.addRow(self.plag_water_btn, self.plag_water_textbox)
		layout.addRow(self.amp_water_btn, self.amp_water_textbox)
		layout.addRow(self.kfelds_water_btn, self.kfelds_water_textbox)
		layout.addRow(self.garnet_water_btn, self.garnet_water_textbox)
		layout.addRow(self.opx_water_btn, self.opx_water_textbox)
		layout.addRow(self.cpx_water_btn, self.cpx_water_textbox)
		layout.addRow(self.ol_water_btn, self.ol_water_textbox)
		layout.addRow(self.mica_water_btn, self.mica_water_textbox)
		layout.addRow(self.mixture_water_btn, self.mixture_water_textbox)
		layout.addRow(self.other_water_btn, self.other_water_textbox)

	def get_water(self,textbox_obj,param):

		text, ok = QInputDialog.getText(self, 'Water content dialogue', 'Enter the value in ppm (bigger than 0)')
		if ok:
			try:
				float(text)
				if (float(text) >= 0):

					textbox_obj.setText(str(text))
					setattr(SEEL, param, np.array([float(text)]))

				else:
					QMessageBox.about(self,"Warning!","Enter a value above 0")
			except ValueError:
				QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")
				
		SEEL.rock_water_list = [SEEL.granite_water, SEEL.granulite_water,
			SEEL.sandstone_water, SEEL.gneiss_water, SEEL.amphibolite_water, SEEL.basalt_water,
			SEEL.mud_water, SEEL.gabbro_water, SEEL.other_rock_water]
			
		SEEL.mineral_water_list = [SEEL.quartz_water, SEEL.plag_water, SEEL.amp_water, SEEL.kfelds_water,
			 SEEL.opx_water, SEEL.cpx_water, SEEL.mica_water, SEEL.garnet_water, SEEL.sulphide_water,
				   SEEL.graphite_water, SEEL.ol_water, SEEL.mixture_water, SEEL.other_water]
				   
class OPTIONAL_PARAM_POP(QWidget):

	def __init__(self):
	
		QWidget.__init__(self)

		layout = QGridLayout(self)

		desc_label = QLabel(self)
		desc_label.setText('---Enter optional parameters required for some models---')
		desc_label.setStyleSheet("QLabel {font:bold};fontsize: 10pt;color: red")
		
		rocks_label = QLabel(self)
		rocks_label.setText('---Rocks---')
		rocks_label.setStyleSheet("QLabel {font:bold};fontsize: 10pt;color: red")
		
		minerals_label = QLabel(self)
		minerals_label.setText('---Minerals---')
		minerals_label.setStyleSheet("QLabel {font:bold};fontsize: 10pt;color: red")
		
		self.granite_param1_btn = QPushButton('Granite param1')
		self.granite_param1_textbox = QLineEdit(str(SEEL.granite_param1[0]))
		self.granite_param1_textbox.setEnabled(False)
		self.granite_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.granite_param1_textbox, param = "granite_param1"))
		
		self.granite_param2_btn = QPushButton('Granite param2')
		self.granite_param2_textbox = QLineEdit(str(SEEL.granite_param2[0]))
		self.granite_param2_textbox.setEnabled(False)
		self.granite_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.granite_param2_textbox, param = "granite_param2"))
		
		self.granulite_param1_btn = QPushButton('Granulite param1')
		self.granulite_param1_textbox = QLineEdit(str(SEEL.granulite_param1[0]))
		self.granulite_param1_textbox.setEnabled(False)
		self.granulite_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.granulite_param1_textbox, param = "granulite_param1"))
		
		self.granulite_param2_btn = QPushButton('Granulite param2')
		self.granulite_param2_textbox = QLineEdit(str(SEEL.granulite_param2[0]))
		self.granulite_param2_textbox.setEnabled(False)
		self.granulite_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.granulite_param2_textbox, param = "granulite_param2"))
		
		self.sandstone_param1_btn = QPushButton('Sandstone param1')
		self.sandstone_param1_textbox = QLineEdit(str(SEEL.sandstone_param1[0]))
		self.sandstone_param1_textbox.setEnabled(False)
		self.sandstone_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.sandstone_param1_textbox, param = "sandstone_param1"))
		
		self.sandstone_param2_btn = QPushButton('Sandstone param2')
		self.sandstone_param2_textbox = QLineEdit(str(SEEL.sandstone_param2[0]))
		self.sandstone_param2_textbox.setEnabled(False)
		self.sandstone_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.sandstone_param2_textbox, param = "sandstone_param2"))
		
		self.gneiss_param1_btn = QPushButton('Gneiss param1')
		self.gneiss_param1_textbox = QLineEdit(str(SEEL.gneiss_param1[0]))
		self.gneiss_param1_textbox.setEnabled(False)
		self.gneiss_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.gneiss_param1_textbox, param = "gneiss_param1"))
		
		self.gneiss_param2_btn = QPushButton('Gneiss param2')
		self.gneiss_param2_textbox = QLineEdit(str(SEEL.gneiss_param2[0]))
		self.gneiss_param2_textbox.setEnabled(False)
		self.gneiss_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.gneiss_param2_textbox, param = "gneiss_param2"))
		
		self.amphibolite_param1_btn = QPushButton('Amphibolite param1')
		self.amphibolite_param1_textbox = QLineEdit(str(SEEL.amphibolite_param1[0]))
		self.amphibolite_param1_textbox.setEnabled(False)
		self.amphibolite_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.amphibolite_param1_textbox, param = "amphibolite_param1"))
		
		self.amphibolite_param2_btn = QPushButton('Amphibolite param2')
		self.amphibolite_param2_textbox = QLineEdit(str(SEEL.amphibolite_param2[0]))
		self.amphibolite_param2_textbox.setEnabled(False)
		self.amphibolite_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.amphibolite_param2_textbox, param = "amphibolite_param2"))
		
		self.basalt_param1_btn = QPushButton('Basalt param1')
		self.basalt_param1_textbox = QLineEdit(str(SEEL.basalt_param1[0]))
		self.basalt_param1_textbox.setEnabled(False)
		self.basalt_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.basalt_param1_textbox, param = "basalt_param1"))
		
		self.basalt_param2_btn = QPushButton('Basalt param2')
		self.basalt_param2_textbox = QLineEdit(str(SEEL.basalt_param2[0]))
		self.basalt_param2_textbox.setEnabled(False)
		self.basalt_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.basalt_param2_textbox, param = "basalt_param2"))
		
		self.mud_param1_btn = QPushButton('Mudstone/Shale param1')
		self.mud_param1_textbox = QLineEdit(str(SEEL.mud_param1[0]))
		self.mud_param1_textbox.setEnabled(False)
		self.mud_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.mud_param1_textbox, param = "mud_param1"))
		
		self.mud_param2_btn = QPushButton('Mudstone/Shale param2')
		self.mud_param2_textbox = QLineEdit(str(SEEL.mud_param2[0]))
		self.mud_param2_textbox.setEnabled(False)
		self.mud_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.mud_param2_textbox, param = "mud_param2"))
		
		self.gabbro_param1_btn = QPushButton('Gabbro param1')
		self.gabbro_param1_textbox = QLineEdit(str(SEEL.gabbro_param1[0]))
		self.gabbro_param1_textbox.setEnabled(False)
		self.gabbro_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.gabbro_param1_textbox, param = "gabbro_param1"))
		
		self.gabbro_param2_btn = QPushButton('Gabbro param2')
		self.gabbro_param2_textbox = QLineEdit(str(SEEL.gabbro_param2[0]))
		self.gabbro_param2_textbox.setEnabled(False)
		self.gabbro_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.gabbro_param2_textbox, param = "gabbro_param2"))
		
		self.other_rock_param1_btn = QPushButton('Other_rock param1')
		self.other_rock_param1_textbox = QLineEdit(str(SEEL.other_rock_param1[0]))
		self.other_rock_param1_textbox.setEnabled(False)
		self.other_rock_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.other_rock_param1_textbox, param = "other_rock_param1"))
		
		self.other_rock_param2_btn = QPushButton('Other_rock param2')
		self.other_rock_param2_textbox = QLineEdit(str(SEEL.other_rock_param2[0]))
		self.other_rock_param2_textbox.setEnabled(False)
		self.other_rock_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.other_rock_param2_textbox, param = "other_rock_param2"))
		
		self.quartz_param1_btn = QPushButton('Quartz param1')
		self.quartz_param1_textbox = QLineEdit(str(SEEL.quartz_param1[0]))
		self.quartz_param1_textbox.setEnabled(False)
		self.quartz_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.quartz_param1_textbox, param = "quartz_param1"))
		
		self.quartz_param2_btn = QPushButton('Quartz param2')
		self.quartz_param2_textbox = QLineEdit(str(SEEL.quartz_param2[0]))
		self.quartz_param2_textbox.setEnabled(False)
		self.quartz_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.quartz_param2_textbox, param = "quartz_param2"))
		
		self.plag_param1_btn = QPushButton('Plagioclase param1')
		self.plag_param1_textbox = QLineEdit(str(SEEL.plag_param1[0]))
		self.plag_param1_textbox.setEnabled(False)
		self.plag_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.plag_param1_textbox, param = "plag_param1"))
		
		self.plag_param2_btn = QPushButton('Plagioclase param2')
		self.plag_param2_textbox = QLineEdit(str(SEEL.plag_param2[0]))
		self.plag_param2_textbox.setEnabled(False)
		self.plag_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.plag_param2_textbox, param = "plag_param2"))
		
		self.amp_param1_btn = QPushButton('Amphibole param1')
		self.amp_param1_textbox = QLineEdit(str(SEEL.amp_param1[0]))
		self.amp_param1_textbox.setEnabled(False)
		self.amp_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.amp_param1_textbox, param = "amp_param1"))
		
		self.amp_param2_btn = QPushButton('Amphibole param2')
		self.amp_param2_textbox = QLineEdit(str(SEEL.amp_param2[0]))
		self.amp_param2_textbox.setEnabled(False)
		self.amp_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.amp_param2_textbox, param = "amp_param2"))
		
		self.kfelds_param1_btn = QPushButton('K-Feldspar param1')
		self.kfelds_param1_textbox = QLineEdit(str(SEEL.kfelds_param1[0]))
		self.kfelds_param1_textbox.setEnabled(False)
		self.kfelds_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.kfelds_param1_textbox, param = "kfelds_param1"))
		
		self.kfelds_param2_btn = QPushButton('K-Feldspar param2')
		self.kfelds_param2_textbox = QLineEdit(str(SEEL.kfelds_param2[0]))
		self.kfelds_param2_textbox.setEnabled(False)
		self.kfelds_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.kfelds_param2_textbox, param = "kfelds_param2"))
		
		self.garnet_param1_btn = QPushButton('Garnet param1')
		self.garnet_param1_textbox = QLineEdit(str(SEEL.garnet_param1[0]))
		self.garnet_param1_textbox.setEnabled(False)
		self.garnet_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.garnet_param1_textbox, param = "garnet_param1"))
		
		self.garnet_param2_btn = QPushButton('Garnet param2')
		self.garnet_param2_textbox = QLineEdit(str(SEEL.garnet_param2[0]))
		self.garnet_param2_textbox.setEnabled(False)
		self.garnet_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.garnet_param2_textbox, param = "garnet_param2"))
				
		self.opx_param1_btn = QPushButton('Orthopyroxene param1')
		self.opx_param1_textbox = QLineEdit(str(SEEL.opx_param1[0]))
		self.opx_param1_textbox.setEnabled(False)
		self.opx_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.opx_param1_textbox, param = "opx_param1"))
		
		self.opx_param2_btn = QPushButton('Orthopyroxene param2')
		self.opx_param2_textbox = QLineEdit(str(SEEL.opx_param2[0]))
		self.opx_param2_textbox.setEnabled(False)
		self.opx_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.opx_param2_textbox, param = "opx_param2"))
		
		self.cpx_param1_btn = QPushButton('Clinopyroxene param1')
		self.cpx_param1_textbox = QLineEdit(str(SEEL.cpx_param1[0]))
		self.cpx_param1_textbox.setEnabled(False)
		self.cpx_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.cpx_param1_textbox, param = "cpx_param1"))
		
		self.cpx_param2_btn = QPushButton('Clinopyroxene param2')
		self.cpx_param2_textbox = QLineEdit(str(SEEL.cpx_param2[0]))
		self.cpx_param2_textbox.setEnabled(False)
		self.cpx_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.cpx_param2_textbox, param = "cpx_param2"))
		
		self.ol_param1_btn = QPushButton('Olivine param1')
		self.ol_param1_textbox = QLineEdit(str(SEEL.ol_param1[0]))
		self.ol_param1_textbox.setEnabled(False)
		self.ol_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.ol_param1_textbox, param = "ol_param1"))
		
		self.ol_param2_btn = QPushButton('Olivine param2')
		self.ol_param2_textbox = QLineEdit(str(SEEL.ol_param2[0]))
		self.ol_param2_textbox.setEnabled(False)
		self.ol_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.ol_param2_textbox, param = "ol_param2"))
		
		self.mica_param1_btn = QPushButton('Mica param1')
		self.mica_param1_textbox = QLineEdit(str(SEEL.mica_param1[0]))
		self.mica_param1_textbox.setEnabled(False)
		self.mica_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.mica_param1_textbox, param = "mica_param1"))
		
		self.mica_param2_btn = QPushButton('Mica param2')
		self.mica_param2_textbox = QLineEdit(str(SEEL.mica_param2[0]))
		self.mica_param2_textbox.setEnabled(False)
		self.mica_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.mica_param2_textbox, param = "mica_param2"))
				
		self.graphite_param1_btn = QPushButton('Graphite param1')
		self.graphite_param1_textbox = QLineEdit(str(SEEL.graphite_param1[0]))
		self.graphite_param1_textbox.setEnabled(False)
		self.graphite_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.graphite_param1_textbox, param = "graphite_param1"))
		
		self.graphite_param2_btn = QPushButton('Graphite param2')
		self.graphite_param2_textbox = QLineEdit(str(SEEL.graphite_param2[0]))
		self.graphite_param2_textbox.setEnabled(False)
		self.graphite_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.graphite_param2_textbox, param = "graphite_param2"))
		
		self.sulphide_param1_btn = QPushButton('Sulphide param1')
		self.sulphide_param1_textbox = QLineEdit(str(SEEL.sulphide_param1[0]))
		self.sulphide_param1_textbox.setEnabled(False)
		self.sulphide_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.sulphide_param1_textbox, param = "sulphide_param1"))
		
		self.sulphide_param2_btn = QPushButton('Sulphide param2')
		self.sulphide_param2_textbox = QLineEdit(str(SEEL.sulphide_param2[0]))
		self.sulphide_param2_textbox.setEnabled(False)
		self.sulphide_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.sulphide_param2_textbox, param = "sulphide_param2"))
		
		self.mixture_param1_btn = QPushButton('Mixture param1')
		self.mixture_param1_textbox = QLineEdit(str(SEEL.mixture_param1[0]))
		self.mixture_param1_textbox.setEnabled(False)
		self.mixture_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.mixture_param1_textbox, param = "mixture_param1"))
		
		self.mixture_param2_btn = QPushButton('Mixture param2')
		self.mixture_param2_textbox = QLineEdit(str(SEEL.mixture_param2[0]))
		self.mixture_param2_textbox.setEnabled(False)
		self.mixture_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.mixture_param2_textbox, param = "mixture_param2"))
		
		self.other_param1_btn = QPushButton('Other param1')
		self.other_param1_textbox = QLineEdit(str(SEEL.other_param1[0]))
		self.other_param1_textbox.setEnabled(False)
		self.other_param1_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.other_param1_textbox, param = "other_param1"))
		
		self.other_param2_btn = QPushButton('Other param2')
		self.other_param2_textbox = QLineEdit(str(SEEL.other_param2[0]))
		self.other_param2_textbox.setEnabled(False)
		self.other_param2_btn.clicked.connect(lambda: self.get_param(textbox_obj=self.other_param2_textbox, param = "other_param2"))
		
		layout.addWidget(desc_label,0,2)
		layout.addWidget(rocks_label,1,0)
		layout.addWidget(self.granite_param1_btn,2,0)
		layout.addWidget(self.granite_param1_textbox,2,1)
		layout.addWidget(self.granite_param2_btn,2,2)
		layout.addWidget(self.granite_param2_textbox,2,3)
		layout.addWidget(self.granulite_param1_btn,3,0)
		layout.addWidget(self.granulite_param1_textbox,3,1)
		layout.addWidget(self.granulite_param2_btn,3,2)
		layout.addWidget(self.granulite_param2_textbox,3,3)
		layout.addWidget(self.sandstone_param1_btn,4,0)
		layout.addWidget(self.sandstone_param1_textbox,4,1)
		layout.addWidget(self.sandstone_param2_btn,4,2)
		layout.addWidget(self.sandstone_param2_textbox,4,3)
		layout.addWidget(self.gneiss_param1_btn,5,0)
		layout.addWidget(self.gneiss_param1_textbox,5,1)
		layout.addWidget(self.gneiss_param2_btn,5,2)
		layout.addWidget(self.gneiss_param2_textbox,5,3)
		layout.addWidget(self.amphibolite_param1_btn,6,0)
		layout.addWidget(self.amphibolite_param1_textbox,6,1)
		layout.addWidget(self.amphibolite_param2_btn,6,2)
		layout.addWidget(self.amphibolite_param2_textbox,6,3)
		layout.addWidget(self.basalt_param1_btn,7,0)
		layout.addWidget(self.basalt_param1_textbox,7,1)
		layout.addWidget(self.basalt_param2_btn,7,2)
		layout.addWidget(self.basalt_param2_textbox,7,3)
		layout.addWidget(self.mud_param1_btn,8,0)
		layout.addWidget(self.mud_param1_textbox,8,1)
		layout.addWidget(self.mud_param2_btn,8,2)
		layout.addWidget(self.mud_param2_textbox,8,3)
		layout.addWidget(self.gabbro_param1_btn,9,0)
		layout.addWidget(self.gabbro_param1_textbox,9,1)
		layout.addWidget(self.gabbro_param2_btn,9,2)
		layout.addWidget(self.gabbro_param2_textbox,9,3)
		layout.addWidget(self.other_rock_param1_btn,10,0)
		layout.addWidget(self.other_rock_param1_textbox,10,1)
		layout.addWidget(self.other_rock_param2_btn,10,2)
		layout.addWidget(self.other_rock_param2_textbox,10,3)
		layout.addWidget(minerals_label,11,0)
		layout.addWidget(self.quartz_param1_btn,12,0)
		layout.addWidget(self.quartz_param1_textbox,12,1)
		layout.addWidget(self.quartz_param2_btn,12,2)
		layout.addWidget(self.quartz_param2_textbox,12,3)
		layout.addWidget(self.plag_param1_btn,13,0)
		layout.addWidget(self.plag_param1_textbox,13,1)
		layout.addWidget(self.plag_param2_btn,13,2)
		layout.addWidget(self.plag_param2_textbox,13,3)
		layout.addWidget(self.amp_param1_btn,14,0)
		layout.addWidget(self.amp_param1_textbox,14,1)
		layout.addWidget(self.amp_param2_btn,14,2)
		layout.addWidget(self.amp_param2_textbox,14,3)
		layout.addWidget(self.kfelds_param1_btn,15,0)
		layout.addWidget(self.kfelds_param1_textbox,15,1)
		layout.addWidget(self.kfelds_param2_btn,15,2)
		layout.addWidget(self.kfelds_param2_textbox,15,3)
		layout.addWidget(self.garnet_param1_btn,16,0)
		layout.addWidget(self.garnet_param1_textbox,16,1)
		layout.addWidget(self.garnet_param2_btn,16,2)
		layout.addWidget(self.garnet_param2_textbox,16,3)
		layout.addWidget(self.opx_param1_btn,17,0)
		layout.addWidget(self.opx_param1_textbox,17,1)
		layout.addWidget(self.opx_param2_btn,17,2)
		layout.addWidget(self.opx_param2_textbox,17,3)
		layout.addWidget(self.cpx_param1_btn,18,0)
		layout.addWidget(self.cpx_param1_textbox,18,1)
		layout.addWidget(self.cpx_param2_btn,18,2)
		layout.addWidget(self.cpx_param2_textbox,18,3)
		layout.addWidget(self.ol_param1_btn,21,0)
		layout.addWidget(self.ol_param1_textbox,21,1)
		layout.addWidget(self.ol_param2_btn,21,2)
		layout.addWidget(self.ol_param2_textbox,21,3)
		layout.addWidget(self.mica_param1_btn,22,0)
		layout.addWidget(self.mica_param1_textbox,22,1)
		layout.addWidget(self.mica_param2_btn,22,2)
		layout.addWidget(self.mica_param2_textbox,22,3)
		layout.addWidget(self.graphite_param1_btn,23,0)
		layout.addWidget(self.graphite_param1_textbox,23,1)
		layout.addWidget(self.graphite_param2_btn,23,2)
		layout.addWidget(self.graphite_param2_textbox,23,3)
		layout.addWidget(self.sulphide_param1_btn,24,0)
		layout.addWidget(self.sulphide_param1_textbox,24,1)
		layout.addWidget(self.sulphide_param2_btn,24,2)
		layout.addWidget(self.sulphide_param2_textbox,24,3)
		layout.addWidget(self.mixture_param1_btn,25,0)
		layout.addWidget(self.mixture_param1_textbox,25,1)
		layout.addWidget(self.mixture_param2_btn,25,2)
		layout.addWidget(self.mixture_param2_textbox,25,3)
		layout.addWidget(self.other_param1_btn,26,0)
		layout.addWidget(self.other_param1_textbox,26,1)
		layout.addWidget(self.other_param2_btn,26,2)
		layout.addWidget(self.other_param2_textbox,26,3)
		
	def get_param(self,textbox_obj,param):

		text, ok = QInputDialog.getText(self, 'Parameter dialogue', 'Enter the value (bigger than 0)')
		if ok:
			try:
				float(text)
				if (float(text) >= 0):

					textbox_obj.setText(str(text))
					setattr(SEEL, param, np.array([float(text)]))

				else:
					QMessageBox.about(self,"Warning!","Enter a value above 0")
			except ValueError:
				QMessageBox.about(self,"Warning!","Please enter a value that can be converted to floating number.")
				
				
		SEEL.param1_mineral_list = [SEEL.quartz_param1,SEEL.plag_param1,SEEL.amp_param1,SEEL.kfelds_param1,SEEL.opx_param1,SEEL.cpx_param1,SEEL.mica_param1,SEEL.garnet_param1,
			SEEL.sulphide_param1,SEEL.graphite_param1,SEEL.ol_param1,SEEL.mixture_param1,SEEL.other_param1]		
		SEEL.param2_mineral_list = [SEEL.quartz_param2,SEEL.plag_param2,SEEL.amp_param2,SEEL.kfelds_param2,SEEL.opx_param2,SEEL.cpx_param2,SEEL.mica_param2,SEEL.garnet_param2,
			SEEL.sulphide_param2,SEEL.graphite_param2,SEEL.ol_param2,SEEL.mixture_param2,SEEL.other_param2]
			
		SEEL.param1_rock_list = [SEEL.granite_param1, SEEL.granulite_param1, SEEL.sandstone_param1, SEEL.gneiss_param1, SEEL.amphibolite_param1,
			SEEL.basalt_param1, SEEL.mud_param1, SEEL.gabbro_param1, SEEL.other_rock_param1]
		SEEL.param2_rock_list = [SEEL.granite_param2, SEEL.granulite_param2, SEEL.sandstone_param2, SEEL.gneiss_param2, SEEL.amphibolite_param2,
			SEEL.basalt_param2, SEEL.mud_param2, SEEL.gabbro_param2, SEEL.other_rock_param2]
				
		
				
class FUG_POP(QWidget):

	def __init__(self):

		QWidget.__init__(self)

		fug_layout = QVBoxLayout(self)

		self.fug_radio_1 = QRadioButton("FMQ")
		self.fug_radio_2 = QRadioButton("IW")
		self.fug_radio_3 = QRadioButton("QIF")
		self.fug_radio_4 = QRadioButton("NNO")
		self.fug_radio_5 = QRadioButton("MMO")

		self.fug_radio_1.toggled.connect(lambda:self.btnstate_fug(self.fug_radio_1))
		self.fug_radio_2.toggled.connect(lambda:self.btnstate_fug(self.fug_radio_2))
		self.fug_radio_3.toggled.connect(lambda:self.btnstate_fug(self.fug_radio_3))
		self.fug_radio_4.toggled.connect(lambda:self.btnstate_fug(self.fug_radio_4))
		self.fug_radio_5.toggled.connect(lambda:self.btnstate_fug(self.fug_radio_5))

		if SEEL.o2_buffer == 0:
			self.fug_radio_1.setChecked(True)
		elif SEEL.o2_buffer == 1:
			self.fug_radio_2.setChecked(True)
		elif SEEL.o2_buffer == 2:
			self.fug_radio_3.setChecked(True)
		elif SEEL.o2_buffer == 3:
			self.fug_radio_4.setChecked(True)
		elif SEEL.o2_buffer == 4:
			self.fug_radio_5.setChecked(True)

		fug_layout.addWidget(self.fug_radio_1)
		fug_layout.addWidget(self.fug_radio_2)
		fug_layout.addWidget(self.fug_radio_3)
		fug_layout.addWidget(self.fug_radio_4)
		fug_layout.addWidget(self.fug_radio_5)

	def btnstate_fug(self,b):

		if b.text() == "FMQ":
			if b.isChecked() == True:
				SEEL.o2_buffer = 0
		elif b.text() == "IW":
			if b.isChecked() == True:
				SEEL.o2_buffer = 1
		elif b.text() == "QIF":
			if b.isChecked() == True:
				SEEL.o2_buffer = 2
		elif b.text() == "NNO":
			if b.isChecked() == True:
				SEEL.o2_buffer = 3
		elif b.text() == "MMO":
			if b.isChecked() == True:
				SEEL.o2_buffer = 4
				
class WATER_CALIB_POP(QWidget):

	def __init__(self):
		
		QWidget.__init__(self)
		

		calib_layout = QGridLayout(self)
		
		bg_ol = QButtonGroup(self)
		
		label_ol_calib = QLabel(self)
		label_ol_calib.setText('--------Olivine Calibration--------')
		label_ol_calib.setStyleSheet("QLabel {font:bold};min-width: 10em; fontsize: 10pt;color: red")
		calib_layout.addWidget(label_ol_calib,1,0)

		self.calib_radio_ol_0 = QRadioButton("Default")
		self.calib_radio_ol_1 = QRadioButton("Withers2012")
		self.calib_radio_ol_2 = QRadioButton("Bell2003")
		self.calib_radio_ol_3 = QRadioButton("Paterson1980")

		self.calib_radio_ol_0.toggled.connect(lambda:self.btnstate_ol_calib(self.calib_radio_ol_0))
		self.calib_radio_ol_1.toggled.connect(lambda:self.btnstate_ol_calib(self.calib_radio_ol_1))
		self.calib_radio_ol_2.toggled.connect(lambda:self.btnstate_ol_calib(self.calib_radio_ol_2))
		self.calib_radio_ol_3.toggled.connect(lambda:self.btnstate_ol_calib(self.calib_radio_ol_3))

		if SEEL.ol_calib == 0:
			self.calib_radio_ol_1.setChecked(True)
		elif SEEL.ol_calib == 1:
			self.calib_radio_ol_2.setChecked(True)
		elif SEEL.ol_calib == 2:
			self.calib_radio_ol_3.setChecked(True)
		elif SEEL.ol_calib == 3:
			self.calib_radio_ol_0.setChecked(True)

		bg_ol.addButton(self.calib_radio_ol_0)
		bg_ol.addButton(self.calib_radio_ol_1)
		bg_ol.addButton(self.calib_radio_ol_2)
		bg_ol.addButton(self.calib_radio_ol_3)
		
		calib_layout.addWidget(self.calib_radio_ol_0,2,0)
		calib_layout.addWidget(self.calib_radio_ol_1,2,1)
		calib_layout.addWidget(self.calib_radio_ol_2,2,2)
		calib_layout.addWidget(self.calib_radio_ol_3,2,3)
		################################3
		
		bg_px_gt = QButtonGroup(self)
		label_px_gt_calib = QLabel(self)
		label_px_gt_calib.setText('--------Pyroxenes/Garnet Calibration--------')
		label_px_gt_calib.setStyleSheet("QLabel {font:bold};min-width: 10em; fontsize: 10pt;color: red")
		calib_layout.addWidget(label_px_gt_calib,4,0)

		self.calib_radio_px_gt_0 = QRadioButton("Default")
		self.calib_radio_px_gt_1 = QRadioButton("Bell1995")
		self.calib_radio_px_gt_2 = QRadioButton("Paterson1980")

		self.calib_radio_px_gt_0.toggled.connect(lambda:self.btnstate_px_gt_calib(self.calib_radio_px_gt_0))
		self.calib_radio_px_gt_1.toggled.connect(lambda:self.btnstate_px_gt_calib(self.calib_radio_px_gt_1))
		self.calib_radio_px_gt_2.toggled.connect(lambda:self.btnstate_px_gt_calib(self.calib_radio_px_gt_2))

		if SEEL.px_gt_calib == 0:
			self.calib_radio_px_gt_1.setChecked(True)
		elif SEEL.px_gt_calib == 1:
			self.calib_radio_px_gt_2.setChecked(True)
		elif SEEL.px_gt_calib == 2:
			self.calib_radio_px_gt_0.setChecked(True)

		bg_px_gt.addButton(self.calib_radio_px_gt_0)
		bg_px_gt.addButton(self.calib_radio_px_gt_1)
		bg_px_gt.addButton(self.calib_radio_px_gt_2)

		calib_layout.addWidget(self.calib_radio_px_gt_0,5,0)
		calib_layout.addWidget(self.calib_radio_px_gt_1,5,1)
		calib_layout.addWidget(self.calib_radio_px_gt_2,5,2)
		
		################################3
		
		bg_feldspar = QButtonGroup(self)
		label_feldspar_calib = QLabel(self)
		label_feldspar_calib.setText('--------Feldspar Calibration--------')
		label_feldspar_calib.setStyleSheet("QLabel {font:bold};min-width: 10em; fontsize: 10pt;color: red")
		calib_layout.addWidget(label_feldspar_calib,6,0)

		self.calib_radio_feldspar_0 = QRadioButton("Default")
		self.calib_radio_feldspar_1 = QRadioButton("Johnson2003")
		self.calib_radio_feldspar_2 = QRadioButton("Mosenfelder2015")

		self.calib_radio_feldspar_0.toggled.connect(lambda:self.btnstate_feldspar_calib(self.calib_radio_feldspar_0))
		self.calib_radio_feldspar_1.toggled.connect(lambda:self.btnstate_feldspar_calib(self.calib_radio_feldspar_1))
		self.calib_radio_feldspar_2.toggled.connect(lambda:self.btnstate_feldspar_calib(self.calib_radio_feldspar_2))

		if SEEL.feldspar_calib == 0:
			self.calib_radio_feldspar_1.setChecked(True)
		elif SEEL.feldspar_calib == 1:
			self.calib_radio_feldspar_2.setChecked(True)
		elif SEEL.feldspar_calib == 2:
			self.calib_radio_feldspar_0.setChecked(True)

		bg_feldspar.addButton(self.calib_radio_feldspar_0)
		bg_feldspar.addButton(self.calib_radio_feldspar_1)
		bg_feldspar.addButton(self.calib_radio_feldspar_2)

		calib_layout.addWidget(self.calib_radio_feldspar_0,7,0)
		calib_layout.addWidget(self.calib_radio_feldspar_1,7,1)
		calib_layout.addWidget(self.calib_radio_feldspar_2,7,2)

		self.calib_info_btn = QPushButton('Info')
		self.calib_info_btn.clicked.connect(self.calib_info_box)

		calib_layout.addWidget(self.calib_info_btn,8,0)
		
	def btnstate_ol_calib(self,b):

		if b.text() == "Withers2012":
			if b.isChecked() == True:
				SEEL.ol_calib = 0
		elif b.text() == "Bell2003":
			if b.isChecked() == True:
				SEEL.ol_calib = 1
		elif b.text() == "Paterson1980":
			if b.isChecked() == True:
				SEEL.ol_calib = 2
		elif b.text() == "Default":
			if b.isChecked() == True:
				SEEL.ol_calib = 3
				
	def btnstate_px_gt_calib(self,b):

		if b.text() == "Bell1995":
			if b.isChecked() == True:
				SEEL.px_gt_calib = 0
		elif b.text() == "Paterson1980":
			if b.isChecked() == True:
				SEEL.px_gt_calib = 1
		elif b.text() == "Default":
			if b.isChecked() == True:
				SEEL.px_gt_calib = 2
				
	def btnstate_feldspar_calib(self,b):

		if b.text() == "Johnson2003":
			if b.isChecked() == True:
				SEEL.feldspar_calib = 0
		elif b.text() == "Mosenfelder2015":
			if b.isChecked() == True:
				SEEL.feldspar_calib = 1
		elif b.text() == "Default":
			if b.isChecked() == True:
				SEEL.feldspar_calib = 2
				
	def calib_info_box(self):

		QMessageBox.about(self, "Info on this", "This preferential settings relates to the selection of fixes related to water-calibrations."+
		" Calibration method selected here affects the water-uptake of conductivity models solubility models.")
		
def main():

	app = QApplication(sys.argv)
	GUI = SEEL()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()