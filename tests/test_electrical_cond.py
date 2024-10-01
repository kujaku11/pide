import pide
import unittest



class test_conductivity_functions(unittest.TestCase):

	@classmethod
	def setUpClass(self):
		
		temp = [1000]
		pres = 2.0

		p_obj = pide.pide()

		p_obj.set_temperature(temp)
		p_obj.set_pressure(pres)
		p_obj.set_param1_mineral(mica = 0.2, plag = 0.1)

		mineral_cond_list_check = [[0.0002147666215751601, 0.0019628863936549724, 0.0019628863936549724, 1.0190583930014192e-05,
						8.208132334583077e-05, 0.00020788083347927274, 0.0001440326145468413, 6.855909754207005e-07, 0.0010714138960102133,
						7.377942552234648e-06, 1.7927554236795322e-06, 3.297803999685759e-06, 1.7484794023483996e-06,
						0.00018056600809558101, 1.6910366224498637e-06, 1.325877798709181e-05, 5.684421480001739e-06, 3.826141179766439e-06,
						5.065540593063711e-06, 4.670308887813639e-05, 1.0328167482905911e-07], [0.000781880478677682,
						0.0041784297728858005, 7.933807799716656e-05, 6.5886975752919734e-06, 2.079446696555967e-06, 8.528539400246339e-07,
						2.465168638439833e-06], [0.0004962607047489137, 0.002462870542595579, 0.007108929846228112, 2.77195158939179e-06,
						0.0009367836943396204, 0.00020649961515201444, 0.0003657934479451687, 5.342668461994264e-07, 3.036074531806225e-07,
						0.0006794702021050355, 0.002166081366067568, 0.0020843655959144006], [0.017628516537043188, 3.419744010057346e-05,
						1.2886396201172216e-10, 1.9792124574723175e-11, 3.8305090578826584e-06, 0.00036438748674276397, 0.20570613002486426,
						2.623717614437895, 6.958467616527965, 0.0027019883214688574, 0.0005859226310618902, 0.0034794253202184602,
						5.2657573700746e-05, 7.373852865647446e-05, 0.00012507246648229607, 0.0016101702596428337,
						2.2867640880756637e-07, 0.0011355912598567696, 7.758182189447044e-05], [0.008479833615942118,
						0.1640862682924139], [0.0070481722066036735,
						0.02080240802198666, 13667.57423820947, 0.03391151823805323, 0.14736974502790565,
						0.04356001857421698], [0.0003188940114855732, 0.013619445169725835, 0.00012394697219022993,
						2.506389402139377e-05, 3.689650732899158e-05, 3.2249459603471138e-06, 6.596016408306563,
						0.025493674803551688, 0.004856571995839248], [0.0004128716087684925, 2.197819422218023e-05,
						0.0018054801889687924, 4.18379313046424e-06, 0.30574923240698204,
						0.5276860781809379, 0.02360645107435132], [0.0910880250289498,
						0.06145860932937158, 0.05067569206031278, 0.0989669940613521], 
						[3332.728995761379, 344.3499307633384, 153.81546403030342],
						[100000.0], [15.668221458353507, 232.0239164777426], 
						[0.00038867129908321056, 6.617775585469027e-05, 7.855161191415685e-05,
						5.96958471942372e-05, 0.000725938263780609, 0.0001791219710105094, 0.00029143475739094724, 1.7437241829326952e-05,
						1.4652025419612293e-05, 1.3456087012655397e-05, 7.869745619559822e-05, 0.0003563383662745001],
						[9.136938593750724e-05, 0.00031829235011104895, 35.07677858258606, 0.016354842407704934, 0.007612290451624446,
						46.83657179784756], [0.00019107660645723495, 0.0009147662433918977, 0.0025793801343671945, 0.19739108420395143, 2.170179463231433,
						0.09033385965305728, 0.023804816701909138, 0.031559219353188686, 0.026456434639873783, 0.15243823410196836,
						0.6470873295769766, 8.420299371544626, 8.63964005700373, 122.06699678239542, 0.0003513802736255081, 0.0003931961527606333,
						0.0005317099241385271, 0.0025914554862907784, 0.04564406736998614, 0.14886276382806088,
						0.7179351351044376, 2.4126573631693167], [244.21164927494843, 0.0027744528159345428, 0.003604655509112567,
						0.0003936708988150554]]


	def test_mineral_conds(self):

		pass