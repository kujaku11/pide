#!/usr/bin/env python3

import SEL

class Material(object):

	def __init__(self, name = "Unnamed", material_index = None, calculation_type = 'mineral', composition = None, interconnectivities = None, param1 = None, param2 = None, el_cond_selections = None, water_distr = False,
	water = None, xfe = None, phase_mixing_idx = 0, deformation_dict = None, **kwargs):
	
		self.mineral_list = ['ol','opx','cpx','garnet','mica','amp','quartz','plag','kfelds','sulphide','graphite','mixture','sp','wds','rwd','perov','other','bulk']
		self.rock_list = ['granite', 'granulite', 'sandstone', 'gneiss', 'amphibolite', 'basalt', 'mud', 'gabbro', 'other_rock']
		self.name = name
		self.material_index = material_index
		self.calculation_type = calculation_type
		
		if composition == None:
			if self.calculation_type == 'rock':
				composition = {'granite':1}
			else:
				composition = {'ol':1}
		self._composition = None
		self.composition = composition
		
		if interconnectivities == None:
			if self.calculation_type == 'rock':
				interconnectivities = {'granite':1}
			else:
				interconnectivities = {'ol':1}
		self._interconnectivities = None
		self.interconnectivities = interconnectivities
		
		if el_cond_selections == None:
			if self.calculation_type == 'rock':
				el_cond_selections = {'granite':0}
			else:
				el_cond_selections = {'ol':0}
		self._el_cond_selections = None
		self.el_cond_selections = el_cond_selections
		
		self.water_distr = water_distr
		
		if water == None:
			if self.calculation_type == 'rock':
				water = {'granite':0}
			else:
				water = {'ol':0}
		self._water = None
		self.water = water
		
		if param1 == None:
			if self.calculation_type == 'rock':
				param1 = {'granite':0}
			else:
				param1 = {'ol':0}
				
		self._param1 = None
		self.param1 = param1
				
		if param2 == None:
			if self.calculation_type == 'rock':
				param2 = {'granite':0}
			else:
				param2 = {'ol':0}
		
		self._param2 = None
		self.param2 = param2
		
		if xfe == None:
			if self.calculation_type == 'rock':
				xfe = {'granite':0.1}
			else:
				xfe = {'ol':0.1}
		self._xfe = None
		self.xfe = xfe
		
		self._phase_mixing_idx = None
		self.phase_mixing_idx = phase_mixing_idx
		
		if deformation_dict == None:
			deformation_dict = {'function_method':'linear','conductivity_decay_factor':0, 'strain_decay_factor':0, 'strain_percolation_threshold': None}
		
		self._deformation_dict = None
		self.deformation_dict = deformation_dict
				
		self._mantle_water_part = None
		self.mantle_water_part = kwargs.pop('mantle_water_part', {'opx_ol':0,'cpx_ol':0,'garnet_ol':0, 'ol_melt':0, 'opx_melt':0, 'cpx_melt':0,'garnet_melt':0})
		
		self.mantle_water_sol_ref = kwargs.pop('mantle_water_sol_ref', 'ol')
		
		self.resistivity_medium = kwargs.pop('resistivity_medium', None)
		
		self.water_calib = kwargs.pop('water_calib', {'ol':3,'px-gt':2,'feldspar':2})
		
		self.o2_buffer = kwargs.pop('o2_buffer', 0)
		
		self.linked_material_index = kwargs.pop('linked_material_index', None)
		
		if (self.calculation_type == 'value') and (self.resistivity_medium == None):
		
			raise AttributeError('Calculation type is selected as value. You have to set resistivity medium as a floating number in Ohm meters.')
			
	def check_vals(self,value,type):
		
		for item in value:
			
			if self.calculation_type == 'mineral':
				if (item in self.mineral_list) == False:
					raise ValueError('The mineral ' + item + ' is wrongly defined in the composition dictionary. The possible mineral names are:' + str(self.mineral_list))
			elif self.calculation_type == 'rock':
				if (item in self.rock_list) == False:
					raise ValueError('The rock ' + item + ' is wrongly defined in the composition dictionary. The possible rock names are:' + str(self.rock_list))
			elif self.calculation_type == 'value':
				pass
			else:
				raise ValueError('The calculation type is wrongly defined. It has to be one of those three: 1.mineral, 2.rock, 3.value.')
		
		if self.calculation_type == 'mineral':
			list2check = self.mineral_list
		elif self.calculation_type == 'rock':
			list2check = self.rock_list
		else:
			list2check = None
		
		if list2check != None:
			for item in list2check:
				if item not in value:
					if type == 'comp':
						value[item] = 0
					elif type == 'archie':
						value[item] = 8.0
		else:
			value = None
			
		return value
		
	#attributes listing here
	@property
	def composition(self):
		return self._composition
		
	@composition.setter
	def composition(self, value):
		self._composition = self.check_vals(value=value,type = 'comp')
		
	@property
	def interconnectivities(self):
		return self._interconnectivities
		
	@interconnectivities.setter
	def interconnectivities(self, value):
		self._interconnectivities = self.check_vals(value=value,type = 'archie')
		
	@property
	def param1(self):
		return self._param1
		
	@param1.setter
	def param1(self, value):
		self._param1 = self.check_vals(value=value,type = 'comp')
		
	@property
	def param2(self):
		return self._param2
		
	@param2.setter
	def param2(self, value):
		self._param2 = self.check_vals(value=value,type = 'comp')
		
	@property
	def water(self):
		return self._water
		
	@water.setter
	def water(self, value):
		self._water = self.check_vals(value=value,type = 'comp')
		
	@property
	def el_cond_selections(self):
		return self._el_cond_selections
		
	@el_cond_selections.setter
	def el_cond_selections(self, value):
		self._el_cond_selections = self.check_vals(value=value,type = 'comp')
		
	@property
	def xfe(self):
		return self._xfe
		
	@xfe.setter
	def xfe(self, value):
		self._xfe = self.check_vals(value=value,type = 'comp')
		
		
	@property
	def solid_phase_mixing_idx(self):
		return self._solid_phase_mixing_idx
		
	@solid_phase_mixing_idx.setter
	def solid_phase_mixing_idx(self, value):
		self._solid_phase_mixing_idx = value
		
	@property
	def deformation_dict(self):
		return self._deformation_dict
		
	@deformation_dict.setter
	def deformation_dict(self, value):
		self._deformation_dict = value
		
		
		
		
		

		
		