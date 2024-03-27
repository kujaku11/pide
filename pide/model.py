#!/usr/bin/env python3

import numpy as np

import pide
from geodyn.material_process import return_material_bool

#importing the function
from geodyn.deform_cond import plastic_strain_2_conductivity

def run_conductivity_model(index_list, material, pide_object, t_array, p_array, melt_array):

	#global function to run conductivity model. designed to be global def to run parallel with multiprocessing
	
	#setting temperatures at the pide_object
	pide_object.set_temperature(t_array[index_list])
	pide_object.set_pressure(p_array[index_list])
	
	pide_object.set_o2_buffer(material.o2_buffer)
	pide_object.set_solid_phs_mix_method(material.solid_phase_mixing_idx)
	pide_object.set_solid_melt_fluid_mix_method(material.melt_fluid_phase_mixing_idx)
	
	if melt_array[index_list].any() > 0.0:
		material.melt_fluid_incorporation_method == 'field' #if melt exists it overwrites the field value.
		

	if material.melt_fluid_incorporation_method == 'value':

		if material.melt_or_fluid == 'melt':
			pide_object.set_melt_or_fluid_mode('melt')
		else:
			pide_object.set_melt_or_fluid_mode('fluid')

		pide_object.set_melt_fluid_frac(material.melt_fluid_frac)

	elif material.melt_fluid_incorporation_method == 'field':

		pide_object.set_melt_or_fluid_mode('melt') #only melt field can be taken from the area
		pide_object.set_melt_fluid_frac(melt_array[index_list])

	else:
		pass
		
	pide_object.set_watercalib(ol = material.water_calib['ol'], px_gt = material.water_calib['px_gt'], feldspar = material.water_calib['feldspar'])
	pide_object.set_o2_buffer(o2_buffer = material.o2_buffer)
		
	#adjusting material parameters for the pide_object
	if material.calculation_type == 'mineral':
	
		pide_object.set_composition_solid_mineral(ol = material.composition['ol'],
		opx = material.composition['opx'],
		cpx = material.composition['cpx'],
		garnet = material.composition['garnet'],
		mica = material.composition['mica'],
		amp = material.composition['amp'],
		quartz = material.composition['quartz'],
		plag = material.composition['plag'],
		kfelds = material.composition['kfelds'],
		sulphide = material.composition['sulphide'],
		graphite = material.composition['graphite'],
		mixture = material.composition['mixture'],
		sp = material.composition['sp'],
		wds = material.composition['wds'],
		rwd = material.composition['rwd'],
		perov = material.composition['perov'],
		other = material.composition['other'])
		
		if material.solid_phase_mixing_idx == 0:
		
			pide_object.set_phase_interconnectivities(ol = material.interconnectivities['ol'],
			opx = material.interconnectivities['opx'],
			cpx = material.interconnectivities['cpx'],
			garnet = material.interconnectivities['garnet'],
			mica = material.interconnectivities['mica'],
			amp = material.interconnectivities['amp'],
			quartz = material.interconnectivities['quartz'],
			plag = material.interconnectivities['plag'],
			kfelds = material.interconnectivities['kfelds'],
			sulphide = material.interconnectivities['sulphide'],
			graphite = material.interconnectivities['graphite'],
			mixture = material.interconnectivities['mixture'],
			sp = material.interconnectivities['sp'],
			wds = material.interconnectivities['wds'],
			rwd = material.interconnectivities['rwd'],
			perov = material.interconnectivities['perov'],
			other = material.interconnectivities['other'],
			)
			
		if material.water_distr == False:
		
			pide_object.set_mineral_water(ol = material.water['ol'],
			opx = material.water['opx'],
			cpx = material.water['cpx'],
			garnet = material.water['garnet'],
			mica = material.water['mica'],
			amp = material.water['amp'],
			quartz = material.water['quartz'],
			plag = material.water['plag'],
			kfelds = material.water['kfelds'],
			sulphide = material.water['sulphide'],
			graphite = material.water['graphite'],
			mixture = material.water['mixture'],
			sp = material.water['sp'],
			wds = material.water['wds'],
			rwd = material.water['rwd'],
			perov = material.water['perov'],
			other = material.water['other'])
			
		else:
		
			pide_object.set_bulk_water(material.water['bulk'])
			pide_object.set_mantle_water_partitions(opx_ol = material.mantle_water_part['opx_ol'],
			cpx_ol = material.mantle_water_part['cpx_ol'],
			garnet_ol = material.mantle_water_part['garnet_ol'],
			ol_melt = material.mantle_water_part['ol_melt'],
			opx_melt = material.mantle_water_part['opx_melt'],
			cpx_melt = material.mantle_water_part['cpx_melt'],
			garnet_melt = material.mantle_water_part['garnet_melt'])
			pide_object.mantle_water_distribute(method = 'array')
			
		pide_object.set_mineral_conductivity_choice(ol = material.el_cond_selections['ol'],
			opx = material.el_cond_selections['opx'],
			cpx = material.el_cond_selections['cpx'],
			garnet = material.el_cond_selections['garnet'],
			mica = material.el_cond_selections['mica'],
			amp = material.el_cond_selections['amp'],
			quartz = material.el_cond_selections['quartz'],
			plag = material.el_cond_selections['plag'],
			kfelds = material.el_cond_selections['kfelds'],
			sulphide = material.el_cond_selections['sulphide'],
			graphite = material.el_cond_selections['graphite'],
			mixture = material.el_cond_selections['mixture'],
			sp = material.el_cond_selections['sp'],
			wds = material.el_cond_selections['wds'],
			rwd = material.el_cond_selections['rwd'],
			perov = material.el_cond_selections['perov'],
			other = material.el_cond_selections['other'])
									
	elif material.calculation_type == 'rock':
	
		pide_object.set_composition_solid_rock(granite = material.composition['granite'],
		granulite = material.composition['granulite'],
		sandstone = material.composition['sandstone'],
		gneiss = material.composition['gneiss'],
		amphibolite = material.composition['amphibolite'],
		basalt = material.composition['basalt'],
		mud = material.composition['mud'],
		gabbro = material.composition['gabbro'],
		other_rock = material.composition['other_rock'])
		
		if material.solid_phase_mixing_idx == 0:
			
			pide_object.set_phase_interconnectivities(granite = material.interconnectivities['granite'],
			granulite = material.interconnectivities['granulite'],
			sandstone = material.interconnectivities['sandstone'],
			gneiss = material.interconnectivities['gneiss'],
			amphibolite = material.interconnectivities['amphibolite'],
			basalt = material.interconnectivities['basalt'],
			mud = material.interconnectivities['mud'],
			gabbro = material.interconnectivities['gabbro'],
			other_rock = material.interconnectivities['other_rock'])
			
		if material.water_distr == False:
		
			pide_object.set_rock_water(granite = material.water['granite'],
			granulite = material.water['granulite'],
			sandstone = material.water['sandstone'],
			gneiss = material.water['gneiss'],
			amphibolite = material.water['amphibolite'],
			basalt = material.water['basalt'],
			mud = material.water['mud'],
			gabbro = material.water['gabbro'],
			other_rock = material.water['other_rock'])
			
		pide_object.set_rock_conductivity_choice(granite = material.el_cond_selections['granite'],
			granulite = material.el_cond_selections['granulite'],
			sandstone = material.el_cond_selections['sandstone'],
			gneiss = material.el_cond_selections['gneiss'],
			amphibolite = material.el_cond_selections['amphibolite'],
			basalt = material.el_cond_selections['basalt'],
			mud = material.el_cond_selections['mud'],
			gabbro = material.el_cond_selections['gabbro'],
			other_rock = material.el_cond_selections['other_rock'])
	
	if material.melt_fluid_cond_selection != None:
		if material.melt_or_fluid == 'melt':
			
			pide_object.set_melt_fluid_conductivity_choice(melt = material.melt_fluid_cond_selection)
			if material.melt_fluid_phase_mixing_idx == 0:
				pide_object.set_melt_fluid_interconnectivity(melt = material.melt_fluid_m)
		elif material.melt_or_fluid == 'fluid':
			pide_object.set_melt_fluid_conductivity_choice(fluid = material.melt_fluid_cond_selection)
			pide_object.set_fluid_properties(salinity = material.fluid_salinity)
			if material.melt_fluid_phase_mixing_idx == 0:
				pide_object.set_melt_fluid_interconnectivity(fluid = material.melt_fluid_m)
		
	c = pide_object.calculate_conductivity(method = 'array')
	
	return c
	
def run_deform2cond(index_number,p_strain, background_cond, max_cond, low_deformation_threshold, high_deformation_threshold, function_method, conductivity_decay_factor,strain_decay_factor):
	
	#Global function to link deformation and conductivity.
	if (background_cond[index_number[0],index_number[1],index_number[2]] == np.nan) or (max_cond[index_number[0],index_number[1],index_number[2]] == np.nan): 
	
		c = np.nan
		str_dcy = np.nan
		cnd_dcy = np.nan
		msft = np.nan
	
	else:
	
		if p_strain[index_number[0],index_number[1],index_number[2]] <= low_deformation_threshold:
			
			c = background_cond[index_number[0],index_number[1],index_number[2]]
			str_dcy = np.nan
			cnd_dcy = np.nan
			msft = np.nan
			
		elif p_strain[index_number[0],index_number[1],index_number[2]] >= high_deformation_threshold:
			
			c = max_cond[index_number[0],index_number[1],index_number[2]]
			str_dcy = np.nan
			cnd_dcy = np.nan
			msft = np.nan
			
		else:
			
			c, str_dcy, cnd_dcy, msft = plastic_strain_2_conductivity(strain = p_strain[index_number[0],index_number[1],index_number[2]],low_cond = background_cond[index_number[0],index_number[1],index_number[2]],
				high_cond=max_cond[index_number[0],index_number[1],index_number[2]],low_strain=low_deformation_threshold, high_strain=high_deformation_threshold,
				function_method = function_method, conductivity_decay_factor = conductivity_decay_factor, strain_decay_factor = strain_decay_factor, return_all_params = True)
	
	
	return c, str_dcy, cnd_dcy, msft

class Model(object):

	def __init__(self, material_list, material_array, T, P, model_type = 'underworld_2d', material_list_2 = None,
	melt = None, p_strain = None, strain_rate = None, material_node_skip_rate_list = None):

		self.material_list = material_list
		self.material_list_2 = material_list_2
		self.material_array = material_array
		self.T = T
		self.P = P
		self.model_type = model_type
		self.melt_frac = melt
		self.p_strain = p_strain
		self.strain_rate = strain_rate
		self.material_node_skip_rate_list = material_node_skip_rate_list
		
	def calculate_conductivity(self,type = 'background', num_cpu = 1):
	
		if num_cpu > 1:
		
			import multiprocessing
			import os
			from functools import partial
			
			max_num_cores = os.cpu_count()
			
			if num_cpu > max_num_cores:
				raise ValueError('There are not enough cpus in the machine to run this action with ' + str(num_cpu) + ' cores.')

		cond = np.zeros_like(self.T)
		
		if type == 'background':
			material_list_holder = [self.material_list]
		elif type == 'maximum':
			material_list_holder = [self.material_list_2]
		else:
			material_list_holder = [self.material_list]
			if self.material_list_2 != None:
				material_list_holder.append(self.material_list_2)
		
		cond_list = []
			
		for l in range(0,len(material_list_holder)):
			print('Initiating calculation for the materials appended to the model.')
			print('##############################################################')
			for i in range(0,len(material_list_holder[l])):
	
				#determining the material indexes from the material array
				
				if self.material_node_skip_rate_list != None:
					if self.material_node_skip_rate_list[i] != None:
						mat_skip = self.material_node_skip_rate_list[i]
					else:
						mat_skip = None
				else:
					mat_skip = None
				
				#getting the relevant indexes with information given for it
				
				material_idx = return_material_bool(material_index = material_list_holder[l][i].material_index,
				model_array = self.material_array, material_skip = mat_skip, model_type = self.model_type)		
				
				#setting up the object for the material
				mat_pide_obj = pide.pide()
				
				if material_list_holder[l][i].calculation_type != 'value':
					mat_pide_obj.set_solid_phase_method(material_list_holder[l][i].calculation_type)
				else:
					num_cpu = 1 #defaulting num_cpu for 1 since it is not needed for value-method
					
				#Slicing the array for parallel calculation
				if num_cpu > 1:
					if len(material_idx) == 3: #if clause for 2D underworld model, yes the number is 3 for 2D and 1 for 3D. You do not need to confuse!
						#condition to check if array is too small to parallelize for the material num_cpu*num_cpu 
						if len(material_idx[0]) > (num_cpu*num_cpu):
							size_arrays = len(material_idx[0]) // num_cpu
							sliced_material_idx = []
							#adjusting the material_index_array
							for idx in range(0, len(material_idx[0]), size_arrays):
								if idx >= (size_arrays*num_cpu):
									sliced_material_idx.append(tuple((material_idx[0][idx:len(material_idx[0])], material_idx[1][idx:len(material_idx[1])],material_idx[2][idx:len(material_idx[2])])))
								else:
									sliced_material_idx.append(tuple((material_idx[0][idx:idx+size_arrays], material_idx[1][idx:idx+size_arrays],material_idx[2][idx:idx+size_arrays])))
						else:
							#revert back to the single cpu if the material_idx_list is not long enough
							num_cpu = 1
							sliced_material_idx = material_idx
					else: #if clause for 3D underworld model
					
						if len(material_idx) > (num_cpu*num_cpu):
							size_arrays = len(material_idx) // num_cpu
							sliced_material_idx = []
							for idx in range(0, len(material_idx), size_arrays):
								if idx >= (size_arrays*num_cpu):
									sliced_material_idx.append(material_idx[idx:len(material_idx)])
								else:
									sliced_material_idx.append(material_idx[idx:idx+size_arrays])
						else:	
							#revert back to the single_cpu if the material_idx is not long enough
							num_cpu = 1
							sliced_material_idx = material_idx
						
				#if not parallel material_idx stays the same for both 2-D and 3-D cases.
				elif num_cpu == 1:
					
					sliced_material_idx = material_idx

				if material_list_holder[l][i].calculation_type == 'value':
					#calculation not necessary for value method so automatically not parallel and indexed into sliced_material_idx
					cond[sliced_material_idx] = 1.0 / material_list_holder[l][i].resistivity_medium
					
				else:
				
					if num_cpu == 1:
						
						cond[sliced_material_idx] = run_conductivity_model(index_list= sliced_material_idx, material = material_list_holder[l][i], pide_object = mat_pide_obj,
						t_array = self.T, p_array=self.P, melt_array=self.melt_frac)
						
					else:
						#solving for parallel with multiprocessing
						with multiprocessing.Pool(processes=num_cpu) as pool:
							
							process_item_partial = partial(run_conductivity_model, material =  material_list_holder[l][i], pide_object = mat_pide_obj, t_array = self.T,
							p_array = self.P, melt_array = self.melt_frac)
							
							c = pool.map(process_item_partial, sliced_material_idx)
						
						#assigning to the global cond list
						for idx in range(0,len(sliced_material_idx)):
							cond[sliced_material_idx[idx]] = c[idx]
				
				print('The conductivity for the material ' + material_list_holder[l][i].name + ' is calculated.')
				
			#converting all zero vals in the cond to None values
			
			cond[cond == 0.0] = np.nan
						
			cond_list.append(cond)
			print('##############################################################')
				
		if type == 'background':
			self.background_cond = cond_list[0]
			return cond_list[0]
		elif type == 'maximum':
			self.maximum_cond = cond_list[0]
			return cond_list[0]
		else:
			self.background_cond = cond_list[0]
			self.maximum_cond = cond_list[1]
			return cond_list[0],cond_list[1]
	
	def calculate_deformation_related_conductivity(self, method = 'plastic_strain', function_method = 'linear',
		low_deformation_threshold = 1e-2, high_deformation_threshold = 100, num_cpu = 1):
	
		try:
			self.background_cond
			self.maximum_cond
			
		except NameError:
			raise NameError('Background and maximum conductivities has to be assigned first to the model object to use deformation related conductivity function.')
	
		if num_cpu > 1:
			import multiprocessing
			import os
			from functools import partial
			
			max_num_cores = os.cpu_count()
			
			if num_cpu > max_num_cores:
				raise ValueError('There are not enough cpus in the machine to run this action with ' + str(num_cpu) + ' cores.')
	
		deform_cond = np.zeros_like(self.T)
		strain_decay = np.zeros_like(self.T)
		cond_decay = np.zeros_like(self.T)
		misfit = np.zeros_like(self.T)
		
		if method == 'plastic_strain':
						
			for i in range(0,len(self.material_list)):
			
				if self.material_node_skip_rate_list != None:
					if self.material_node_skip_rate_list[i] != None:
						mat_skip = self.material_node_skip_rate_list[i]
					else:
						mat_skip = None
				else:
					mat_skip = None
				
				#getting material index for each material
				material_idx = return_material_bool(material_index = self.material_list[i].material_index, model_array = self.material_array, material_skip = mat_skip)
				#turning material index list to be useable format for the np.ndarray fields
				material_idx_list = [[material_idx[0][idx],material_idx[1][idx],material_idx[2][idx]] for idx in range(0,len(material_idx[0]))]
				
				#multiprocessing loop for each material
				with multiprocessing.Pool(processes=num_cpu) as pool:
					
					process_item_partial = partial(run_deform2cond, p_strain = self.p_strain, background_cond = self.background_cond,
					max_cond = self.maximum_cond, low_deformation_threshold = low_deformation_threshold,
					high_deformation_threshold = high_deformation_threshold, function_method = function_method,
					conductivity_decay_factor = self.material_list[i].deformation_dict['conductivity_decay_factor'],
					strain_decay_factor = self.material_list[i].deformation_dict['strain_decay_factor'])
					
					c = pool.map(process_item_partial, material_idx_list)
									
				deform_cond[material_idx] = [x[0] for x in c]
				strain_decay[material_idx] = [x[1] for x in c]
				cond_decay[material_idx] = [x[2] for x in c]
				misfit[material_idx] = [x[3] for x in c]
				
				print('The deformation related conductivity for the material ' + self.material_list[i].name + ' is calculated.')
			
			#converting all zero vals in the cond to None values
			deform_cond[deform_cond == 0.0] = np.nan
			strain_decay[strain_decay == 0.0] = np.nan
			cond_decay[cond_decay == 0.0] = np.nan
			misfit[misfit == 0.0] = np.nan
			
		return deform_cond, strain_decay, cond_decay, misfit
		



