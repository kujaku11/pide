import pide
import unittest
import numpy as np

class test_inversion_and_geotherm(unittest.TestCase):

	@classmethod
	def setUpClass(self):
	
		#Test written for electrical conductivity models at October 2 2024. With newly added functions, this test file has to change
		#since there are new studies added to the arrays.
		
		#tolerance of acceptance value
		self.atol = 1e-3
		
		self.geotherm_check = [298.0, 310.4200028903184, 322.71369349550923, 334.9758311552669, 347.1877592106995, 359.3328353384015,
		371.39543370915834, 383.36093207763616, 395.2156851840189, 406.9469936865668, 418.5430696791802, 429.99299974077053,
		441.2867063149084, 452.4149080878951, 463.36907991964256, 474.1414127831915, 484.72477408387454, 495.11266865651777,
		506.5156036964089, 517.766514458218, 528.8639956679107, 539.8047128767944, 550.5856255510686, 561.2039613809226,
		571.6571963533186, 581.9430363933021, 592.0594004424398, 602.004404848924, 611.7763489555439, 621.3737017823543,
		630.7950897105463, 640.0392850827975, 649.1051956433168, 657.9918547479825, 666.6984122814409, 675.224126223883,
		683.5683548154775, 691.7305492711894, 699.7102470029878, 707.5070653103031, 712.7054253199909, 717.901615320773,
		723.092194969475, 728.2770188547134, 733.4559403882583, 738.6288158725082, 743.7955044381787, 748.955867988141,
		754.1097711422777, 759.25708118335, 764.3976680038658, 769.5314040539371, 774.5343649208719, 779.53007088,
		784.5182830174514, 789.498894796334, 794.4718016473095, 799.4369010617172, 804.3940925495335, 809.3432775983132,
		814.2843596329607, 819.2172439763139, 824.1418378105278, 829.0580501392437, 833.9657917505289, 838.864975180573,
		843.7555146781286, 848.63732616968, 853.5103272253273, 858.3744370253736, 863.2295763275998, 868.0756674352158,
		872.9126341654732, 877.7404018189281, 882.5588971493413, 887.3680483342016, 892.1677849458625, 896.9580379232782,
		901.7387395443274, 906.5098233987138, 911.2712243614316, 916.0228785667828, 920.7647233829382, 925.4966973870288,
		930.2187403407572, 934.930793166519, 939.6327979240233, 944.324697787402, 949.0064370227981, 953.677960966423,
		958.3392160030731, 962.9901495450958, 967.6307100117965, 972.2608468092764, 976.8805103106928, 981.4896518369331, 
		986.0882236376934, 990.6761788729531, 995.2534715948383, 999.820056729865, 1004.3758900615542, 1008.9209282134107,
		1013.4551286322595, 1017.9784495719306, 1022.4908500772851, 1026.992289968577, 1031.4827298261418, 1035.962130975405,
		1040.4304554722064, 1044.8876660884298, 1049.3337262979342, 1053.76860026278, 1058.1922528197422, 1062.6046494671075,
		1067.005756351746, 1071.395540256454, 1075.7739685875629, 1080.1410093628047, 1084.496631199434, 1088.8408033025955,
		1093.173495453938, 1097.4946780004639, 1101.8043218436137, 1106.1023984285769, 1110.3888797338282, 1114.6637382608812,
		1118.9269470242575, 1123.1784795416643, 1127.418309824378, 1131.6464123678293, 1135.8627621423848, 1140.0673345843213,
		1144.2601055869889, 1148.4410514921594, 1152.6101490815554, 1156.7673755685569, 1160.9127085900814, 1165.046126198634,
		1169.1676068545248, 1173.2771294182473, 1177.374673143019, 1181.4602176674778, 1185.53374300853, 1189.595229554351,
		1193.6446580575296, 1197.6820096283607, 1201.7072657282747, 1205.7204081634086, 1209.721419078309, 1213.7102809497717,
		1217.686976580807, 1221.6514890947353, 1225.6038019294067, 1229.543898831541, 1233.47176385119, 1237.3873813363148,
		1241.2907359274798, 1245.1818125526574, 1249.060596422145, 1252.9270730235874, 1256.7812281171084, 1260.6230477305435,
		1264.4525181547754, 1268.2696259391691, 1272.0743578871047, 1275.866701051605, 1279.6466427310588, 1283.414170465034,
		1287.1692720301821, 1290.911935436231, 1294.6421489220638, 1298.3599009518828, 1302.0651802114562, 1305.7579756044477,
		1309.4382762488237, 1313.1060714733412, 1316.7613508141108, 1320.404104011236, 1324.0343210055262, 1327.651991935281,
		1331.257107133147, 1334.8496571230426, 1338.429632617153, 1341.9970245129894, 1345.5518238905165, 1349.0940220093419,
		1352.6236103059698, 1356.1405803911168, 1359.6449240470874, 1363.1366332252092, 1366.615700043326, 1370.0821167833492,
		1373.5358758888644, 1376.9769699627925, 1380.4053917651052, 1383.8211342105938, 1387.2241903666886, 1390.6145534513305,
		1393.992216830891, 1397.3571740181424, 1400.7094186702743, 1404.0489445869598, 1407.375745708464, 1410.6898161138008,
		1413.991150018934, 1417.279741775018, 1420.555585866687, 1423.8186769103806, 1427.0690096527144, 1430.3065789688883,
		1433.531379861135, 1436.7434074572081, 1439.9426570089063, 1443.129123890636, 1446.302803598011, 1449.4636917464861,
		1452.6117840700267, 1455.7470764198138, 1458.869564762981, 1461.9792451813862, 1465.0761138704136, 1468.16016713781,
		1471.2314014025505, 1474.289813193736, 1477.335399149519, 1480.36815601606, 1483.388080646514, 1486.395170000042,
		1489.389421140853, 1492.3708312372714, 1495.3393975608326, 1498.2951174854031, 1501.2379884863274, 1504.1680081395991,
		1507.0851741210574, 1509.9894842056067, 1512.8809362664606, 1515.7595282744085, 1518.6252582971053, 1521.4781244983833,
		1524.3181251375852, 1527.1452585689185, 1529.959523240832, 1532.7609176954109, 1535.549440567794, 1538.3250905856078, 
		1541.087866568423, 1543.8377674272267, 1546.574792163916, 1549.2989398708066, 1552.0102097301615]
		
		self.inversion_check = [1.0215640496960677e-16, 8.528006821794987e-16, 5.9489302039901225e-15,
		3.590485800478801e-14, 1.9010495418650123e-13, 8.940133600743598e-13, 3.775600690191617e-12,
		1.4460020279541329e-11, 5.066087825085554e-11, 1.6363037177535723e-10, 4.906189038553529e-10,
		1.3740242921799758e-09, 3.6142008136066835e-09, 8.973196727789262e-09, 2.112174102574426e-08,
		4.732579734211896e-08, 1.013025601339791e-07, 2.0783380159120128e-07, 4.3942316691518453e-07,
		8.930130018660593e-07, 1.7494671631687958e-06, 3.3122421337575474e-06, 6.074395281667714e-06,
		1.081328383995161e-05, 1.872047152533204e-05, 3.1574913036127064e-05, 5.196765306501209e-05,
		8.358591103630161e-05, 0.00013156343574628534, 0.00020290235364396448, 0.0003069693953512509,
		0.00045606641255101595, 0.0006660715870229927, 0.000957143825844261, 0.0013544787081396805, 
		0.0018891002001576339, 0.00259866839875669, 0.003528280007846294, 0.00473123529161478, 
		0.00633381163627852, 0.007842743223173522, 0.009678082691459765, 0.011901931880124256, 
		0.014587491272894436, 0.01781995621920896, 0.02169816718564847, 0.026336437282755407, 
		0.031866570822953987, 0.03844008597208157, 0.046230654682908816, 0.055436773132208905, 
		0.06628467581371959, 0.07881148425367186, 0.09345432872430157, 0.1105259522693427, 
		0.13037858593507998, 0.15340771571758394, 0.18005633121216857, 0.21081946523946138, 
		0.2462490311631036, 0.2869589628852144, 0.3336306607596252, 0.38701874462729446, 
		0.447957112822564, 0.5173653032879618, 0.5962551498346115, 0.6857377230563539, 
		0.7870305414119168, 0.9014650334943813, 1.0304942274771522, 1.1757006381339128, 1.3388043156567973,
		1.5216710137373848, 1.7263204270407562, 1.9549344403296132, 2.2098653231485774, 
		2.493643795266156, 2.8089868791404746, 3.1588054467373823, 3.5462113593562075, 
		3.9745240910571633, 4.447276719266967, 4.968221160677437, 5.5413325272533935,
		6.170812476718225, 6.861091435043246, 7.616829576051455, 8.442916456074403, 
		9.344469220485983, 10.326829324591353, 11.395557744331137, 12.556428692880113, 
		13.815421907446822, 15.178713625943058, 16.652666434675943, 18.243818234194844,
		19.958870638610698, 21.804677191109896, 23.78823184142615, 25.916658185589235, 
		28.197200009934924, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 60.0, 
		60.0, 60.0, 60.0, 60.0, 60.0, 90.0, 90.0, 90.0, 90.0, 90.0, 120.0, 120.0, 120.0, 
		150.0, 150.0, 150.0, 150.0, 180.0, 180.0, 210.0, 210.0, 210.0, 240.0, 240.0, 241.875,
		232.5, 225.0, 215.625, 208.125, 198.75, 193.125, 185.625, 180.0, 172.5, 166.875, 161.25,
		155.625, 150.0, 144.375, 337.5, 326.25, 315.0, 303.75, 296.25, 285.0, 277.5, 266.25,
		258.75, 251.25, 243.75, 236.25, 228.75, 221.25, 215.625, 210.0, 202.5, 196.875, 191.25,
		185.625, 180.0, 174.375, 168.75, 165.0, 161.25, 155.625, 151.875, 146.25, 142.5, 138.75,
		135.0, 131.25, 127.5, 124.6875, 121.875, 118.125, 114.375, 112.5, 108.75, 105.9375, 103.125,
		101.25, 97.5, 95.625, 92.8125, 90.0, 88.125, 86.25, 84.375, 81.5625, 79.6875, 77.8125, 75.9375,
		74.0625, 72.1875, 70.3125, 68.4375, 66.5625, 64.6875, 63.75, 61.875, 60.0, 59.0625, 57.1875,
		56.25, 54.375, 53.4375, 51.5625, 50.625, 49.21875, 47.8125, 46.875, 45.9375, 44.53125, 43.125,
		42.1875, 41.25, 40.3125, 39.375, 38.4375, 37.5, 36.5625, 35.625, 34.6875, 33.75, 32.8125, 31.875,
		30.9375, 30.46875, 29.53125, 28.59375, 28.125, 27.1875, 26.25, 25.78125, 24.84375, 24.375,
		23.4375, 22.96875, 22.5, 21.5625]

	
	def test_1_geotherm(self):
	
		from pide.geodyn.geotherm import calculate_hasterok2011_geotherm

		moho = 38 #km
		max_depth = 250
		
		self.T, depth, self.p, idx_LAB = calculate_hasterok2011_geotherm(SHF = 36, T_0 =25.0,max_depth = max_depth, moho = moho)
		
		assert np.allclose(self.T, np.array(self.geotherm_check),atol = self.atol)
		
	def test_2_inversion(self):
	
		from pide.geodyn.geotherm import calculate_hasterok2011_geotherm

		moho = 38 #km
		max_depth = 250
		
		self.T, depth, self.p, idx_LAB = calculate_hasterok2011_geotherm(SHF = 36, T_0 =25.0,max_depth = max_depth, moho = moho)
	
		from pide.inversion import conductivity_solver_single_param
		
		p_obj = pide.pide() #creating the initial object
		p_obj.set_temperature(self.T)
		p_obj.set_pressure(self.p)
		
		p_obj.set_composition_solid_mineral(ol = 0.65, opx = 0.2, cpx = 0.1, garnet = 0.05)
		p_obj.set_solid_phs_mix_method(2) #Hashin-Shtrikman
		
		p_obj.set_mantle_water_solubility(ol = 4,opx = 3, cpx = 0, garnet = 0)
		p_obj.set_mantle_water_partitions(opx_ol = 3, cpx_ol = 4, garnet_ol = 0)
		p_obj.revalue_arrays()
		
		p_obj.set_parameter('ti_ol', 0.01)
		max_water = p_obj.calculate_bulk_mantle_water_solubility(method = 'array')
		
		cond_list_to_invert = np.ones(len(self.T)) * 1e4 #first 75 km, just creating a array to change the rest.
		cond_list_to_invert[75:100] = 1000 #from 75 to 100 km
		cond_list_to_invert[100:150] = 100 #from 100 to 150 km
		cond_list_to_invert[150:] = 50 #from 150 to 250 km.
		cond_list_to_invert = 1.0 / cond_list_to_invert #converting to conductivity
		
		c_list, residual_list = conductivity_solver_single_param(object = p_obj, cond_list = cond_list_to_invert,
		param_name = 'bulk_water', upper_limit_list = max_water, lower_limit_list= np.zeros(len(max_water)),
		search_start = 30, acceptence_threshold = 0.5, num_cpu = 2)
		
		assert np.allclose(np.array(c_list),np.array(self.inversion_check), atol = self.atol)

if __name__ == "__main__":
	
	unittest.main()