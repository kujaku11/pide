#!/usr/bin/env python3

import numpy as np

R_const = 8.3144621

def Yoshino2012_DryRingwoodite_Xfe(T, P, water, xFe ,param1, param2, fo2 = None, fo2_ref = None, method = None):

	A = 1885.0
	E = 193000.0 #J/mol
	alpha = 146000.0 #J/mol
	dv = -0.33e-6 #m3/mol
	beta = 0.72e-6 #m3/mol
	P = P * 1e9 #converting to Pa - J/m3
	
	cond = A * xFe * np.exp(-((E - (alpha * xFe**(1.0/3.0))) + (P*(dv - beta*xFe))) / (R_const*T))
	
	return cond
	
def Yoshino2009_DryRingwoodite_Xfe(T, P, water, xFe ,param1, param2, fo2 = None, fo2_ref = None, method = None):

	A = 10042.0
	E = 208000.0
	alpha = 155000.0
	
	cond = A * xFe * np.exp(-((E - (alpha * xFe**(1.0/3.0)))) / (R_const*T))
	
	return cond
	