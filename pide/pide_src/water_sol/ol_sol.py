#!/usr/bin/env python3

import numpy as np
R_const = 8.3144621

def Ferot2012_OlSol(T,P,depth,h2o_fug,o2_fug,fe_ol,ti_ol,method):

	max_ol_h2o = 68.113 * np.exp(0.0080613 * depth / 1000.0)  * 0.666 #in ppm

	return max_ol_h2o

def Gaetani2014_OlSol(T,P,depth,h2o_fug,o2_fug,fe_ol,ti_ol,method):

	o2_fug = o2_fug * 0.1 #converting to MPa from bar
	A_gaetani = 29 #H/Si^6
	alpha_1_gaetani = 0.59
	alpha_2_gaetani = 0.03
	dv_gaetani = 5e-6 #m^3/mol
	P = P * 1e9
	max_ol_h2o = A_gaetani * ((h2o_fug * 1e3)**alpha_1_gaetani) * (o2_fug**alpha_2_gaetani) *\
	np.exp(-(P * dv_gaetani) / (R_const * T))

	max_ol_h2o = max_ol_h2o * 0.0613895 #Converting to ppm wt

	return max_ol_h2o
	
def Zhao2004_OlSol(T,P,depth,h2o_fug,o2_fug,fe_ol,ti_ol,method):

	A_zhao = 90
	E_zhao = 50e3
	dv_zhao = 10e-6
	alpha_zhao = 97e3
	P = P * 1e9 #converting to Pa
	h2o_fug = h2o_fug * 1e3 #converting to mpa
	max_ol_h2o = A_zhao * (h2o_fug) * np.exp(-(E_zhao + (P * dv_zhao)) / (R_const * T)) * np.exp((alpha_zhao * fe_ol) / (R_const * T))

	max_ol_h2o = max_ol_h2o * 0.0613895 #Converting to ppm wt (Demouchy and Bolfan-Casanova 2016)

	return max_ol_h2o

def Ardia2012_OlSol(T,P,depth,h2o_fug,o2_fug,fe_ol,ti_ol,method):

	#Olivine solubility from Tenner and Ardia (2012)

	max_ol_h2o = (39.1 * P) - 66.0 #Curve from Ardia et al. (2012) with data from Tenner et al. (2012).
	#This is along the mantle adiabat that resembles the oceanic environment calculated with the model of
	#Stixrude and Lithgow-Bertolloni (2007). So it is not wise to use this equation for colder geotherms (cratons,protons?).

	return max_ol_h2o

def PadronNavarta2017_OlSol(T,P,depth,h2o_fug,o2_fug,fe_ol,ti_ol,method):

	X_ol_si = np.exp((-580000.0 + (14.0*T) + (44300.0*np.log(10000.0*(2.1+P)))) / (T * R_const))
	max_ol_h2o_si = (360400.0 * 4.0 * X_ol_si * 1e4) / (56292.0 - (2405.0 * 4.0 * X_ol_si))
	XX_ti = -124000.0 + (78.0*(T)) + (10600.0*P)
	X_ol_ti = (np.exp(XX_ti/((T)*R_const)) * ((ti_ol*14073.0) / ((1979.0*ti_ol)+798800.0))) / (np.exp(XX_ti/((T)*R_const)) + 1)
	max_ol_h2o_ti = ((180200.0*X_ol_ti*2.0) / ((-249.0*X_ol_ti*2.0) + 28146))*10000.0
	max_ol_h2o = max_ol_h2o_si + max_ol_h2o_ti
	
	return max_ol_h2o

def Mosenfelder2006_OlSol(T,P,depth,h2o_fug,o2_fug,fe_ol,ti_ol,method):
	
	h2o_fug = h2o_fug * 1e3 #MPa
	A = 2.45 #H/106 Si / MPa
	dv = 10.2 * 1e-6
	P = P *1e9#converting to Pa

	max_ol_h2o = A * h2o_fug * np.exp((-P*dv) / (R_const * T))
	
	max_ol_h2o = max_ol_h2o * 0.0613895 #Converting to ppm wt (Demouchy and Bolfan-Casanova 2016)

	return max_ol_h2o

def Kohlstedt1996_OlSol(T,P,depth,h2o_fug,o2_fug,fe_ol,ti_ol,method):

	#This value was re-determined by the study of Hirschmann et al. (2005, EPSL).
	#while fitting to the Bell calibration of the data.
	
	P = P*1e9 #convering to Pa
	h2o_fug = h2o_fug * 1e3 #MPa

	max_ol_h2o = 1.1 * h2o_fug * np.exp(-(P *10.6e-6) / (R_const * T))
	
	max_ol_h2o = max_ol_h2o * 0.0613895 #Converting to ppm wt (Demouchy and Bolfan-Casanova 2016)

	return max_ol_h2o


def Yang2015_H2O_OlSol(T,P,depth,h2o_fug,o2_fug,fe_ol,ti_ol,method):

	max_ol_h2o = 34.9 + (53.9*P)

	return max_ol_h2o

def Yang2015_H2O_CH4_OlSol(T,P,depth,h2o_fug,o2_fug,fe_ol,ti_ol,method):

	max_ol_h2o = 19.4 + (20.8*P)

	return max_ol_h2o
