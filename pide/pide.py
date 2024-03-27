#!/usr/bin/env python3

import os

core_path_ext = os.path.join(os.path.dirname(os.path.abspath(__file__)) , 'pide_src')

import sys, csv, warnings, json
import numpy as np
from scipy.interpolate import interp1d

#imports from satex
from satex import Isotropy

#Importing external functions

sys.path.append(core_path_ext)

#importing odd melt/fluid functions
from pide_src.cond_models.melt_odd import * 
from pide_src.cond_models.fluids_odd import * 
#importing odd rock functions
from pide_src.cond_models.rocks.granite_odd import * 
from pide_src.cond_models.rocks.granulite_odd import *
from pide_src.cond_models.rocks.sandstone_odd import *
from pide_src.cond_models.rocks.gneiss_odd import *
from pide_src.cond_models.rocks.amphibolite_odd import *
from pide_src.cond_models.rocks.basalt_odd import *
from pide_src.cond_models.rocks.mud_odd import *
from pide_src.cond_models.rocks.gabbro_odd import *
from pide_src.cond_models.rocks.other_rocks_odd import *
#importing odd mineral functions
from pide_src.cond_models.minerals.quartz_odd import *
from pide_src.cond_models.minerals.plag_odd import *
from pide_src.cond_models.minerals.amp_odd import *
from pide_src.cond_models.minerals.kfelds_odd import *
from pide_src.cond_models.minerals.opx_odd import *
from pide_src.cond_models.minerals.cpx_odd import *
from pide_src.cond_models.minerals.mica_odd import *
from pide_src.cond_models.minerals.garnet_odd import *
from pide_src.cond_models.minerals.ol_odd import *
from pide_src.cond_models.minerals.mixtures_odd import *
from pide_src.cond_models.minerals.rwd_wds_odd import *
from pide_src.cond_models.minerals.other_odd import *
#importing water-partitioning odd functions
from pide_src.water_partitioning.water_part_odd import *
#importing mineral solubility functions
from pide_src.water_sol.ol_sol import *
from pide_src.water_sol.opx_sol import * 
from pide_src.water_sol.rwd_wds_sol import *
#importing eos functions
from pide_src.eos.fluid_eos import *
#importing mineral stability functions
from pide_src.min_stab.min_stab import *
#importing utils
from utils.utils import *


warnings.filterwarnings("ignore", category=RuntimeWarning) #ignoring many RuntimeWarning printouts that are useless

#version 0.1, June. 2023.
#pide - (P)etrophysical (I)nterpretation tools for geo(D)ynamic (E)xploration
#initially developed by Sinan Ozaydin (University of Sydney, School of Geosciences
#sciences, Sydney, Australia).

#indentation method: hard tabs ('\t')

#works with Python3
#required libraries: numpy, scipy
#optional libraries: matplotlib,h5py,harmonica

class pide(object):
	
	def __init__(self, core_path = core_path_ext):
	
		"""
		This is the core object to create to use the functions of pide.
		
		---------------------------------- -----------------------------------------
		Methods                             Description
		---------------------------------- -------------------------------------------
		set_temperature                     Function to set temperature. When making
											a calculation, it is best to set the 
											temperature first, since all the other
											parameters are adjusted to the length
											of the temperature array, if they do
											not match in length.
											Unit: Kelvin
											
		set_pressure                        Function to set pressure.
											Unit: GPa

		set_parameter                       Function to set any parameter. Some cal-
											culations might ask you for certain para-
											meters. In this case, you might want to
											use this function to set these parameters.

											Inputs:
											param_name - str value for param name
											value - value of the parameter, in array
											or scalar. If scalar is entered it will
											sync up with the length of the T array.
																					
		
		set_composition_solid_mineral       Function to set the modal composition
											of a mineral assemblage. 
											Unit: Fraction (0 to 1)
		set_composition_solid_rock          Function to set the composition of a
											rock mixture.
											Unit: Fraction (0 to 1)
		
		
		set_watercalib                      Function to set water corrections
											due to the choice of water measurement
											calibration. Integer.
											
											Olivine:
											0:Withers2012
											1:Bell2003
											2:Paterson1980
											3:Default choice of the conductivity model
											
											Pyroxenes and Garnet:
											0:Bell1995
											1:Paterson1980
											2:Default hoice of the conductivity model
											
											Feldspars (Plagioclase and K-Feldspar)
											0:Johnson2003
											1:Mosenfelder2015
											2:Default hoice of the conductivity model
											
		set_o2_buffer                       Function to set oxygen fugacity buffer.
											
											0: FMQ
											1: IW: Hirsch (1991)
											2: QIF
											3: NNO: Li et al. (1998)
											4: MMO: Xu et al. (2000)
											
		get_mineral_index                   Function to get the index of the mineral in
											mineral lists used in conductivity calulcation
											methods.
											
											Input: mineral name
											ol,opx,cpx,garnet,quartz,plag,amp,kfelds,mica,
											graphite,sulphide,mixture,other
											
											Returns: mineral index
											
		get_rock_index                      Function to get the index of the mineral in
											mineral lists.
											Input: rock name
											granite,granulite,sandstone,gneiss,amphibolite,
											basalt,mud(mudstone/shale),gabbro,other_rock
											
											Returns: rock index
		
		list_mineral_econd_models           Functions that lists the available electrical
											conductivity models for the given mineral index.
											
											Input: mineral name
											ol,opx,cpx,garnet,quartz,plag,amp,kfelds,mica,
											graphite,sulphide,mixture,other
											
											Prints and returns: list of electrical conductivity
											models for the chosen mineral.
											
		list_rock_econd_models              Functions that lists the available electrical
											conductivity models for the given rock index.
											
											Input: rock name
											granite,granulite,sandstone,gneiss,amphibolite,
											basalt,mud(mudstone/shale),gabbro,other_rock
											
											Prints and returns: list of electrical conductivity
											models for the chosen rock.
											
		list_melt_econd_models              Functions that lists the available electrical
											conductivity models for melts.
											
											Prints and returns: list of electrical conductivity
											models for the melt.
											
		list_fluid_econd_models             Functions that lists the available electrical
											conductivity models for fluids.
											
											Prints and returns: list of electrical conductivity
											models for the fluid.
											
		set_melt_fluid_conductivity_choice  Function to set the electrical conductivity choice
											for melts.
		
											Input: model index for,
											melt,fluid
											
		set_mineral_conductivity_choice     Function to set the electrical conductivity choice
											for minerals.
											
											Input: model index for,
											ol,opx,cpx,garnet,quartz,plag,amp,kfelds,mica,
											graphite,sulphide,mixture,other
											
		set_rock_conductivity_choice        Function to set the electrical conductivity choice
											for minerals.
											
											Input: model index for,
											granite,granulite,sandstone,gneiss,amphibolite,
											basalt,mud(mudstone/shale),gabbro,other_rock
											
		set_mineral_water                   Function to set the water content for minerals.
		
											Input:
											ol,opx,cpx,garnet,quartz,plag,amp,kfelds,mica,
											graphite,sulphide,mixture,other
											
		set_rock_water                      Function to set the water content for minerals.
		
											Input:
											granite,granulite,sandstone,gneiss,amphibolite,
											basalt,mud(mudstone/shale),gabbro,other_rock
											
		set_param1_mineral                  Function to set the param1 for minerals. These 
											denote to specific parameters that is required
											by the chosen electrical conductivity model.
											These parameters are indicated in the csv files
											with _param1_X
											
											Input:
											ol,opx,cpx,garnet,quartz,plag,amp,kfelds,mica,
											graphite,sulphide,mixture,other
											Unit: Varies
											
											
		set_param1_rock                     Function to set the param1 for rocks. These 
											denote to specific parameters that is required
											by the chosen electrical conductivity model.
											These parameters are indicated in the csv files
											with _param1_X
											
											Input:
											granite,granulite,sandstone,gneiss,amphibolite,
											basalt,mud(mudstone/shale),gabbro,other_rock
											Unit: Varies
																						
		set_melt_fluid_frac                 Function to set melt/fluid mass fraction
		
											Input:
											'melt', 'fluid'
											Unit:Fraction (0 to 1)
											
										
		set_melt_or_fluid_mode              Function to define if you are going to use
											melt or fluid in the matrix.
											
											Input:
											'melt', 'fluid'
											
		set_melt_properties                 Function to set some of the properties of the melt.
		
											Input:
											'co2' - in ppm
											'water' - in ppm
											'na2o' - in wt%
											'k2o' - in wt%
											
		set_fluid_properties                Function to set some of the properties of the fluid.
		
											Input:
											'salinity' - in wt%
											
													
		set_solid_phase_method              Function to set whether to mix minerals or rocks in
											the solid phases. The two cannot be intermixed.
											
											Input:
											'mineral','rock'
											
												
		set_phase_interconnectivities       Function to set interconnectivities via the cementation
											exponent included in The Generalized Archie's Law
											or Modified Archie's Law.
											
											Input:
											ol,opx,cpx,garnet,quartz,plag,amp,kfelds,mica,
											graphite,sulphide,mixture,other,granite,granulite,sandstone,gneiss,amphibolite,
											basalt,mud(mudstone/shale),gabbro,other_rock,fluid,melt
											
											Unit: Float bigger than 1
											
		set_solid_phs_mix_method           Function to set solid phases mixing function.
		
											Input:
											Index number denoting to the chosen phases mixing function
											Unit: Integer
											
		set_solid_melt_fluid_mix_method     Function to set solid-fluid phases mixing function.
		
											Input:
											Index number denoting to the chosen phases mixing function
											Unit: Integer

		set_mantle_water_solubility         Function to set mantle water solubility of minerals.

											Input:
											ol, opx, cpx, garnet, rwd_wds, perov
											in index values corresponding to the given solubility model.
																						
											Example:
											set_mantle_water_solubility(ol=0)

											To get the mantle water solubility models for minerals use method:

											list_mantle_water_solubility

											
		list_phs_mix_methods                Function to get a list of phase mixing functions for solid
											phases.
											
											Returns and prints:
											List of strings related to phase mixing functions
											
									
		list_phs_melt_fluid_mix_methods     Function to get a list of solid-fluid phase mixing
											functions
											
											Returns and prints:
											List of strings related to solid-fluid phase mixing functions		
											
		calculate_arrhenian_single          Function to calculate a simple arrhenian function in form:
		
											cond = sigma * water**r * exp(-(E + (alpha*water)**1/3) / RT)
											
											Input: 
											T - temperature in Kelvin
											sigma - preexponential term in log10(S/m)
											E - activation enthalpy in J/mol
											r - water exponent (unitless)
											alpha - water activation enthalpy modifier in J/mol
											water - water content of the phase in ppm
											
											Returns:
											Conductivity in S/m
											
		calculate_fluids_conductivity       Function to calculate conductivity of fluids.
		
											Input:
											method - 'array','index'
											this entry denotes to whether calculation will be made
											with an array or a single value (index)
											
											Returns:
											Conductivity in S/m
											
		calculate_melt_conductivity         Function to calculate conductivity of melts.
		
											Input:
											method - 'array','index'
											this entry denotes to whether calculation will be made
											with an array or a single value (index)
											
											Returns:
											Conductivity in S/m
											
		calculate_mineral_conductivity      Function to calculate conductivity of minerals.
		
											Input:
											method - 'array','index'
											this entry denotes to whether calculation will be made
											with an array or a single value (index)
											
											min_idx - Index denotes to the mineral chosen. in Integer
											
											Returns:
											Conductivity in S/m
											
		calculate_rock_conductivity         Function to calculate conductivity of rocks.
		
											Input:
											method - 'array','index'
											this entry denotes to whether calculation will be made
											with an array or a single value (index)
											
											rock_idx - Index denotes to the rock chosen. in Integer
											
											Returns:
											Conductivity in S/m
											
		calculate_conductivity              Function to calculate bulk conductivity of the arraged medium.
		
		
											Input:
											method - 'array','index'
											this entry denotes to whether calculation will be made
											with an array or a single value (index)
											
											Returns:
											Conductivity in S/m
											
		"""

		self.core_path = core_path
				
		self.form_object()
		
	def form_object(self):
		
		#Setting up initial variables.

		pide.loaded_file = False
		self.cond_calculated = False
		self.temperature_default = False
		self.density_loaded = False
		self.seis_property_overwrite = [False] * 16
		
		self.read_cond_models()
		self.read_params()
		self.read_water_part()
		self.read_mineral_water_solubility()
		self.object_formed = False
		#setting up default values for the pide object
		self.set_temperature(np.ones(1) * 900.0) #in Kelvin
		self.set_pressure(np.ones(1) * 1.0) #in GPa
		self.set_composition_solid_mineral(overlookError = True)
		self.set_composition_solid_rock(overlookError = True)
		self.set_mineral_conductivity_choice()
		self.set_rock_conductivity_choice()
		self.set_mineral_water()
		self.set_bulk_water(0.0)
		self.set_alopx(0)
		self.set_rock_water()
		self.set_watercalib()
		self.set_o2_buffer()
		self.set_xfe_mineral()
		self.set_param1_mineral()
		self.set_param1_rock()
		self.set_melt_or_fluid_mode(mode = 'melt') #default choice is melt - 1
		self.set_solid_phase_method(mode = 'mineral') #default choice is mineral - 2
		self.set_solid_phs_mix_method(method = 0)
		self.set_solid_melt_fluid_mix_method(method = 0)
		self.set_melt_fluid_conductivity_choice()
		self.set_melt_fluid_frac(0)
		self.set_melt_properties()
		self.set_fluid_properties()
		self.set_phase_interconnectivities()
		self.set_melt_fluid_interconnectivity()
		self.set_mantle_water_partitions()
		self.set_mantle_water_solubility()
		self.object_formed = True

		#Some check for temperature being the controlling array errors.
		self.temperature_default = True
		
	def revalue_arrays(self):
		
		#revaluing the arrays with the length of the T if needed by the user.
		
		#arrays with single values
		self.set_temperature(self.T) #in Kelvin
		self.set_pressure(self.p) #in GPa
		self.set_bulk_water(self.bulk_water)
		self.set_alopx(self.al_opx)
		self.set_melt_fluid_frac(self.melt_fluid_mass_frac)
		
		#arrays with mineral specific arrays
		if pide.solid_phase_method == 2:
			self.set_composition_solid_mineral(reval = True,overlookError = True)
			self.set_mineral_water(reval = True)
			self.set_xfe_mineral(reval = True)
			self.set_param1_mineral(reval = True)
			
		elif pide.solid_phase_method == 1:
			self.set_composition_solid_rock(reval = True,overlookError = True)
			self.set_rock_water(reval = True)
			self.set_param1_rock(reval = True)
			
		self.set_phase_interconnectivities(reval = True)
		if self.phs_melt_mix_method == 0:
			self.set_melt_fluid_interconnectivity(reval = True)
		
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
		self.spinel_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'spinel.csv'),delim = ',')
		self.rwd_wds_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'ringwoodite_wadsleyite.csv'),delim = ',')
		self.perovskite_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'perovskite.csv'),delim = ',')
		self.mixture_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'mixtures.csv'),delim = ',')
		self.other_cond_data = self.read_csv(os.path.join(self.core_path, 'cond_models' , 'minerals', 'other.csv'),delim = ',')
		
		self.cond_data_array = [self.fluid_cond_data, self.melt_cond_data, self.granite_cond_data, self.granulite_cond_data,
			  self.sandstone_cond_data, self.gneiss_cond_data, self.amphibolite_cond_data, self.basalt_cond_data, self.mud_cond_data,
			   self.gabbro_cond_data, self.other_rock_cond_data, self.quartz_cond_data, self.plag_cond_data,
			  self.amp_cond_data, self.kfelds_cond_data, self.opx_cond_data, self.cpx_cond_data, self.mica_cond_data,
			  self.garnet_cond_data, self.sulphides_cond_data, self.graphite_cond_data, self.ol_cond_data, self.spinel_cond_data, 
			  self.rwd_wds_cond_data, self.perovskite_cond_data, self.mixture_cond_data, self.other_cond_data]
			  
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
		len_sp = len(self.spinel_cond_data) - 1
		len_rwd_wds = len(self.rwd_wds_cond_data) - 1
		len_perov = len(self.perovskite_cond_data) - 1
		len_mixture = len(self.mixture_cond_data) - 1
		len_other = len(self.other_cond_data) - 1
		
		self.mineral_num = 16
		
		def create_nan_array():
		
			array = [[None] * len_fluid, [None] * len_melt, [None] * len_granite, [None] * len_granulite, [None] * len_sandstone, [None] * len_gneiss,
			[None] * len_amphibolite, [None] * len_basalt, [None] * len_mud, [None] * len_gabbro, [None] * len_other_rock, [None] * len_quartz,
			[None] * len_plag, [None] * len_amp, [None] * len_kfelds, [None] * len_opx, [None] * len_cpx, [None] * len_mica,
			[None] * len_garnet, [None] * len_sulphides, [None] * len_graphite, [None] * len_ol, [None] * len_sp, [None] * len_rwd_wds, 
			[None] * len_perov, [None] * len_mixture, [None] * len_other]
			
			return array

		#Creating empty arrays for appending new data.
		pide.name = create_nan_array()
		pide.type = create_nan_array()
		pide.t_min = create_nan_array()
		pide.t_max = create_nan_array()
		self.p_min = create_nan_array()
		self.p_max = create_nan_array()
		self.w_calib = create_nan_array()
		self.mg_cond = create_nan_array()
		self.sigma_i =  create_nan_array()
		self.sigma_i_err =  create_nan_array()
		self.h_i =  create_nan_array()
		self.h_i_err =  create_nan_array()
		self.sigma_pol = create_nan_array()
		self.sigma_pol_err = create_nan_array()
		self.h_pol = create_nan_array()
		self.h_pol_err = create_nan_array()
		self.sigma_p = create_nan_array()
		self.sigma_p_err = create_nan_array()
		self.h_p = create_nan_array()
		self.h_p_err = create_nan_array()
		self.r = create_nan_array()
		self.r_err = create_nan_array()
		self.alpha_p = create_nan_array()
		self.alpha_p_err = create_nan_array()
		self.wtype = create_nan_array()
		self.dens_mat = create_nan_array()
		self.mat_ref = create_nan_array()
		
		#Filling up the arrays.
		for i in range(0,len(pide.type)):
			count = 1
			
			for j in range(0,len(pide.type[i])):

				pide.name[i][count-1] = self.cond_data_array[i][count][0]
				pide.type[i][count-1] = self.cond_data_array[i][count][1]
				pide.t_min[i][count-1] = float(self.cond_data_array[i][count][2])
				pide.t_max[i][count-1] = float(self.cond_data_array[i][count][3])
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
				try:
					self.dens_mat[i][count-1] = float(self.cond_data_array[i][count][25])
				except ValueError:
					self.dens_mat[i][count-1] = self.cond_data_array[i][count][25]
				self.mat_ref[i][count-1] = self.cond_data_array[i][count][26]
				count += 1

	def read_params(self):

		#READING THE PARAMETERS IN PARAMS.CSV WHICH ARE GENERAL PHYSICAL CONSTANTS
		#AND PROPERTIES OF MATERIALS

		params_dat = self.read_csv(os.path.join(self.core_path, 'params.csv'), delim = ',')

		self.g = float(params_dat[0][1]) # in kg/
		self.R = float(params_dat[1][1]) # in JK-1 mol-1
		self.avog = float(params_dat[2][1]) 
		self.boltz = float(params_dat[3][1])
		self.el_q = float(params_dat[4][1])
		pide.spreadsheet = str(params_dat[5][1])
		self.mu = 4.0 * np.pi * 10**(-7)
		
		#materials.json from satex
		json_file = 'materials.json'
		json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pide_src', json_file)
		with open(json_path, 'r') as f:
			self.materials_data = json.load(f)
					
	def read_water_part(self):
	
		self.ol_min_partitioning_list = ['opx_part.csv','cpx_part.csv','gt_part.csv']
		self.ol_min_part_index = [15,16,18] #mineral indexes for the file read
		self.melt_partitioning_list = ['opx_melt_part.csv','cpx_melt_part.csv','gt_melt_part.csv', 'ol_melt_part.csv']
		self.melt_min_part_index = [15,16,18,21] #mineral indexes for the file read
		self.rwd_wds_min_partitioning_list = ['maj_part.csv', 'cpx_tz_part.csv', 'perov_part.csv']
		self.rwd_wds_min_part_index = [18, 16, 24]
		
		self.water_ol_part_name = []
		self.water_ol_part_type = []
		self.water_ol_part_function = []
		self.water_ol_part_pchange = []
		
		index_read = 0
		for i in range(11,26):
		
			if (i in self.ol_min_part_index) == True:
				data = self.read_csv(os.path.join(self.core_path, 'water_partitioning', self.ol_min_partitioning_list[index_read]), delim = ',')
				index_read = index_read + 1
				data_name = []
				data_type = []
				data_function_1 = []
				data_pchange = []

				for j in range(1,len(data)):
					data_name.append(data[j][0])
					data_type.append(int(data[j][1]))
					data_function_1.append(float(data[j][2]))
					data_pchange.append(float(data[j][3]))
					
				self.water_ol_part_name.append(data_name)
				self.water_ol_part_type.append(data_type)
				self.water_ol_part_function.append(data_function_1)
				self.water_ol_part_pchange.append(data_pchange)
				
			else:
			
				self.water_ol_part_name.append(None)
				self.water_ol_part_type.append(None)
				self.water_ol_part_function.append(None)
				self.water_ol_part_pchange.append(None)
						
		self.water_melt_part_name = []
		self.water_melt_part_type = []
		self.water_melt_part_function = []
		self.water_melt_part_pchange = []
		
		index_read = 0
		for i in range(11,26):
		
			if (i in self.melt_min_part_index) == True:
				data = self.read_csv(os.path.join(self.core_path, 'water_partitioning', self.melt_partitioning_list[index_read]), delim = ',')
				index_read = index_read + 1
				data_name = []
				data_type = []
				data_function_1 = []
				data_pchange = []

				for j in range(1,len(data)):
					data_name.append(data[j][0])
					data_type.append(int(data[j][1]))
					data_function_1.append(float(data[j][2]))
					data_pchange.append(float(data[j][3]))
					
				self.water_melt_part_name.append(data_name)
				self.water_melt_part_type.append(data_type)
				self.water_melt_part_function.append(data_function_1)
				self.water_melt_part_pchange.append(data_pchange)
				
			else:
			
				self.water_melt_part_name.append(None)
				self.water_melt_part_type.append(None)
				self.water_melt_part_function.append(None)
				self.water_melt_part_pchange.append(None)
				
		self.water_rwd_wds_part_name = []
		self.water_rwd_wds_part_type = []
		self.water_rwd_wds_part_function = []
		self.water_rwd_wds_part_pchange = []
		
		index_read = 0
		for i in range(11,26):
		
			if (i in self.rwd_wds_min_part_index) == True:
				data = self.read_csv(os.path.join(self.core_path, 'water_partitioning', self.rwd_wds_min_partitioning_list[index_read]), delim = ',')
				index_read = index_read + 1
				data_name = []
				data_type = []
				data_function_1 = []
				data_pchange = []

				for j in range(1,len(data)):
					data_name.append(data[j][0])
					data_type.append(int(data[j][1]))
					data_function_1.append(float(data[j][2]))
					data_pchange.append(float(data[j][3]))
					
				self.water_rwd_wds_part_name.append(data_name)
				self.water_rwd_wds_part_type.append(data_type)
				self.water_rwd_wds_part_function.append(data_function_1)
				self.water_rwd_wds_part_pchange.append(data_pchange)
				
			else:
			
				self.water_rwd_wds_part_name.append(None)
				self.water_rwd_wds_part_type.append(None)
				self.water_rwd_wds_part_function.append(None)
				self.water_rwd_wds_part_pchange.append(None)
			
	def read_mineral_water_solubility(self):
	
		self.mineral_sol_file_list = ['opx_sol.csv','cpx_sol.csv','garnet_sol.csv','ol_sol.csv','rwd_wds_sol.csv','perov_sol.csv']
		self.mineral_sol_index = [15,16,18,21,23,24] #mineral indexes for the file read
		
		self.mineral_sol_name = []
		self.mineral_sol_fug = []
		self.mineral_sol_o2_fug = []
		self.mineral_sol_calib = []
		
		index_read = 0
		for i in range(11,26):
		
			if (i in self.mineral_sol_index) == True:
				data = self.read_csv(os.path.join(self.core_path, 'water_sol', self.mineral_sol_file_list[index_read]), delim = ',')
				index_read = index_read + 1
				sol_name = []
				sol_fug = []
				sol_o2_fug = []
				sol_calib = []

				for j in range(1,len(data)):
					sol_name.append(data[j][0])
					sol_fug.append(str(data[j][1]))
					sol_o2_fug.append(str(data[j][2]))
					sol_calib.append(int(data[j][3]))
					
				self.mineral_sol_name.append(sol_name)
				self.mineral_sol_fug.append(sol_fug)
				self.mineral_sol_o2_fug.append(sol_o2_fug)
				self.mineral_sol_calib.append(sol_calib)
				
			else:
			
				self.mineral_sol_name.append(None)
				self.mineral_sol_fug.append(None)
				self.mineral_sol_o2_fug.append(None)
				self.mineral_sol_calib.append(None)
				
	def set_parameter(self, param_name, value):
		
		setattr(self, param_name, self.array_modifier(input = value, array=self.T,varname = param_name))
	
	def set_composition_solid_mineral(self, reval = False, **kwargs):
			
		if self.temperature_default == True:
			self.suggestion_temp_array()
		
		if reval == False:
			self.ol_frac = self.array_modifier(input = kwargs.pop('ol', 0), array = self.T, varname = 'ol_frac')
			self.opx_frac = self.array_modifier(input = kwargs.pop('opx', 0), array = self.T, varname = 'opx_frac')
			self.cpx_frac = self.array_modifier(input = kwargs.pop('cpx', 0), array = self.T, varname = 'cpx_frac')
			self.garnet_frac = self.array_modifier(input = kwargs.pop('garnet', 0), array = self.T, varname = 'garnet_frac')
			self.mica_frac = self.array_modifier(input = kwargs.pop('mica', 0), array = self.T, varname = 'mica_frac')
			self.amp_frac = self.array_modifier(input = kwargs.pop('amp', 0), array = self.T, varname = 'amp_frac')
			self.quartz_frac = self.array_modifier(input = kwargs.pop('quartz', 0), array = self.T, varname = 'quartz_frac')
			self.plag_frac = self.array_modifier(input = kwargs.pop('plag', 0), array = self.T, varname = 'plag_frac')
			self.kfelds_frac = self.array_modifier(input = kwargs.pop('kfelds', 0), array = self.T, varname = 'kfelds_frac')
			self.sulphide_frac = self.array_modifier(input = kwargs.pop('sulphide', 0), array = self.T, varname = 'sulphide_frac')
			self.graphite_frac = self.array_modifier(input = kwargs.pop('graphite', 0), array = self.T, varname = 'graphite_frac')
			self.mixture_frac = self.array_modifier(input = kwargs.pop('mixture', 0), array = self.T, varname = 'mixture_frac')
			self.sp_frac = self.array_modifier(input = kwargs.pop('sp', 0), array = self.T, varname = 'sp_frac')
			self.rwd_wds_frac = self.array_modifier(input = kwargs.pop('rwd_wds', 0), array = self.T, varname = 'rwd_wds_frac')
			self.perov_frac = self.array_modifier(input = kwargs.pop('perov', 0), array = self.T, varname = 'perov_frac')
			self.other_frac = self.array_modifier(input = kwargs.pop('other', 0), array = self.T, varname = 'other_frac')
		elif reval == True:
			self.ol_frac = self.array_modifier(input = self.ol_frac, array = self.T, varname = 'ol_frac')
			self.opx_frac = self.array_modifier(input = self.opx_frac, array = self.T, varname = 'opx_frac')
			self.cpx_frac = self.array_modifier(input = self.cpx_frac, array = self.T, varname = 'cpx_frac')
			self.garnet_frac = self.array_modifier(input = self.garnet_frac, array = self.T, varname = 'garnet_frac')
			self.mica_frac = self.array_modifier(input = self.mica_frac, array = self.T, varname = 'mica_frac')
			self.amp_frac = self.array_modifier(input = self.amp_frac, array = self.T, varname = 'amp_frac')
			self.quartz_frac = self.array_modifier(input = self.quartz_frac, array = self.T, varname = 'quartz_frac')
			self.plag_frac = self.array_modifier(input = self.plag_frac, array = self.T, varname = 'plag_frac')
			self.kfelds_frac = self.array_modifier(input = self.kfelds_frac, array = self.T, varname = 'kfelds_frac')
			self.sulphide_frac = self.array_modifier(input = self.sulphide_frac, array = self.T, varname = 'sulphide_frac')
			self.graphite_frac = self.array_modifier(input = self.graphite_frac, array = self.T, varname = 'graphite_frac')
			self.mixture_frac = self.array_modifier(input = self.mixture_frac, array = self.T, varname = 'mixture_frac')
			self.sp_frac = self.array_modifier(input = self.sp_frac, array = self.T, varname = 'sp_frac')
			self.rwd_wds_frac = self.array_modifier(input = self.rwd_wds_frac, array = self.T, varname = 'rwd_wds_frac')
			self.perov_frac = self.array_modifier(input = self.perov_frac, array = self.T, varname = 'perov_frac')
			self.other_frac = self.array_modifier(input = self.other_frac, array = self.T, varname = 'other_frac')
		
		#Converting fractions to water holding species that has an exchange with coexisting melt. 
		#Calculation of equilibrium of water with other minerals are not constrained.
		wt_all = (self.ol_frac + self.opx_frac + self.cpx_frac + self.garnet_frac + self.plag_frac +\
		self.kfelds_frac + self.rwd_wds_frac + self.perov_frac)
		self.ol_frac_wt = self.ol_frac / wt_all
		self.opx_frac_wt = self.opx_frac / wt_all
		self.cpx_frac_wt = self.cpx_frac / wt_all
		self.garnet_frac_wt = self.garnet_frac / wt_all
		self.plag_frac_wt = self.plag_frac / wt_all
		self.kfelds_frac_wt = self.kfelds_frac / wt_all
		self.rwd_wds_frac_wt = self.rwd_wds_frac / wt_all
		self.perov_frac_wt = self.perov_frac / wt_all
		
		overlookError = kwargs.pop('overlookError', False)
		
		self.mineral_frac_list = [self.quartz_frac, self.plag_frac, self.amp_frac, self.kfelds_frac, self.opx_frac, self.cpx_frac,
		self.mica_frac, self.garnet_frac, self.sulphide_frac, self.graphite_frac, self.ol_frac, self.sp_frac, self.rwd_wds_frac,
		self.perov_frac, self.mixture_frac, self.other_frac]
			
		if overlookError == False:
			
			for i in range(0,len(self.mineral_frac_list)):
				if len(np.flatnonzero(self.mineral_frac_list[i] < 0)) != 0:
				
					raise ValueError('There is a value entered in mineral fraction contents that is below zero.')
		
		if overlookError == False:
			bool_composition = self.check_composition(method = 'mineral')
	
			if bool_composition == False:
			
				raise ValueError('The values entered in mineral composition do not add up to 1.')
				
		self.density_loaded = False
			
	def set_composition_solid_rock(self, reval = False, **kwargs):
	
		#Enter composition in fraction 0.6 == 60% volumetric percentage
		
		if self.temperature_default == True:
			self.suggestion_temp_array()
		
		if reval == False:
			self.granite_frac = self.array_modifier(input = kwargs.pop('granite', 0), array = self.T, varname = 'granite_frac')
			self.granulite_frac = self.array_modifier(input = kwargs.pop('granulite', 0), array = self.T, varname = 'granulite_frac')
			self.sandstone_frac = self.array_modifier(input = kwargs.pop('sandstone', 0), array = self.T, varname = 'sandstone_frac')
			self.gneiss_frac = self.array_modifier(input = kwargs.pop('gneiss', 0), array = self.T, varname = 'gneiss_frac')
			self.amphibolite_frac = self.array_modifier(input = kwargs.pop('amphibolite', 0), array = self.T, varname = 'amphibolite_frac')
			self.basalt_frac = self.array_modifier(input = kwargs.pop('basalt', 0), array = self.T, varname = 'basalt_frac')
			self.mud_frac = self.array_modifier(input = kwargs.pop('mud', 0), array = self.T, varname = 'mud_frac')
			self.gabbro_frac = self.array_modifier(input = kwargs.pop('gabbro', 0), array = self.T, varname = 'gabbro_frac')
			self.other_rock_frac = self.array_modifier(input = kwargs.pop('other_rock', 0), array = self.T, varname = 'other_rock_frac')
		elif reval == True:
			self.granite_frac = self.array_modifier(input = self.granite_frac, array = self.T, varname = 'granite_frac')
			self.granulite_frac = self.array_modifier(input = self.granulite_frac, array = self.T, varname = 'granulite_frac')
			self.sandstone_frac = self.array_modifier(input = self.sandstone_frac, array = self.T, varname = 'sandstone_frac')
			self.gneiss_frac = self.array_modifier(input = self.gneiss_frac, array = self.T, varname = 'gneiss_frac')
			self.amphibolite_frac = self.array_modifier(input = self.amphibolite_frac, array = self.T, varname = 'amphibolite_frac')
			self.basalt_frac = self.array_modifier(input = self.basalt_frac, array = self.T, varname = 'basalt_frac')
			self.mud_frac = self.array_modifier(input = self.mud_frac, array = self.T, varname = 'mud_frac')
			self.gabbro_frac = self.array_modifier(input = self.gabbro_frac, array = self.T, varname = 'gabbro_frac')
			self.other_rock_frac = self.array_modifier(input = self.other_rock_frac, array = self.T, varname = 'other_rock_frac')
		
		overlookError = kwargs.pop('overlookError', False)
		
		if overlookError == False:
			rock_frac_list = [self.granite_frac,self.granulite_frac,self.sandstone_frac,self.gneiss_frac,self.amphibolite_frac,
			self.basalt_frac,self.mud_frac,self.gabbro_frac,self.other_rock_frac]
			
			for i in range(0,len(rock_frac_list)):
				if len(np.flatnonzero(rock_frac_list[i] < 0)) != 0:
				
					raise ValueError('There is a value entered in rock fraction contents that is below zero.')
		
		if overlookError == False:
			bool_composition = self.check_composition(method = 'rock')
	
			if bool_composition == False:
			
				raise ValueError('The entered in rock composition do not add up to 1.')
				
		self.density_loaded = False			
			
	def set_temperature(self,T):
	
		try: 
			self.T = T
		except TypeError:
			self.T = np.array(T)
			
		if len(np.flatnonzero(self.T < 0)) != 0:
		
			raise ValueError('There is a value entered in temperature contents that is below zero.')
			
		self.temperature_default = False
		self.water_fugacity_calculated = False
		
		self.density_loaded = False
		
	def set_pressure(self,P):
		
		try: 
			self.p = np.array(P)
			t_check = self.check_p_n_T()
			if t_check == False:
				raise ValueError('The arrays of pressure and temperature are not the same...')
				
		except TypeError:
			try:
				self.p = np.ones(len(self.T)) * P
			except TypeError:
				self.p = np.ones(1) * P
		
		self.set_depth(depth = 'auto')
		self.water_fugacity_calculated = False
		
		self.density_loaded = False
	
	def set_depth(self,depth):
	
		if depth == 'auto':
			self.depth = self.p * 33.0
			
		else:
		
			self.depth = self.array_modifier(input = depth, array = self.T, varname = 'depth')
			
		self.density_loaded = False
	
	def check_p_n_T(self):
	
		if len(self.T) != len(self.p):
			T_check = False
		else:
			T_check = True
			
		return T_check
		
	def set_watercalib(self,**kwargs):
	
		pide.ol_calib = kwargs.pop('ol', 3)
		pide.px_gt_calib = kwargs.pop('px_gt', 2)
		pide.feldspar_calib = kwargs.pop('feldspar', 2)
		
		if (pide.ol_calib < 0) or (pide.ol_calib > 3):
			raise ValueError('The olivine calibration method has entered incorrectly. The value has to be 0-Withers2012, 1-Bell2003, 2-Paterson1980 or 3-Default')
			
		if (pide.px_gt_calib < 0) or (pide.px_gt_calib > 2):
			raise ValueError('The pyroxene-garnet calibration method has entered incorrectly. The value has to be 0-Bell1995 1-Paterson1980 or 2-Default.')
			
		if (pide.feldspar_calib < 0) or (pide.feldspar_calib > 2):
			raise ValueError('The feldspar calibration method has entered incorrectly. The value has to be 0-Johnson2003 1-Mosenfelder2015 or 2-Default.')
		
	def set_o2_buffer(self, o2_buffer = 0):
		
		# pide.o2_buffer = kwargs.pop('o2_buffer', 0)
		pide.o2_buffer = o2_buffer
		
		if (pide.o2_buffer < 0) or (pide.o2_buffer > 4):
			raise ValueError('The oxygen fugacity buffer has entered incorrectly. The value has to be 0-FMQ, 1-IW, 2-QIF, 3-NNO, 4-MMO')
			
	def set_mantle_water_solubility(self,**kwargs):
	
		self.ol_sol_choice = kwargs.pop('ol', 0)
		self.opx_sol_choice = kwargs.pop('opx', 0)
		self.cpx_sol_choice = kwargs.pop('cpx', 0)
		self.garnet_sol_choice = kwargs.pop('garnet', 0)
		self.rwd_wds_sol_choice = kwargs.pop('rwd_wds', 0)
		self.perov_sol_choice = kwargs.pop('perov', 0)
		
		if self.mineral_sol_name[10][self.ol_sol_choice] == 'FromOpx':
			if self.mineral_sol_name[4][self.opx_sol_choice] == 'FromOl':
				self.ol_sol_choice = 0
				raise ValueError('The olivine and opx water solubilities references each other, this will generate an infinite loop during calculation. Reverting to the default value for olivine.')
			
	def set_mantle_water_partitions(self,**kwargs):
	
		self.d_water_opx_ol_choice = kwargs.pop('opx_ol', 0)
		self.d_water_cpx_ol_choice = kwargs.pop('cpx_ol', 0)
		self.d_water_garnet_ol_choice = kwargs.pop('garnet_ol', 0)
		
		self.d_water_ol_melt_choice = kwargs.pop('ol_melt',0)
		self.d_water_opx_melt_choice = kwargs.pop('opx_melt',0)
		self.d_water_cpx_melt_choice = kwargs.pop('cpx_melt',0)
		self.d_water_garnet_melt_choice = kwargs.pop('garnet_melt',0)
		
		self.load_mantle_water_partitions(method = 'array')
		
	def set_mantle_transition_zone_water_partitions(self, **kwargs):
	
		self.d_water_garnet_rwd_wds_choice = kwargs.pop('garnet_rwd_wds', 0)
		self.d_water_perov_rwd_wds_choice = kwargs.pop('perov_rwd_wds', 0)
		self.d_water_cpx_rwd_wds_choice = kwargs.pop('cpx_rwd_wds', 0)
		
		self.load_mantle_transition_zone_water_partitions(method = 'array')
		
	def check_composition(self, method = None):

		continue_adjusting = True

		if method == 'rock':

			tot = self.granite_frac + self.granulite_frac + self.sandstone_frac +\
			self.gneiss_frac + self.amphibolite_frac + self.basalt_frac + self.mud_frac +\
				 self.gabbro_frac + self.other_rock_frac
			
			if any(item <= 0.99 for item in tot) == True:
				continue_adjusting = False
			
			if any(item >= 1.01 for item in tot) == True:
				continue_adjusting = False
				
		elif method == 'mineral':
			
			tot = self.quartz_frac + self.plag_frac + self.amp_frac + self.kfelds_frac +\
			self.opx_frac + self.cpx_frac + self.mica_frac + self.garnet_frac + self.sulphide_frac + self.graphite_frac +\
			self.ol_frac + self.sp_frac + self.rwd_wds_frac + self.perov_frac + self.mixture_frac + self.other_frac

			if any(item <= 0.99 for item in tot) == True:
			
				continue_adjusting = False
			
			if any(item >= 1.01 for item in tot) == True:

				continue_adjusting = False

		return continue_adjusting
	
	def get_mineral_index(self, mineral_name):
	
		if (mineral_name == 'ol') or (mineral_name == 'olivine'):
			min_index = 21
		elif (mineral_name == 'opx') or (mineral_name == 'orthopyroxene'):
			min_index = 15
		elif (mineral_name == 'cpx') or (mineral_name == 'clinopyroxene'):
			min_index = 16
		elif (mineral_name == 'garnet') or (mineral_name == 'gt'):
			min_index = 18
		elif (mineral_name == 'mica') or (mineral_name == 'Mica'):
			min_index = 17
		elif (mineral_name == 'amp') or (mineral_name == 'amphibole'):
			min_index = 13
		elif (mineral_name == 'quartz') or (mineral_name == 'qtz'):
			min_index = 11
		elif (mineral_name == 'plag') or (mineral_name == 'plagioclase'):
			min_index = 12
		elif (mineral_name == 'kfelds') or (mineral_name == 'kfeldspar'):
			min_index = 14
		elif (mineral_name == 'sulphide') or (mineral_name == 'Sulphide'):
			min_index = 19
		elif (mineral_name == 'graphite') or (mineral_name == 'Graphite'):
			min_index = 20
		elif (mineral_name == 'spinel') or (mineral_name == 'sp'):
			min_index = 22
		elif (mineral_name == 'ringwoodite_wadsleyite') or (mineral_name == 'rwd_wds'):
			min_index = 23
		elif (mineral_name == 'perovskite') or (mineral_name == 'perov'):
			min_index = 24
		elif (mineral_name == 'mixture') or (mineral_name == 'mixtures'):
			min_index = 25
		elif (mineral_name == 'other') or (mineral_name == 'other'):
			min_index = 26
			
		else:
		
			raise ValueError('There is no such a mineral specifier called :' + mineral_name)
			
		return min_index
		
	def get_rock_index(self, rock_name):
	
		if (rock_name == 'granite'):
			rock_index = 2
		elif (rock_name == 'granulite'):
			rock_index = 3
		elif (rock_name == 'sandstone'):
			rock_index = 4
		elif (rock_name == 'gneiss'):
			rock_index = 5
		elif (rock_name == 'amphibolite'):
			rock_index = 6
		elif (rock_name == 'basalt'):
			rock_index = 7
		elif (rock_name == 'mud'):
			rock_index = 8
		elif (rock_name == 'gabbro'):
			rock_index = 9
		elif (rock_name == 'other_rock'):
			rock_index = 10
			
		else:
		
			raise ValueError('There is no such a mineral specifier called :' + rock_name)
			
		return rock_index
		
	def list_mineral_econd_models(self, mineral_name):
		
		if (mineral_name == 'ol') or (mineral_name == 'olivine'):
			min_index = 21
		elif (mineral_name == 'opx') or (mineral_name == 'orthopyroxene'):
			min_index = 15
		elif (mineral_name == 'cpx') or (mineral_name == 'clinopyroxene'):
			min_index = 16
		elif (mineral_name == 'garnet') or (mineral_name == 'gt'):
			min_index = 18
		elif (mineral_name == 'mica') or (mineral_name == 'Mica'):
			min_index = 17
		elif (mineral_name == 'amp') or (mineral_name == 'amphibole'):
			min_index = 13
		elif (mineral_name == 'quartz') or (mineral_name == 'qtz'):
			min_index = 11
		elif (mineral_name == 'plag') or (mineral_name == 'plagioclase'):
			min_index = 12
		elif (mineral_name == 'kfelds') or (mineral_name == 'kfeldspar'):
			min_index = 14
		elif (mineral_name == 'sulphide') or (mineral_name == 'Sulphide'):
			min_index = 19
		elif (mineral_name == 'graphite') or (mineral_name == 'Graphite'):
			min_index = 20
		elif (mineral_name == 'spinel') or (mineral_name == 'sp'):
			min_index = 22
		elif (mineral_name == 'ringwoodite_wadsleyite') or (mineral_name == 'rwd_wds'):
			min_index = 23
		elif (mineral_name == 'perovskite') or (mineral_name == 'perov'):
			min_index = 24
		elif (mineral_name == 'mixture') or (mineral_name == 'mixtures'):
			min_index = 25
		elif (mineral_name == 'other') or (mineral_name == 'other'):
			min_index = 26
			
		else:
			raise ValueError('There is no such a mineral specifier called :' + mineral_name)
			
		print(color.RED + 'Electrical conductivity models for the given mineral: ' + mineral_name + color.END)
		def print_lists(min_idx):
		
			for i in range(0,len(self.name[min_idx])):
				print(str(i) + '.  ' + self.name[min_idx][i])
			
		print_lists(min_idx = min_index)
		
		return self.name[min_index]
		
	def list_rock_econd_models(self, rock_name):
		
		if (rock_name == 'granite'):
			rock_idx = 2
		elif (rock_name == 'granulite'):
			rock_idx = 3
		elif (rock_name == 'sandstone'):
			rock_idx = 4
		elif (rock_name == 'gneiss'):
			rock_idx = 5
		elif (rock_name == 'amphibolite'):
			rock_idx = 6
		elif (rock_name == 'basalt'):
			rock_idx = 7
		elif (rock_name == 'mud'):
			rock_idx = 8
		elif (rock_name == 'gabbro'):
			rock_idx = 9
		elif (rock_name == 'other_rock'):
			rock_idx = 10
			
		else:
		
			raise ValueError('There is no such a mineral specifier called :' + rock_name)
		
		print(color.RED +'Conductivity models for the selected rock:' + color.END)
		def print_lists(rock_idx):
		
			for i in range(0,len(self.name[rock_idx])):
				print(str(i) + '.  ' + self.name[rock_idx][i])
			print('                 ')
			print('                 ')
		print_lists(rock_idx = rock_idx)
		
		return self.name[rock_idx]
		
	def list_melt_econd_models(self):
	
		print(color.RED +'Conductivity models for melts:' + color.END)
		for i in range(0,len(self.name[1])):
			print(str(i) + '.  ' + self.name[1][i])
			
		print('                 ')
		print('                 ')
			
		return self.name[1]
		
	def list_fluid_econd_models(self):
		
		print(color.BLUE +'Conductivity models for fluids:' + color.END)
		for i in range(0,len(self.name[0])):
			print(str(i) + '.  ' + self.name[0][i])
			
		print('                 ')
		print('                 ')
		
		return self.name[0]
		
	def list_mantle_water_partitions_solid(self, mineral_name):
	
		if (mineral_name == 'opx') or (mineral_name == 'orthopyroxene'):
			min_index = 4
			min_str = 'Opx/Ol'
		elif (mineral_name == 'cpx') or (mineral_name == 'clinopyroxene'):
			min_index = 5
			min_str = 'Cpx/Ol'
		elif (mineral_name == 'garnet') or (mineral_name == 'gt'):
			min_index = 7
			min_str = 'Garnet/Ol'
		else:
			raise AttributeError('There is no mantle water partition coefficients for the chosen mineral: ' + mineral_name)
			
		def print_lists(min_idx):
			
			print(color.RED + 'Mantle solid-state water partition coefficients for the mineral: ' + mineral_name + color.END)
			for i in range(0,len(self.water_ol_part_name[min_idx])):
				if self.water_ol_part_type[min_index][i] == 0:
					print(str(i) + '.  ' + self.water_ol_part_name[min_index][i] + ' -  Type ' + str(self.water_ol_part_type[min_index][i]) + '  -  ' + min_str + ': ' + str(self.water_ol_part_function[min_index][i]))
				else:
					print(str(i) + '.  ' + self.water_ol_part_name[min_index][i] + ' -  Type ' + str(self.water_ol_part_type[min_index][i]))
			print('                 ')
			print('                 ')	
			
		print_lists(min_idx = min_index)
		
		return self.water_ol_part_name[min_index]
		
	def list_transition_zone_water_partitions_solid(self, mineral_name):
	
		if (mineral_name == 'cpx') or (mineral_name == 'clinopyroxene'):
			min_index = 5
			min_str = 'Cpx/RwdWds'
		elif (mineral_name == 'garnet') or (mineral_name == 'gt'):
			min_index = 7
			min_str = 'Garnet/RwdWds'
		elif (mineral_name == 'perovskite') or (mineral_name == 'perov'):
			min_index = 13
			min_str = 'Perov/RwdWds'
		else:
			raise AttributeError('There is no transition zone water partition coefficients for the chosen mineral: ' + mineral_name)
			
		def print_lists(min_idx):
		
			print(color.RED + 'Transition zone solid-state water partition coefficients for the mineral: ' + mineral_name + color.END)
			for i in range(0,len(self.water_rwd_wds_part_name[min_idx])):
				if self.water_rwd_wds_part_type[min_index][i] == 0:
					print(str(i) + '.  ' + self.water_rwd_wds_part_name[min_index][i] + ' -  Type ' + str(self.water_rwd_wds_part_type[min_index][i]) + '  -  ' + min_str + ': ' + str(self.water_rwd_wds_part_function[min_index][i]))
				else:
					print(str(i) + '.  ' + self.water_rwd_wds_part_name[min_index][i] + ' -  Type ' + str(self.water_rwd_wds_part_type[min_index][i]) + '  -  Specific Function.' )
		
			print('                 ')
			print('                 ')	
			
		print_lists(min_idx = min_index)
		
		return self.water_rwd_wds_part_name[min_index]
		
	def list_mantle_water_partitions_melt(self, mineral_name):
		
		print('Mantle melt/NAMs water partition coefficients for the mineral: ' + mineral_name)
		
		if (mineral_name == 'ol') or (mineral_name == 'olivine'):
			min_index = 10
			min_str = 'Ol/Melt'
		elif (mineral_name == 'opx') or (mineral_name == 'orthopyroxene'):
			min_index = 4
			min_str = 'Opx/Melt'
		elif (mineral_name == 'cpx') or (mineral_name == 'clinopyroxene'):
			min_index = 5
			min_str = 'Cpx/Melt'
		elif (mineral_name == 'garnet') or (mineral_name == 'gt'):
			min_index = 7
			min_str = 'Garnet/Melt'
		else:
			raise AttributeError('There is no mantle water partition coefficients for the chosen mineral: ' + mineral_name)
			
		def print_lists(min_idx):
		
			for i in range(0,len(self.water_melt_part_name[min_idx])):
				if self.water_melt_part_type[min_index][i] == 0:
					print(str(i) + '.  ' + self.water_melt_part_name[min_index][i] + ' -  Type ' + str(self.water_melt_part_type[min_index][i]) + '  -  ' + min_str + ': ' + str(self.water_melt_part_function[min_index][i]))
				else:
					print(str(i) + '.  ' + self.water_melt_part_name[min_index][i] + ' -  Type ' + str(self.water_melt_part_type[min_index][i]) + '  -  Specific Function.' )
					
		print_lists(min_idx = min_index)
		
		return self.water_melt_part_name[min_index]
		
	def list_mantle_water_solubilities(self, mineral_name):
	
		print('Mantle NAM water solubility for: ' + mineral_name)
		
		if (mineral_name == 'ol') or (mineral_name == 'olivine'):
			min_index = 10
		elif (mineral_name == 'opx') or (mineral_name == 'orthopyroxene'):
			min_index = 4
		elif (mineral_name == 'cpx') or (mineral_name == 'clinopyroxene'):
			min_index = 5
		elif (mineral_name == 'garnet') or (mineral_name == 'gt'):
			min_index = 7
		elif (mineral_name == 'rwd_wds'):
			min_index = 12
		else:
			raise AttributeError('There is no mantle water solubility adjust for the chosen mineral: ' + mineral_name)
		
		
		def print_lists(min_idx):
		
			for i in range(0,len(self.mineral_sol_name[min_idx])):
				print(str(i) + '.  ' + self.mineral_sol_name[min_idx][i])
				
		print_lists(min_idx = min_index)
		
		return self.mineral_sol_name[min_index]
		
	def set_melt_fluid_conductivity_choice(self,**kwargs):
	
		pide.melt_cond_selection = kwargs.pop('melt', 0)
		pide.fluid_cond_selection = kwargs.pop('fluid', 0)
		
		if (pide.melt_cond_selection < 0) or (pide.melt_cond_selection > len(self.name[1])):
		
			raise ValueError('Bad entry for melt conductivity selection. Indexes allowed are from 0 to ' + str(len(self.name[1])))
			
		if (pide.fluid_cond_selection < 0) or (pide.fluid_cond_selection > len(self.name[0])):
		
			raise ValueError('Bad entry for fluid conductivity selection. Indexes allowed are from 0 to ' + str(len(self.name[0])))
		
	def set_mineral_conductivity_choice(self,**kwargs):
	
		pide.ol_cond_selection = kwargs.pop('ol', 0)
		pide.opx_cond_selection = kwargs.pop('opx', 0)
		pide.cpx_cond_selection = kwargs.pop('cpx', 0)
		pide.garnet_cond_selection = kwargs.pop('garnet', 0)
		pide.mica_cond_selection = kwargs.pop('mica', 0)
		pide.amp_cond_selection = kwargs.pop('amp', 0)
		pide.quartz_cond_selection = kwargs.pop('quartz', 0)
		pide.plag_cond_selection = kwargs.pop('plag', 0)
		pide.kfelds_cond_selection = kwargs.pop('kfelds', 0)
		pide.sulphide_cond_selection = kwargs.pop('sulphide', 0)
		pide.graphite_cond_selection = kwargs.pop('graphite', 0)
		pide.sp_cond_selection = kwargs.pop('sp',0)
		pide.rwd_wds_cond_selection = kwargs.pop('rwd_wds',0)
		pide.perov_cond_selection = kwargs.pop('perov',0)
		pide.mixture_cond_selection = kwargs.pop('mixture', 0)
		pide.other_cond_selection = kwargs.pop('other', 0)
		
		pide.minerals_cond_selections = [pide.quartz_cond_selection, pide.plag_cond_selection, pide.amp_cond_selection, pide.kfelds_cond_selection, pide.opx_cond_selection,
				   pide.cpx_cond_selection, pide.mica_cond_selection, pide.garnet_cond_selection, pide.sulphide_cond_selection,
				   pide.graphite_cond_selection, pide.ol_cond_selection, pide.sp_cond_selection, pide.rwd_wds_cond_selection, pide.perov_cond_selection,
				   pide.mixture_cond_selection, pide.other_cond_selection]
				   
		self.mineral_conductivity_choice_check()
		
		self.density_loaded = False
		
	def mineral_conductivity_choice_check(self):
		
		mineral_idx = list(range(11,28))
		mineral_names = ['qtz','plag','amp','kfelds','opx','cpx','mica','garnet','sulphide','graphite','ol','sp','rwd_wds','perov','mixture','other']
		
		for i in range(0,len(pide.minerals_cond_selections)):
		
			if (pide.minerals_cond_selections[i] < 0) or (pide.minerals_cond_selections[i] > len(self.name[mineral_idx[i]])):
			
				raise ValueError('Bad entry for mineral conductivity selection. Indexes allowed are from 0 to ' + str(len(self.name[mineral_idx[i]])) + ' for the mineral ' + mineral_names[i])
	
	def set_rock_conductivity_choice(self,**kwargs):
	
		pide.granite_cond_selection = kwargs.pop('granite', 0)
		pide.granulite_cond_selection = kwargs.pop('granulite', 0)
		pide.sandstone_cond_selection = kwargs.pop('sandstone', 0)
		pide.gneiss_cond_selection = kwargs.pop('gneiss', 0)
		pide.amphibolite_cond_selection = kwargs.pop('amphibolite', 0)
		pide.basalt_cond_selection = kwargs.pop('basalt', 0)
		pide.mud_cond_selection = kwargs.pop('mud', 0)
		pide.gabbro_cond_selection = kwargs.pop('gabbro', 0)
		pide.other_rock_cond_selection = kwargs.pop('other_rock', 0)
		
		pide.rock_cond_selections = [pide.granite_cond_selection, pide.granulite_cond_selection, pide.sandstone_cond_selection, pide.gneiss_cond_selection,
				   pide.amphibolite_cond_selection, pide.basalt_cond_selection, pide.mud_cond_selection, pide.gabbro_cond_selection, pide.other_rock_cond_selection]
				   
				   
		self.rock_conductivity_choice_check()
		
		self.density_loaded = False
		
	def rock_conductivity_choice_check(self):
		
		rock_idx = list(range(2,12))
		rock_names = ['granite','granulite','sandstone','gneiss','amphibolite','basalt','mud','gabbro','other_rock']
		
		for i in range(0,len(pide.rock_cond_selections)):
		
			if (pide.rock_cond_selections[i] < 0) or (pide.rock_cond_selections[i] > len(self.name[rock_idx[i]])):
			
				raise ValueError('Bad entry for rock conductivity selection. Indexes allowed are from 0 to ' + str(len(self.name[rock_idx[i]])) + ' for the rock ' + rock_names[i])
				   
	def set_mineral_water(self, reval = False, **kwargs):
	
		if self.temperature_default == True:
			self.suggestion_temp_array()
			
		if reval == False:
			pide.ol_water = self.array_modifier(input = kwargs.pop('ol', 0), array = self.T, varname = 'ol_water')
			pide.opx_water = self.array_modifier(input = kwargs.pop('opx', 0), array = self.T, varname = 'opx_water')
			pide.cpx_water = self.array_modifier(input = kwargs.pop('cpx', 0), array = self.T, varname = 'cpx_water')
			pide.garnet_water = self.array_modifier(input = kwargs.pop('garnet', 0), array = self.T, varname = 'garnet_water')
			pide.mica_water = self.array_modifier(input = kwargs.pop('mica', 0), array = self.T, varname = 'mica_water')
			pide.amp_water = self.array_modifier(input = kwargs.pop('amp', 0), array = self.T, varname = 'amp_water')
			pide.quartz_water = self.array_modifier(input = kwargs.pop('quartz', 0), array = self.T, varname = 'quartz_water')
			pide.plag_water = self.array_modifier(input = kwargs.pop('plag', 0), array = self.T, varname = 'plag_water')
			pide.kfelds_water = self.array_modifier(input = kwargs.pop('kfelds', 0), array = self.T, varname = 'kfelds_water')
			pide.sulphide_water = self.array_modifier(input = kwargs.pop('sulphide', 0), array = self.T, varname = 'sulphide_water')
			pide.graphite_water = self.array_modifier(input = kwargs.pop('graphite', 0), array = self.T, varname = 'graphite_water')
			pide.sp_water = self.array_modifier(input = kwargs.pop('sp', 0), array = self.T, varname = 'sp_water')
			pide.rwd_wds_water = self.array_modifier(input = kwargs.pop('rwd_wds', 0), array = self.T, varname = 'rwd_wds_water')
			pide.perov_water = self.array_modifier(input = kwargs.pop('perov', 0), array = self.T, varname = 'perov_water')
			pide.mixture_water = self.array_modifier(input = kwargs.pop('mixture', 0), array = self.T, varname = 'mixture_water')
			pide.other_water = self.array_modifier(input = kwargs.pop('other', 0), array = self.T, varname = 'other_water')
			
		elif reval == True:
		
			pide.ol_water = self.array_modifier(input = pide.ol_water, array = self.T, varname = 'ol_water')
			pide.opx_water = self.array_modifier(input = pide.opx_water, array = self.T, varname = 'opx_water')
			pide.cpx_water = self.array_modifier(input = pide.cpx_water, array = self.T, varname = 'cpx_water')
			pide.garnet_water = self.array_modifier(input = pide.garnet_water, array = self.T, varname = 'garnet_water')
			pide.mica_water = self.array_modifier(input = pide.mica_water, array = self.T, varname = 'mica_water')
			pide.amp_water = self.array_modifier(input = pide.amp_water, array = self.T, varname = 'amp_water')
			pide.quartz_water = self.array_modifier(input = pide.quartz_water, array = self.T, varname = 'quartz_water')
			pide.plag_water = self.array_modifier(input = pide.plag_water, array = self.T, varname = 'plag_water')
			pide.kfelds_water = self.array_modifier(input = pide.kfelds_water, array = self.T, varname = 'kfelds_water')
			pide.sulphide_water = self.array_modifier(input = pide.sulphide_water, array = self.T, varname = 'sulphide_water')
			pide.graphite_water = self.array_modifier(input = pide.graphite_water, array = self.T, varname = 'graphite_water')
			pide.sp_water = self.array_modifier(input = pide.sp_water, array = self.T, varname = 'sp_water')
			pide.rwd_wds_water = self.array_modifier(input = pide.rwd_wds_water, array = self.T, varname = 'rwd_wds_water')
			pide.perov_water = self.array_modifier(input = pide.perov_water, array = self.T, varname = 'perov_water')
			pide.mixture_water = self.array_modifier(input = pide.mixture_water, array = self.T, varname = 'mixture_water')
			pide.other_water = self.array_modifier(input = pide.other_water, array = self.T, varname = 'other_water')
			
		overlookError = kwargs.pop('overlookError', False)

		pide.mineral_water_list = [pide.quartz_water, pide.plag_water, pide.amp_water, pide.kfelds_water,
			 pide.opx_water, pide.cpx_water, pide.mica_water, pide.garnet_water, pide.sulphide_water,
				   pide.graphite_water, pide.ol_water, pide.sp_water, pide.rwd_wds_water, pide.perov_water,
				   pide.mixture_water, pide.other_water]
	
		if overlookError == False:
					
			for i in range(0,len(pide.mineral_water_list)):
				if len(np.flatnonzero(pide.mineral_water_list[i] < 0)) != 0:
				
					raise ValueError('There is a value entered in mineral water contents that is below zero.')
				   
	def set_rock_water(self, reval = False, **kwargs):
	
		if self.temperature_default == True:
			self.suggestion_temp_array()
		
		if reval == False:
		
			pide.granite_water = self.array_modifier(input = kwargs.pop('granite', 0), array = self.T, varname = 'granite_water')
			pide.granulite_water = self.array_modifier(input = kwargs.pop('granulite', 0), array = self.T, varname = 'granulite_water')
			pide.sandstone_water = self.array_modifier(input = kwargs.pop('sandstone', 0), array = self.T, varname = 'sandstone_water')
			pide.gneiss_water = self.array_modifier(input = kwargs.pop('gneiss', 0), array = self.T, varname = 'gneiss_water')
			pide.amphibolite_water = self.array_modifier(input = kwargs.pop('amphibolite', 0), array = self.T, varname = 'amphibolite_water')
			pide.basalt_water = self.array_modifier(input = kwargs.pop('basalt', 0), array = self.T, varname = 'basalt_water')
			pide.mud_water = self.array_modifier(input = kwargs.pop('mud', 0), array = self.T, varname = 'mud_water')
			pide.gabbro_water = self.array_modifier(input = kwargs.pop('gabbro', 0), array = self.T, varname = 'gabbro_water')
			pide.other_rock_water = self.array_modifier(input = kwargs.pop('other_rock', 0), array = self.T, varname = 'other_rock_water')
			
		elif reval == True:
		
			pide.granite_water = self.array_modifier(input = pide.granite_water, array = self.T, varname = 'granite_water')
			pide.granulite_water = self.array_modifier(input = pide.granulite_water, array = self.T, varname = 'granulite_water')
			pide.sandstone_water = self.array_modifier(input = pide.sandstone_water, array = self.T, varname = 'sandstone_water')
			pide.gneiss_water = self.array_modifier(input = pide.gneiss_water, array = self.T, varname = 'gneiss_water')
			pide.amphibolite_water = self.array_modifier(input = pide.amphibolite_water, array = self.T, varname = 'amphibolite_water')
			pide.basalt_water = self.array_modifier(input = pide.basalt_water, array = self.T, varname = 'basalt_water')
			pide.mud_water = self.array_modifier(input = pide.mud_water, array = self.T, varname = 'mud_water')
			pide.gabbro_water = self.array_modifier(input = pide.gabbro_water, array = self.T, varname = 'gabbro_water')
			pide.other_rock_water = self.array_modifier(input = pide.other_rock_water, array = self.T, varname = 'other_rock_water')
			
		
		pide.rock_water_list = [pide.granite_water, pide.granulite_water,
			pide.sandstone_water, pide.gneiss_water, pide.amphibolite_water, pide.basalt_water,
			pide.mud_water, pide.gabbro_water, pide.other_rock_water]
			
	def set_bulk_water(self,value, index = None):
	
		#Running this function overrides the individual mineral water contents until another action is taken.
	
		if self.temperature_default == True:
			self.suggestion_temp_array()
			
		self.bulk_water = self.array_modifier(input = value, array = self.T, varname = 'bulk_water')
		self.solid_water = self.array_modifier(input = value, array = self.T, varname = 'solid_water')
		
		self.set_mineral_water() #Running an empty run of this to equate the length of mineral water arrays with the defined T
		
		if len(np.flatnonzero(self.bulk_water < 0)) != 0:
				
			raise ValueError('There is a value entered in bulk_water content that is below zero.')
			
	def set_xfe_mineral(self, reval = False, **kwargs):
	
		if self.temperature_default == True:
			self.suggestion_temp_array()
		
		if reval == False:
		
			pide.ol_xfe = self.array_modifier(input = kwargs.pop('ol', 0.1), array = self.T, varname = 'ol_xfe')
			pide.opx_xfe = self.array_modifier(input = kwargs.pop('opx', 0.1), array = self.T, varname = 'opx_xfe')
			pide.cpx_xfe = self.array_modifier(input = kwargs.pop('cpx', 0.1), array = self.T, varname = 'cpx_xfe')
			pide.garnet_xfe = self.array_modifier(input = kwargs.pop('garnet', 0.1), array = self.T, varname = 'garnet_xfe')
			pide.mica_xfe = self.array_modifier(input = kwargs.pop('mica', 0.1), array = self.T, varname = 'mica_xfe')
			pide.amp_xfe = self.array_modifier(input = kwargs.pop('amp', 0.1), array = self.T, varname = 'amp_xfe')
			pide.quartz_xfe = self.array_modifier(input = kwargs.pop('quartz', 0.1), array = self.T, varname = 'quartz_xfe')
			pide.plag_xfe = self.array_modifier(input = kwargs.pop('plag', 0.1), array = self.T, varname = 'plag_xfe')
			pide.kfelds_xfe = self.array_modifier(input = kwargs.pop('kfelds', 0.1), array = self.T, varname = 'kfelds_xfe')
			pide.sulphide_xfe = self.array_modifier(input = kwargs.pop('sulphide', 0.1), array = self.T, varname = 'sulphide_xfe')
			pide.graphite_xfe = self.array_modifier(input = kwargs.pop('graphite', 0.1), array = self.T, varname = 'graphite_xfe')
			pide.sp_xfe = self.array_modifier(input = kwargs.pop('sp', 0.1), array = self.T, varname = 'sp_xfe')
			pide.rwd_wds_xfe = self.array_modifier(input = kwargs.pop('rwd_wds', 0.1), array = self.T, varname = 'rwd_wds_xfe')
			pide.perov_xfe = self.array_modifier(input = kwargs.pop('perov', 0.1), array = self.T, varname = 'perov_xfe')
			pide.mixture_xfe = self.array_modifier(input = kwargs.pop('mixture', 0.1), array = self.T, varname = 'mixture_xfe')
			pide.other_xfe = self.array_modifier(input = kwargs.pop('other', 0.1), array = self.T, varname = 'other_xfe')
			
		elif reval == True:
		
			pide.ol_xfe = self.array_modifier(input = pide.ol_xfe, array = self.T, varname = 'ol_xfe')
			pide.opx_xfe = self.array_modifier(input = pide.opx_xfe, array = self.T, varname = 'opx_xfe')
			pide.cpx_xfe = self.array_modifier(input = pide.cpx_xfe, array = self.T, varname = 'cpx_xfe')
			pide.garnet_xfe = self.array_modifier(input = pide.garnet_xfe, array = self.T, varname = 'garnet_xfe')
			pide.mica_xfe = self.array_modifier(input = pide.mica_xfe, array = self.T, varname = 'mica_xfe')
			pide.amp_xfe = self.array_modifier(input = pide.amp_xfe, array = self.T, varname = 'amp_xfe')
			pide.quartz_xfe = self.array_modifier(input = pide.quartz_xfe, array = self.T, varname = 'quartz_xfe')
			pide.plag_xfe = self.array_modifier(input = pide.plag_xfe, array = self.T, varname = 'plag_xfe')
			pide.kfelds_xfe = self.array_modifier(input = pide.kfelds_xfe, array = self.T, varname = 'kfelds_xfe')
			pide.sulphide_xfe = self.array_modifier(input = pide.sulphide_xfe, array = self.T, varname = 'sulphide_xfe')
			pide.graphite_xfe = self.array_modifier(input = pide.graphite_xfe, array = self.T, varname = 'graphite_xfe')
			pide.sp_xfe = self.array_modifier(input = pide.sp_xfe, array = self.T, varname = 'sp_xfe')
			pide.rwd_wds_xfe = self.array_modifier(input = pide.rwd_wds_xfe, array = self.T, varname = 'rwd_wds_xfe')
			pide.perov_xfe = self.array_modifier(input = pide.perov_xfe, array = self.T, varname = 'perov_xfe')
			pide.mixture_xfe = self.array_modifier(input = pide.mixture_xfe, array = self.T, varname = 'mixture_xfe')
			pide.other_xfe = self.array_modifier(input = pide.other_xfe, array = self.T, varname = 'other_xfe')
		
		pide.xfe_mineral_list = [pide.quartz_xfe, pide.plag_xfe, pide.amp_xfe, pide.kfelds_xfe,
			 pide.opx_xfe, pide.cpx_xfe, pide.mica_xfe, pide.garnet_xfe, pide.sulphide_xfe,
				   pide.graphite_xfe, pide.ol_xfe, pide.sp_xfe, pide.rwd_wds_xfe, pide.perov_xfe, pide.mixture_xfe, pide.other_xfe]
				   
		self.density_loaded = False
			
	def set_param1_mineral(self, reval = False, **kwargs):
	
		if self.temperature_default == True:
			self.suggestion_temp_array()
		
		if reval == False:
			pide.ol_param1 = self.array_modifier(input = kwargs.pop('ol', 0), array = self.T, varname = 'ol_param1')
			pide.opx_param1 = self.array_modifier(input = kwargs.pop('opx', 0), array = self.T, varname = 'opx_param1')
			pide.cpx_param1 = self.array_modifier(input = kwargs.pop('cpx', 0), array = self.T, varname = 'cpx_param1')
			pide.garnet_param1 = self.array_modifier(input = kwargs.pop('garnet', 0), array = self.T, varname = 'garnet_param1')
			pide.mica_param1 = self.array_modifier(input = kwargs.pop('mica', 0), array = self.T, varname = 'mica_param1')
			pide.amp_param1 = self.array_modifier(input = kwargs.pop('amp', 0), array = self.T, varname = 'amp_param1')
			pide.quartz_param1 = self.array_modifier(input = kwargs.pop('quartz', 0), array = self.T, varname = 'quartz_param1')
			pide.plag_param1 = self.array_modifier(input = kwargs.pop('plag', 0), array = self.T, varname = 'plag_param1')
			pide.kfelds_param1 = self.array_modifier(input = kwargs.pop('kfelds', 0), array = self.T, varname = 'kfelds_param1')
			pide.sulphide_param1 = self.array_modifier(input = kwargs.pop('sulphide', 0), array = self.T, varname = 'sulphide_param1')
			pide.graphite_param1 = self.array_modifier(input = kwargs.pop('graphite', 0), array = self.T, varname = 'graphite_param1')
			pide.sp_param1 = self.array_modifier(input = kwargs.pop('sp', 0.1), array = self.T, varname = 'sp_param1')
			pide.rwd_wds_param1 = self.array_modifier(input = kwargs.pop('rwd_wds', 0.1), array = self.T, varname = 'rwd_wds_param1')
			pide.perov_param1 = self.array_modifier(input = kwargs.pop('perov', 0.1), array = self.T, varname = 'perov_param1')
			pide.mixture_param1 = self.array_modifier(input = kwargs.pop('mixture', 0), array = self.T, varname = 'mixture_param1')
			pide.other_param1 = self.array_modifier(input = kwargs.pop('other', 0), array = self.T, varname = 'other_param1')
		
		elif reval == True:
			
			pide.ol_param1 = self.array_modifier(input = pide.ol_param1, array = self.T, varname = 'ol_param1')
			pide.opx_param1 = self.array_modifier(input = pide.opx_param1, array = self.T, varname = 'opx_param1')
			pide.cpx_param1 = self.array_modifier(input = pide.cpx_param1, array = self.T, varname = 'cpx_param1')
			pide.garnet_param1 = self.array_modifier(input = pide.garnet_param1, array = self.T, varname = 'garnet_param1')
			pide.mica_param1 = self.array_modifier(input = pide.mica_param1, array = self.T, varname = 'mica_param1')
			pide.amp_param1 = self.array_modifier(input = pide.amp_param1, array = self.T, varname = 'amp_param1')
			pide.quartz_param1 = self.array_modifier(input = pide.quartz_param1, array = self.T, varname = 'quartz_param1')
			pide.plag_param1 = self.array_modifier(input = pide.plag_param1, array = self.T, varname = 'plag_param1')
			pide.kfelds_param1 = self.array_modifier(input = pide.kfelds_param1, array = self.T, varname = 'kfelds_param1')
			pide.sulphide_param1 = self.array_modifier(input = pide.sulphide_param1, array = self.T, varname = 'sulphide_param1')
			pide.graphite_param1 = self.array_modifier(input = pide.graphite_param1, array = self.T, varname = 'graphite_param1')
			pide.sp_param1 = self.array_modifier(input = pide.sp_param1, array = self.T, varname = 'sp_param1')
			pide.rwd_wds_param1 = self.array_modifier(input = pide.rwd_wds_param1, array = self.T, varname = 'rwd_wds_param1')
			pide.perov_param1 = self.array_modifier(input = pide.perov_param1, array = self.T, varname = 'perov_param1')
			pide.mixture_param1 = self.array_modifier(input = pide.mixture_param1, array = self.T, varname = 'mixture_param1')
			pide.other_param1 = self.array_modifier(input = pide.other_param1, array = self.T, varname = 'other_param1')
			
		pide.param1_mineral_list = [pide.quartz_param1, pide.plag_param1, pide.amp_param1, pide.kfelds_param1,
			 pide.opx_param1, pide.cpx_param1, pide.mica_param1, pide.garnet_param1, pide.sulphide_param1,
				   pide.graphite_param1, pide.ol_param1, pide.sp_param1, pide.rwd_wds_param1, pide.perov_param1, pide.mixture_param1, pide.other_param1]
				   
	def set_param1_rock(self, reval = False, **kwargs):
	
		if self.temperature_default == True:
			self.suggestion_temp_array()
		
		if reval == False:
			pide.granite_param1 = self.array_modifier(input = kwargs.pop('granite', 0), array = self.T, varname = 'granite_param1')
			pide.granulite_param1 = self.array_modifier(input = kwargs.pop('granulite', 0), array = self.T, varname = 'granulite_param1')
			pide.sandstone_param1 = self.array_modifier(input = kwargs.pop('sandstone', 0), array = self.T, varname = 'sandstone_param1')
			pide.gneiss_param1 = self.array_modifier(input = kwargs.pop('gneiss', 0), array = self.T, varname = 'gneiss_param1')
			pide.amphibolite_param1 = self.array_modifier(input = kwargs.pop('amphibolite', 0), array = self.T, varname = 'amphibolite_param1')
			pide.basalt_param1 = self.array_modifier(input = kwargs.pop('basalt', 0), array = self.T, varname = 'basalt_param1')
			pide.mud_param1 = self.array_modifier(input = kwargs.pop('mud', 0), array = self.T, varname = 'mud_param1')
			pide.gabbro_param1 = self.array_modifier(input = kwargs.pop('gabbro', 0), array = self.T, varname = 'gabbro_param1')
			pide.other_rock_param1 = self.array_modifier(input = kwargs.pop('other_rock', 0), array = self.T, varname = 'other_rock_param1')
			
		elif reval == True:
		
			pide.granite_param1 = self.array_modifier(input = pide.granite_param1, array = self.T, varname = 'granite_param1')
			pide.granulite_param1 = self.array_modifier(input = pide.granulite_param1, array = self.T, varname = 'granulite_param1')
			pide.sandstone_param1 = self.array_modifier(input = pide.sandstone_param1, array = self.T, varname = 'sandstone_param1')
			pide.gneiss_param1 = self.array_modifier(input = pide.gneiss_param1, array = self.T, varname = 'gneiss_param1')
			pide.amphibolite_param1 = self.array_modifier(input = pide.amphibolite_param1, array = self.T, varname = 'amphibolite_param1')
			pide.basalt_param1 = self.array_modifier(input = pide.basalt_param1, array = self.T, varname = 'basalt_param1')
			pide.mud_param1 = self.array_modifier(input = pide.mud_param1, array = self.T, varname = 'mud_param1')
			pide.gabbro_param1 = self.array_modifier(input = pide.gabbro_param1, array = self.T, varname = 'gabbro_param1')
			pide.other_rock_param1 = self.array_modifier(input = pide.other_rock_param1, array = self.T, varname = 'other_rock_param1')
		
		pide.param1_rock_list = [pide.granite_param1, pide.granulite_param1,
			pide.sandstone_param1, pide.gneiss_param1, pide.amphibolite_param1, pide.basalt_param1,
			pide.mud_param1, pide.gabbro_param1, pide.other_rock_param1]
						
	def set_melt_fluid_frac(self, value):
	
		if self.temperature_default == True:
			self.suggestion_temp_array()
	
		self.melt_fluid_mass_frac = self.array_modifier(input = value, array = self.T, varname = 'melt_fluid_mass_frac')
		
		if len(np.flatnonzero(self.melt_fluid_mass_frac < 0)) != 0:
		
			raise ValueError('There is a value entered for melt/fluid fraction that is below zero.')
		
	def set_melt_or_fluid_mode(self,mode):
	
		if mode == 'melt':
			pide.fluid_or_melt_method = 1
		elif mode == 'fluid':
			pide.fluid_or_melt_method = 0
		else:
			raise ValueError("You have to enter 'melt' or 'fluid' as strings.")
		
	def set_solid_phase_method(self,mode):
	
		if mode == 'mineral':
			pide.solid_phase_method = 2
		elif mode == 'rock':
			pide.solid_phase_method = 1
		else:
			raise ValueError("You have to enter 'mineral' or 'rock' as strings.")
			
		self.density_loaded = False
			
	def set_melt_properties(self, **kwargs):
	
		if self.temperature_default == True:
			self.suggestion_temp_array()
	
		self.co2_melt = self.array_modifier(input = kwargs.pop('co2', 0), array = self.T, varname = 'co2_melt')  #in ppm
		self.h2o_melt = self.array_modifier(input = kwargs.pop('water', 0), array = self.T, varname = 'h2o_melt')  #in ppm
		self.na2o_melt = self.array_modifier(input = kwargs.pop('na2o', 0), array = self.T, varname = 'na2o_melt')  #in wt
		self.k2o_melt = self.array_modifier(input = kwargs.pop('k2o', 0), array = self.T, varname = 'k2o_melt')  #in wt
		
		overlookError = kwargs.pop('overlookError', False)
		
		if overlookError == False:
		
			list_of_values = [self.co2_melt,self.h2o_melt,self.na2o_melt,self.k2o_melt]
			
			for i in range(0,len(list_of_values)):
				if len(np.flatnonzero(list_of_values[i] < 0)) != 0:
				
					raise ValueError('There is a value entered in melt properties that is below zero.')
				
	def set_fluid_properties(self, **kwargs):
	
		if self.temperature_default == True:
			self.suggestion_temp_array()

		self.salinity_fluid = self.array_modifier(input = kwargs.pop('salinity', 0), array = self.T, varname = 'salinity_fluid') 
		
		if len(np.flatnonzero(self.salinity_fluid < 0)) != 0:
		
			raise ValueError('There is a value entered for fluid properties that is below zero.')
			
	def set_alopx(self,value = 0):
	
		if self.temperature_default == True:
			self.suggestion_temp_array()
			
		self.al_opx = self.array_modifier(input = value, array = self.T, varname = 'al_opx') 
		
	def set_phase_interconnectivities(self,reval = False,**kwargs):
	
		if self.temperature_default == True:
			self.suggestion_temp_array()
		if reval == False:
			pide.ol_m = self.array_modifier(input = kwargs.pop('ol', 4), array = self.T, varname = 'ol_m') 
			pide.opx_m = self.array_modifier(input = kwargs.pop('opx', 4), array = self.T, varname = 'opx_m') 
			pide.cpx_m = self.array_modifier(input = kwargs.pop('cpx', 4), array = self.T, varname = 'cpx_m') 
			pide.garnet_m = self.array_modifier(input = kwargs.pop('garnet', 4), array = self.T, varname = 'garnet_m') 
			pide.mica_m = self.array_modifier(input = kwargs.pop('mica', 4), array = self.T, varname = 'mica_m') 
			pide.amp_m = self.array_modifier(input = kwargs.pop('amp', 4), array = self.T, varname = 'amp_m') 
			pide.quartz_m = self.array_modifier(input = kwargs.pop('quartz', 4), array = self.T, varname = 'quartz_m') 
			pide.plag_m = self.array_modifier(input = kwargs.pop('plag', 4), array = self.T, varname = 'plag_m') 
			pide.kfelds_m = self.array_modifier(input = kwargs.pop('kfelds', 4), array = self.T, varname = 'kfelds_m') 
			pide.sulphide_m = self.array_modifier(input = kwargs.pop('sulphide', 4), array = self.T, varname = 'sulphide_m') 
			pide.graphite_m = self.array_modifier(input = kwargs.pop('graphite', 4), array = self.T, varname = 'graphite_m') 
			pide.mixture_m = self.array_modifier(input = kwargs.pop('mixture', 4), array = self.T, varname = 'mixture_m')
			pide.sp_m = self.array_modifier(input = kwargs.pop('sp', 4), array = self.T, varname = 'sp_m')
			pide.rwd_wds_m = self.array_modifier(input = kwargs.pop('rwd_wds', 4), array = self.T, varname = 'rwd_wds_m')
			pide.perov_m = self.array_modifier(input = kwargs.pop('perov', 4), array = self.T, varname = 'perov_m')
			pide.other_m = self.array_modifier(input = kwargs.pop('other', 4), array = self.T, varname = 'other_m') 
			
			pide.granite_m = self.array_modifier(input = kwargs.pop('granite', 4), array = self.T, varname = 'granite_m') 
			pide.granulite_m = self.array_modifier(input = kwargs.pop('granulite', 4), array = self.T, varname = 'granulite_m') 
			pide.sandstone_m = self.array_modifier(input = kwargs.pop('sandstone', 4), array = self.T, varname = 'sandstone_m') 
			pide.gneiss_m = self.array_modifier(input = kwargs.pop('gneiss', 4), array = self.T, varname = 'gneiss_m') 
			pide.amphibolite_m = self.array_modifier(input = kwargs.pop('amphibolite', 4), array = self.T, varname = 'amphibolite_m') 
			pide.basalt_m = self.array_modifier(input = kwargs.pop('basalt', 4), array = self.T, varname = 'basalt_m') 
			pide.mud_m = self.array_modifier(input = kwargs.pop('mud', 4), array = self.T, varname = 'mud_m') 
			pide.gabbro_m = self.array_modifier(input = kwargs.pop('gabbro', 4), array = self.T, varname = 'gabbro_m') 
			pide.other_rock_m = self.array_modifier(input = kwargs.pop('other_rock', 4), array = self.T, varname = 'other_rock_m') 
			
		elif reval == True:
		
			pide.ol_m = self.array_modifier(input = pide.ol_m, array = self.T, varname = 'ol_m') 
			pide.opx_m = self.array_modifier(input = pide.opx_m, array = self.T, varname = 'opx_m') 
			pide.cpx_m = self.array_modifier(input = pide.cpx_m, array = self.T, varname = 'cpx_m') 
			pide.garnet_m = self.array_modifier(input = pide.garnet_m, array = self.T, varname = 'garnet_m') 
			pide.mica_m = self.array_modifier(input = pide.mica_m, array = self.T, varname = 'mica_m') 
			pide.amp_m = self.array_modifier(input = pide.amp_m, array = self.T, varname = 'amp_m') 
			pide.quartz_m = self.array_modifier(input = pide.quartz_m, array = self.T, varname = 'quartz_m') 
			pide.plag_m = self.array_modifier(input = pide.plag_m, array = self.T, varname = 'plag_m') 
			pide.kfelds_m = self.array_modifier(input = pide.kfelds_m, array = self.T, varname = 'kfelds_m') 
			pide.sulphide_m = self.array_modifier(input = pide.sulphide_m, array = self.T, varname = 'sulphide_m') 
			pide.graphite_m = self.array_modifier(input = pide.graphite_m, array = self.T, varname = 'graphite_m') 
			pide.mixture_m = self.array_modifier(input = pide.mixture_m, array = self.T, varname = 'mixture_m')
			pide.sp_m = self.array_modifier(input = pide.sp_m, array = self.T, varname = 'sp_m')
			pide.rwd_wds_m = self.array_modifier(input = pide.rwd_wds_m, array = self.T, varname = 'rwd_wds_m')
			pide.perov_m = self.array_modifier(input = pide.perov_m, array = self.T, varname = 'perov_m')
			pide.other_m = self.array_modifier(input = pide.other_m, array = self.T, varname = 'other_m') 
			
			pide.granite_m = self.array_modifier(input = pide.granite_m, array = self.T, varname = 'granite_m') 
			pide.granulite_m = self.array_modifier(input = pide.granulite_m, array = self.T, varname = 'granulite_m') 
			pide.sandstone_m = self.array_modifier(input = pide.sandstone_m, array = self.T, varname = 'sandstone_m') 
			pide.gneiss_m = self.array_modifier(input = pide.gneiss_m, array = self.T, varname = 'gneiss_m') 
			pide.amphibolite_m = self.array_modifier(input = pide.amphibolite_m, array = self.T, varname = 'amphibolite_m') 
			pide.basalt_m = self.array_modifier(input = pide.basalt_m, array = self.T, varname = 'basalt_m') 
			pide.mud_m = self.array_modifier(input = pide.ol_m, array = self.T, varname = 'mud_m') 
			pide.gabbro_m = self.array_modifier(input = pide.ol_m, array = self.T, varname = 'gabbro_m') 
			pide.other_rock_m = self.array_modifier(input = pide.ol_m, array = self.T, varname = 'other_rock_m')
		
		overlookError = kwargs.pop('overlookError', False)
		
		if overlookError == False:
		
			list_of_values_minerals = [pide.ol_m,pide.opx_m,pide.cpx_m,pide.garnet_m,pide.mica_m,pide.amp_m,pide.quartz_m,pide.plag_m,pide.kfelds_m,
			pide.sulphide_m,pide.graphite_m, pide.sp_m, pide.rwd_wds_m,pide.perov_m, pide.mixture_m,pide.other_m]
			
			for i in range(0,len(list_of_values_minerals)):
			
				if len(np.flatnonzero(list_of_values_minerals[i] < 1)) != 0:
				
					raise ValueError('There is a value entered in mineral phase interconnectivities that apperas to be below 1.')
					
			list_of_values_rocks = [pide.granite_m, pide.granulite_m, pide.sandstone_m, pide.gneiss_m, pide.amphibolite_m, pide.basalt_m,
			pide.mud_m, pide.gabbro_m, pide.other_rock_m]
			
			for i in range(0,len(list_of_values_rocks)):
			
				if len(np.flatnonzero(list_of_values_rocks[i] < 1)) != 0:
				
					raise ValueError('There is a value entered in rock phase interconnectivities that apperas to be below 1.')
					
	def set_melt_fluid_interconnectivity(self, value = None, reval = False):
	
		if value == None:
			value = 8.0
	
		if reval == False:
		
			if pide.fluid_or_melt_method == 0:
				pide.melt_fluid_m = self.array_modifier(input = value, array = self.T, varname = 'melt_fluid_m') 
			elif pide.fluid_or_melt_method == 1:
				pide.melt_fluid_m = self.array_modifier(input = value, array = self.T, varname = 'melt_fluid_m') 
		
		elif reval == True:
			
			if pide.fluid_or_melt_method == 0:
				pide.melt_fluid_m = self.array_modifier(input = pide.melt_fluid_m, array = self.T, varname = 'melt_fluid_m') 
			elif pide.fluid_or_melt_method == 1:
				pide.melt_fluid_m = self.array_modifier(input = pide.melt_fluid_m, array = self.T, varname = 'melt_fluid_m') 
				
		if pide.melt_fluid_m.any() < 1.0:
		
			raise ValueError('The fluid_melt interconnectivity value is below 0, which is not accepted.')
	
	def set_solid_phs_mix_method(self, method):
	
		pide.phs_mix_method = method
		
		if (pide.phs_mix_method < 0) or (pide.phs_mix_method > 6):
		
			raise ValueError('The solid phase mixing method is not entered correctly, the value is not between 0 and 6')
		
	def set_solid_melt_fluid_mix_method(self, method):
	
		pide.phs_melt_mix_method = method
		
		if (pide.phs_melt_mix_method < 0) or (pide.phs_melt_mix_method > 6):
		
			raise ValueError('The solid-fluid phase mixing method is not entered correctly, the value is not between 0 and 6')
				
	def set_seismic_velocity_properties(self, **kwargs):

		if 'ol' in kwargs:
			pide.ol_seis_selection = kwargs.pop('ol', "fo")
			self.seis_property_overwrite[10] = True
		if 'opx' in kwargs:
			pide.opx_seis_selection = kwargs.pop('opx', "en")
			self.seis_property_overwrite[4] = True
		if 'cpx' in kwargs:
			pide.cpx_seis_selection = kwargs.pop('cpx', "di")
			self.seis_property_overwrite[5] = True
		if 'garnet' in kwargs:
			pide.garnet_seis_selection = kwargs.pop('garnet', "py")
			self.seis_property_overwrite[7] = True
		if 'mica' in kwargs:
			pide.mica_seis_selection = kwargs.pop('mica', "phlg")
			self.seis_property_overwrite[6] = True
		if 'amp' in kwargs:
			pide.amp_seis_selection = kwargs.pop('amp', "parg")
			self.seis_property_overwrite[2] = True
		if 'quartz' in kwargs:	
			pide.quartz_seis_selection = kwargs.pop('quartz', "bqz")
			self.seis_property_overwrite[0] = True
		if 'plag' in kwargs:
			pide.plag_seis_selection = kwargs.pop('plag', "hAb")
			self.seis_property_overwrite[1] = True
		if 'kfelds' in kwargs:
			pide.kfelds_seis_selection = kwargs.pop('kfelds', "or")
			self.seis_property_overwrite[3] = True
		if 'sulphide' in kwargs:
			pide.sulphide_seis_selection = kwargs.pop('sulphide', 0)
			self.seis_property_overwrite[8] = True
		if 'graphite' in kwargs:	
			pide.graphite_seis_selection = kwargs.pop('graphite', 0)
			self.seis_property_overwrite[9] = True
		if 'sp' in kwargs:	
			pide.sp_seis_selection = kwargs.pop('sp',"mt")
			self.seis_property_overwrite[11] = True
		if 'rwd_wds' in kwargs:	
			pide.rwd_wds_seis_selection = kwargs.pop('rwd_wds',"fo")
			self.seis_property_overwrite[12] = True
		if 'perov' in kwargs:	
			pide.perov_seis_selection = kwargs.pop('perov',"fo")
			self.seis_property_overwrite[13] = True
		if 'mixture' in kwargs:	
			pide.mixture_seis_selection = kwargs.pop('mixture', "fo")
			self.seis_property_overwrite[14] = True
		if 'other' in kwargs:	
			pide.other_seis_selection = kwargs.pop('other', "fo")
			self.seis_property_overwrite[15] = True

		pide.minerals_seis_selections = [pide.quartz_seis_selection, pide.plag_seis_selection, pide.amp_seis_selection, pide.kfelds_seis_selection, pide.opx_seis_selection,
				   pide.cpx_seis_selection, pide.mica_seis_selection, pide.garnet_seis_selection, pide.sulphide_seis_selection,
				   pide.graphite_seis_selection, pide.ol_seis_selection, pide.sp_seis_selection, pide.rwd_wds_seis_selection, pide.perov_seis_selection,
				   pide.mixture_seis_selection, pide.other_seis_selection]
		
		
	def list_phs_mix_methods(self):
	
		phs_mix_list = ["Generalized Archie's Law (Glover, 2010)","Hashin-Shtrikman Lower Bound (Berryman, 1995)",
		"Hashin-Shtrikman Upper Bound (Berryman, 1995)","Parallel Model (Guegen and Palciauskas, 1994)",
		"Perpendicular Model (Guegen and Palciauskas, 1994)","Random Model (Guegen and Palciauskas, 1994)"]
		
		print('Solid Phases Mixing Models:')
		for i in range(0,len(phs_mix_list)):
			print(str(i) + '.  ' + phs_mix_list[i])
		
		return phs_mix_list
		
	def list_phs_melt_fluid_mix_methods(self):
	
		phs_melt_mix_list = ["Modified Archie's Law (Glover et al., 2000)","Tubes Model (ten Grotenhuis et al., 2005)",
		"Spheres Model (ten Grotenhuis et al., 2005)","Modified Brick-layer Model (Schilling et al., 1997)",
		"Hashin-Shtrikman Upper-Bound (Glover et al., 2000)","Hashin-Shtrikman Lower-Bound (Glover et al., 2000)"]
		
		print('Solid-Fluid/Melt Mixing models:')
		for i in range(0,len(phs_melt_mix_list)):
			print(str(i) + '.  ' + phs_melt_mix_list[i])
		
		return phs_melt_mix_list
		
	def array_modifier(self, input, array, varname):
		
		if type(input) == int:
			
			ret_array = np.ones(len(array)) * input
			
		elif type(input) == float:
			
			ret_array = np.ones(len(array)) * input
			
		elif type(input) == np.float64:
			
			ret_array = np.ones(len(array)) * input
			
		elif type(input) == list:
			
			if len(input) == 1:
				ret_array = np.ones(len(array)) * input[0]
			else:
				ret_array = np.array(input)
				if len(ret_array) != len(array):
					
					raise RuntimeError('The entered list of ***' + varname + '*** does not match the length of the entered temperature array.')
			
		elif type(input) == np.ndarray:
		
			if len(input) == 1:
				ret_array = np.ones(len(array)) * input[0]
			else:
				ret_array = input
				if len(ret_array) != len(array):
					raise RuntimeError('The entered list of ***' + varname + '*** does not match the length of the entered temperature array.')
				
		return ret_array
		
	def suggestion_temp_array(self):
	
		print('SUGGESTION: Temperature set up seems to be the default value. You might want to set up the temperature array first before setting up other parameters. You will likely to be get errors from this action.')
		
		
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
		else:
			raise ValueError("The method entered incorrectly. It has to be either 'array' or 'index'.")

		cond_fluids = np.zeros(len(self.T))

		if pide.type[0][pide.fluid_cond_selection] == '0':

			cond_fluids[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[0][pide.fluid_cond_selection],
								   E = self.h_i[0][pide.fluid_cond_selection],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[0][pide.fluid_cond_selection],
								   E = self.h_pol[0][pide.fluid_cond_selection],r = 0, alpha = 0, water = 0)
			
		elif pide.type[0][pide.fluid_cond_selection] == '1':

			cond_fluids[idx_node] =  self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[0][pide.fluid_cond_selection],
								   E = self.h_i[0][pide.fluid_cond_selection],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[0][pide.fluid_cond_selection],
								   E = self.h_pol[0][pide.fluid_cond_selection],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_p[0][pide.fluid_cond_selection],
								   E = self.h_p[0][pide.fluid_cond_selection],r = 0, alpha = 0, water = 0)
			
		elif pide.type[0][pide.fluid_cond_selection] == '3':

			if ('*' in pide.name[0][pide.fluid_cond_selection]) == True:

				fluids_odd_function = pide.name[0][pide.fluid_cond_selection].replace('*','')

			else:

				fluids_odd_function = pide.name[0][pide.fluid_cond_selection]

			cond_fluids[idx_node] = eval(fluids_odd_function + '(T = self.T[idx_node], P = self.p[idx_node], salinity = self.salinity_fluid[idx_node], method = method)')
	
		return cond_fluids

	def calculate_melt_conductivity(self, method, sol_idx = None):

		if method == 'array':
			idx_node = None
		elif method == 'index':
			idx_node = sol_idx
		else:
			raise ValueError("The method entered incorrectly. It has to be either 'array' or 'index'.")

		cond_melt = np.zeros(len(self.T))
		
		if ("Wet" in self.name[1][pide.melt_cond_selection]) == True:
					
			if self.wtype[1][pide.melt_cond_selection] == 0:
				water_corr_factor = 1e4 #converting to wt % if the model requires
			else:
				water_corr_factor = 1.0
			
		else:
			
			water_corr_factor = 1.0

		if pide.type[1][pide.melt_cond_selection] == '0':

			cond_melt[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[1][pide.melt_cond_selection],
								   E = self.h_i[1][pide.melt_cond_selection],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[1][pide.melt_cond_selection],
								   E = self.h_pol[1][pide.melt_cond_selection],r = 0, alpha = 0, water = 0)
			
		elif pide.type[1][pide.melt_cond_selection] == '1':

			cond_melt[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[1][pide.melt_cond_selection],
								   E = self.h_i[1][pide.melt_cond_selection],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[1][pide.melt_cond_selection],
								   E = self.h_pol[1][pide.melt_cond_selection],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_p[1][pide.melt_cond_selection],
								   E = self.h_p[1][pide.melt_cond_selection], r = self.r[1][pide.melt_cond_selection], alpha = self.alpha_p[1][pide.melt_cond_selection],
								   water = self.h2o_melt/water_corr_factor)
			
		elif pide.type[1][pide.melt_cond_selection] == '3':

			if ('*' in pide.name[1][pide.melt_cond_selection]) == True:

				melt_odd_function = pide.name[1][pide.melt_cond_selection].replace('*','')

			else:

				melt_odd_function = pide.name[1][pide.melt_cond_selection]
			
			
			cond_melt[idx_node] = eval(melt_odd_function + '(T = self.T[idx_node], P = self.p[idx_node], Melt_H2O = self.h2o_melt[idx_node]/water_corr_factor,' +
			'Melt_CO2 = self.co2_melt, Melt_Na2O = self.na2o_melt[idx_node], Melt_K2O = self.k2o_melt[idx_node], method = method)')
		
		return cond_melt

	def calculate_rock_conductivity(self, method, rock_idx = None, sol_idx = None):

		if method == 'array':
			idx_node = None
		elif method == 'index':
			idx_node = sol_idx
		else:
			raise ValueError("The method entered incorrectly. It has to be either 'array' or 'index'.")

		if (rock_idx < 2) or (rock_idx > 10):
			raise ValueError("The index chosen for rock conductivity does not appear to be correct. It has to be a value between 2 and 10.")

		cond = np.zeros(len(self.T))

		rock_sub_idx = rock_idx - self.fluid_num
		
		if ("Wet" in self.name[rock_idx][pide.rock_cond_selections[rock_sub_idx]]) == True:
					
			if self.wtype[rock_idx][pide.rock_cond_selections[rock_sub_idx]] == 0:
				water_corr_factor = water_corr_factor * 1e4 #converting to wt % if the model requires
			else:
				water_corr_factor = 1.0
			
		else:
			
			water_corr_factor = 1.0

		if pide.type[rock_idx][pide.rock_cond_selections[rock_sub_idx]] == '0':

			cond[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[rock_idx][pide.rock_cond_selections[rock_sub_idx]],
								   E = self.h_i[rock_idx][pide.rock_cond_selections[rock_sub_idx]],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[rock_idx][pide.rock_cond_selections[rock_sub_idx]],
								   E = self.h_pol[rock_idx][pide.rock_cond_selections[rock_sub_idx]],r = 0, alpha = 0, water = 0)
			
		elif pide.type[rock_idx][pide.rock_cond_selections[rock_sub_idx]] == '1':

			cond[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[rock_idx][pide.rock_cond_selections[rock_sub_idx]],
								   E = self.h_i[rock_idx][pide.rock_cond_selections[rock_sub_idx]],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[rock_idx][pide.rock_cond_selections[rock_sub_idx]],
								   E = self.h_pol[rock_idx][pide.rock_cond_selections[rock_sub_idx]],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_p[rock_idx][pide.rock_cond_selections[rock_sub_idx]],
								   E = self.h_p[rock_idx][pide.rock_cond_selections[rock_sub_idx]], r = self.r[rock_idx][pide.rock_cond_selections[rock_sub_idx]],
								   alpha = self.alpha_p[rock_idx][pide.rock_cond_selections[rock_sub_idx]], water = pide.rock_water_list[rock_sub_idx][idx_node] / water_corr_factor)
			
		elif pide.type[rock_idx][pide.rock_cond_selections[rock_sub_idx]] == '3':

			if ('*' in pide.name[rock_idx][pide.rock_cond_selections[rock_sub_idx]]) == True:

				odd_function = pide.name[rock_idx][pide.rock_cond_selections[rock_sub_idx]].replace('*','')

			else:

				odd_function = pide.name[rock_idx][pide.rock_cond_selections[rock_sub_idx]]

			if ('fo2' in odd_function) == True:
				cond[idx_node] = eval(odd_function + '(T = self.T[idx_node], P = self.p[idx_node], water = pide.rock_water_list[rock_sub_idx][idx_node] \
						  / water_corr_factor, param1 = pide.param1_rock_list[rock_sub_idx][idx_node],\
						   fo2 = self.calculate_fugacity(pide.o2_buffer),fo2_ref = self.calculate_fugacity(3), method = method)')
			else:
				cond[idx_node] = eval(odd_function + '(T = self.T[idx_node], P = self.p[idx_node], water = pide.rock_water_list[rock_sub_idx][idx_node] \
						  / water_corr_factor, param1 = pide.param1_rock_list[rock_sub_idx][idx_node],\
						   method = method)')
		
		return cond
	
	def calculate_mineral_conductivity(self, method, min_idx = None, **kwargs):
	
		sol_idx = kwargs.pop('sol_idx', 0)
	
		if method == 'array':
			idx_node = None
		elif method == 'index':
			idx_node = sol_idx
		else:
			raise ValueError("The method entered incorrectly. It has to be either 'array' or 'index'.")

		if (min_idx < 11) or (min_idx > 27):
			raise ValueError("The index chosen for mineral conductivity does not appear to be correct. It has to be a value between 11 and 27.")

		cond = np.zeros(len(self.T))

		min_sub_idx = min_idx - self.fluid_num - self.rock_num
		
		if ("Wet" in self.name[min_idx][pide.minerals_cond_selections[min_sub_idx]]) == True:
		
			water_corr_factor = self.Water_correction(min_idx = min_idx)
			
			if self.wtype[min_idx][pide.minerals_cond_selections[min_sub_idx]] == 0:
				
				water_corr_factor = water_corr_factor * 1e4 #converting to wt % if the model requires

			else:
			
				pass
			
		else:
			
			water_corr_factor = 1.0

		
		if pide.type[min_idx][pide.minerals_cond_selections[min_sub_idx]] == '0':

			cond[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[min_idx][pide.minerals_cond_selections[min_sub_idx]],
								   E = self.h_i[min_idx][pide.minerals_cond_selections[min_sub_idx]],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[min_idx][pide.minerals_cond_selections[min_sub_idx]],
								   E = self.h_pol[min_idx][pide.minerals_cond_selections[min_sub_idx]],r = 0, alpha = 0, water = 0)
			
		elif pide.type[min_idx][pide.minerals_cond_selections[min_sub_idx]] == '1':
		
			cond[idx_node] = self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_i[min_idx][pide.minerals_cond_selections[min_sub_idx]],
								   E = self.h_i[min_idx][pide.minerals_cond_selections[min_sub_idx]],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_pol[min_idx][pide.minerals_cond_selections[min_sub_idx]],
								   E = self.h_pol[min_idx][pide.minerals_cond_selections[min_sub_idx]],r = 0, alpha = 0, water = 0) + self.calculate_arrhenian_single(T = self.T[idx_node],
								   sigma = self.sigma_p[min_idx][pide.minerals_cond_selections[min_sub_idx]],
								   E = self.h_p[min_idx][pide.minerals_cond_selections[min_sub_idx]], r = self.r[min_idx][pide.minerals_cond_selections[min_sub_idx]],
								   alpha = self.alpha_p[min_idx][pide.minerals_cond_selections[min_sub_idx]], water = pide.mineral_water_list[min_sub_idx][idx_node] / water_corr_factor)
			
		elif pide.type[min_idx][pide.minerals_cond_selections[min_sub_idx]] == '3':

			if ('*' in pide.name[min_idx][pide.minerals_cond_selections[min_sub_idx]]) == True:

				odd_function = pide.name[min_idx][pide.minerals_cond_selections[min_sub_idx]].replace('*','')

			else:

				odd_function = pide.name[min_idx][pide.minerals_cond_selections[min_sub_idx]]

			if ('fo2' in odd_function) == True:
				
				cond[idx_node] = eval(odd_function + '(T = self.T[idx_node], P = self.p[idx_node],\
				water = pide.mineral_water_list[min_sub_idx][idx_node] / water_corr_factor, xFe = pide.xfe_mineral_list[min_sub_idx][idx_node],\
				param1 = pide.param1_mineral_list[min_sub_idx][idx_node],\
				fo2 = self.calculate_fugacity(pide.o2_buffer)[idx_node],fo2_ref = self.calculate_fugacity(3)[idx_node], method = method)')

			else:
				
				cond[idx_node] = eval(odd_function + '(T = self.T[idx_node], P = self.p[idx_node],\
				water = pide.mineral_water_list[min_sub_idx][idx_node] / water_corr_factor,\
				xFe = pide.xfe_mineral_list[min_sub_idx][idx_node], param1 = pide.param1_mineral_list[min_sub_idx][idx_node],\
				fo2 = None, fo2_ref = None, method = method)')

		return cond
		
	def Water_correction(self, min_idx = None):

		#A function that corrects the water content to desired calibration. Numbers are taken from Demouchy and Bolfan-Casanova (2016, Lithos) for olivine, pyroxene and garnet.
		#For feldspars, the correction number is taken from Mosenfelder et al. (2015, Am. Min.)

		if min_idx == 21:
		#olivine

			calib_object = self.w_calib[min_idx][pide.ol_cond_selection]
			calib_object_2 = pide.ol_calib

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

			calib_object = self.w_calib[min_idx][pide.minerals_cond_selections[min_idx - self.rock_num - self.fluid_num]]
			calib_object_2 = pide.px_gt_calib

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
			
			calib_object = self.w_calib[min_idx][pide.minerals_cond_selections[min_idx - self.rock_num - self.fluid_num]]
			calib_object_2 = pide.feldspar_calib
				
			if calib_object_2 == 0:

				if calib_object == 0:

					CORR_Factor = self.john2mosen

				else:

					CORR_Factor = 1.0

			elif calib_object_2 == 1:

				if calib_object == 1:

					CORR_Factor = self.mosen2john

				else:

					CORR_Factor = 1.0
					
			else:
			
				CORR_Factor = 1.0

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
			
				if pide.solid_phase_method == 1:
					phase_list = [self.granite_frac[i],self.granulite_frac[i],self.sandstone_frac[i],
					self.gneiss_frac[i], self.amphibolite_frac[i], self.basalt_frac[i], self.mud_frac[i],
					 self.gabbro_frac[i], self.other_rock_frac[i]]
					m_list = [pide.granite_m[i],pide.granulite_m[i],pide.sandstone_m[i],
					pide.gneiss_m[i], pide.amphibolite_m[i], pide.basalt_m[i], pide.mud_m[i],
					 pide.gabbro_m[i], pide.other_rock_m[i]]
				elif pide.solid_phase_method == 2:
					phase_list = [self.quartz_frac[i], self.plag_frac[i], self.amp_frac[i], self.kfelds_frac[i],
					self.opx_frac[i], self.cpx_frac[i], self.mica_frac[i], self.garnet_frac[i],
					self.sulphide_frac[i], self.graphite_frac[i], self.ol_frac[i], self.sp_frac[i], self.rwd_wds_frac[i], self.perov_frac[i],
					self.mixture_frac[i], self.other_frac[i]]
					m_list = [pide.quartz_m[i], pide.plag_m[i], pide.amp_m[i], pide.kfelds_m[i],
					pide.opx_m[i], pide.cpx_m[i], pide.mica_m[i], pide.garnet_m[i],
					pide.sulphide_m[i], pide.graphite_m[i], pide.ol_m[i], pide.sp_m[i], pide.rwd_wds_m[i], pide.perov_m[i],
					pide.mixture_m[i], pide.other_m[i]]
					
				frac_abundant = max(phase_list) #fraction of abundant mineral
				idx_max_ph = phase_list.index(frac_abundant) #index of the abundant mineral
				del phase_list[idx_max_ph] #deleting the abundant mineral form local list
				del m_list[idx_max_ph] #deleting the exponent of the abundant mineral from local list
				connectedness = np.asarray(phase_list)**np.asarray(m_list) #calculating the connectedness of the rest

				if sum(phase_list) != 0.0:
					m_abundant = np.log(1.0 - np.sum(connectedness)) / np.log(frac_abundant) #analytic solution to the problem
				else:
					m_abundant = 1

				if pide.solid_phase_method == 1:
					
					if idx_max_ph == 0:
						pide.granite_m[idx_node] = m_abundant
					elif idx_max_ph == 1:
						pide.granulite_m[idx_node] = m_abundant
					elif idx_max_ph == 2:
						pide.sandstone_m[idx_node] = m_abundant
					elif idx_max_ph == 3:
						pide.gneiss_m[idx_node] = m_abundant
					elif idx_max_ph == 4:
						pide.amphibolite_m[idx_node] = m_abundant
					elif idx_max_ph == 5:
						pide.basalt_m[idx_node] = m_abundant
					elif idx_max_ph == 6:
						pide.mud_m[idx_node] = m_abundant
					elif idx_max_ph == 7:
						pide.gabbro_m[idx_node] = m_abundant
					elif idx_max_ph == 8:
						pide.other_rock_m[idx_node] = m_abundant
					
					self.bulk_cond[idx_node] = (self.granite_cond[idx_node]*(self.granite_frac[idx_node]**pide.granite_m[idx_node])) +\
					(self.granulite_cond[idx_node]*(self.granulite_frac[idx_node]**pide.granulite_m[idx_node])) +\
					(self.sandstone_cond[idx_node]*(self.sandstone_frac[idx_node]**pide.sandstone_m[idx_node])) +\
					(self.gneiss_cond[idx_node]*(self.gneiss_frac[idx_node]**pide.gneiss_m[idx_node])) +\
					(self.amphibolite_cond[idx_node]*(self.amphibolite_frac[idx_node]**pide.amphibolite_m[idx_node])) +\
					(self.basalt_cond[idx_node]*(self.basalt_frac[idx_node]**pide.basalt_m[idx_node])) +\
					(self.mud_cond[idx_node]*(self.mud_frac[idx_node]**pide.mud_m[idx_node])) +\
					(self.gabbro_cond[idx_node]*(self.gabbro_frac[idx_node]**pide.gabbro_m[idx_node])) +\
					(self.other_rock_cond[idx_node]*(self.other_rock_frac[idx_node]**pide.other_rock_m[idx_node]))
				
				elif pide.solid_phase_method == 2:
					if idx_max_ph == 0:
						pide.quartz_m[idx_node] = m_abundant
					elif idx_max_ph == 1:
						pide.plag_m[idx_node] = m_abundant
					elif idx_max_ph == 2:
						pide.amp_m[idx_node] = m_abundant
					elif idx_max_ph == 3:
						pide.kfelds_m[idx_node] = m_abundant
					elif idx_max_ph == 4:
						pide.opx_m[idx_node] = m_abundant
					elif idx_max_ph == 5:
						pide.cpx_m[idx_node] = m_abundant
					elif idx_max_ph == 6:
						pide.mica_m[idx_node] = m_abundant
					elif idx_max_ph == 7:
						pide.garnet_m[idx_node] = m_abundant
					elif idx_max_ph == 8:
						pide.sulphide_m[idx_node] = m_abundant
					elif idx_max_ph == 9:
						pide.graphite_m[idx_node] = m_abundant
					elif idx_max_ph == 10:
						pide.ol_m[idx_node] = m_abundant
					elif idx_max_ph == 11:
						pide.sp_m[idx_node] = m_abundant
					elif idx_max_ph == 12:
						pide.rwd_wds_m[idx_node] = m_abundant
					elif idx_max_ph == 13:
						pide.perov_m[idx_node] = m_abundant
					elif idx_max_ph == 14:
						pide.mixture_m[idx_node] = m_abundant
					elif idx_max_ph == 15:
						pide.other_m[idx_node] = m_abundant
						
					self.bulk_cond[idx_node] = (self.quartz_cond[idx_node]*(self.quartz_frac[idx_node]**pide.quartz_m[idx_node])) +\
					(self.plag_cond[idx_node]*(self.plag_frac[idx_node]**pide.plag_m[idx_node])) +\
					(self.amp_cond[idx_node]*(self.amp_frac[idx_node]**pide.amp_m[idx_node])) +\
					(self.kfelds_cond[idx_node]*(self.kfelds_frac[idx_node]**pide.kfelds_m[idx_node])) +\
					(self.opx_cond[idx_node]*(self.opx_frac[idx_node]**pide.opx_m[idx_node])) +\
					(self.cpx_cond[idx_node]*(self.cpx_frac[idx_node]**pide.cpx_m[idx_node])) +\
					(self.mica_cond[idx_node]*(self.mica_frac[idx_node]**pide.mica_m[idx_node])) +\
					(self.garnet_cond[idx_node]*(self.garnet_frac[idx_node]**pide.garnet_m[idx_node])) +\
					(self.sulphide_cond[idx_node]*(self.sulphide_frac[idx_node]**pide.sulphide_m[idx_node])) +\
					(self.graphite_cond[idx_node]*(self.graphite_frac[idx_node]**pide.graphite_m[idx_node])) +\
					(self.ol_cond[idx_node]*(self.ol_frac[idx_node]**pide.ol_m[idx_node])) +\
					(self.sp_cond[idx_node]*(self.sp_frac[idx_node]**pide.sp_m[idx_node])) +\
					(self.rwd_wds_cond[idx_node]*(self.rwd_wds_frac[idx_node]**pide.rwd_wds_m[idx_node])) +\
					(self.perov_cond[idx_node]*(self.perov_frac[idx_node]**pide.perov_m[idx_node])) +\
					(self.mixture_cond[idx_node]*(self.mixture_frac[idx_node]**pide.mixture_m[idx_node])) +\
					(self.other_cond[idx_node]*(self.other_frac[idx_node]**pide.other_m[idx_node]))
					
		elif method == 1:
			
			if indexing_method == 'array':
				
				self.bulk_cond = np.zeros(len(self.T))
				start_idx = 0
				end_idx = len(self.T)
			elif indexing_method == 'index':
				start_idx = sol_idx
				end_idx = sol_idx + 1
				
			for i in range(start_idx,end_idx):
				
				if pide.solid_phase_method == 1:
					list_i = [self.granite_cond[i], self.granulite_cond[i], self.sandstone_cond[i],
					self.gneiss_cond[i],self.amphibolite_cond[i], self.basalt_cond[i], self.mud_cond[i],
					  self.gabbro_cond[i], self.other_rock_cond[i]]
				elif pide.solid_phase_method == 2:
					list_i = [self.quartz_cond[i], self.plag_cond[i], self.amp_cond[i],
					self.kfelds_cond[i],self.opx_cond[i],self.cpx_cond[i],self.mica_cond[i],
					self.garnet_cond[i],self.sulphide_cond[i],self.graphite_cond[i],self.ol_cond[i], self.sp_cond[i],
					self.rwd_wds_cond[i], self.perov_cond[i], self.mixture_cond[i], self.other_cond[i]]				
					
				while True:
				
					#while loop for deleting the zero arrays that could be encountered due to non-existence of the mineral.
					min_local = np.amin(np.asarray(list_i))
				
					if (min_local != 0.0):
						
						break
					
					else:
					
						list_i = np.delete(list_i, np.argwhere(list_i == 0))
						
				if pide.solid_phase_method == 1:
				
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
						
				elif pide.solid_phase_method == 2:
				
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
					(self.sp_frac[i] / (self.sp_cond[i] + (2*min_local))) +\
					(self.rwd_wds_frac[i] / (self.rwd_wds_cond[i] + (2*min_local))) +\
					(self.perov_frac[i] / (self.perov_cond[i] + (2*min_local))) +\
					(self.mixture_frac[i] / (self.mixture_cond[i] + (2*min_local))) +\
					(self.other_frac[i] / (self.other_cond[i] + (2*min_local)))
					)**(-1.0)) -\
					2.0*min_local
					
		elif method == 2:
		
			if indexing_method == 'array':
				
				self.bulk_cond = np.zeros(len(self.T))
				start_idx = 0
				end_idx = len(self.T)
			elif indexing_method == 'index':
				start_idx = sol_idx
				end_idx = sol_idx + 1
				
			for i in range(start_idx,end_idx):
				
				if pide.solid_phase_method == 1:
					list_i = [self.granite_cond[i], self.granulite_cond[i], self.sandstone_cond[i],
					self.gneiss_cond[i],self.amphibolite_cond[i], self.basalt_cond[i], self.mud_cond[i],
					  self.gabbro_cond[i], self.other_rock_cond[i]]
				elif pide.solid_phase_method == 2:
					list_i = [self.quartz_cond[i], self.plag_cond[i], self.amp_cond[i],
					self.kfelds_cond[i],self.opx_cond[i],self.cpx_cond[i],self.mica_cond[i],
					self.garnet_cond[i],self.sulphide_cond[i],
					self.graphite_cond[i],self.ol_cond[i], self.sp_cond[i], 
					self.rwd_wds_cond[i], self.perov_cond[i], self.mixture_cond[i], self.other_cond[i]]
					
				while True:
				
					#while loop for deleting the zero arrays that could be encountered due to non-existence of the mineral.
					
					max_local = np.amax(np.asarray(list_i))
				
					if (max_local != 0.0):
						
						break
					
					else:
					
						list_i = np.delete(list_i, np.argwhere(list_i == 0))
						
				if pide.solid_phase_method == 1:
				
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
						
				elif pide.solid_phase_method == 2:
				
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
					(self.sp_frac[i] / (self.sp_cond[i] + (2*max_local))) +\
					(self.rwd_wds_frac[i] / (self.rwd_wds_cond[i] + (2*max_local))) +\
					(self.perov_frac[i] / (self.perov_cond[i] + (2*max_local))) +\
					(self.mixture_frac[i] / (self.mixture_cond[i] + (2*max_local))) +\
					(self.other_frac[i] / (self.other_cond[i] + (2*max_local)))					
					)**(-1.0)) -\
					2.0*max_local
					
		elif method == 3:
		
			#Parallel model for maximum, minimum bounds and neutral w/o errors
			
			if pide.solid_phase_method == 1:
				self.bulk_cond[idx_node] = (self.granite_frac[idx_node]*self.granite_cond[idx_node]) +\
				(self.granulite_frac[idx_node]*self.granulite_cond[idx_node]) +\
				(self.sandstone_frac[idx_node]*self.sandstone_cond[idx_node]) +\
				(self.gneiss_frac[idx_node]*self.gneiss_cond[idx_node]) +\
				(self.amphibolite_frac[idx_node]*self.amphibolite_cond[idx_node]) +\
				(self.basalt_frac[idx_node]*self.basalt_cond[idx_node]) +\
				(self.mud_frac[idx_node]*self.mud_cond[idx_node]) +\
				(self.gabbro_frac[idx_node]*self.gabbro_cond[idx_node]) +\
				(self.other_rock_frac[idx_node]*self.other_rock_cond[idx_node])
				
			elif pide.solid_phase_method == 2:
			
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
				(self.sp_frac[idx_node]*self.sp_cond[idx_node]) +\
				(self.rwd_wds_frac[idx_node]*self.rwd_wds_cond[idx_node]) +\
				(self.perov_frac[idx_node]*self.perov_cond[idx_node]) +\
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
			if pide.solid_phase_method == 1:
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
				
			elif pide.solid_phase_method == 2:
			
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
					if self.sp_frac[i] == 0.0:
						self.sp_cond[i] = -999
					if self.rwd_wds_frac[i] == 0.0:
						self.rwd_wds_cond[i] = -999
					if self.perov_frac[i] == 0.0:
						self.perov_cond[i] = -999
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
				(self.sp_frac[idx_node] / self.sp_cond[idx_node]) +\
				(self.rwd_wds_frac[idx_node] / self.rwd_wds_cond[idx_node]) +\
				(self.perov_frac[idx_node] / self.perov_cond[idx_node]) +\
				(self.mixture_frac[idx_node] / self.mixture_cond[idx_node]) +\
				(self.other_frac[idx_node] / self.other_cond[idx_node]))
				
		elif method == 5:
		
			#Random model for maximum, minimum bounds and neutral w/o errors
			
			if pide.solid_phase_method == 1:
				
				self.bulk_cond[idx_node] = (self.granite_cond[idx_node]**self.granite_frac[idx_node]) *\
				(self.granulite_cond[idx_node]**self.granulite_frac[idx_node]) *\
				(self.sandstone_cond[idx_node]**self.sandstone_frac[idx_node]) *\
				(self.gneiss_cond[idx_node]**self.gneiss_frac[idx_node]) *\
				(self.amphibolite_cond[idx_node]**self.amphibolite_frac[idx_node]) *\
				(self.basalt_cond[idx_node]**self.basalt_frac[idx_node]) *\
				(self.mud_cond[idx_node]**self.mud_frac[idx_node]) *\
				(self.gabbro_cond[idx_node]**self.gabbro_frac[idx_node]) *\
				(self.other_rock_cond[idx_node]**self.other_rock_frac[idx_node]) 
				
			elif pide.solid_phase_method == 2:

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
				(self.sp_cond[idx_node]**self.sp_frac[idx_node]) *\
				(self.rwd_wds_cond[idx_node]**self.rwd_wds_frac[idx_node]) *\
				(self.perov_cond[idx_node]**self.perov_frac[idx_node]) *\
				(self.mixture_cond[idx_node]**self.mixture_frac[idx_node]) *\
				(self.other_cond[idx_node]**self.other_frac[idx_node])
				
		elif method == -1:
			
			#In case the bulk conductivity is determined by a solid phase conductivity entry...
			
			self.bulk_cond = self.bckgr_res

		self.solid_phase_cond = np.array(self.bulk_cond)
			
		#Calculations regarding solid phases and fluid phases mixing take place after this.
		#checking if there's any melt/fluid on the list at all.
		if np.mean(self.melt_fluid_mass_frac) != 0:
			
			if pide.fluid_or_melt_method == 0:
				
				dens = Sanchez_Valle_2013_WaterDensity(T = self.T[idx_node], P = self.p[idx_node])
				self.dens_melt_fluid[idx_node] = dens / 1e3
				
			elif pide.fluid_or_melt_method == 1:
				
				self.dens_melt_dry = float(self.dens_mat[1][pide.melt_cond_selection]) / 1e3 #index 1 is equate to melt
				#Determining xvol, first have to calculate the density of the melt from Sifre et al. (2014)

				self.dens_melt_fluid[idx_node] = (((self.h2o_melt[idx_node] * 1e-4) / 1e2) * 1.4) +\
				(((self.co2_melt[idx_node] * 1e-4) / 1e2) * 2.4) + (1 - (((self.h2o_melt[idx_node] * 1e-4) +\
				(self.co2_melt[idx_node] * 1e-4)) / 1e2)) * self.dens_melt_dry #calculating how much volatiles changed its density
			
			if indexing_method == 'array':
				self.melt_fluid_frac = np.zeros(len(self.melt_fluid_mass_frac))
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
						
						p = np.log10(1.0 - self.melt_fluid_frac[i]**pide.melt_fluid_m[i]) / np.log10(1.0 - self.melt_fluid_frac[i])

						self.bulk_cond[i] = (self.bulk_cond[i] * (1.0 - self.melt_fluid_frac[i])**p) + (self.melt_fluid_cond[i] * (self.melt_fluid_frac[i]**pide.melt_fluid_m[i]))
							
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
			
	def calculate_conductivity(self, method = None,**kwargs):
		
		sol_idx = kwargs.pop('sol_idx', 0)
		
		if method == 'index':
			index = sol_idx
		elif method == 'array':
			index = None
		else:
			raise ValueError("The method entered incorrectly. It has to be either 'array' or 'index'.")
			
		if np.mean(self.melt_fluid_mass_frac) != 0.0:
		
			self.calculate_density_solid() #calculate solid density only when it is needed.
			
			if pide.fluid_or_melt_method == 0:
				self.melt_fluid_cond = self.calculate_fluids_conductivity(method= method, sol_idx = index)
			elif pide.fluid_or_melt_method == 1:
				self.melt_fluid_cond = self.calculate_melt_conductivity(method = method, sol_idx = index)
	
		if pide.solid_phase_method == 1:
		
			if np.mean(self.granite_frac) != 0:
				self.granite_cond = self.calculate_rock_conductivity(method = method, rock_idx= 2, sol_idx = index)
			else:
				self.granite_cond = np.zeros(len(self.T))
				
			if np.mean(self.granulite_frac) != 0:
				self.granulite_cond = self.calculate_rock_conductivity(method = method, rock_idx= 3, sol_idx = index)
			else:
				self.granulite_cond = np.zeros(len(self.T))
				
			if np.mean(self.sandstone_frac) != 0:
				self.sandstone_cond = self.calculate_rock_conductivity(method = method, rock_idx= 4, sol_idx = index)
			else:
				self.sandstone_cond = np.zeros(len(self.T))
				
			if np.mean(self.gneiss_frac) != 0:
				self.gneiss_cond = self.calculate_rock_conductivity(method = method, rock_idx= 5, sol_idx = index)
			else:
				self.gneiss_cond = np.zeros(len(self.T))
				
			if np.mean(self.amphibolite_frac) != 0:
				self.amphibolite_cond = self.calculate_rock_conductivity(method = method, rock_idx= 6, sol_idx = index)
			else:
				self.amphibolite_cond = np.zeros(len(self.T))

			if np.mean(self.basalt_frac) != 0:
				self.basalt_cond = self.calculate_rock_conductivity(method = method, rock_idx= 7, sol_idx = index)
			else:
				self.basalt_cond = np.zeros(len(self.T))

			if np.mean(self.mud_frac) != 0:
				self.mud_cond = self.calculate_rock_conductivity(method = method, rock_idx= 8, sol_idx = index)
			else:
				self.mud_cond = np.zeros(len(self.T))

			if np.mean(self.gabbro_frac) != 0:
				self.gabbro_cond = self.calculate_rock_conductivity(method = method, rock_idx= 9, sol_idx = index)
			else:
				self.gabbro_cond = np.zeros(len(self.T))
				
			if np.mean(self.other_rock_frac) != 0:
				self.other_rock_cond = self.calculate_rock_conductivity(method = method, rock_idx= 10, sol_idx = index)
			else:
				self.other_rock_cond = np.zeros(len(self.T))
						
			self.phase_mixing_function(method = pide.phs_mix_method, melt_method = pide.phs_melt_mix_method, indexing_method= method, sol_idx = index)
			
		elif pide.solid_phase_method == 2:
		
			if np.mean(self.quartz_frac) != 0:
				self.quartz_cond = self.calculate_mineral_conductivity(method = method, min_idx= 11, sol_idx = index)
			else:
				self.quartz_cond = np.zeros(len(self.T))
				
			if np.mean(self.plag_frac) != 0:
				self.plag_cond = self.calculate_mineral_conductivity(method = method, min_idx= 12, sol_idx = index)
			else:
				self.plag_cond = np.zeros(len(self.T))
				
			if np.mean(self.amp_frac) != 0:
				self.amp_cond = self.calculate_mineral_conductivity(method = method, min_idx= 13, sol_idx = index)
			else:
				self.amp_cond = np.zeros(len(self.T))
				
			if np.mean(self.kfelds_frac) != 0:
				self.kfelds_cond = self.calculate_mineral_conductivity(method = method, min_idx= 14, sol_idx = index)
			else:
				self.kfelds_cond = np.zeros(len(self.T))
				
			if np.mean(self.opx_frac) != 0:
				self.opx_cond = self.calculate_mineral_conductivity(method = method, min_idx= 15, sol_idx = index)
			else:
				self.opx_cond = np.zeros(len(self.T))
				
			if np.mean(self.cpx_frac) != 0:
				self.cpx_cond = self.calculate_mineral_conductivity(method = method, min_idx= 16, sol_idx = index)
			else:
				self.cpx_cond = np.zeros(len(self.T))
				
			if np.mean(self.mica_frac) != 0:
				self.mica_cond = self.calculate_mineral_conductivity(method = method, min_idx= 17, sol_idx = index)
			else:
				self.mica_cond = np.zeros(len(self.T))
				
			if np.mean(self.garnet_frac) != 0:
				self.garnet_cond = self.calculate_mineral_conductivity(method = method, min_idx = 18, sol_idx = index)
			else:
				self.garnet_cond = np.zeros(len(self.T))

			if np.mean(self.sulphide_frac) != 0:
				self.sulphide_cond = self.calculate_mineral_conductivity(method = method, min_idx= 19, sol_idx = index)
			else:
				self.sulphide_cond = np.zeros(len(self.T))

			if np.mean(self.graphite_frac) != 0:
				self.graphite_cond = self.calculate_mineral_conductivity(method = method, min_idx= 20, sol_idx = index)
			else:
				self.graphite_cond = np.zeros(len(self.T))

			if np.mean(self.ol_frac) != 0:
				self.ol_cond = self.calculate_mineral_conductivity(method = method, min_idx= 21, sol_idx = index)
			else:
				self.ol_cond = np.zeros(len(self.T))
				
			if np.mean(self.sp_frac) != 0:
				self.sp_cond = self.calculate_mineral_conductivity(method = method, min_idx= 22, sol_idx = index)
			else:
				self.sp_cond = np.zeros(len(self.T))
								
			if np.mean(self.rwd_wds_frac) != 0:
				self.rwd_wds_cond = self.calculate_mineral_conductivity(method = method, min_idx= 23, sol_idx = index)
			else:
				self.rwd_wds_cond = np.zeros(len(self.T))
				
			if np.mean(self.perov_frac) != 0:
				self.perov_cond = self.calculate_mineral_conductivity(method = method, min_idx= 24, sol_idx = index)
			else:
				self.perov_cond = np.zeros(len(self.T))
				
			if np.mean(self.mixture_frac) != 0:
				self.mixture_cond = self.calculate_mineral_conductivity(method = method, min_idx= 25, sol_idx = index)
			else:
				self.mixture_cond = np.zeros(len(self.T))
	
			if np.mean(self.other_frac) != 0:
				self.other_cond = self.calculate_mineral_conductivity(method = method, min_idx= 26, sol_idx = index)
			else:
				self.other_cond = np.zeros(len(self.T))
					
			self.phase_mixing_function(method = pide.phs_mix_method, melt_method = pide.phs_melt_mix_method, indexing_method= method, sol_idx = index)
		
		self.cond_calculated = True
		
		if method == 'array':
			return self.bulk_cond
		elif method == 'index':
			return self.bulk_cond[index]
		
	def calculate_seismic_velocities(self, mixing_method = 'HS'):
	
		"""
		Calculates seismic velocities of the composition array with the given mixing function.
		
		cansu
		"""
		id_list_global = []
		if pide.solid_phase_method == 2:
		
			if np.mean(self.quartz_frac) != 0.0:
				if self.seis_property_overwrite[0] == False:
					#handling quartz transitions for calculating velocities with entered T and P
					quartz_id_list = np.array(["bqz"] * len(self.T))
					#calculating transitions
					idx_coesite = Boyd1960_quartz_coesite_trans(T = self.T, P = self.p)
					idx_alpha = alpha_beta_quartz(T = self.T)
					try:
						quartz_id_list[idx_coesite] = "coe"
						quartz_id_list[idx_alpha] = "aqz"
					except IndexError:
						pass
				else:
					quartz_id_list = np.array([self.quartz_seis_selection] * len(self.T))
				
				id_list_global.append(quartz_id_list)
				
			if np.mean(self.plag_frac) != 0.0:
				
				if self.seis_property_overwrite[1] == False:
					plag_id_list = np.array([self.mat_ref[12][pide.minerals_cond_selections[1]]] * len(self.T))
				else:
					plag_id_list = np.array([self.plag_seis_selection] * len(self.T))
				
				id_list_global.append(plag_id_list)

			if np.mean(self.amp_frac) != 0.0:
				
				if self.seis_property_overwrite[2] == False:
					amp_id_list = np.array([self.mat_ref[13][pide.minerals_cond_selections[2]]] * len(self.T))
				else:
					amp_id_list = np.array([self.amp_seis_selection] * len(self.T))
				
				id_list_global.append(amp_id_list)

			if np.mean(self.kfelds_frac) != 0.0:
				
				if self.seis_property_overwrite[3] == False:
					kfelds_id_list = np.array([self.mat_ref[14][pide.minerals_cond_selections[3]]] * len(self.T))
				else:
					kfelds_id_list = np.array([self.kfelds_seis_selection] * len(self.T))
				
				id_list_global.append(kfelds_id_list)

			if np.mean(self.opx_frac) != 0.0:
				
				if self.seis_property_overwrite[4] == False:
					opx_id_list = np.array([self.mat_ref[15][pide.minerals_cond_selections[4]]] * len(self.T))
				else:
					opx_id_list = np.array([self.opx_seis_selection] * len(self.T))
				
				id_list_global.append(opx_id_list)

			if np.mean(self.cpx_frac) != 0.0:
				
				if self.seis_property_overwrite[5] == False:
					cpx_id_list = np.array([self.mat_ref[16][pide.minerals_cond_selections[5]]] * len(self.T))
				else:
					cpx_id_list = np.array([self.cpx_seis_selection] * len(self.T))
				
				id_list_global.append(cpx_id_list)

			if np.mean(self.mica_frac) != 0.0:
				
				if self.seis_property_overwrite[6] == False:
					mica_id_list = np.array([self.mat_ref[17][pide.minerals_cond_selections[6]]] * len(self.T))
				else:
					mica_id_list = np.array([self.mica_seis_selection] * len(self.T))
				
				id_list_global.append(mica_id_list)

			if np.mean(self.garnet_frac) != 0.0:
				
				if self.seis_property_overwrite[7] == False:
					garnet_id_list = np.array([self.mat_ref[18][pide.minerals_cond_selections[7]]] * len(self.T))
				else:
					garnet_id_list = np.array([self.garnet_seis_selection] * len(self.T))
				
				id_list_global.append(garnet_id_list)

			if np.mean(self.sulphide_frac) != 0.0:
				
				if self.seis_property_overwrite[8] == False:
					sulphide_id_list = np.array([self.mat_ref[19][pide.minerals_cond_selections[8]]] * len(self.T))
				else:
					sulphide_id_list = np.array([self.sulphide_seis_selection] * len(self.T))
				
				id_list_global.append(sulphide_id_list)

			if np.mean(self.graphite_frac) != 0.0:
				
				if self.seis_property_overwrite[9] == False:
					graphite_id_list = np.array([self.mat_ref[20][pide.minerals_cond_selections[9]]] * len(self.T))
				else:
					graphite_id_list = np.array([self.graphite_seis_selection] * len(self.T))
				
				id_list_global.append(graphite_id_list)

			if np.mean(self.ol_frac) != 0.0:
				
				if self.seis_property_overwrite[10] == False:
					ol_id_list = np.array([self.mat_ref[21][pide.minerals_cond_selections[10]]] * len(self.T))
				else:
					ol_id_list = np.array([self.ol_seis_selection] * len(self.T))
				
				id_list_global.append(ol_id_list)

			if np.mean(self.sp_frac) != 0.0:
				
				if self.seis_property_overwrite[11] == False:
					sp_id_list = np.array([self.mat_ref[22][pide.minerals_cond_selections[11]]] * len(self.T))
				else:
					sp_id_list = np.array([self.sp_seis_selection] * len(self.T))
				
				id_list_global.append(sp_id_list)

			if np.mean(self.rwd_wds_frac) != 0.0:
				
				if self.seis_property_overwrite[12] == False:
					rwd_wds_id_list = np.array([self.mat_ref[23][pide.minerals_cond_selections[12]]] * len(self.T))
				else:
					rwd_wds_id_list = np.array([self.rwd_wds_seis_selection] * len(self.T))
				
				id_list_global.append(rwd_wds_id_list)

			if np.mean(self.perov_frac) != 0.0:
				
				if self.seis_property_overwrite[13] == False:
					perov_id_list = np.array([self.mat_ref[24][pide.minerals_cond_selections[13]]] * len(self.T))
				else:
					perov_id_list = np.array([self.perov_seis_selection] * len(self.T))
				
				id_list_global.append(perov_id_list)

			if np.mean(self.mixture_frac) != 0.0:
				
				if self.seis_property_overwrite[14] == False:
					mixture_id_list = np.array([self.mat_ref[25][pide.minerals_cond_selections[14]]] * len(self.T))
				else:
					mixture_id_list = np.array([self.mixture_seis_selection] * len(self.T))
				
				id_list_global.append(mixture_id_list)

			if np.mean(self.other_frac) != 0.0:
				
				if self.seis_property_overwrite[15] == False:
					other_id_list = np.array([self.mat_ref[26][pide.minerals_cond_selections[15]]] * len(self.T))
				else:
					other_id_list = np.array([self.other_seis_selection] * len(self.T))
				
				id_list_global.append(other_id_list)

	def calculate_density_solid(self):
		
		def linear_density(xfe_input, density_list):
		
			f_dens = interp1d([0,1], density_list)
			
			ref_dens = f_dens(xfe_input)
			
			return ref_dens
						
		min_sel_list = [pide.quartz_cond_selection,pide.plag_cond_selection,
				pide.amp_cond_selection, pide.kfelds_cond_selection, pide.opx_cond_selection,
				pide.cpx_cond_selection, pide.mica_cond_selection, pide.garnet_cond_selection,
				pide.sulphide_cond_selection, pide.graphite_cond_selection, pide.ol_cond_selection,
				pide.sp_cond_selection, pide.rwd_wds_cond_selection, pide.perov_cond_selection,
				pide.mixture_cond_selection, pide.other_cond_selection]
				
		id_mineral_ref_list = [None, None, None, None, ["13","14"],["16","17"], None,
		["10","8"],None, None, ["11", "12"], None, ["11", "12"], None, None, None]
				
		dens_xfe_calc_list = ["fo", "fa", "en", "fs", "py", "alm", "di", "hed"]
			
		if self.density_loaded == False:
					
			if pide.solid_phase_method == 1:
			
				dens_list = [float(self.dens_mat[2][pide.granite_cond_selection])/1e3,
				float(self.dens_mat[3][pide.granulite_cond_selection])/1e3,
				float(self.dens_mat[4][pide.sandstone_cond_selection])/1e3,
				float(self.dens_mat[5][pide.gneiss_cond_selection])/1e3,
				float(self.dens_mat[6][pide.amphibolite_cond_selection])/1e3,
				float(self.dens_mat[7][pide.basalt_cond_selection])/1e3,
				float(self.dens_mat[8][pide.mud_cond_selection])/1e3,
				float(self.dens_mat[9][pide.gabbro_cond_selection])/1e3,
				float(self.dens_mat[10][pide.other_rock_cond_selection])/1e3]
				
				self.density_solids = np.zeros(len(self.T))
				
				for i in range(0,len(self.T)):
				
					density_indv = 0.0
					
					phase_list = [self.granite_frac[i],self.granulite_frac[i],self.sandstone_frac[i],
							self.gneiss_frac[i], self.amphibolite_frac[i], self.basalt_frac[i], self.mud_frac[i],
							 self.gabbro_frac[i], self.other_rock_frac[i]]
					
					for j in range(0,len(phase_list)):
						density_indv = density_indv + (phase_list[j] * dens_list[j])
						
					self.density_solids[i] = density_indv
					
				self.density_loaded = True					
				
			elif pide.solid_phase_method == 2:
							
				dens_list = []
				
				phase_list = [self.quartz_frac, self.plag_frac, self.amp_frac, self.kfelds_frac,
				self.opx_frac, self.cpx_frac, self.mica_frac, self.garnet_frac,
				self.sulphide_frac, self.graphite_frac, self.ol_frac, self.sp_frac,
				self.rwd_wds_frac, self.perov_frac, self.mixture_frac, self.other_frac]
								
				#calling satex object to calculate density under P-T conditions
				satex_isot_object = Isotropy()
				
				for mineral in range(11,27):
					if np.mean(phase_list[mineral-11]) != 0.0:
					
						if type(self.dens_mat[mineral][min_sel_list[mineral-11]]) == float:
							#if no reference given to a materials.json instance take the float as the density
							dens_list.append(float(self.dens_mat[mineral][min_sel_list[mineral-11]])/1e3 * np.ones(len(self.T)))
							
						else:
						
							if self.dens_mat[mineral][min_sel_list[mineral-11]] not in dens_xfe_calc_list:
								#if material reference density is not dependent on xfe
								
								density, aks, amu = satex_isot_object.calculate_seismic_properties(self.dens_mat[mineral][min_sel_list[mineral-11]],
								temperature = self.T, pressure = self.p, return_vp_vs_vbulk=False, return_aktout=False)
								
								dens_list.append(density / 1e3)
								
							else:
								
								#if material reference density is dependent on xfe: ol,opx,cpx,gt,rwd_wds
								ref_0 = self.materials_data[id_mineral_ref_list[mineral-11][0]]['density_298K(kg/m3)']
								ref_1 = self.materials_data[id_mineral_ref_list[mineral-11][1]]['density_298K(kg/m3)']
								
								if 'xFe' in self.name[mineral][min_sel_list[mineral-11]]:
								
									ref_dens = linear_density(xfe_input=pide.xfe_mineral_list[mineral-11], density_list = [ref_0, ref_1])
								
									density, aks, amu = satex_isot_object.calculate_seismic_properties(self.dens_mat[mineral][min_sel_list[mineral-11]],
									temperature = self.T, pressure = self.p, ref_density = ref_dens, return_vp_vs_vbulk=False, return_aktout=False)
								
									dens_list.append(density / 1e3)
									
								else:
								
									xfe_experiment = (100 - self.mg_cond[mineral][min_sel_list[mineral-11]]) * 1e-2 #converting mg number to xFe
									
									ref_dens = linear_density(xfe_input=xfe_experiment, density_list = [ref_0, ref_1])
									
									density, aks, amu = satex_isot_object.calculate_seismic_properties(self.dens_mat[mineral][min_sel_list[mineral-11]],
									temperature = self.T, pressure = self.p, ref_density = ref_dens, return_vp_vs_vbulk=False, return_aktout=False)
								
									dens_list.append(density / 1e3)
									
					else:
					
						dens_list.append(0.0)
							
				self.density_loaded = True

			density_indv = 0.0
						
			for j in range(0,len(phase_list)):
				density_indv = density_indv + (phase_list[j] * dens_list[j])
			
			self.density_solids = density_indv
			
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
		
	def calculate_water_fugacity(self):
	
		if self.water_fugacity_calculated == False:
		
			self.water_fugacity = Pitzer_and_Sterner_1994_PureWaterEOS(T = self.T, P = self.p)
			
			self.water_fugacity_calculated = True
		
	def load_mantle_water_partitions(self, method, **kwargs):
	
		sol_idx = kwargs.pop('sol_idx', 0)
	
		if method == 'array':
			idx_node = None
		elif method == 'index':
			idx_node = sol_idx
		
		if (np.mean(self.melt_fluid_mass_frac) != 0.0) and (pide.fluid_or_melt_method == 1):
		
			#calculating melt/nams water partitioning coefficients if theres any melt in the equilibrium 
		
			if self.water_melt_part_type[4][self.d_water_opx_melt_choice] == 0: #index 4 because it is in 4th index at the minerals list
				
				self.d_melt_opx = self.water_melt_part_function[4][self.d_water_opx_melt_choice] * np.ones(len(self.T))
				
			else:
				
				self.d_melt_opx = eval(self.water_melt_part_name[4][self.d_water_opx_melt_choice] + '(al_opx = self.al_opx[idx_node], p = self.p[idx_node], p_change = self.water_melt_part_pchange[4][self.d_water_opx_melt_choice], d_opx_ol = None, method = method)')
			
			if self.water_melt_part_type[5][self.d_water_cpx_melt_choice] == 0:
			
				self.d_melt_cpx = self.water_melt_part_function[5][self.d_water_cpx_melt_choice] * np.ones(len(self.T))
				
			else:
				
				self.d_melt_cpx = eval(self.water_melt_part_name[5][self.d_water_cpx_melt_choice] + '(al_opx = self.al_opx[idx_node], p = self.p[idx_node], p_change = self.water_melt_part_pchange[5][self.d_water_cpx_melt_choice], d_opx_ol = None, method = method)')
			
			if self.water_melt_part_type[7][self.d_water_garnet_melt_choice] == 0:
			
				self.d_melt_garnet = self.water_melt_part_function[7][self.d_water_garnet_melt_choice] * np.ones(len(self.T))
				
			else:
				
				self.d_melt_garnet = eval(self.water_melt_part_name[10][self.d_water_ol_melt_choice] + '(al_opx = self.al_opx[idx_node], p = self.p[idx_node], p_change = self.water_melt_part_pchange[7][self.d_water_garnet_melt_choice], d_opx_ol = None, method = method)')
			
			if self.water_melt_part_type[10][self.d_water_ol_melt_choice] == 0:
			
				self.d_melt_ol = self.water_melt_part_function[10][self.d_water_ol_melt_choice] * np.ones(len(self.T))
				
			else:
				
				self.d_melt_ol = eval(self.water_melt_part_name + '(al_opx = self.al_opx[idx_node], p = self.p[idx_node], p_change = self.water_melt_part_pchange[10][self.d_water_ol_melt_choice], d_opx_ol = None, method = method)')
		
		#determining chosen nam/olivine water partitioning coefficients.
		if self.water_ol_part_type[4][self.d_water_opx_ol_choice] == 0:
		
			self.d_opx_ol = self.water_ol_part_function[4][self.d_water_opx_ol_choice] * np.ones(len(self.T))
			
		else:
			
			self.d_opx_ol = eval(self.water_ol_part_name[4][self.d_water_opx_ol_choice] + '(al_opx = self.al_opx[idx_node], p = self.p[idx_node], p_change = self.water_ol_part_pchange[4][self.d_water_opx_ol_choice], d_opx_ol = 0, method = method)')
		
		if self.water_ol_part_type[5][self.d_water_cpx_ol_choice] == 0:
		
			self.d_cpx_ol = self.water_ol_part_function[5][self.d_water_cpx_ol_choice] * np.ones(len(self.T))
			
		else:
			
			self.d_cpx_ol = eval(self.water_ol_part_name[5][self.d_water_cpx_ol_choice] + '(al_opx = self.al_opx[idx_node], p = self.p[idx_node], p_change = self.water_ol_part_pchange[5][self.d_water_cpx_ol_choice], d_opx_ol = self.d_opx_ol[idx_node], method = method)')
		
		if self.water_ol_part_type[7][self.d_water_garnet_ol_choice] == 0:
		
			self.d_garnet_ol = self.water_ol_part_function[7][self.d_water_garnet_ol_choice] * np.ones(len(self.T))
			
		else:
			
			self.d_garnet_ol = eval(self.water_ol_part_name[7][self.d_water_garnet_ol_choice] + '(al_opx = self.al_opx[idx_node], p = self.p[idx_node], p_change = self.water_ol_part_pchange[7][self.d_water_garnet_ol_choice], d_opx_ol = self.d_opx_ol[idx_node], method = method)')
		
		
	def load_mantle_transition_zone_water_partitions(self, method, **kwargs):
	
		sol_idx = kwargs.pop('sol_idx', 0)
	
		if method == 'array':
			idx_node = None
		elif method == 'index':
			idx_node = sol_idx
	
		if self.water_rwd_wds_part_type[7][self.d_water_garnet_rwd_wds_choice] == 0:
			
			self.d_garnet_rwd_wds = self.water_rwd_wds_part_function[7][self.d_water_garnet_rwd_wds_choice] * np.ones(len(self.T))
		else:
			
			self.d_garnet_rwd_wds = eval(self.water_rwd_wds_part_name[7][self.d_water_garnet_rwd_wds_choice] + '(p = self.p[idx_node],\
			p_change = self.water_rwd_wds_part_pchange[7][self.d_water_garnet_rwd_wds_choice], method = method)')
			
		if self.water_rwd_wds_part_type[13][self.d_water_perov_rwd_wds_choice] == 0:
			
			self.d_perov_rwd_wds = self.water_rwd_wds_part_function[13][self.d_water_perov_rwd_wds_choice] * np.ones(len(self.T))
			
		else:
			
			self.d_perov_rwd_wds = eval(self.water_rwd_wds_part_name[13][self.d_water_perov_rwd_wds_choice] + '(p = self.p[idx_node],\
			p_change = self.water_rwd_wds_part_pchange[13][self.d_water_perov_rwd_wds_choice], method = method)')
			
		if self.water_rwd_wds_part_type[5][self.d_water_cpx_rwd_wds_choice] == 0:
			
			self.d_cpx_rwd_wds = self.water_rwd_wds_part_function[5][self.d_water_cpx_rwd_wds_choice] * np.ones(len(self.T))
			
		else:
			
			self.d_cpx_rwd_wds = eval(self.water_rwd_wds_part_name[5][self.d_water_cpx_rwd_wds_choice] + '(p = self.p[idx_node],\
			p_change = self.water_rwd_wds_part_pchange[5][self.d_water_cpx_rwd_wds_choice], method = method)')
		
	def mantle_water_distribute(self, method, **kwargs):
	
		sol_idx = kwargs.pop('sol_idx', 0)
	
		if method == 'array':
			idx_node = None
		elif method == 'index':
			idx_node = sol_idx
						
		if (np.mean(self.melt_fluid_mass_frac) != 0.0) and (pide.fluid_or_melt_method == 1):
		
			self.melt_water = np.zeros(len(self.T))
		
			#peridotite melt partitioning
			self.d_per_melt = (self.ol_frac_wt * self.d_melt_ol) +\
					(self.opx_frac_wt * self.d_melt_opx) +\
					(self.cpx_frac_wt * self.d_melt_cpx) +\
					(self.garnet_frac_wt * self.d_melt_garnet)
					
			self.melt_water[idx_node] = self.calculate_melt_water(h2o_bulk = self.bulk_water[idx_node], melt_mass_frac = self.melt_fluid_mass_frac[idx_node], d_per_melt = self.d_per_melt[idx_node])

			#reassigning the zero mass frac melt layers using pre-mapped indexing array.
			if idx_node == None:
				self.melt_water[self.melt_fluid_mass_frac <= 0.0] = 0.0
				
			self.solid_water[idx_node] = (self.bulk_water[idx_node] * self.d_per_melt[idx_node]) /\
				(self.melt_fluid_mass_frac[idx_node] + ((1.0 - self.melt_fluid_mass_frac[idx_node]) * self.d_per_melt[idx_node]))
				
		else:
		
			self.solid_water[idx_node] = self.bulk_water[idx_node]
		
		#calculating olivine water content from bulk water using mineral partitioning contents
				
		pide.ol_water[idx_node] = self.solid_water[idx_node] / (self.ol_frac_wt[idx_node] + ((self.opx_frac_wt[idx_node] * self.d_opx_ol[idx_node]) +\
		(self.cpx_frac_wt[idx_node] * self.d_cpx_ol[idx_node]) + (self.garnet_frac_wt[idx_node] * self.d_garnet_ol[idx_node])))
		
		#calculating opx water content
		pide.opx_water[idx_node] = pide.ol_water[idx_node] * self.d_opx_ol[idx_node]
		pide.opx_water[self.opx_frac == 0] = 0.0
		
		#calculating cpx water content
		pide.cpx_water[idx_node] = pide.ol_water[idx_node] * self.d_cpx_ol[idx_node]
		pide.cpx_water[self.cpx_frac == 0] = 0.0
		
		#calculating garnet water content
		pide.garnet_water[idx_node] = pide.ol_water[idx_node] * self.d_garnet_ol[idx_node]
		pide.garnet_water[self.garnet_frac == 0] = 0.0
		
	def transition_zone_water_distribute(self, method, **kwargs):
	
		sol_idx = kwargs.pop('sol_idx', 0)
	
		if method == 'array':
			idx_node = None
		elif method == 'index':
			idx_node = sol_idx
			
		#assuming not melting in transition zone
		self.solid_water[idx_node] = self.bulk_water[idx_node]
		
		pide.rwd_wds_water[idx_node] = self.solid_water[idx_node] / (self.rwd_wds_frac_wt[idx_node] + ((self.cpx_frac_wt[idx_node] * self.d_cpx_rwd_wds[idx_node]) +\
		(self.perov_frac_wt[idx_node] * self.d_perov_rwd_wds[idx_node]) + (self.garnet_frac_wt[idx_node] * self.d_garnet_rwd_wds[idx_node])))
		
		#calculating cpx water content
		pide.cpx_water[idx_node] = pide.rwd_wds_water[idx_node] * self.d_cpx_rwd_wds[idx_node]
		pide.cpx_water[self.cpx_frac == 0] = 0.0
		
		#calculating garnet water content
		pide.garnet_water[idx_node] = pide.rwd_wds_water[idx_node] * self.d_garnet_rwd_wds[idx_node]
		pide.garnet_water[self.garnet_frac == 0] = 0.0
		
		#calculating perovskite water content
		pide.perov_water[idx_node] = pide.rwd_wds_water[idx_node] * self.d_perov_rwd_wds[idx_node]
		pide.perov_water[self.perov_frac == 0] = 0.0
							
	def calculate_melt_water(self, h2o_bulk, melt_mass_frac, d_per_melt):

		#Calculating the h2o content of melt that is in equilibrium with the entered solid-mixture, from Sifre et al. (2014)
		melt_water = h2o_bulk / (melt_mass_frac + ((1.0 - melt_mass_frac) * d_per_melt))

		return melt_water
		
	def conditional_fugacity_calculations(self, min_idx, sol_choice):
	
		if self.mineral_sol_fug[min_idx][sol_choice] == 'Y':
			if self.water_fugacity_calculated == False:
				self.calculate_water_fugacity()
			water_fug = self.water_fugacity	
				
		else:
		
			water_fug = np.zeros(1)
				
		if self.mineral_sol_o2_fug[min_idx][sol_choice] == 'Y':
		
			o2_fug = self.calculate_fugacity(mode = pide.o2_buffer)
			
		else:
			o2_fug = np.zeros(1)
			
		return water_fug, o2_fug
			
	def calculate_mineral_water_solubility(self, method, mineral_name, **kwargs):
	
		sol_idx = kwargs.pop('sol_idx', 0)
	
		if method == 'array':
			idx_node = None
		elif method == 'index':
			idx_node = sol_idx
			
		if mineral_name == 'ol':
			
			min_idx = 10
			water_fug, o2_fug = self.conditional_fugacity_calculations(min_idx = min_idx, sol_choice= self.ol_sol_choice)
				
			if ('From' in self.mineral_sol_name[min_idx][self.ol_sol_choice]) == True:
			
				if ('Opx' in self.mineral_sol_name[min_idx][self.ol_sol_choice]) == True:
				
					
					try:
						max_mineral_water = self.max_opx_water / self.d_opx_ol
					except AttributeError:
						
						self.max_opx_water = self.rerun_sol(mineral = 'opx', method = method)
						max_mineral_water = self.max_opx_water / self.d_opx_ol
						self.max_ol_water = np.array(max_mineral_water) 
			else:
				try:
					max_mineral_water = eval(self.mineral_sol_name[min_idx][self.ol_sol_choice] + "(T = self.T[idx_node],P = self.p[idx_node],depth = self.depth[idx_node],h2o_fug = water_fug[idx_node], o2_fug = o2_fug, fe_ol = self.ol_xfe[idx_node], ti_ol = self.ti_ol[idx_node],method = 'array')")
					self.max_ol_water = np.array(max_mineral_water)
				except AttributeError:
					raise AttributeError('You have to enter ti_ol as a different parameter by the pide.set_parameter method')
				
		elif mineral_name == 'opx':
			
			min_idx = 4
				
			if ('From' in self.mineral_sol_name[min_idx][self.opx_sol_choice]) == True:
			
				if ('Ol' in self.mineral_sol_name[min_idx][self.opx_sol_choice]) == True:
									
					try:
						max_mineral_water = self.max_ol_water * self.d_opx_ol
					except AttributeError:
						
						self.max_ol_water = self.rerun_sol(mineral = 'ol', method = method)
						max_mineral_water = self.max_ol_water * self.d_opx_ol
						self.max_opx_water = np.array(max_mineral_water)
					
			else:
				
				max_mineral_water = eval(self.mineral_sol_name[min_idx][self.opx_sol_choice] + "(T = self.T[idx_node],P = self.p[idx_node],depth = self.depth[idx_node],h2o_fug = water_fug[idx_node], o2_fug = o2_fug, fe_opx = self.opx_xfe[idx_node], al_opx = self.al_opx[idx_node], method = 'array')")
				self.max_opx_water = np.array(max_mineral_water)
			
		elif mineral_name == 'cpx':
			
			min_idx = 5
			
			water_fug, o2_fug = self.conditional_fugacity_calculations(min_idx = min_idx, sol_choice= self.cpx_sol_choice)
			
				
			if ('From' in self.mineral_sol_name[min_idx][self.cpx_sol_choice]) == True:
			
				if ('Ol' in self.mineral_sol_name[min_idx][self.cpx_sol_choice]) == True:
														
					try:
						max_mineral_water = self.max_ol_water * self.d_cpx_ol
					except AttributeError:
						self.max_ol_water = self.rerun_sol(mineral = 'ol', method = method)
						max_mineral_water = self.max_ol_water * self.d_cpx_ol
						self.max_cpx_water = np.array(max_mineral_water)
									
				elif ('Opx' in self.mineral_sol_name[min_idx][self.cpx_sol_choice]) == True:
									
					try:
						max_mineral_water = self.max_ol_water * (self.d_cpx_ol/self.d_opx_ol)
					except AttributeError:
						self.max_opx_water = self.rerun_sol(mineral = 'opx', method = method)
						max_mineral_water = self.max_opx_water * (self.d_cpx_ol/self.d_opx_ol)
						self.max_cpx_water = np.array(max_mineral_water)
						
				elif ('Rwd_Wds' in self.mineral_sol_name[min_idx][self.cpx_sol_choice]) == True:
				
					try:
						max_mineral_water = self.max_rwd_wds_water * self.d_cpx_rwd_wds
					except AttributeError:
						self.max_rwd_wds_water = self.rerun_sol(mineral = 'rwd_wds', method = method)
						max_mineral_water = self.max_rwd_wds_water * self.d_cpx_rwd_wds
						self.max_cpx_water = np.array(max_mineral_water)	
					
						
			else:
				
				max_mineral_water = eval(self.mineral_sol_name[min_idx][self.cpx_sol_choice] + "(T = self.T[idx_node],P = self.p[idx_node],depth = self.depth[idx_node],h2o_fug = water_fug[idx_node], o2_fug = o2_fug, fe_opx = self.cpx_xfe[idx_node], al_opx = self.al_cpx[idx_node], method = 'array')")
			
		elif mineral_name == 'garnet':
			
			min_idx = 7
			water_fug, o2_fug = self.conditional_fugacity_calculations(min_idx = min_idx, sol_choice= self.garnet_sol_choice)
				
			if ('From' in self.mineral_sol_name[min_idx][self.garnet_sol_choice]) == True:
			
				if ('Ol' in self.mineral_sol_name[min_idx][self.garnet_sol_choice]) == True:
									
					try:
						max_mineral_water = self.max_ol_water * self.d_garnet_ol
					except AttributeError:
						self.max_ol_water = self.rerun_sol(mineral = 'garnet', method = method)
						max_mineral_water = self.max_ol_water * self.d_garnet_ol
						self.max_garnet_water = np.array(max_mineral_water)
					
				elif ('Opx' in self.mineral_sol_name[min_idx][self.garnet_sol_choice]) == True:
					
					try:
						max_mineral_water = self.max_opx_water * (self.d_garnet_ol/self.d_opx_ol)
					except AttributeError:
						self.max_opx_water = self.rerun_sol(mineral = 'opx', method = method)
						max_mineral_water = self.max_opx_water * (self.d_garnet_ol/self.d_opx_ol)
						self.max_garnet_water = np.array(max_mineral_water)
						
				elif ('Rwd_Wds' in self.mineral_sol_name[min_idx][self.garnet_sol_choice]) == True:
				
					try:
						max_mineral_water = self.max_rwd_wds_water * self.d_cpx_rwd_wds
					except AttributeError:
						self.max_rwd_wds_water = self.rerun_sol(mineral = 'rwd_wds', method = method)
						max_mineral_water = self.max_rwd_wds_water * self.d_cpx_rwd_wds
						self.max_garnet_water = np.array(max_mineral_water)
					
			else:
				
				max_mineral_water = eval(self.mineral_sol_name[min_idx][self.garnet_sol_choice] + "(T = self.T[idx_node],P = self.p[idx_node],depth = self.depth[idx_node],h2o_fug = water_fug[idx_node], o2_fug = o2_fug, fe_garnet = self.garnet_xfe[idx_node], method = 'array')")
		
		elif mineral_name == 'rwd_wds':
		
			min_idx = 12
			water_fug, o2_fug = self.conditional_fugacity_calculations(min_idx = min_idx, sol_choice = self.rwd_wds_sol_choice)
			
			max_mineral_water = eval(self.mineral_sol_name[min_idx][self.garnet_sol_choice] + "(T = self.T[idx_node],P = self.p[idx_node],depth = self.depth[idx_node],\
			h2o_fug = water_fug[idx_node], o2_fug = o2_fug, fe_rwd_wds = self.rwd_wds_xfe[idx_node], method = 'array')")
			self.max_rwd_wds_water = np.array(max_mineral_water)
			
		elif mineral_name == 'perov':
		
			min_idx = 13 
			water_fug, o2_fug = self.conditional_fugacity_calculations(min_idx = min_idx, sol_choice = self.perov_sol_choice)
			
			if ('From' in self.mineral_sol_name[min_idx][self.perov_sol_choice]) == True:
			
				if ('Rwd_Wds' in self.mineral_sol_name[min_idx][self.perov_sol_choice]) == True:
				
					try:
						max_mineral_water = self.max_rwd_wds_water * self.d_perov_rwd_wds
					except AttributeError:
						self.max_rwd_wds_water = self.rerun_sol(mineral = 'rwd_wds', method = method)
						max_mineral_water = self.max_rwd_wds_water * self.d_perov_rwd_wds
						self.max_perov_water = np.array(max_mineral_water)
			
		if method == 'array':
			if len(max_mineral_water) == 1:
				return max_mineral_water[0]
			else:
				return max_mineral_water
		elif method == 'index':
			return max_mineral_water
		
	def rerun_sol(self, mineral, method):
		
		if mineral == 'ol':
			water_calc = self.calculate_mineral_water_solubility(mineral_name = 'ol', method = method)
		elif mineral == 'opx':
			water_calc= self.calculate_mineral_water_solubility(mineral_name = 'opx', method = method)
		elif mineral == 'cpx':
			water_calc = self.calculate_mineral_water_solubility(mineral_name = 'cpx', method = method)
		elif mineral == 'garnet':
			water_calc = self.calculate_mineral_water_solubility(mineral_name = 'garnet', method = method)
		elif mineral == 'rwd_wds':
			water_calc = self.calculate_mineral_water_solubility(mineral_name = 'rwd_wds', method = method)
		elif mineral == 'perov':
			water_calc = self.calculate_mineral_water_solubility(mineral_name = 'perov', method = method)
			
		return water_calc
		
	def calculate_bulk_mantle_water_solubility(self, method, **kwargs):
	
		self.max_ol_water = self.calculate_mineral_water_solubility(mineral_name = 'ol', method = method)
		self.max_opx_water = self.calculate_mineral_water_solubility(mineral_name = 'opx', method = method)
		self.max_cpx_water = self.calculate_mineral_water_solubility(mineral_name = 'cpx', method = method)
		self.max_garnet_water = self.calculate_mineral_water_solubility(mineral_name = 'garnet', method = method)
		
		self.max_bulk_water = (self.max_ol_water * self.ol_frac_wt) + (self.max_opx_water * self.opx_frac_wt) + (self.max_cpx_water * self.cpx_frac_wt) + (self.max_garnet_water * self.garnet_frac_wt)
		
		return self.max_bulk_water
		
	def calculate_transition_zone_water_solubility(self, method, **kwargs):
	
		self.max_rwd_wds_water = self.calculate_mineral_water_solubility(mineral_name = 'rwd_wds', method = method)
		self.max_cpx_water = self.calculate_mineral_water_solubility(mineral_name = 'cpx', method = method)
		self.max_garnet_water = self.calculate_mineral_water_solubility(mineral_name = 'garnet', method = method)
		self.max_perov_water = self.calculate_mineral_water_solubility(mineral_name = 'perov', method = method)
		
		self.max_bulk_water = (self.max_rwd_wds_water * self.rwd_wds_frac_wt) +  (self.max_cpx_water * self.cpx_frac_wt) + (self.max_garnet_water * self.garnet_frac_wt) + (self.max_perov_water * self.perov_frac_wt)

		return self.max_bulk_water

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'