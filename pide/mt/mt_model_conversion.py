#!/usr/bin/env python3

import os, csv
import numpy as np

def convert_2DModel_2_MARE2DEM(file_out, conductivity_array, mesh, boundaries = None, **kwargs):

	import scipy.io

	#This is a function that converts the constructed 2D geodynamic model into data points
	#that can be read by Mamba software that is used for creating model files for MARE2DEM.
	"""
	Input Paramaters
	-----------------
	file_out: filename or full directory to output the result. Includes the format (e.g., csv)
	conductivity_array: calculated conductivity field in np.ndarray()
	mesh: mesh of the associated conductivity field.
	boundaries: boundaries dictionary in  {'left','right','top','bottom'}	
	
	cond_unit: 'conductivity' or 'resistivity'
	mesh_unit: 'kilometres' or 'metres'
	"""
	
	#optional kwarg calls
	cond_unit = kwargs.pop('cond_unit', 'conductivity')
	mesh_unit = kwargs.pop('mesh_unit', 'kilometres')
	
	if cond_unit == 'conductivity':
		conductivity_array = 1.0 / conductivity_array
	elif cond_unit == 'resistivity':
		pass
	else:
		raise ValueError('Please enter a valid response for cond_unit: "conductivity" or "resistivity".')
		
	
		
	boundary_list = ['left','right','top','bottom']
	#Defaulting into mesh boundaries if w
	if boundaries == None:
		boundaries = {'left': np.amin(mesh[0]), 'right': np.amax(mesh[0]), 'top': 0, 'bottom':np.amax(mesh[1])}
	else:
		for item in boundary_list:
			if item not in boundaries:
				if item == 'top':
					boundaries[item] = 0.0
				elif item == 'right':
					boundaries[item] = np.amax(mesh[0])
				elif item == 'left':
					boundaries[item] = np.amin(mesh[0])
				elif item == 'bottom':
					boundaries[item] = np.amax(mesh[1])
						
	#converting mesh in kilometers into meters.
	if mesh_unit == 'kilometres':
		mesh[0] = mesh[0] * 1e3
		mesh[1] = mesh[1] * 1e3
		boundaries['top'] = boundaries['top'] * 1e3
		boundaries['right'] = boundaries['right'] * 1e3
		boundaries['left'] = boundaries['left'] * 1e3
		boundaries['bottom'] = boundaries['bottom'] * 1e3
	elif mesh_unit == 'metres':
		pass
	else:
		raise ValueError('Please enter a valid response for mesh_unit: "kilometres" or "metres".')
		
	#finding mesh_center
	mc_lateral = (boundaries['right'] - boundaries['left']) / 2.0
	
	#centering the mesh and boundaries with the center point in [y] direction.
	mesh[0] = mesh[0] - mc_lateral
	boundaries['right'] = boundaries['right'] - mc_lateral
	boundaries['left'] = boundaries['left'] - mc_lateral
	
	#appending lines to write from te conductivity array and mesh
	lines = []
	array_y = []
	array_z = []
	array_rho = []
	array_save = []
	
	for i in range(0,len(conductivity_array)):
		for j in range(0,len(conductivity_array[0])):
			if np.isnan(conductivity_array[i][j][0]) == False:
				if (mesh[0][i][j] <= boundaries['right']):
					if (mesh[0][i][j] >= boundaries['left']):
						if (mesh[1][i][j] <= boundaries['bottom']):
							if (mesh[1][i][j] >= boundaries['top']):
								# array_save.append([mesh[0][i][j],mesh[1][i][j],conductivity_array[i][j][0]])
								array_y.append(mesh[0][i][j])
								array_z.append(mesh[1][i][j])
								array_rho.append(conductivity_array[i][j][0])
								# lines.append('  '.join((str(mesh[0][i][j]),str(mesh[1][i][j]),str(np.log10(conductivity_array[i][j][0])) + '\n')))
	
	#saving the file
	# filesave_composition = open(file_out ,'w')
	# filesave_composition.writelines(lines)
	# filesave_composition.close()
	data_2_write = {
	'y': array_y,
	'z': array_z,
	'rho': array_rho}
	
	# data_2_write = {
	# 'yzrho': array_save
	# }
	
	scipy.io.savemat(file_out, data_2_write)
	
	print('The synthetic conductivity model had been succesfully written as MARE2DEM/Mamba input at: ')
	print(file_out)
	print('##################')
	print('Model bounds entered:')
	print('--------- ' + str(boundaries['top']) + '---------')
	print('|                                |')
	print('|                                |')
	print(str(boundaries['left']) + '                    ' + str(boundaries['right']))
	print('|                                |')
	print('|                                |')
	print('--------- ' + str(boundaries['bottom']) + '---------')
	
	
def convert_3DModel_2_ModEM(file_out, conductivity_array, mesh, core_bounds = None, station_array = None, **kwargs):

	#This is a function that converts the constructed 3D geodynamic model into data points
	#that can be readable by the 3D MT modelling algorithm ModEM.
	"""
	Input Paramaters
	-----------------
	file_out: filename or full directory to output the result. Includes the format (e.g., csv)
	conductivity_array: calculated conductivity field in np.ndarray()
	mesh: mesh of the associated conductivity field.
	core_bounds: boundaries dictionary in  {'left','right','top','bottom'}	
	
	Keyword Arguments:
	core_mesh_size:
	num_horiz_bounds:
	horiz_bound_incr:
	num_vert_bounds:
	vert_bound_incr:
	"""
	
	# core_mesh_size = kwargs.pop('core_mesh_size', mesh[0][0][1][0] - mesh[0][0][0][0])
	num_horiz_bounds = kwargs.pop('num_horiz_bounds', 8)
	horiz_bound_incr = kwargs.pop('horiz_bound_incr', 2)
	num_vert_bounds = kwargs.pop('num_vert_bounds', 9)
	vert_bound_incr = kwargs.pop('vert_bound_incr', 2)
	
	from pide.geodyn.interpolate_fields import interpolate_3d_fields

	x_mesh = mesh[0]
	y_mesh = mesh[1]
	z_mesh = mesh[2]

	slice_len = len(x_mesh) * len(y_mesh)
	rho = np.zeros((len(z_mesh),slice_len))
	for i in range(0,len(z_mesh)):
		for j in range(0, slice_len):
			try:		
				rho[i][j] = conductivity_array[(i*slice_len)+j]
			except IndexError:
				raise IndexError('The mesh structure entered does not match the conductivity array. Be sure the entered format mesh = (x_mesh_centers,y_mesh_centers,z_mesh_centers) in tuples are correct.')
							
	#determining the 
	
	start_index_list = []
	sea_index_list = []
	for i in range(0,len(rho)):
		if np.all(rho[i] == rho[i][0]) == True:
			start_index_list.append(i)
		if (-999.0 in rho[i]) == False:
			sea_index_list.append(i)
	
	air_start_index = start_index_list[0]
	sea_index = sea_index_list[-1]
	
	for i in range(0,len(rho)):
		if i > sea_index:
			rho[i][(rho[i] == -999.0)] = 1e-14
	
	outs = np.float64(x_mesh[1] - x_mesh[0])
	xy_out = []
	for i in range(0, num_horiz_bounds):
		outs = outs * horiz_bound_incr
		xy_out.append(outs)
	xy_out = np.array(xy_out)
		
	outs_y = np.float64(y_mesh[1] - y_mesh[0])
	yx_out = []
	for i in range(0, num_horiz_bounds):
		outs_y = outs_y * horiz_bound_incr
		yx_out.append(outs_y)
	yx_out = np.array(yx_out)
	
	outs_z = np.float64(z_mesh[-2] - z_mesh[-1])
	z_out = []
	for i in range(0, num_vert_bounds):
		outs_z = outs_z * vert_bound_incr
		z_out.append(outs_z)
	outs_z = np.array(outs_z)
	
	x_core = np.ones(len(x_mesh)) * np.float64(x_mesh[1] - x_mesh[0])
	y_core = np.ones(len(y_mesh)) * np.float64(y_mesh[1] - y_mesh[0])
	z_core = np.ones(len(z_mesh)) * np.abs(np.float64(z_mesh[0] - z_mesh[1]))
	
	x_out = np.concatenate([xy_out[::-1],x_core,xy_out])
	y_out = np.concatenate([yx_out[::-1],y_core,yx_out])
	z_out = np.concatenate([z_core,z_out])
	
	n_len = len(x_out) * len(y_out)
		
	rho_new = []
	
	for i in range(0,len(z_mesh)):
		rho_local = []
		for j in range(0,(num_horiz_bounds*((2*num_horiz_bounds)+len(x_core)))):
			rho_local.append(np.nan)
		for j in range(0,len(y_core)):
			for k in range(0,num_horiz_bounds):
				rho_local.append(np.nan)
			for k in range(j*len(x_core),j*len(x_core) + len(x_core)):
				rho_local.append(rho[i][k])
			for k in range(0,num_horiz_bounds):
				rho_local.append(np.nan)
		for j in range(0,(num_horiz_bounds*((2*num_horiz_bounds)+len(x_core)))):
			rho_local.append(np.nan)
		rho_new.append(np.array(rho_local))
	
	rho_new = np.array(rho_new)
	for i in range(0,num_vert_bounds):
		rho_new = np.insert(rho_new,0,np.ones(len(rho_new[-1])) * np.nan)
	
	for i in range(0,len(rho)):
		rho_new[i][0] = rho[i][0]
		rho_new[i][len(x_core) + 2*len(xy_out)] = rho[i][len(x_core)]
		rho_new[i][-(len(x_core) + 2*len(xy_out))] = rho[i][-len(x_core)]
		rho_new[i][-1] = rho[i][-1]
		
	for i in range(len(rho),len(rho_new)):
		rho_new[i] = rho_new[len(rho)]
	
	rho_interp_array = rho_new.ravel()
	
	xi = np.cumsum(x_out)
	yi = np.cumsum(y_out)
	zi = np.cumsum(z_out)

	xi = np.insert(xi,0,0.0)
	yi = np.insert(yi,0,0.0)
	zi = np.insert(zi,0,0.0)
	
	
	
	
	xi_n = [((xi[i] - xi[i-1]) / 2.0) + xi[i-1] for i in range(1, len(xi))]
	yi_n = [((yi[i] - yi[i-1]) / 2.0) + yi[i-1] for i in range(1, len(yi))]
	zi_n = [((zi[i] - zi[i-1]) / 2.0) + zi[i-1] for i in range(1, len(zi))]
	
	zi_n = zi_n[::-1]
	
	import ipdb
	ipdb.set_trace()
	
	
	
	"""
	
	
	x_i,  y_i = np.meshgrid(xi_n,yi_n)
	
	
	for i in range(0,len(rho_new)):
		fnew = rho_new[i]
		mask = np.isnan(fnew)
		points = np.column_stack((x_i,y_i))
		values = fnew[~mask]
		import ipdb
		ipdb.set_trace()
		fnew = griddata(points, values, (x_i, y_i),method = 'linear')
		
		rho_new[i] = fnew
	"""
		
	
	rho_new = np.log(1.0 / rho_new) #ModEM rho format with natural logarithm of resistivityrho_
	
	lines = ["# 3D MT model written by ModEM in WS format\n"]
	lines.append('  '+str(len(x_out))+ '   ' +str(len(y_out))+ '   '+str(len(z_out))+ '\n')
	
	line = np.array2string(x_out*1e3, separator=' ', max_line_width=np.inf, formatter={'all': lambda x: f'{x:10.3f}'})
	lines.append('  ' + line[1:-1] + '\n')
	
	line = np.array2string(y_out*1e3, separator=' ', max_line_width=np.inf, formatter={'all': lambda x: f'{x:10.3f}'})
	lines.append('  ' + line[1:-1] + '\n')
	
	line = np.array2string(z_out*1e3, separator=' ', max_line_width=np.inf, formatter={'all': lambda x: f'{x:10.3f}'})
	lines.append('  ' + line[1:-1] + '\n')
	
	for i in range(0,len(rho_new)):
		line = []
		for j in range(0,len(rho_new[i]),len(x_out)):
			
			line = np.array2string(rho_new[i][j*len(x_out):(j*len(x_out) + len(x_out))]*1e3, separator=' ', max_line_width=np.inf, formatter={'all': lambda x: f'{x:.5E}'})
			lines.append('  ' + line[1:-1] + '\n')
	
	
	#Finding the uppermost layer with no nan values
	
		
	
	
	
	