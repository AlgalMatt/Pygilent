
from  importlib import resources
import pandas as pd
import numpy as np
from decimal import Decimal

def get_default_stndvals():
    with resources.path("Pygilent.data", "stnd_conc_vals.csv") as f:
        stndvals_default_df = pd.read_csv(f, index_col=0)
    return stndvals_default_df


def make_stndvals_df(df, stnd_names, isotopes, cali_mode, dilutions=np.array([]), units='moles', ratio_element=None):
    
    if cali_mode not in ['ratio curve', 'ratio single', 'conc curve', 'conc single']:
            raise ValueError('Invalid calibration mode. Please select from: ratio curve, ratio single, conc curve, conc single.')
    
    if units not in ['moles', 'grams']:
        raise ValueError('Invalid units. Please select from: moles or grams.')
    
    
    #if  cali_mode=='conc curve':        
    #    if len(stnd_names)!=1 and type(stnd_names)!=str:
    #        raise ValueError(f'Only one standard name can be used for {cali_mode}.')
    """
    if 'conc single' in cali_mode and len(dilutions)>1:
        raise ValueError(f'Only one dilution can be used for {cali_mode}.')
    """
    if type(stnd_names) is str:
        stnd_names=[stnd_names]
    
    if type(dilutions) is int or type(dilutions) is float:
        dilutions=np.array([dilutions])
    else:
        dilutions=np.array(dilutions)
    
    if len(stnd_names)<2 and cali_mode=='ratio curve':
            raise ValueError(f'More than one standard name must be provided for {cali_mode}.')
        
    
    from Pygilent.pygilent import deconstruct_isotope_gas
    
    units_array=df.loc[deconstruct_isotope_gas(isotopes, 'element'), 'units'].values
    
    if 'conc' in cali_mode:
        if dilutions.size==0:
            raise ValueError(f'Dilutions must be provided for {cali_mode}.')
        
        elements=deconstruct_isotope_gas(isotopes, 'element')
        
        vals_arr=df.loc[elements, stnd_names].values
        
        if len(stnd_names)> 1:
            
            if dilutions.size>1 | dilutions.size!=len(stnd_names):
                raise ValueError('If using multiple standards, dilutions must be either a scalar or vector of length stnd_names')
            
            col_names=[]
            for name, dilution in zip(stnd_names, dilutions):
                col_names.append(str(dilution)+'_'+name)    
            
        else:
            col_names=np.char.add(dilutions.astype(str), '_'+stnd_names[0])
            
        stnd_vals_df=pd.DataFrame([], columns=col_names, index=isotopes)
        stnd_vals_df.loc[:, col_names]=dilutions*vals_arr
        stnd_vals_df.insert(0, 'units', units_array)
            
    else:
        if ratio_element is None:
            raise ValueError(f'Ratio element must be provided for {cali_mode}.')

        ratio_el_arr=df.loc[ratio_element, stnd_names].values
        stnd_vals_df=df.loc[deconstruct_isotope_gas(isotopes, 'element'), stnd_names]
        stnd_vals_df=stnd_vals_df/ratio_el_arr
        ratio_el_unit=df.loc[ratio_element, 'units']
        units_array=np.array([convert_units_to_ratio(u, denominator_unit=ratio_el_unit)  for u in units_array]).astype('object')
        stnd_vals_df.insert(0, 'units', units_array+' '+ratio_element)  
        
    
        
    stnd_vals_df.set_index(pd.Index(isotopes), inplace=True)

    
    if units=='moles':
        masses=np.array(get_atomic_mass(deconstruct_isotope_gas(isotopes, 'element'), out_type=float))
        stnd_vals_df.iloc[:,1:]=stnd_vals_df.iloc[:,1:]/masses[:, None]
        #replace 'g' with 'mol'
        stnd_vals_df['units']=(pd.Series(units_array).str.replace('g', 'mol')).values
        
        if 'ratio' in cali_mode:
            ratio_el_mass=get_atomic_mass(ratio_element, out_type=float)
            stnd_vals_df.loc[:,stnd_names]=stnd_vals_df.loc[:,stnd_names]*ratio_el_mass
            stnd_vals_df['units']=stnd_vals_df['units']+' '+ratio_element
        
    return stnd_vals_df



magnitude_sequence=['T', 'G', 'M', 'k', '', 'm', 'u', 'n', 'p', 'f', 'a']
magnitude_sym_to_fact_dict=dict(zip(magnitude_sequence, [Decimal('1E'+str(x)) for x in np.arange(12, -21, -3)]))
magnitude_fact_to_sym_dict={v: k for k, v in magnitude_sym_to_fact_dict.items()}




def convert_units_to_ratio(numerator_unit, denominator_unit):
    numerator_mag_sym=numerator_unit[0]
    denominator_mag_sym=denominator_unit[0] 
    ratio_mag=magnitude_sym_to_fact_dict[numerator_mag_sym]/magnitude_sym_to_fact_dict[denominator_mag_sym]
    ratio_mag_sym=magnitude_fact_to_sym_dict[ratio_mag]
    ratio_unit=ratio_mag_sym+numerator_unit.split('/')[0][1:]+'/'+denominator_unit.split('/')[0][1:]
    return ratio_unit

def convert_magnitude_ratio_2(numerator_val, denominator_val, numerator_unit, denominator_unit, stable=False):
    numerator_mag_sym=numerator_unit[0]
    denominator_mag_sym=denominator_unit[0]
    
    ratio_val=numerator_val/denominator_val
    
    ratio_mag=magnitude_sym_to_fact_dict[numerator_mag_sym]/magnitude_sym_to_fact_dict[denominator_mag_sym]
    
    if not stable:
        while ratio_val>1000 and ratio_mag<np.max(list(magnitude_fact_to_sym_dict.keys())):
            ratio_val=ratio_val/1000
            ratio_mag=ratio_mag*1000
        while ratio_val<0.1 and ratio_mag>np.min(list(magnitude_fact_to_sym_dict.keys())):
            ratio_val=ratio_val*1000
            ratio_mag=ratio_mag/1000
    
    ratio_mag_sym=magnitude_fact_to_sym_dict[ratio_mag]
    
    ratio_unit=ratio_mag_sym+numerator_unit[1:]
    
    return ratio_val, ratio_unit

#Copyright (c) 2018, Hegeman Lab
#All rights reserved.
#https://github.com/HegemanLab/atomicWeightsDecimal
# A Python dictionary of atomic weights in Decimal
atomicWeightsDecimal = {
        "H":	{
                    "standard":Decimal((0,(1,0,0,7,9,4),-5)),
            "abundant":Decimal((0,(1,0,0,7,8,2,5,0,3,1,9),-10))
            },
        "He":	{
            "standard":Decimal((0,(4,0,0,2,6,0,2),-6)),
            "abundant":Decimal((0,(4,0,0,2,6,0,3,2,4,9,7),-10))
            },
        "Li":	{
            "standard":Decimal((0,(6,9,4,1),-3)),
            "abundant":Decimal((0,(7,0,1,6,0,0,4,1),-7))
            },
        "Be":	{
            "standard":Decimal((0,(9,0,1,2,1,8,2),-6)),
            "abundant":Decimal((0,(9,0,1,2,1,8,2,2),-7))
            },
        "B":	{
            "standard":Decimal((0,(1,0,8,1,1),-3)),
            "abundant":Decimal((0,(1,1,0,0,9,3,0,5,5),-7))
            },
        "C":	{
            "standard":Decimal((0,(1,2,0,1,0,7),-4)),
            "abundant":Decimal((0,(1,2,0,0,0,0,0,0,0,0,0,0),-10))
            },
        "N":	{
            "standard":Decimal((0,(1,4,0,0,6,7),-4)),
            "abundant":Decimal((0,(1,4,0,0,3,0,7,4,0,0,7,4),-10))
                    },
        "O":	{
            "standard":Decimal((0,(1,5,9,9,9,4),-4)),
            "abundant":Decimal((0,(1,5,9,9,4,9,1,4,6,2,2,3),-10))
            },
        "F":	{
            "standard":Decimal((0,(1,8,9,9,8,4,0,3,2),-7)),
            "abundant":Decimal((0,(1,8,9,9,8,4,0,3,2,0),-8))
            },
        "Ne":	{
            "standard":Decimal((0,(2,0,1,7,9,7),-5)),
            "abundant":Decimal((0,(1,9,9,9,2,4,4,0,1,7,6),-9))
            },
        "Na":	{
            "standard":Decimal((0,(2,2,9,8,9,7,7,0),-6)),
            "abundant":Decimal((0,(2,2,9,8,9,7,6,9,6,6),-8))
            },
        "Mg":	{
            "standard":Decimal((0,(2,4,3,0,5,0),-4)),
            "abundant":Decimal((0,(2,3,9,8,5,0,4,1,8,7),-8))
            },
        "Al":	{
            "standard":Decimal((0,(2,6,9,8,1,5,3,8),-6)),
            "abundant":Decimal((0,(2,6,9,8,1,5,3,8,4,1),-8))
            },
        "Si":	{
            "standard":Decimal((0,(2,8,0,8,5,5),-4)),
            "abundant":Decimal((0,(2,7,9,7,6,9,2,6,4,9),-8))
            },
        "P":	{
            "standard":Decimal((0,(3,0,9,7,3,7,6,1),-6)),
            "abundant":Decimal((0,(3,0,9,7,3,7,6,1,4,9),-8))
            },
        "S":	{
            "standard":Decimal((0,(3,2,0,6,5),-3)),
            "abundant":Decimal((0,(3,1,9,7,2,0,7,0,7,3),-8))
            },
        "Cl":	{
            "standard":Decimal((0,(3,5,4,5,3),-3)),
            "abundant":Decimal((0,(3,4,9,6,8,8,5,2,7,1),-8))
            },
        "Ar":	{
            "standard":Decimal((0,(3,9,9,4,8),-3)),
            "abundant":Decimal((0,(3,9,9,6,2,3,8,3,1,2,4),-9))
            },
        "K":	{
            "standard":Decimal((0,(3,9,0,9,8,3),-4)),
            "abundant":Decimal((0,(3,8,9,6,3,7,0,6,9),-7))
            },
        "Ca":	{
            "standard":Decimal((0,(4,0,0,7,8),-3)),
            "abundant":Decimal((0,(3,9,9,6,2,5,9,1,2),-7))
            },
        "Sc":	{
            "standard":Decimal((0,(4,4,9,5,5,9,1,0),-6)),
            "abundant":Decimal((0,(4,4,9,5,5,9,1,0,2),-7))
            },
        "Ti":	{
            "standard":Decimal((0,(4,7,8,6,7),-3)),
            "abundant":Decimal((0,(4,7,9,4,7,9,4,7,0),-7))
            },
        "V":	{
            "standard":Decimal((0,(5,0,9,4,1,5),-4)),
            "abundant":Decimal((0,(5,0,9,4,3,9,6,3,5),-7))
            },
        "Cr":	{
            "standard":Decimal((0,(5,1,9,9,6,1),-4)),
            "abundant":Decimal((0,(5,1,9,4,0,5,1,1,5),-7))
            },
        "Mn":	{
            "standard":Decimal((0,(5,4,9,3,8,0,4,9),-6)),
            "abundant":Decimal((0,(5,4,9,3,8,0,4,9,3),-7))
            },
        "Fe":	{
            "standard":Decimal((0,(5,5,8,4,5),-3)),
            "abundant":Decimal((0,(5,5,9,3,4,9,4,1,8),-7))
            },
        "Co":	{
            "standard":Decimal((0,(5,8,9,3,3,2,0,0),-6)),
            "abundant":Decimal((0,(5,8,9,3,3,1,9,9,9),-7))
            },
        "Ni":	{
            "standard":Decimal((0,(5,8,6,9,3,4),-4)),
            "abundant":Decimal((0,(5,7,9,3,5,3,4,7,7),-7))
            },
        "Cu":	{
            "standard":Decimal((0,(6,3,5,4,6),-3)),
            "abundant":Decimal((0,(6,2,9,2,9,6,0,0,7),-7))
            },
        "Zn":	{
            "standard":Decimal((0,(6,5,4,0,9),-3)),
            "abundant":Decimal((0,(6,3,9,2,9,1,4,6,1),-7))
            },
        "Ga":	{
            "standard":Decimal((0,(6,9,7,2,3),-3)),
            "abundant":Decimal((0,(6,8,9,2,5,5,8,1),-6))
            },
        "Ge":	{
            "standard":Decimal((0,(7,2,6,4),-2)),
            "abundant":Decimal((0,(7,3,9,2,1,1,7,8,4),-7))
            },
        "As":	{
            "standard":Decimal((0,(7,4,9,2,1,6,0),-5)),
            "abundant":Decimal((0,(7,4,9,2,1,5,9,6,6),-7))
            },
        "Se":	{
            "standard":Decimal((0,(7,8,9,6),-2)),
            "abundant":Decimal((0,(7,7,9,1,6,5,2,2,1),-7))
            },
        "Br":	{
            "standard":Decimal((0,(7,9,9,0,4),-3)),
            "abundant":Decimal((0,(7,8,9,1,8,3,3,7,9),-7))
            },
        "Kr":	{
            "standard":Decimal((0,(8,3,7,9,8),-3)),
            "abundant":Decimal((0,(8,3,9,1,1,5,0,8),-6))
            },
        "Rb":	{
            "standard":Decimal((0,(8,5,4,6,7,8),-4)),
            "abundant":Decimal((0,(8,4,9,1,1,7,9,2,4),-7))
            },
        "Sr":	{
            "standard":Decimal((0,(8,7,6,2),-2)),
            "abundant":Decimal((0,(8,7,9,0,5,6,1,6,7),-7))
            },
        "Y":	{
            "standard":Decimal((0,(8,8,9,0,5,8,5),-5)),
            "abundant":Decimal((0,(8,8,9,0,5,8,4,8,5),-7))
            },
        "Zr":	{
            "standard":Decimal((0,(9,1,2,2,4),-3)),
            "abundant":Decimal((0,(8,9,9,0,4,7,0,2,2),-7))
            },
        "Nb":	{
            "standard":Decimal((0,(9,2,9,0,6,3,8),-5)),
            "abundant":Decimal((0,(9,2,9,0,6,3,7,6,2),-7))
            },
        "Mo":	{
            "standard":Decimal((0,(9,5,9,4),-2)),
            "abundant":Decimal((0,(9,7,9,0,5,4,0,6,9),-7))
            },
        "Ru":	{
            "standard":Decimal((0,(1,0,1,0,7),-2)),
            "abundant":Decimal((0,(1,0,1,9,0,4,3,4,8,8),-7))
            },
        "Rh":	{
            "standard":Decimal((0,(1,0,2,9,0,5,5,0),-5)),
            "abundant":Decimal((0,(1,0,2,9,0,5,5,0,4),-6))
            },
        "Pd":	{
            "standard":Decimal((0,(1,0,6,4,2),-2)),
            "abundant":Decimal((0,(1,0,5,9,0,3,4,8,4),-6))
            },
        "Ag":	{
            "standard":Decimal((0,(1,0,7,8,6,8,2),-4)),
            "abundant":Decimal((0,(1,0,6,9,0,5,0,9,3),-6))
            },
        "Cd":	{
            "standard":Decimal((0,(1,1,2,4,1,1),-3)),
            "abundant":Decimal((0,(1,1,3,9,0,3,3,5,8,6),-7))
            },
        "In":	{
            "standard":Decimal((0,(1,1,4,8,1,8),-3)),
            "abundant":Decimal((0,(1,1,4,9,0,3,8,7,9),-6))
            },
        "Sn":	{
            "standard":Decimal((0,(1,1,8,7,1,0),-3)),
            "abundant":Decimal((0,(1,1,9,9,0,2,1,9,8,5),-7))
            },
        "Sb":	{
            "standard":Decimal((0,(1,2,1,7,6,0),-3)),
            "abundant":Decimal((0,(1,2,0,9,0,3,8,2,2,2),-7))
            },
        "Te":	{
            "standard":Decimal((0,(1,2,7,6,0),-2)),
            "abundant":Decimal((0,(1,2,9,9,0,6,2,2,2,9),-7))
            },
        "I":	{
            "standard":Decimal((0,(1,2,6,9,0,4,4,7),-5)),
            "abundant":Decimal((0,(1,2,6,9,0,4,4,6,8),-6))
            },
        "Xe":	{
            "standard":Decimal((0,(1,3,1,2,9,3),-3)),
            "abundant":Decimal((0,(1,3,1,9,0,4,1,5,4,6),-7))
            },
        "Cs":	{
            "standard":Decimal((0,(1,3,2,9,0,5,4,5),-5)),
            "abundant":Decimal((0,(1,3,2,9,0,5,4,4,7),-6))
            },
        "Ba":	{
            "standard":Decimal((0,(1,3,7,3,2,7),-3)),
            "abundant":Decimal((0,(1,3,7,9,0,5,2,4,2),-6))
            },
        "La":	{
            "standard":Decimal((0,(1,3,8,9,0,5,5),-4)),
            "abundant":Decimal((0,(1,3,8,9,0,6,3,4,9),-6))
            },
        "Ce":	{
            "standard":Decimal((0,(1,4,0,1,1,6),-3)),
            "abundant":Decimal((0,(1,3,9,9,0,5,4,3,5),-6))
            },
        "Pr":	{
            "standard":Decimal((0,(1,4,0,9,0,7,6,5),-5)),
            "abundant":Decimal((0,(1,4,0,9,0,7,6,4,8),-6))
            },
        "Nd":	{
            "standard":Decimal((0,(1,4,4,2,4),-2)),
            "abundant":Decimal((0,(1,4,1,9,0,7,7,1,9),-6))
            },
        "Sm":	{
            "standard":Decimal((0,(1,5,0,3,6),-2)),
            "abundant":Decimal((0,(1,5,1,9,1,9,7,2,9),-6))
            },
        "Eu":	{
            "standard":Decimal((0,(1,5,1,9,6,4),-3)),
            "abundant":Decimal((0,(1,5,2,9,2,1,2,2,7),-6))
            },
        "Gd":	{
            "standard":Decimal((0,(1,5,7,2,5),-2)),
            "abundant":Decimal((0,(1,5,7,9,2,4,1,0,1),-6))
            },
        "Tb":	{
            "standard":Decimal((0,(1,5,8,9,2,5,3,4),-5)),
            "abundant":Decimal((0,(1,5,8,9,2,5,3,4,3),-6))
            },
        "Dy":	{
            "standard":Decimal((0,(1,6,2,5,0,0),-3)),
            "abundant":Decimal((0,(1,6,3,9,2,9,1,7,1),-6))
            },
        "Ho":	{
            "standard":Decimal((0,(1,6,4,9,3,0,3,2),-5)),
            "abundant":Decimal((0,(1,6,4,9,3,0,3,1,9),-6))
            },
        "Er":	{
            "standard":Decimal((0,(1,6,7,2,5,9),-3)),
            "abundant":Decimal((0,(1,6,5,9,3,0,2,9,0),-6))
            },
        "Tm":	{
            "standard":Decimal((0,(1,6,8,9,3,4,2,1),-5)),
            "abundant":Decimal((0,(1,6,8,9,3,4,2,1,1),-6))
            },
        "Yb":	{
            "standard":Decimal((0,(1,7,3,0,4),-2)),
            "abundant":Decimal((0,(1,7,3,9,3,8,8,5,8),-6))
            },
        "Lu":	{
            "standard":Decimal((0,(1,7,4,9,6,7),-3)),
            "abundant":Decimal((0,(1,7,4,9,4,0,7,6,8,2),-7))
            },
        "Hf":	{
            "standard":Decimal((0,(1,7,8,4,9),-2)),
            "abundant":Decimal((0,(1,7,9,9,4,6,5,4,8,8),-7))
            },
        "Ta":	{
            "standard":Decimal((0,(1,8,0,9,4,7,9),-4)),
            "abundant":Decimal((0,(1,8,0,9,4,7,9,9,6),-6))
            },
        "W":	{
            "standard":Decimal((0,(1,8,3,8,4),-2)),
            "abundant":Decimal((0,(1,8,3,9,5,0,9,3,2,3),-7))
            },
        "Re":	{
            "standard":Decimal((0,(1,8,6,2,0,7),-3)),
            "abundant":Decimal((0,(1,8,6,9,5,5,7,5,0,5),-7))
            },
        "Os":	{
            "standard":Decimal((0,(1,9,0,2,3),-2)),
            "abundant":Decimal((0,(1,9,1,9,6,1,4,7,9),-6))
            },
        "Ir":	{
            "standard":Decimal((0,(1,9,2,2,1,7),-3)),
            "abundant":Decimal((0,(1,9,2,9,6,2,9,2,3),-6))
            },
        "Pt":	{
            "standard":Decimal((0,(1,9,5,0,7,8),-3)),
            "abundant":Decimal((0,(1,9,4,9,6,4,7,7,4),-6))
            },
        "Au":	{
            "standard":Decimal((0,(1,9,6,9,6,6,5,5),-5)),
            "abundant":Decimal((0,(1,9,6,9,6,6,5,5,1),-6))
            },
        "Hg":	{
            "standard":Decimal((0,(2,0,0,5,9),-2)),
            "abundant":Decimal((0,(2,0,1,9,7,0,6,2,5),-6))
            },
        "Tl":	{
            "standard":Decimal((0,(2,0,4,3,8,3,3),-4)),
            "abundant":Decimal((0,(2,0,4,9,7,4,4,1,2),-6))
            },
        "Pb":	{
            "standard":Decimal((0,(2,0,7,2),-1)),
            "abundant":Decimal((0,(2,0,7,9,7,6,6,3,6),-6))
            },
        "Bi":	{
            "standard":Decimal((0,(2,0,8,9,8,0,3,8),-5)),
            "abundant":Decimal((0,(2,0,8,9,8,0,3,8,4),-6))
            },
        "Th":	{
            "standard":Decimal((0,(2,3,2,0,3,8,1),-4)),
            "abundant":Decimal((0,(2,3,2,0,3,8,0,4,9,5),-7))
            },
        "Pa":	{
            "standard":Decimal((0,(2,3,1,0,3,5,8,8),-5)),
            "abundant":Decimal((0,(2,3,1,0,3,5,8,8),-5))
            },
        "U":	{
            "standard":Decimal((0,(2,3,8,0,2,8,9,1),-5)),
            "abundant":Decimal((0,(2,3,8,0,5,0,7,8,3,5),-7))
                    }
    }



def get_atomic_mass(elements, out_type=float):
    if type(elements)==str:
        return out_type(atomicWeightsDecimal[elements]['standard'])
    else:
        return [out_type(atomicWeightsDecimal[element]['standard']) for element in elements]
    
    

    
