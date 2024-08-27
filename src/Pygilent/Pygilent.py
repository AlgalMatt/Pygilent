import numpy as np
import pandas as pd
import os
from pathlib import Path
import warnings
from Pygilent.stnds import get_default_stndvals, make_stndvals_df
import sympy as sym
from math import gamma
import re
import statsmodels.api as sm
import matplotlib.pyplot as plt
gamma_vectorized=np.vectorize(gamma)
##Functions

def find_substrings(array1, string1, ret_array=True, case=False):
    """
    Looks for occurrences of substring(s) within an array of strings, returning
    a boolean array. Works similarly to the Pandas str.contains method but can 
    for multiple strings in a list.
    
    Parameters
    ----------
    array1 : 1d array (list, numpy array)
        array to search.
    string1 : string, or 1d array of strings (list or numpy array)
        substrings used to search for within array1.
    ret_array : boolean, optional
        If true, then the output will be a boolean 1d array of the same size 
        as array1, providing True/False values for each element that 
        contains/does not contain any of the substrings within string1. 
        If false, then the output will be a matrix of len(array1) by
        len(string1) with each column being a separate boolean array of 
        occurrences of each substring in string1 within array1.
        The default is True.
    case_sensitive : boolean, optional
        If true, the search will be case-sensitive. The default is False.

    Returns
    -------
    retarray : numpy array or matrix of len(array1)
        An array of boolean values where True values indicate the presence of the 
        substring, string1, at the same index of array1. An element-wise 
        string1 in array1.

    """
    
    #vectorize lower cases
    nlower=np.vectorize(str.lower)
    
    retarray=[]
    #if argument string1 is a single string
    if type(string1)==str:
        #lower all cases
        if case==False:
            array1=nlower(array1)
            string1=string1.lower()
        for i in array1:
            retarray.append(string1 in i)   
    #if string1 is a list of strings             
    else:
        #lower all cases
        if case==False:
            array1=nlower(array1)
            string1=nlower(string1)
        retarray=np.full((len(array1), len(string1)), False)
        #iterate over the list of substrings
        for j, s in enumerate(string1):
            #iterate over the array of strings a check if the iterated 
            #substring is in it            
            for i, a in enumerate(array1):
                retarray[i, j]=s in a
        #if true, return a 1D array, else it returns a len(array1) by 
        #len(string1) matrix of occurrences of each substring within the array
        if ret_array:
            retarray=np.any(retarray, axis=1)           
    return retarray

def find_outliers(array1, mod=1.5):
    """
    Returns boolean array where true values denote outliers in original array
    
    Parameters
    ----------
    array1 : 1d or 2d array (numpy array)
        array to search for outliers.
    mod : modifier of outlier distance (iqr multiplier), default 1.5.

    Returns
    -------
    retarray : numpy array of len(array1)
        An array of boolean values where True values indicate the presence of 
        outliers at the same index of array1.

    """
    array1=np.array(array1, dtype=float)
    array1=array1.flatten()
    x = array1[~np.isnan(array1)]
    if len(x)>2:
        q75, q25 = np.percentile(x, [75 ,25])
        iqr = q75 - q25
        outs=((array1>iqr*mod+q75) | (array1<q25-iqr*mod))
    else:
        outs=np.isnan(array1)
        
    return outs

def deconstruct_isotope_gas(input, output='all'):
    """Deconstructs an isotope_gas string into constituent parts. The isotope_gas 
    string is assumed to be in the format of 'mass_element_gas_mode' and ignores
    Q2 masses. The function returns the mass, element, and gas mode as separate
    strings.

    Args:
        input (string): isotope_gas string
        output (str, optional): Define the output component ('mass', 'element', 
        'gas_mode' or 'all'). Defaults to 'all'.

    Raises:
        ValueError: if output is not one of 'mass', 'element', 'gas_mode' or 'all'

    Returns:
        strings of mass, element, and gas mode as strings
    """
    
    str_series=pd.Series(input)
    
    mass=str_series.str.extract(r'(\d+)').values.flatten()
    element=str_series.str.extract(r'([A-Z][a-z]*)').values.flatten()
    gas_mode=str_series.str.split('_').str[-1].values
    if type(input) is str:
        mass=mass[0]
        element=element[0]
        gas_mode=gas_mode[0]
        

    if output=='all':
        return mass, element, gas_mode
    elif output=='mass':
        return mass
    elif output=='element':
        return element
    elif output=='gas_mode':
        return gas_mode
    else:
        raise ValueError('Invalid output type. Please select from: all, mass, element, gas_mode.')
    
def unarchive_replicates(rep_series):
    """Extracts replicates from a list of strings and returns a dataframe of
    replicates. The function assumes that the replicates are in the format of
    #,#,# where # is a number (for cps) or 'PAU' (for det mode). 

    Args:
        rep_list (Pandas.Series): A series of lists containing replicates as strings.

    Returns:
        Pandas.DataFrame: A dataframe of the same length as the input series with
        columns of replicates. The columns are named by the order of the replicates.
    """
    
    
    pattern=r'(\d*\.\d+|[PAU])'
    rep_df=rep_series.str.extractall(pattern).unstack()
    rep_df=rep_df.droplevel(0, axis=1)
    rep_df.rename(columns={i: i+1 for i in rep_df.columns}, inplace=True)
    return rep_df

def extract_float_substring(input_string):
    # Regular expression to match a substring that can be converted to a float
    float_pattern = re.compile(r'[-+]?\d*\.\d+|\d+')

    # Search for the pattern in the input string
    match = float_pattern.search(input_string)

    if match:
        # Extract the matched substring
        float_substring = match.group()
        return float_substring
    else:
        # Return an empty string if no match is found
        return ""


def pivot_isotopes(df, var, index=['run_order', 'sample_name']):
    df_piv=df.pivot_table(index=index, columns='isotope_gas', values=var, sort=False, 
                          aggfunc='first', observed=False)
    df_piv.reset_index(inplace=True)
    df_piv.columns.name=None
    return df_piv
    
def make_empty_batch():
    default_columns=['run_name', 'run_order', 'time','sample_name', 'total_reps',
                     'isotope_gas', 'cps_mean', 'cps_std', 
                     'rep_list', 'sample_type', 'brkt_stnd', 'cali_curve', 'ratio_iso']     

def det_mode_mean_pivot(df, var='det_mode', pivot=True):

    df['det_mode_digi']=df[var].str.contains('P').astype(int)
    det_mode_mean=df.groupby(['run_order', 'isotope_gas'], sort=False, observed=False)['det_mode_digi'].agg('mean')
    det_mode_mean=det_mode_mean.reset_index()
    det_mode_mean['det_mode']='M'
    det_mode_mean.loc[det_mode_mean['det_mode_digi']==1, 'det_mode']='P'
    det_mode_mean.loc[det_mode_mean['det_mode_digi']==0, 'det_mode']='A'
    
    if pivot:
        return pivot_isotopes(det_mode_mean, 'det_mode', index=['run_order']).reset_index(drop=True)
    else:
        return det_mode_mean['run_order', 'isotope_gas', 'det_mode']


def archive_csv_to_batch(df, run_name=None, stnd_df=None):
    if run_name is None:
        run_name=pd.unique(df['run_name'])
        if len(run_name)>1:
            raise ValueError('Multiple run names detected. Please specify a run name.')
        
    df=df.loc[df['run_name']==run_name].copy()

    df['time']=pd.to_datetime(df['time'])
    
    #get the isotopes, ratio isotopes, gas modes, blank order, bracket order
    isotopes=pd.unique(df['isotope_gas'])
    ratio_iso=pd.unique(df['ratio_iso'])
    gas_modes=pd.unique(df['gas_mode'])
    blk_order=pd.unique(df.loc[df['sample_type'].str.contains('Blank'), 'run_order'])
    brkt_order=pd.unique(df.loc[df['sample_type'].str.contains('Bracket'), 'run_order'])
    cali_mode=pd.unique(df['cali_mode'])[0]

    timings=df[['run_order', 'time', 'session_time']].groupby('run_order').agg('first').reset_index()
    
    #define the number of replicates
    rep_num=pd.unique(df['total_reps'])[0]
    
    #NEEDED???
    #define the brkt stnd name
    brkt_stnd=pd.unique(df['brkt_stnd'])[0]
    
    #define the order of the calibration stnds as a dict
    cali_order={}
    cali_type_names=pd.unique(df.loc[df['sample_type'].str.contains('Cali'), 'sample_type'])
    for type_name in cali_type_names:
        type_name_arr=np.array(type_name.split())
        idx=np.char.find(type_name_arr, 'Cali')==0
        cali_name=type_name_arr[idx][0].strip('Cali_')
        cali_name_order=pd.unique(df.loc[df['sample_type'].str.contains(cali_name), 'run_order'])
        cali_order[cali_name]=cali_name_order
    
    
    
    
    #define the replicate df
    
    rep_df=unarchive_replicates(df['rep_list'])
    rep_PA_df=unarchive_replicates(df['rep_pa_list'])
    rep_df=pd.concat([df[['run_order', 'isotope_gas']], rep_df], axis=1)
    rep_PA_df=pd.concat([df[['run_order', 'isotope_gas']], rep_PA_df], axis=1)
    rep_df.reset_index(drop=True, inplace=True)
    rep_PA_df.reset_index(drop=True, inplace=True)
    rep_long_PA_df=rep_PA_df.melt(var_name='replicate', value_name='det_mode', id_vars=['run_order', 'isotope_gas'])
    rep_long_df=rep_df.melt(var_name='replicate', value_name='cps', id_vars=['run_order', 'isotope_gas'])
    rep_df=pd.concat([rep_long_df, rep_long_PA_df['det_mode']], axis=1)
    rep_df['isotope_gas']=pd.Categorical(rep_df['isotope_gas'], categories=pd.unique(rep_df['isotope_gas']))
    rep_df.sort_values(by=['run_order','isotope_gas', 'replicate'], inplace=True)
    
    
    cps_mean=pivot_isotopes(df, 'cps_mean')
    cps_std=pivot_isotopes(df, 'cps_std')
    ratio_cps=pivot_isotopes(df, 'cps_ratio')
    ratio_cps_se=pivot_isotopes(df, 'cps_ratio_se')
    brkted=pivot_isotopes(df, 'brkted')
    brkted_se=pivot_isotopes(df, 'brkted_se')
    
    if cali_mode == 'ratio curve':
        cali_curve={'ratio single':pivot_isotopes(df, 'cali_single'), 
                    'ratio curve':pivot_isotopes(df, 'cali_curve')}
    elif cali_mode in ['ratio single', 'conc single']:
        cali_curve={cali_mode:pivot_isotopes(df, 'cali_single')}
    else:
        cali_curve={cali_mode:pivot_isotopes(df, 'cali_curve')}
        
    
    if 'int_time' in  df.columns:
        int_dict=dict(zip(df['isotope_gas'], df['int_time']))
    elif 'cpc' in df.columns:
        int_group=df.groupby('isotope_gas', sort=False)[['cpc', 'cps_mean']].max()
        int_group['int_time']=int_group['cpc']/int_group['cps_mean']
        int_dict=dict(zip(int_group.index, int_group['int_time'].round(2)))
    else:
        int_dict=dict(zip(df['isotope_gas'], np.nan))
    
    #make analyte df
    mass, element, gas_mode=deconstruct_isotope_gas(isotopes)
    analytes=pd.DataFrame({'isotope_gas': isotopes, 
                             'mass': mass, 
                             'element': element, 
                             'gas_mode': gas_mode})
    analytes['int_time']=analytes['isotope_gas'].map(int_dict)
    units_dict=dict(zip(df['isotope_gas'], df['units']))
    analytes['units']=analytes['isotope_gas'].map(units_dict)
    
    
    if 'ratio' in cali_mode:
        ratio_iso_dict=dict(zip(df['isotope_gas'], df['ratio_iso']))
        analytes['ratio_iso']=analytes['isotope_gas'].map(ratio_iso_dict)
    
    
    default_stnds=get_default_stndvals()
    cali_stnd_df=make_stndvals_df(default_stnds, list(cali_order.keys()), isotopes)
    
    batched=Batch(run_name, isotopes, ratio_iso, gas_modes,  rep_long_df, 
                  blk_order, brkt_order, brkt_stnd, cali_mode, 
                  rep_num, cali_order, stnd_df)   
        
def sd_to_se(sd, rep_num):
    c4=gamma_vectorized(rep_num/2)/gamma_vectorized((rep_num-1)/2)*(2/(rep_num-1))**0.5
    return sd/c4/rep_num**0.5
    
def import_batch(path=None, ui=False, stnd_df=None):
    
    if ui or path is None:
        from Pygilent.uitools import select_folder
        
        path=select_folder()
        
    #try to convert path to Path object 
    try:
        path=Path(path)
    except TypeError:
        raise TypeError('Invalid path. Please provide a valid path.')

    
    
    #search for batch file
    
    if not os.path.isfile(path/'BatchLog.csv'):
        raise FileNotFoundError('No batch log found in the directory.')

    #load the batch log
    batch_df=pd.read_csv(path/'BatchLog.csv')
    batch_df.dropna(axis=0, how='all', inplace=True)
    
    #Re-format time
    batch_df.rename(columns={'Acq. Date-Time': 'time'}, inplace=True)
    
    #gets time string and converts to datetime
    
    if np.any(batch_df['time'].str.contains('/')):
        
        if np.any(batch_df['time'].str.contains('M')):
        
            batch_df['time']=pd.to_datetime(batch_df['time'], 
                                        format="%m/%d/%Y %I:%M:%S %p")    
            
        else:
            batch_df['time']=pd.to_datetime(batch_df['time'], 
                                        format="%d/%m/%Y %H:%M") 
    else:
        
        try:
            batch_df['time']=pd.to_datetime(batch_df['time'], format="%d-%b-%y %I:%M:%S %p") 
        except ValueError:
            batch_df['time']=pd.to_datetime(batch_df['time'])
    
    
    batch_df=batch_df.loc[(batch_df['Acquisition Result']=='Pass') & 
                          (batch_df["Sample Type"].str.contains("Tune")==False) &
                          (~(batch_df["Vial#"]=="-"))]

    batch_df.reset_index(drop=True, inplace=True)
    
    #Get a list of the sample names, make them into directories and put them into the main df
    subfolder_list=[path/Path(x).name for x in batch_df["File Name"]]
    batch_df['directory']=subfolder_list

    #Setup run info table
    batch_info=pd.DataFrame()
    batch_info[['sample_name',   'vial','time']]=batch_df[['Sample Name',  'Vial#', 'time']].copy()

    #give error if no samples found
    if len(batch_df)==0:
        raise ValueError('No valid samples found in batch log.')
    
    #Get the total elapsed time since first sample
    batch_info['session_time']=batch_df['time']-batch_df.loc[0,'time']
    #Convert to seconds
    batch_info['session_time']=batch_info['session_time'].dt.total_seconds()
    
    batch_info['run_order']=np.arange(0, len(batch_info))
    batch_info['sample_type']='sample'
    
    #This speeds up the processing to find the gas modes and number of repeats
    from concurrent.futures import ThreadPoolExecutor
    import csv
    def extract_gas_mode(file_path):
        with open(file_path, newline='') as f:
            reader = csv.reader(f)
            row1 = next(reader)[0].rsplit('/')[-1].strip('\n ')
        return row1
    
    
    
    
    #Find out how many repeats and gas modes there are by reading first sample
    first_sample_folder=subfolder_list[0]
    #First get a directory list of all .csv files in the sample folder
    csvlist = [s for s in os.listdir(first_sample_folder) if ".csv" in s and "quickscan" 
                not in s and first_sample_folder.name[0:-2] in s]
    file_paths = [first_sample_folder/c for c in csvlist]
    
    #Read the first file to get the number of repeats
    first_file=pd.read_csv(file_paths[0], skiprows=list(range(0, 7)), header=0)
    n=int(first_file['n'].values[0])
    
    if n > 1:
        replicates_in_files=False
        warnings.warn('Replicate data not found. Element ratio standard errors cannot be calculated.')
    else:
        replicates_in_files=True
    
    
    #Then quickly (using ThreadPoolExecutor) get the gas modes from files.
    testmode=[]
    with ThreadPoolExecutor() as executor:
        testmode = list(executor.map(extract_gas_mode, file_paths))
    
    #Get the number of repeats and gases by counting occurrences of gas modes
    total_reps=int(testmode.count(list(set(testmode))[0]))
    numgases=len(set(testmode))
    
    compile_df=pd.DataFrame()
    #Start iterating through samples
    for s_num, subfolder in enumerate(subfolder_list):   

        #Get list of subfolders containing replicates and gas modes. Exclude quickscan
        csvlist = [s for s in os.listdir(subfolder) if ".csv" in s and "quickscan" 
                not in s and subfolder.name[0:-2] in s]
        file_paths = [subfolder/c for c in csvlist]

        #iterate through replicates  
        for r in range(total_reps):
            #Empty dataframe for each repeat
            allgas_df=pd.DataFrame()
            #iterate through gas modes
            for g in range(numgases):

                fileloc=subfolder/csvlist[r+g*total_reps] #directory of file
                #Read the data
                gas_df=pd.read_csv(fileloc, skiprows=list(range(0, 7)), header=0) 
                #remove print info                               
                gas_df=gas_df.drop(gas_df.tail(1).index) 
                #get the current gas mode
                gasmodetxt=testmode[r+g*total_reps].strip(' ') 
                
                #Get the element and mass info, which is printed differently in csv
                #depending on whether using single or double quads.
                if 'Q1' in gas_df.columns and 'Q2' in gas_df.columns:
                    
                    gas_df["isotope_gas"]=(gas_df["Element"]
                                            +np.array(gas_df['Q1'], 
                                                    dtype=int).astype('str')
                                            +"_"+np.array(gas_df['Q2'], 
                                                        dtype=int).astype('str')
                                            +"_"+gasmodetxt)
                    gas_df["mass"]=np.array(gas_df['Q1'], dtype=int)   
                else:                    
                    #Make df of current gas mode
                    #Combine mass and element to make isotope column
                    gas_df["isotope_gas"]=(gas_df["Element"]
                                        +gas_df.iloc[:, 0]+"_"+gasmodetxt) 
                    gas_df["mass"]=np.array(gas_df['Mass'], dtype=int)  
        
                        
                gas_df["gas_mode"]=gasmodetxt
                            
                #PA column often wrongly named, so need to rename it.
                #first find the column next to CPS            
                idx=np.where(gas_df.columns == 'CPS')[0]+1
                gas_df['det_mode']=gas_df.iloc[:, idx]
                #Concat all gas modes of this repeat
                allgas_df=pd.concat([allgas_df, gas_df], ignore_index=True)
                
                
            single_rep_df=pd.DataFrame(np.array([list(batch_info.loc[s_num])]*len(allgas_df)), 
                                       columns=batch_info.columns)
            
            single_rep_df['run_order']=s_num
            single_rep_df['replicate']=r+1
            
            single_rep_df[['element', 'isotope_gas', 'mass', 'gas_mode', 'total_reps', 'det_mode', 'int_time', 
                           'cps', 'sd']]=allgas_df[['Element', 'isotope_gas', 'mass', 'gas_mode', 'n', 'det_mode', 'Time(Sec)', 
                           'CPS', 'SD']]

            single_rep_df['total_reps']=total_reps
            compile_df=pd.concat([compile_df, single_rep_df], axis=0)
    
    run_name=path.name
    
    compile_df['isotope_gas']=pd.Categorical(compile_df['isotope_gas'], categories=pd.unique(compile_df['isotope_gas']))
    compile_df['det_mode_digi']=compile_df['det_mode'].str.contains('P').astype(int)
    
    
    if replicates_in_files:
        rep_df=compile_df[['run_order', 'isotope_gas', 'replicate',  'cps', 'det_mode']].copy()
        rep_df.sort_values(by=['run_order','isotope_gas', 'replicate'], inplace=True)
        means_df=rep_df.groupby(['run_order', 'isotope_gas'], sort=False, observed=False)['cps'].agg(['mean', 'std'])
        means_df.reset_index(inplace=True, drop=False)
        cps_mean=pivot_isotopes(means_df, 'mean', index=['run_order'])
        cps_sd=pivot_isotopes(means_df, 'std', index=['run_order'])
        det_mode=det_mode_mean_pivot(compile_df)
        
        

    else:
        total_reps=n
        rep_df=None
        cps_mean=pivot_isotopes(compile_df[['run_order', 'isotope_gas',  'cps']].copy(), 'cps', index=['run_order'])
        cps_sd=pivot_isotopes(compile_df[['run_order', 'isotope_gas',  'sd']].copy(), 'sd', index=['run_order'])
        det_mode=pivot_isotopes(compile_df[['run_order', 'isotope_gas',  'det_mode']].copy(), 'det_mode', index=['run_order'])
        
    
    #insert sample names
    cps_mean.insert(0, 'sample_name', batch_info['sample_name'])
    cps_sd.insert(0, 'sample_name', batch_info['sample_name'])
    det_mode.insert(0, 'sample_name', batch_info['sample_name'])
    

    analytes=single_rep_df[['isotope_gas', 'element', 'mass', 'gas_mode', 'int_time']]
    rep_numbers_df=cps_mean.copy()
    rep_numbers_df.loc[:, analytes['isotope_gas']]=total_reps
    
    return Batch(run_name, batch_info, total_reps, analytes, rep_df, cps_mean, cps_sd, det_mode, rep_numbers_df)
    

    
def add_batch_to_archive(batch, archive_df):
    pass
            

def select_run_order(batch, run_order=np.array([], dtype=int), how='manual', keyword=None, case=False, sample_type='sample'):
    
    if sample_type == 'blank' and keyword is None:
        keyword='blk'
    
    if how=='auto':
        if keyword is None:
            raise ValueError('Keyword required for auto method.')
        run_order=batch.batch_info.loc[batch.batch_info['sample_name'].str.contains(keyword, case=case), 'run_order'].values
    elif how=='manual':
        run_order=np.array(run_order)
    else:
        from Pygilent.uitools import fancycheckbox
        if keyword is not None:
            idx=fancycheckbox(batch.batch_info['sample_name'], 'Select bracket standards', 
                                     defaults=batch.batch_info['sample_name'].str.contains(keyword, case=case))  
        else:
            idx=fancycheckbox(batch.batch_info['sample_name'], 'Select bracket standards')
        run_order=batch.batch_info.loc[idx, 'run_order'].values
    return run_order



def find_brackets(sample_pos, targets_orders):
    target_closest_1=[]
    target_closest_2=[]
    
    delta=targets_orders-sample_pos
    #find the closest blank before the sample order
    closest_array=np.vstack((targets_orders, np.abs(delta)))
    closest_array=np.vstack((closest_array, delta))
    closest_array = closest_array[:, np.argsort(closest_array[1,:], axis=0)]
    #If sample is before or after all targets, use just one closest
    if np.all(delta>=0) or np.all(delta<=0):
        target_closest_1= closest_array[0, 0]
        target_closest_2= closest_array[0, 0]
    #Otherwise use the two closest (bracketing)
    #If the first is before the sample in the run find one after
    elif closest_array[2, 0]<0:
        target_closest_1 = closest_array[0, 0]
        target_closest_2 = closest_array[0, np.where(closest_array[2, 1:]>0)[0][0]+1] 
    else:
        target_closest_1 = closest_array[0, np.where(closest_array[2, 1:]<0)[0][0]+1]
        target_closest_2 = closest_array[0, 0]
    return target_closest_1, target_closest_2
    



## Symbolic equations


#Use symbolic mode to apply data processing
#Define symbols
x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym=sym.symbols(
    'x_sym xb2_sym xb1_sym y_sym yb2_sym yb1_sym')
xs1_sym, xs2_sym, ys1_sym, ys2_sym=sym.symbols(
    'xs1_sym xs2_sym ys1_sym ys2_sym')
Dts_sym, Dts1b_sym, Dts2b_sym, Dtb_sym=sym.symbols(
    'Dts_sym Dts1b_sym Dts2b_sym Dtb_sym')
cov_xy_sym, cov_xs1ys1_sym, cov_xs2ys2_sym, cov_xb1yb1_sym, cov_xb2yb2_sym= \
    sym.symbols('''cov_xy_sym cov_xs1ys1_sym cov_xs2ys2_sym cov_xb1yb1_sym 
    cov_xb2yb2_sym''')
s_x_sym, s_y_sym, s_xb1_sym, s_xb2_sym, s_yb1_sym, s_yb2_sym, s_xs1_sym, \
    s_xs2_sym, s_ys1_sym, s_ys2_sym=sym.symbols(
    '''s_x_sym s_y_sym s_xb1_sym s_xb2_sym s_yb1_sym s_yb2_sym s_xs1_sym 
    s_xs2_sym s_ys1_sym s_ys2_sym''')



blkcorr_x_sym=(x_sym - Dtb_sym*xb2_sym + xb1_sym*(Dtb_sym - 1))

calc_blkcorr=sym.lambdify((x_sym, xb2_sym, xb1_sym, Dtb_sym), blkcorr_x_sym)

blkcorr_x_var_sym=(s_x_sym**2*blkcorr_x_sym.diff(x_sym)**2+s_xb1_sym**2*blkcorr_x_sym.diff(xb1_sym)**2
                   +s_xb2_sym**2*blkcorr_x_sym.diff(xb2_sym)**2)

calc_blkcorr_variance=sym.lambdify((x_sym, xb2_sym, xb1_sym, Dtb_sym, s_x_sym, s_xb1_sym, s_xb2_sym), blkcorr_x_var_sym)

blkcorr_y_sym=(y_sym - Dtb_sym*yb2_sym + yb1_sym*(Dtb_sym - 1))

R_sym=blkcorr_x_sym/blkcorr_y_sym

calc_R = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, 
                            Dtb_sym), R_sym)


R_var_sym=(s_x_sym**2*R_sym.diff(x_sym)**2+s_y_sym**2*R_sym.diff(y_sym)**2
                   +s_xb1_sym**2*R_sym.diff(xb1_sym)**2+s_xb2_sym**2*R_sym.diff(xb2_sym)**2
                   +s_yb1_sym**2*R_sym.diff(yb1_sym)**2+s_yb2_sym**2*R_sym.diff(yb2_sym)**2
                   +2*cov_xy_sym*R_sym.diff(x_sym)*R_sym.diff(y_sym)
                   +2*cov_xb1yb1_sym*R_sym.diff(xb1_sym)*R_sym.diff(yb1_sym)
                   +2*cov_xb2yb2_sym*R_sym.diff(xb2_sym)*R_sym.diff(yb2_sym))  

calc_R_variance=sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, 
                        Dtb_sym, cov_xy_sym, cov_xb1yb1_sym, cov_xb2yb2_sym, 
                        s_x_sym, s_y_sym, s_xb1_sym, s_xb2_sym, s_yb1_sym, 
                        s_yb2_sym), R_var_sym)



bracketed_R_sym=-blkcorr_x_sym/((((Dts_sym - 1)\
    *(xs1_sym - Dts1b_sym*xb2_sym + xb1_sym*(Dts1b_sym - 1)))\
    /(ys1_sym - Dts1b_sym*yb2_sym + yb1_sym*(Dts1b_sym - 1))\
    -(Dts_sym*(xs2_sym - Dts2b_sym*xb2_sym + xb1_sym*(Dts2b_sym - 1)))\
    /(ys2_sym - Dts2b_sym*yb2_sym + yb1_sym*(Dts2b_sym - 1)))\
    *blkcorr_y_sym)

calc_bracketed_R = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, Dtb_sym, 
              xs1_sym, ys1_sym, Dts1b_sym, xs2_sym, ys2_sym, Dts2b_sym, 
              Dts_sym), bracketed_R_sym)  

bracketed_R_var_sym=(s_x_sym**2*bracketed_R_sym.diff(x_sym)**2+s_y_sym**2*bracketed_R_sym.diff(y_sym)**2
                   +s_xb1_sym**2*bracketed_R_sym.diff(xb1_sym)**2+s_xb2_sym**2*bracketed_R_sym.diff(xb2_sym)**2
                   +s_xs1_sym**2*bracketed_R_sym.diff(xs1_sym)**2+s_xs2_sym**2*bracketed_R_sym.diff(xs2_sym)**2
                   +s_yb1_sym**2*bracketed_R_sym.diff(yb1_sym)**2+s_yb2_sym**2*bracketed_R_sym.diff(yb2_sym)**2
                   +s_ys1_sym**2*bracketed_R_sym.diff(ys1_sym)**2+s_ys2_sym**2*bracketed_R_sym.diff(ys2_sym)**2
                   +2*cov_xy_sym*bracketed_R_sym.diff(x_sym)*bracketed_R_sym.diff(y_sym)
                   +2*cov_xb1yb1_sym*bracketed_R_sym.diff(xb1_sym)*bracketed_R_sym.diff(yb1_sym)
                   +2*cov_xb2yb2_sym*bracketed_R_sym.diff(xb2_sym)*bracketed_R_sym.diff(yb2_sym)
                   +2*cov_xs1ys1_sym*bracketed_R_sym.diff(xs1_sym)*bracketed_R_sym.diff(ys1_sym)
                   +2*cov_xs2ys2_sym*bracketed_R_sym.diff(xs2_sym)*bracketed_R_sym.diff(ys2_sym))

calc_bracketed_R_variance = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, 
                                              Dtb_sym, xs1_sym, ys1_sym, Dts1b_sym, xs2_sym, ys2_sym
                                              ,Dts2b_sym, Dts_sym, cov_xy_sym, cov_xb1yb1_sym, 
                                              cov_xb2yb2_sym, cov_xs1ys1_sym, cov_xs2ys2_sym, 
                                              s_x_sym, s_y_sym, s_xb1_sym, s_xb2_sym,
                                              s_yb1_sym, s_yb2_sym, s_xs1_sym, s_ys1_sym, s_xs2_sym, 
                                              s_ys2_sym), bracketed_R_var_sym)




## Classes


class Batch:   
    """An object for organising and processing Agilent ICP-MS batch data.

    Attributes:
    
    """
    
    mode_options=('ratio curve', 'ratio single', 'conc curve', 'conc single')
    
    def __init__(self, run_name=None, batch_info=None, total_reps=None, analytes=None, rep_df=None, 
                 cps_mean=None, cps_sd=None, det_mode=None, rep_numbers_df=None, cps_ratio=None, cps_ratio_se=None, 
                 calibrated_output=None, calibrated_output_se=None, cov=None, 
                 cali_stnd_df=None, curve_mdl=None, blk_order=np.array([], dtype=int), brkt_order=np.array([], dtype=int), 
                 brkt_stnd=None, cali_mode=None, internal_stnd=None, 
                 cali_order={}, stnd_df=None, __process_inputs__=None, cali_blocks=None, bracketed=None, 
                 bracketed_se=None, cps_blk_corrected=None, cps_blk_corrected_se=None, __calibrated_x__=None):
        self.run_name=run_name
        self.batch_info=batch_info
        self.total_reps=total_reps
        self.analytes=analytes
        self.rep_df=rep_df
        self.cps_mean=cps_mean
        self.cps_sd=cps_sd
        self.det_mode=det_mode
        self.rep_numbers_df=rep_numbers_df
        self.cps_ratio=cps_ratio
        self.cps_ratio_se=cps_ratio_se
        self.calibrated_output={k: None for k in self.mode_options}
        self.calibrated_output_se={k: None for k in self.mode_options}
        self.cov=cov
        self.cali_stnd_df=cali_stnd_df
        self.curve_mdl=curve_mdl
        if not np.all(np.isin(blk_order, self.batch_info['run_order'].values)):
            raise ValueError('Invalid bracket order. Must be from array of run orders')
        self.blk_order=np.array(blk_order, dtype=int)
        if not np.all(np.isin(brkt_order, self.batch_info['run_order'].values)):
            raise ValueError(f'Invalid bracket order. Must be from array of run orders.')
        self.brkt_order=np.array(brkt_order, dtype=int)

        self.__process_inputs__=__process_inputs__
        
        self.brkt_stnd=brkt_stnd
        
        if cali_mode is not None:
            if cali_mode.lower() in ['ca check', 'ca_check','check', 'conc check']:
                warnings.warn('Conc check mode selected. Calibration mode will be set to conc single.')
                self.cali_mode = 'conc single'
            if cali_mode.lower() not in self.mode_options:
                raise ValueError(f'Invalid calibration mode. Please select from the following: {self.mode_options}.')
        self.cali_mode=cali_mode
        

        self.internal_stnd=internal_stnd
        
        
        self.bracketed=bracketed
        self.bracketed_se=bracketed_se
        self.cali_order=cali_order
        self.stnd_df=stnd_df
        self.cali_blocks=cali_blocks
        self.cps_blk_corrected=cps_blk_corrected
        self.cps_blk_corrected_se=cps_blk_corrected_se
        self.__calibrated_x__=__calibrated_x__
    
    def set_blks(self, blk_order=np.array([], dtype=int), how='auto', keyword='blk', case=False):
        """Define the positions of the blanks within the batch

        Args:
            blk_order (array, optional): Array of sample positions within the batch.
            how (str, optional): How the blanks should be set. Can be 'auto' (default),
                where the keyword is searched for in the sample name. If 'ui' then a user interface is 
                made for selection of blanks. If 'manual' then the blank positions are set by
                the blk_order argument. 
            keyword (str, optional): Sample name search keyword used when how = 'auto'. 
                Defaults to 'blk'.
            case (bool, optional): Case sensitivity of the keyword. Defaults to False.

        Raises:
            ValueError: If 'auto', 'manual', or 'ui' are not given in how argument.
        """
        
        
        if how not in ['auto', 'manual', 'ui']:
            raise ValueError('Invalid method. Please select from: auto, manual, ui.')

        #reset the original bracket order
        self.batch_info.loc[self.blk_order, 'sample_type']='sample'
        sample_type='blank'
        self.blk_order=select_run_order(self, blk_order, how, keyword, case, sample_type)
        self.batch_info.loc[self.blk_order, 'sample_type']=sample_type
        
        
        
        
            
    def check_blks(self):
        from Pygilent.uitools import pickfig
        cpsblank=self.cps_mean.loc[self.blk_order, np.append('run_order', self.analytes['isotope_gas'].values)]
        deblank=pickfig(cpsblank, 'run_order', 'Click on blanks to remove outliers')
        self.blk_order=self.blk_order[~np.in1d(self.blk_order, deblank)]
        self.batch_info.loc[deblank, 'sample_type']='sample'
        self.batch_info.loc[self.blk_order, 'sample_type']='blank'

    
    
    

    def set_brkt_stnds(self, brkt_order=np.array([], dtype=int), how='manual', keyword=None, case=False):
        if how not in ['auto', 'manual', 'ui']:
            raise ValueError('Invalid method. Please select from: auto, manual, ui.')

        #reset the original bracket order
        self.batch_info.loc[self.brkt_order, 'sample_type']='sample'
        sample_type='bracket'
        self.brkt_order=select_run_order(self, brkt_order, how, keyword, case, sample_type)
        self.batch_info.loc[self.brkt_order, 'sample_type']=sample_type
    
    def check_brkt_stnds(self):
        from Pygilent.uitools import pickfig
        cpsbrkt=self.cps_mean.loc[self.brkt_order, np.append('run_order', self.analytes['isotope_gas'].values)]
        debrkt=pickfig(cpsbrkt, 'run_order', 'Click on bracket standards to remove outliers')
        self.brkt_order=self.brkt_order[~np.in1d(self.brkt_order, debrkt)]
        self.batch_info.loc[debrkt, 'sample_type']='sample'
        self.batch_info.loc[self.brkt_order, 'sample_type']='bracket'
    
    def set_internal_stnd(self, how='manual', ratio_isos=None, keyword=None):
        
        if how not in ['manual', 'ui', 'auto']:
            raise ValueError('Invalid method. Please select from: manual, auto or ui.')

        if how=='auto' and keyword is None:
            raise ValueError('Keyword required for auto method.') 
        
        ratio_isos_bool={}
        
        if keyword is not None:
            for gas in pd.unique(self.analytes['gas_mode']):
                #use str.contains to find the isotope that starts with keyword and ends with gas
                ratio_isos_bool[gas]=self.analytes['isotope_gas'].str.contains(f'{keyword}.*{gas}', case=True)
            if how =='auto':
                ratio_isos={k: self.analytes['isotope_gas'].values[v][0] for k, v in ratio_isos_bool.items()}
            
        
        if how=='manual':  
            if type(ratio_isos) is not dict:
                raise TypeError('Ratio isotopes must be a dictionary of gas_mode: ratio_isotope.')
            if len(ratio_isos) != len(pd.unique(self.analytes['gas_mode'])):
                raise ValueError('Number of ratio isotopes must match number of gas modes.')
            
    
        if how =='ui':
            from Pygilent.uitools import fancycheckbox_2window
            gas_modes=pd.unique(self.analytes['gas_mode'])
            isotopes=pd.unique(self.analytes['isotope_gas'])
            ratio_isos_bool=fancycheckbox_2window(isotopes, gas_modes, 
                                             title_1='Select ratio isotope', 
                                             title_2='Select gas mode', 
                                             single_1=True, defaults=ratio_isos_bool)
            ratio_isos={k: isotopes[v][0] for k, v in ratio_isos_bool.items()}
            
        
        
        for key, val in ratio_isos.items():
            if type(val) is not str:
                raise TypeError('Ratio isotopes must be strings.')
            if val not in pd.unique(self.analytes['isotope_gas']):
                raise ValueError(f'{val} is not a valid isotope gas.')
            if key not in pd.unique(self.analytes['gas_mode']):
                raise ValueError(f'{key} is not a valid gas mode.')
        
        ratio_element_list=[deconstruct_isotope_gas(x, output='element') for x in ratio_isos.values()]
        if len(np.unique(ratio_element_list))>1:
            raise ValueError('Each ratio isotope must be the same element.')
            
        self.internal_stnd=ratio_isos

            
    
    def set_cali_stnds(self, stnd_vals_df, cali_run_order=np.array([], dtype=int), cali_order={}, 
                            how='manual', keyword=None, cali_stnd_df=None, single_conc_dilution=None, 
                            units='moles'):
        if how not in ['auto', 'manual', 'ui']:
            raise ValueError('Invalid method. Please select from: auto, manual, ui.')
        
        if self.cali_mode is None:
            raise ValueError('Calibration mode not set. Please set calibration mode.')
        
        if self.internal_stnd is not None:        
            ratio_element=deconstruct_isotope_gas(list(self.internal_stnd.values())[0], output='element')
        
        if self.cali_mode == 'conc single' and single_conc_dilution is None:
            raise ValueError('Single conc dilution not set. Please set single conc dilution.')
        
        if how =='ui':
            from Pygilent.uitools import fancycheckbox_2window
        
        from pandas.api.types import is_numeric_dtype
        stnd_vals_names = np.array([cols for cols in stnd_vals_df.columns if is_numeric_dtype(stnd_vals_df[cols])])
        
        

        if how == 'manual':
            self.cali_order=cali_order
            self.cali_stnd_df=cali_stnd_df
            
        
        elif 'single' in self.cali_mode:
            cali_run_order=self.brkt_order
            #find the suggested values
            bracket_names=pd.unique(self.batch_info.loc[cali_run_order, 'sample_name'])
            associate_defaults={stnd_name: find_substrings(bracket_names, str(stnd_name), case=False) for stnd_name in stnd_vals_names}
            if how=='ui':
                bracket_dict=fancycheckbox_2window(bracket_names, stnd_vals_names, 
                                                   title_1='Bracketing standard names in sample list', title_2='Link to standard in directory',
                                                   defaults=associate_defaults, single_2=True)
            else:
                bracket_dict=associate_defaults
            
            cali_order={}
            for k, v in bracket_dict.items():
                if np.any(v):
                    name=bracket_names[v]
                    idx=np.isin(self.batch_info.loc[cali_run_order, 'sample_name'] , name)
                    self.cali_order[k]=cali_run_order[idx]
            #make cali_stnd_df
            if self.cali_mode == 'ratio single':
                self.cali_stnd_df=make_stndvals_df(df=stnd_vals_df, stnd_names=list(self.cali_order.keys()), 
                                               isotopes=self.analytes['isotope_gas'].values, 
                                               cali_mode=self.cali_mode, ratio_element=ratio_element, 
                                               units=units)
            else:
                self.cali_stnd_df=make_stndvals_df(df=stnd_vals_df, stnd_names=list(self.cali_order.keys()), 
                                               isotopes=self.analytes['isotope_gas'].values, 
                                               cali_mode=self.cali_mode, dilutions=single_conc_dilution, 
                                               units=units)
                
                
                
        elif self.cali_mode == 'ratio curve':
            if how =='auto' and keyword is None:
                raise ValueError('Keyword required for auto method.')
            if keyword is not None:
                associate_defaults={stnd_name: find_substrings(self.batch_info['sample_name'], str(stnd_name), case=False) for stnd_name in keyword}
            else:
                associate_defaults=None
            if how=='ui':
                cali_dict=fancycheckbox_2window(self.batch_info['sample_name'], stnd_vals_names, 
                                                associate_defaults, 'Associate calibration standards with standards list')
            else:
                cali_dict=associate_defaults
            self.cali_order={k: self.batch_info.loc[v, 'run_order'].values for k, v in cali_dict.items() if np.any(v)}
            
            #make cali_stnd_df
            self.cali_stnd_df=make_stndvals_df(df=stnd_vals_df, stnd_names=list(self.cali_order.keys()), 
                                               isotopes=self.analytes['isotope_gas'].values, 
                                               cali_mode=self.cali_mode, ratio_element=ratio_element, 
                                               units=units)
            
        
        elif self.cali_mode == 'conc curve': 
            if how =='auto' and keyword is None:
                raise ValueError('Keyword required for auto method.')
            if keyword is not None:
                if type(keyword) is not str:
                    raise ValueError('Keyword must be a single standard name for conc curve mode.')
                
                stnd_name_idx=stnd_vals_df.columns.str.contains(keyword.lower(), case=False)
                
                if np.sum(stnd_name_idx)==0:
                    raise ValueError('Keyword not found in standard names.')
                if np.sum(stnd_name_idx)>1:
                    raise ValueError('Keyword found in multiple standard names.')
                
                stnd_name=stnd_vals_df.columns[stnd_name_idx].values[0]
            
                associate_defaults={stnd_name: self.batch_info['sample_name'].str.contains(keyword, case=False)}
            else:
                associate_defaults=None
            if how=='ui':
                cali_dict=fancycheckbox_2window(items_1=self.batch_info['sample_name'], 
                                                items_2=stnd_vals_names, defaults=associate_defaults,
                                               title_1='sample list', title_2='stock standard list', single_2=True)
            else:
                cali_dict=associate_defaults
            
            stnd_name=list(cali_dict.keys())[0]
            cali_rows=self.batch_info.loc[cali_dict[stnd_name], 'run_order'].values
            

            unique_stnd_names=pd.unique(self.batch_info.loc[cali_dict[stnd_name], 'sample_name'])

            stnd_conc_defaults=[extract_float_substring(s) for s in unique_stnd_names]

            if how == 'ui':
                
                from Pygilent.uitools import create_entry_window
                
                stnd_conc_dict = create_entry_window(list(unique_stnd_names), 
                                                     default_values=stnd_conc_defaults)
            else:
                stnd_conc_dict=dict(zip(unique_stnd_names, np.array(stnd_conc_defaults).astype(float)))

            
            dilutions=[val for val in stnd_conc_dict.values()]
            self.cali_order={str(val)+'_'+stnd_name:[] for val in dilutions}

            for key, val in stnd_conc_dict.items():
                key_rows=cali_rows[self.batch_info.loc[cali_rows, 'sample_name']==key]
                self.cali_order[str(val)+'_'+stnd_name].extend(list(key_rows))
            
            #make cali_stnd_df
            self.cali_stnd_df=make_stndvals_df(df=stnd_vals_df, stnd_names=stnd_name, 
                                               isotopes=self.analytes['isotope_gas'].values, 
                                               cali_mode=self.cali_mode, dilutions=dilutions, 
                                               units=units)
        
        for key, val in self.cali_order.items():
            self.batch_info.loc[val, 'calibrant']=key
        
        #if using a cali curve, warn if unequal number of standards
        if 'curve' in self.cali_mode:
            lengths=np.array([len(v) for v in self.cali_order.values()])
            #check if all lengths are the same
            if not np.all(lengths==lengths[0]):
                warnings.warn('It is advisable to have the same number of each standard in the calibration.')

    
    
    def set_calibration_blocks(self, how='auto', cali_blocks=None):
        if how not in ['auto', 'manual']:
            raise ValueError('Invalid method. Please select from: auto or manual')
        
        if self.cali_stnd_df is None:
            raise ValueError('Calibration standards must be set before calibration blocks.')
        
        if how=='auto':
            #find nearest calibration standard to each sample    
            cali_blocks={k:[] for k in self.cali_order.keys()}
            for i, row in self.batch_info.iterrows():
                for k, v in self.cali_order.items():
                    cali_blocks[k].append(v[np.argmin(np.abs(i-v))])
            

                    

        elif how=='manual':
            if cali_blocks is None:
                raise ValueError('Calibration blocks must be set for manual method.')
        
        
        
        cali_blocks_df=pd.DataFrame(cali_blocks)
        cali_blocks_df.insert(0, 'run_order', self.batch_info['run_order'])
        
        cali_blocks_df_unique=cali_blocks_df.drop_duplicates()
        
        for i, row in cali_blocks_df_unique.iterrows():
            cali_blocks_df.loc[np.all(cali_blocks_df==row, axis=1), 'cali_block']=i
        
        self.cali_blocks=cali_blocks_df

    
    
    
    def check_cali_curve(self):
        pass
                
    def initialize(self):
        #check if the batch has correct attributes to proceed
        if type(self.cps_mean) is not pd.core.frame.DataFrame and type(self.rep_cps) is not pd.core.frame.DataFrame:
            raise RuntimeError('No raw data provided. Please provide raw data.')
        elif type(self.rep_cps) is not pd.core.frame.DataFrame:
            warnings.warn('No replicate data provided. Standard errors cannot be calculated.')
        if type(self.timings) is not pd.core.frame.DataFrame:
            raise RuntimeError('No timing data provided. Please provide timing data.')
        if self.cali_mode not in ['ratio curve', 'ratio single', 'conc curve', 'conc single']:
            raise RuntimeError('Invalid calibration mode provided. Please provide a calibration mode using set_cali_mode method.')
        
        if len(self.blk_order)==0:
            warnings.warn('No blank order provided. Blanks will not be removed.')
        
        if len(self.brkt_order)==0:
            if 'single' in self.cali_mode:
                raise RuntimeError('No bracket order provided. Brackets are required for single-point calibration.')
            else:
                warnings.warn('No bracket order provided. Sample will not be drift-corrected.')

        if len(self.cali_order)==0:
            raise RuntimeError('No calibration standards provided.')
        elif len(self.cali_order)==1 and 'curve' in self.cali_mode:
            raise RuntimeError('Only one calibration standard provided. Calibration curve cannot be fit.')
    
    def open_replicate_editor(self):
        pass
    
    

    
    def set_covariances(self):
        #set covariances calculating errors of ratios
        
        if self.internal_stnd is None:
            raise ValueError('Covariances require internal standard to be set.')
        
        repCPS_x=self.rep_df.pivot(index=['run_order', 'replicate'], columns='isotope_gas', values='cps')
        repCPS_y=repCPS_x.copy() 
        for iso in self.analytes['isotope_gas']:
            gas=deconstruct_isotope_gas(iso, 'gas_mode')
            ratio_iso_gasmode=self.internal_stnd[gas]
            repCPS_y.loc[:, iso]=repCPS_x.loc[:, ratio_iso_gasmode]
        
        #covariances
        cov_df=pd.DataFrame([], columns=self.analytes['isotope_gas'].values)
        #cycle through samples with nested loop of isotopes to get covariances
        for runorder in self.cps_mean.index.values:
            cov_array=np.array([])
            for iso in self.analytes['isotope_gas']:
                #array of numerator isotopes
                rep_x_array=repCPS_x.loc[runorder, iso].values
                #array of denominators (Ca)
                rep_y_array=repCPS_y.loc[runorder, iso].values  
                #covariances
                cov_array=np.append(cov_array, 
                                np.cov(np.vstack((rep_x_array, rep_y_array)))[0, 1])
            #make into dataframe   
            cov_df.loc[runorder, :]=cov_array
        self.cov=cov_df
    
    
    def initialise(self):
        #fully process the batch using the calibration mode specified
        
        
        rep_cps_pivot=self.rep_df.pivot(index=['run_order', 'replicate'], columns='isotope_gas', values='cps')
        #rep_pa_pivot=self.rep_df.pivot(index=['run_order', 'replicate'], columns='isotope_gas', values='det_mode')
        #gasmode_isotope_dict={gas_mode: self.analytes.loc[self.analytes['gas_mode']==gas_mode, 'isotope_gas'].values for gas_mode in pd.unique(self.analytes['gas_mode'])}
    
        processing_df=pd.DataFrame([])            
            
        #if ratio mode or using internal standard
        if self.internal_stnd is not None:
            
            y_df=self.cps_mean.copy() #mean denominator cps
            s_y_df=self.cps_sd.copy() #denominator sd  
            repCPS_y_df=rep_cps_pivot.copy() #replicate denominator cps
            #CPC_y_df=self.cps_mean.copy() #for theoretical errors (denominator counts per cycle)


            process_inputs_df=pd.DataFrame([], columns=['run_order', 'isotope_gas', 'x', 'xb1', 'xb2', 'y', 'yb1', 'yb2', 'Dtb', 
                                                        'xs1', 'xs2', 'ys1', 'ys2',
                                                        'Dts1b', 'Dts2b', 'Dts',
                                                        's_x', 's_y', 's_xb1', 's_xb2', 's_yb1', 's_yb2', 's_xs1', 's_xs2', 's_ys1', 's_ys2', 
                                                        'cov_xy', 'cov_xs1ys1', 'cov_xs2ys2', 'cov_xb1yb1', 'cov_xb2yb2'])
            
            
            for iso in self.analytes['isotope_gas']:
                gas=deconstruct_isotope_gas(iso, 'gas_mode')
                ratio_iso_gasmode=self.internal_stnd[gas]
                y_df.loc[:, iso]=self.cps_mean.loc[:, ratio_iso_gasmode]
                s_y_df.loc[:, iso]=self.cps_sd.loc[:, ratio_iso_gasmode]
                repCPS_y_df.loc[:, iso]=rep_cps_pivot.loc[:, ratio_iso_gasmode]
            
            self.set_covariances()
            
        else: #if not using internal standard
            process_inputs_df=pd.DataFrame([], columns=['run_order', 'isotope_gas', 'x', 'xb1', 'xb2', 'Dtb'])
            
        process_inputs_df['isotope_gas']=list(self.analytes['isotope_gas'])*len(self.batch_info)
        
        process_inputs_df['run_order']=np.repeat(self.batch_info['run_order'].values, len(self.analytes['isotope_gas']))
        
        

        #cycle through sample-by-sample
        for samp_pos in self.batch_info['run_order']:
            
            #skip blanks
            if samp_pos in self.blk_order:
                continue
            
            df_idx=process_inputs_df['run_order']==samp_pos
                
            #find bracketing blanks  
            if len(self.blk_order)>0:
                blk1, blk2=find_brackets(samp_pos, self.blk_order)
                processing_df.loc[samp_pos, 'blk1']=blk1
                processing_df.loc[samp_pos, 'blk2']=blk2
                
                #find relative timings between brackets and blanks
                if blk1 == blk2:
                    Dtb=0
                    Dts1b=0
                    Dts2b=0
                    
                    if self.internal_stnd is not None:
                        processing_df.loc[samp_pos, 'brkt1_blk_time']=Dts1b
                        processing_df.loc[samp_pos, 'brkt2_blk_time']=Dts2b
                else:
                    Dtb=(self.batch_info.loc[samp_pos, 'session_time']-self.batch_info.loc[blk1, 'session_time'])/(
                        self.batch_info.loc[blk2, 'session_time']-self.batch_info.loc[blk1, 'session_time'])
                    if self.internal_stnd is not None:
                        Dts1b=(self.batch_info.loc[brkt1, 'session_time']
                                -self.batch_info.loc[blk1, 'session_time'])/(
                                    self.batch_info.loc[blk2, 'session_time']
                                    -self.batch_info.loc[blk1, 'session_time'])
                        processing_df.loc[samp_pos, 'brkt1_blk_time']=Dts1b
                        
                        Dts2b=(self.batch_info.loc[brkt2, 'session_time']
                                -self.batch_info.loc[blk1, 'session_time'])/(
                                    self.batch_info.loc[blk2, 'session_time']
                                    -self.batch_info.loc[blk1, 'session_time'])
                        processing_df.loc[samp_pos, 'brkt2_blk_time']=Dts2b
                processing_df.loc[samp_pos, 'sample_blk_time']=Dtb
                

            #find bracketing standards  
            if len(self.brkt_order)>0:
                brkt1, brkt2=find_brackets(samp_pos, self.brkt_order)
                processing_df.loc[samp_pos, 'brkt1']=brkt1
                processing_df.loc[samp_pos, 'brkt2']=brkt2
                
                if brkt1 == brkt2:
                    Dts=0
                    processing_df.loc[samp_pos, 'sample_stnd_bracket_time']=Dts
                else:
                    Dts=(self.batch_info.loc[samp_pos, 'session_time']-self.batch_info.loc[brkt1, 'session_time'])/(
                        self.batch_info.loc[brkt2, 'session_time']-self.batch_info.loc[brkt1, 'session_time'])
                    processing_df.loc[samp_pos, 'sample_stnd_bracket_time']=Dts
                

            #Assign components of processing
            
            #Assign numerator and denominator
            isotopes=pd.unique(self.analytes['isotope_gas'])
            x=self.cps_mean.loc[samp_pos, isotopes].values 
            xb1=self.cps_mean.loc[blk1, isotopes].values 
            xb2=self.cps_mean.loc[blk2, isotopes].values 
            
            if self.internal_stnd is not None:
                y=y_df.loc[samp_pos, isotopes].values 
                yb1=y_df.loc[blk1, isotopes].values 
                yb2=y_df.loc[blk2, isotopes].values 
                xs1=self.cps_mean.loc[brkt1, isotopes].values 
                ys1=y_df.loc[brkt1, isotopes].values 
                xs2=self.cps_mean.loc[brkt2, isotopes].values 
                ys2=y_df.loc[brkt2, isotopes].values 
            
            
            #Assign errors   
            s_x=self.cps_sd.loc[samp_pos, isotopes].values 
            s_xb1=self.cps_sd.loc[blk1, isotopes].values 
            s_xb2=self.cps_sd.loc[blk2, isotopes].values 
            
            if self.internal_stnd is not None:
                s_y=s_y_df.loc[samp_pos, isotopes].values 
                s_yb1=s_y_df.loc[blk1, isotopes].values 
                s_yb2=s_y_df.loc[blk2, isotopes].values
                s_xs1=self.cps_sd.loc[brkt1, isotopes].values 
                s_ys1=s_y_df.loc[brkt1, isotopes].values 
                s_xs2=self.cps_sd.loc[brkt2, isotopes].values 
                s_ys2=s_y_df.loc[brkt2, isotopes].values 
            
            #convert errors to standard errors
            
            x_n=self.rep_numbers_df.loc[samp_pos, isotopes].values
            xb1_n=self.rep_numbers_df.loc[blk1, isotopes].values
            xb2_n=self.rep_numbers_df.loc[blk2, isotopes].values
            s_x=sd_to_se(s_x, x_n)
            s_xb1=sd_to_se(s_xb1, xb1_n)
            s_xb2=sd_to_se(s_xb2, xb2_n)
            
            process_inputs_df.loc[df_idx, ['x', 'xb1', 'xb2','s_x', 's_xb1', 's_xb2']]=np.array([x, xb1, xb2, s_x, s_xb1, s_xb2]).T
            
            process_inputs_df.loc[df_idx, 'Dtb']=Dtb
    

            if self.internal_stnd is not None:
                xs1_n=self.rep_numbers_df.loc[brkt1, isotopes].values
                xs2_n=self.rep_numbers_df.loc[brkt2, isotopes].values
                s_y=sd_to_se(s_y, x_n)
                s_yb1=sd_to_se(s_yb1, xb1_n)
                s_yb2=sd_to_se(s_yb2, xb2_n)
                s_xs1=sd_to_se(s_xs1, xs1_n)
                s_ys1=sd_to_se(s_ys1, xs1_n)
                s_xs2=sd_to_se(s_xs2, xs2_n)
                s_ys2=sd_to_se(s_ys2, xs2_n)
                
                #Assign covariances        
                cov_xy=self.cov.loc[samp_pos, isotopes].values
                cov_xb1yb1=self.cov.loc[blk1, isotopes].values
                cov_xb2yb2=self.cov.loc[blk2, isotopes].values
                cov_xs1ys1=self.cov.loc[brkt1, isotopes].values
                cov_xs2ys2=self.cov.loc[brkt2, isotopes].values 
            
                process_inputs_df.loc[df_idx, ['x', 'xb1', 'xb2', 'y', 'yb1', 'yb2', 'xs1', 'ys1', 'xs2', 'ys2', 
                                                    's_x', 's_y', 's_xb1', 's_xb2', 's_yb1', 's_yb2', 's_xs1', 's_ys1', 's_xs2', 's_ys2',
                                                    'cov_xy', 'cov_xs1ys1', 'cov_xs2ys2', 'cov_xb1yb1', 'cov_xb2yb2']]=np.array([x, xb1, xb2, y, yb1, yb2, xs1, ys1,  xs2, ys2,
                    s_x, s_y, s_xb1, s_xb2, s_yb1, s_yb2, s_xs1, s_ys1, s_xs2, s_ys2, cov_xy, cov_xs1ys1, cov_xs2ys2, cov_xb1yb1, cov_xb2yb2]).T
            
                process_inputs_df.loc[df_idx, ['Dtb', 'Dts1b', 'Dts2b', 'Dts']]=[Dtb, Dts1b, Dts2b, Dts]
    
        
        self.__process_inputs__=process_inputs_df
        self.processing_df=processing_df
    
    
    def blank_correction(self):
                
        if self.__process_inputs__ is None:
            raise ValueError('Must initialise batch first.')
        
        nan_df=self.cps_mean.copy()
        nan_df.loc[:, self.analytes['isotope_gas']]=np.nan
        self.cps_blk_corrected=nan_df.copy()
        self.cps_blk_corrected_se=nan_df.copy()
        
        for i, row in nan_df.iterrows():
            p_df=self.__process_inputs__.loc[self.__process_inputs__['run_order']==i, :]
            isotopes=pd.unique(p_df['isotope_gas'])
            blkcorr=calc_blkcorr(p_df['x'], p_df['xb2'], p_df['xb1'], p_df['Dtb'])
            blkcorr_se=calc_blkcorr_variance(p_df['x'], p_df['xb2'], p_df['xb1'], p_df['Dtb'], 
                                             p_df['s_x'], p_df['s_xb1'], p_df['s_xb2'])**0.5
            
            self.cps_blk_corrected.loc[i, isotopes]=np.array(blkcorr)
            self.cps_blk_corrected_se.loc[i, isotopes]=np.array(blkcorr_se)
            
            

    
    def ratio_correction(self):

        if self.__process_inputs__ is None:
            raise ValueError('Must initialise batch first.')
        
        nan_df=self.cps_mean.copy()
        nan_df.loc[:, self.analytes['isotope_gas']]=np.nan
        self.cps_ratio=nan_df.copy()
        self.cps_ratio_se=nan_df.copy()
        
        for samp_pos in pd.unique(self.__process_inputs__['run_order']):
            p_df=self.__process_inputs__.loc[self.__process_inputs__['run_order']==samp_pos, :]
            isotopes=pd.unique(p_df['isotope_gas'])
            R=calc_R(p_df['x'], p_df['xb2'], p_df['xb1'], p_df['y'], p_df['yb2'], p_df['yb1'], p_df['Dtb'])
            R_se=calc_R_variance(p_df['x'], p_df['xb2'], p_df['xb1'], p_df['y'], p_df['yb2'], p_df['yb1'], p_df['Dtb'], 
                                    p_df['cov_xy'], p_df['cov_xb1yb1'], p_df['cov_xb2yb2'], 
                                    p_df['s_x'], p_df['s_y'], p_df['s_xb1'], p_df['s_xb2'], p_df['s_yb1'], p_df['s_yb2'])**0.5
            
            self.cps_ratio.loc[samp_pos, isotopes]=np.array(R)
            self.cps_ratio_se.loc[samp_pos, isotopes]=np.array(R_se)

        
        
        
    
    def bracket_correction(self):
        #Calculate bracketed ratios and errors
        
        if self.__process_inputs__ is None:
            raise ValueError('Must initialise batch first.')
        
        nan_df=self.cps_mean.copy()
        nan_df.loc[:, self.analytes['isotope_gas']]=np.nan
        self.bracketed=nan_df.copy()
        self.bracketed_se=nan_df.copy()
        
        for samp_pos in pd.unique(self.__process_inputs__['run_order']):
            p_df=self.__process_inputs__.loc[self.__process_inputs__['run_order']==samp_pos, :]
            isotopes=pd.unique(p_df['isotope_gas'])
            bracketed_ratio=calc_bracketed_R(p_df['x'], p_df['xb2'], p_df['xb1'], p_df['y'], p_df['yb2'], p_df['yb1'], p_df['Dtb'], 
                                        p_df['xs1'], p_df['ys1'], p_df['Dts1b'], p_df['xs2'], p_df['ys2'], p_df['Dts2b'], p_df['Dts'])
            bracketed_ratio_se=calc_bracketed_R_variance(p_df['x'], p_df['xb2'], p_df['xb1'], p_df['y'], p_df['yb2'], p_df['yb1'], p_df['Dtb'],
                                                    p_df['xs1'], p_df['ys1'], p_df['Dts1b'], p_df['xs2'], p_df['ys2'], p_df['Dts2b'], p_df['Dts'], 
                                                    p_df['cov_xy'], p_df['cov_xb1yb1'], p_df['cov_xb2yb2'], 
                                                    p_df['cov_xs1ys1'], p_df['cov_xs2ys2'], 
                                                    p_df['s_x'], p_df['s_y'], p_df['s_xb1'], p_df['s_xb2'], p_df['s_yb1'], p_df['s_yb2'], 
                                                    p_df['s_xs1'], p_df['s_ys1'], p_df['s_xs2'], p_df['s_ys2'])**0.5
            self.bracketed.loc[samp_pos, isotopes]=np.array(bracketed_ratio)
            self.bracketed_se.loc[samp_pos, isotopes]=np.array(bracketed_ratio_se)

        
        
    def calibrate(self, omissions={}):
        #TODO write ability to remove standards from calibration
        #TODO write automatic removal of P/A standards

        for mode in self.mode_options:
            nan_df=self.cps_mean.copy()
            nan_df.loc[:, self.analytes['isotope_gas']]=np.nan
            self.calibrated_output=nan_df.copy()
            self.calibrated_output_se=nan_df.copy()
        
        
        if self.cali_blocks is None:
            cali_blocks=[0]
        else:
            cali_blocks=pd.unique(self.cali_blocks['cali_block'])
        
        
        #choose what to use on x axis (cps, blank corrected cps, R, or B)
        x_list=[self.cps_mean, self.cps_blk_corrected, self.cps_ratio, self.bracketed] 
        se_list=[self.cps_sd, self.cps_blk_corrected_se, self.cps_ratio_se, self.bracketed_se]   
        x_id=['raw CPS', 'blank-corrected CPS', 'ratio CPS', 'bracketed ratio CPS']
        
        x_idx=[x for x in range(4) if x_list[x] is not None][-1]
        
        x_df=x_list[x_idx]
        self.__calibrated_x__=(x_df.copy(), x_id[x_idx])
        
        se_df=se_list[x_idx]
        
        
        if 'single' in self.cali_mode:
            
            isotopes=self.cali_stnd_df.index
            #currently only allows one standard type for single-point calibration
            single_df=x_df[['sample_name', 'run_order']].copy()
            single_df.loc[:, isotopes]=x_df.loc[:, isotopes].mul(dict(self.cali_stnd_df.iloc[:, 1]))
            
            self.calibrated_output=single_df.copy()
        
        if 'curve' in self.cali_mode:  
        
            self.curve_mdl={}
            self.curve_resid={}
            
            curve_mdl_df=pd.DataFrame([], index=self.cali_stnd_df.index, columns=['fit', 'R2', 'b1', 'b1_se', 'b0', 'b0_se'])
            curve_resid_df=pd.DataFrame([])
            
            
                
            for block in cali_blocks:
                    
                for iso in self.cali_stnd_df.index:
                    
                    #skip over the ratio isotope if used
                    if self.internal_stnd is not None and iso in self.internal_stnd.values():
                        continue
                    
                    X=np.array([])
                    X_se=np.array([])
                    y=np.array([])
                    stnd_orders=np.array([])
                    
                    if len(pd.unique(pd.Series(cali_blocks)))==1:
                    
                        for stnd, order in self.cali_order.items():  
                            X=np.append(X, x_df.loc[order, iso].values) 
                            y=np.append(y,[self.cali_stnd_df.loc[iso, stnd]]*len(order))
                            stnd_orders=np.append(stnd_orders, order) 
                    else:
                        stnd_orders=self.cali_blocks.loc[self.cali_blocks['cali_block']==block, self.cali_order.keys()]
                        X=x_df.loc[stnd_orders, iso].values
                        y=self.cali_stnd_df.loc[iso, self.cali_order.keys()].values

                        

                    #remove omissions
                    if iso in omissions.keys():
                        idx=~np.isin(stnd_orders, omissions[iso])
                        X=X[idx]
                        y=y[idx]
                        stnd_orders=stnd_orders[idx]
                        
                    idx=np.isnan(y)
                    X=X[~idx]
                    y=y[~idx]
                    stnd_orders=stnd_orders[~idx]
                    if len(X)<2:
                        continue
                    
                    #remove nans, infs and negatives
                    
                    idx=np.isnan(X) | np.isinf(X) | (X<0)
                    X=X[~idx]
                    y=y[~idx]
                    stnd_orders=stnd_orders[~idx]
                    
                    if len(X)<2:
                        print('Not enough good calibration data for '+iso)
                        print('Consider single-point calibration for this isotope.')
                        continue
                    
                    
                    
                    
                    
                    #fit the curve
                    
                    X=sm.add_constant(X)
                    lm_fit = sm.OLS(y, X).fit()
                    
                    
                    curve_mdl_df.loc[iso, 'fit']=lm_fit
                    curve_mdl_df.loc[iso, 'R2']=lm_fit.rsquared
                    curve_mdl_df.loc[iso, 'b1']=lm_fit.params[1]
                    curve_mdl_df.loc[iso, 'b1_se']=lm_fit.bse[1]
                    curve_mdl_df.loc[iso, 'b0']=lm_fit.params[0]
                    curve_mdl_df.loc[iso, 'b0_se']=lm_fit.bse[0]
                    
                    residuals=pd.Series(lm_fit.resid, index=stnd_orders, name=iso)
                    
                    curve_resid_df=pd.concat([curve_resid_df, residuals], axis=1)
                    
                    #fit data
                    if len(pd.unique(pd.Series(cali_blocks)))==1:
                        data_idx=self.batch_info['run_order'].values
                    else:
                        data_idx=np.array(self.cali_blocks.loc[self.cali_blocks['cali_block']==block, 'run_order'])
                    
                    xdata=np.array(x_df.loc[data_idx, iso])
                    y_predicted=lm_fit.predict(sm.add_constant(xdata))
                    #propagate errors
                    x_se=np.array(se_df.loc[data_idx, iso])
                    y_se=np.sqrt(lm_fit.bse[1]**2*xdata**2
                                +x_se**2*lm_fit.params[1]**2
                                +lm_fit.bse[0]**2)
                    

                    self.calibrated_output.loc[data_idx, iso]=y_predicted
                    self.calibrated_output_se.loc[data_idx, iso]=y_se


                    self.curve_mdl[block]=curve_mdl_df
                    self.curve_resid[block]=curve_resid_df
            
        
        
            
            
    
    
    def get_conversion_to_conc(self, stnd_conc=1, units='moles'):
        stnd_name=list(self.cali_order.keys())[0]
        conc_stnd_df=make_stndvals_df(df=self.cali_stnd_df, stnd_names=stnd_name, 
                                      isotopes=self.cali_stnd_df.index.values, 
                                      cali_mode='conc single', dilutions=stnd_conc, 
                                      units=units)
        
        units_dict=dict(conc_stnd_df['units'])
        if units=='grams':
            from Pygilent.stnds import get_atomic_mass
            
            
            converted_df=self.calibrated_output.copy()
            
            for iso in conc_stnd_df.index:
                molar_mass=get_atomic_mass(deconstruct_isotope_gas(iso, 'element'))
                converted_df.loc[:, iso]*=molar_mass
        
        return converted_df, units_dict
    
    
    def convert_to_grams(self):
        
        if ~np.any(self.cali_stnd_df.loc[:, 'units'].str.contains('mol')):
            raise ValueError('Already in grams')
        
        from Pygilent.stnds import get_atomic_mass
        for iso in self.cali_stnd_df.index:
            molar_mass=get_atomic_mass(deconstruct_isotope_gas(iso, 'element'))
            
            self.calibrated_output.loc[:, iso]*=molar_mass
            self.calibrated_output_se.loc[:, iso]*=molar_mass
            self.cali_stnd_df.loc[iso, list(self.cali_order.keys())]*=molar_mass
            
        self.cali_stnd_df.loc[:, 'units']=self.cali_stnd_df.loc[:, 'units'].str.replace('mol', 'g')


    def convert_to_moles(self):
        
        if np.any(self.cali_stnd_df.loc[:, 'units'].str.contains('mol')):
            raise ValueError('Already in moles')
        
        from Pygilent.stnds import get_atomic_mass
        for iso in self.cali_stnd_df.index:
            molar_mass=get_atomic_mass(deconstruct_isotope_gas(iso, 'element'))
            
            self.calibrated_output.loc[:, iso]/=molar_mass
            self.calibrated_output_se.loc[:, iso]/=molar_mass
            self.cali_stnd_df.loc[iso, list(self.cali_order.keys())]/=molar_mass
            
        self.cali_stnd_df.loc[:, 'units']=self.cali_stnd_df.loc[:, 'units'].str.replace('g', 'mol')
    

    def plot_calibration(self, iso, block=0):
            
            mdl=self.curve_mdl[block].loc[iso, 'fit']

            x_df, x_id=self.__calibrated_x__

            X_pred=x_df[iso].values
            X_pred=X_pred[~np.isnan(X_pred)]
            X_pred=sm.add_constant(X_pred)
            y_pred=mdl.predict(X_pred)

        


            fig, ax = plt.subplots()
            sm.graphics.plot_fit(mdl, 1, ax=ax)
            l1=ax.lines[0]
            l2=ax.lines[1]
            l1.set_label('Standards')
            l2.set_label(f'Fit y = {mdl.params[0]:.2e} + {mdl.params[1]:.2e}x')
            x_stnd=l2.get_xdata()
            y_stnd=l2.get_ydata()
            ax.plot(x_stnd, y_stnd, color='r', label=f'Fit R2={mdl.rsquared:.2f}')
            ax.scatter(X_pred[:, 1], y_pred, color='k', marker='X', label='Predicted samples')
            plt.title(iso)
            plt.legend()
            ax.set_xlabel(x_id)
            ax.set_ylabel(self.cali_stnd_df.loc[iso, 'units'])
            
            plt.show()
            
            
            
            #X=self.bracketed.loc[self.curve_resid.index, isotope].values
            #ypred=self.curve_mdl.loc[isotope, 'fit'].predict(sm.add_constant(X))
            #yresid=self.curve_resid.loc[:, isotope].values
            #y=ypred+yresid
            
            

                
                

                        
                

            
            
    

    

        
    def save_to_excel(self, path):
        with pd.ExcelWriter(path) as writer:
            self.calibrated_output.to_excel(writer, sheet_name='calibrated')
            self.calibrated_output_se.to_excel(writer, sheet_name='1se')
            self.cali_stnd_df.to_excel(writer, sheet_name='cali_stnds')

        

        


