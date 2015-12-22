import math

Z = {'H': 1, 'Ru': 44, 'Re': 75, 'Ra': 88, 'Rb': 37, 'Rn': 86, 'Rh': 45, 'Be': 4, 'Ba': 56, 'Bi': 83, 'Br': 35, 'P': 15, 'Os': 76, 'Ge': 32, 'Gd': 64, 'Ga': 31, 'Pr': 59, 'Pt': 78, 'C': 6, 'Pb': 82, 'Pa': 91, 'Pd': 46, 'Cd': 48, 'Po': 84, 'Pm': 61, 'Ho': 67, 'Hf': 72, 'Hg': 80, 'He': 2, 'Mg': 12, 'K': 19, 'Mn': 25, 'O': 8, 'S': 16, 'W': 74, 'Zn': 30, 'Eu': 63, 'Zr': 40, 'Er': 68, 'Ni': 28, 'Na': 11, 'Nb': 41, 'Nd': 60, 'Ne': 10, 'Fr': 87, 'Fe': 26, 'B': 5, 'F': 9, 'Sr': 38, 'N': 7, 'Kr': 36, 'Si': 14, 'Sn': 50, 'Sm': 62, 'V': 23, 'Sc': 21, 'Sb': 51, 'Se': 34, 'Co': 27, 'Cl': 17, 'Ca': 20, 'Ce': 58, 'Xe': 54, 'Tm': 69, 'Cs': 55, 'Cr': 24, 'Cu': 29, 'La': 57, 'Li': 3, 'Tl': 81, 'Lu': 71, 'Th': 90, 'Ti': 22, 'Te': 52, 'Tb': 65, 'Tc': 43, 'Ta': 73, 'Yb': 70, 'Dy': 66, 'I': 53, 'U': 92, 'Y': 39, 'Ac': 89, 'Ag': 47, 'Ir': 77, 'Al': 13, 'As': 33, 'Ar': 18, 'Au': 79, 'At': 85, 'In': 49, 'Mo': 42, 'Am': 95, 'Pu': 94, 'Cm': 96}

# CODATA2006
speed_light_si = 299792458.0
mu_0_si = 4.0*math.pi*1e-7
epsilon_0_si = 1.0/(mu_0_si*speed_light_si**2)
planck_si = 6.62606896e-34
elementary_charge_si = 1.602176487e-19
electron_mass_si = 9.10938215e-31
proton_mass_si = 1.672621637e-27
electron_gyromagnetic_ratio_si = 1.76085977e11
avogadro_si = 6.02214179e23
molar_gas_si = 8.314472
hbar_si = planck_si / (2.0 * math.pi)
fine_structure_si = elementary_charge_si**2/(4.0*math.pi*epsilon_0_si*hbar_si*speed_light_si)
boltzmann_si = molar_gas_si/avogadro_si
amu_si = 1e-3/avogadro_si
