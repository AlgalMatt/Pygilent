import numpy as np
import pandas as pd
import os
from pathlib import Path
import warnings
from Pygilent.stnds import get_default_stndvals, make_stndvals_df

##Functions

def find_substrings(array1, string1, ret_array=True, case_sensitive=False):
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
        if case_sensitive==False:
            array1=nlower(array1)
            string1=string1.lower()
        for i in array1:
            retarray.append(string1 in i)   
    #if string1 is a list of strings             
    else:
        #lower all cases
        if case_sensitive==False:
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

def deconstruct_isotope_gas(string, output='all'):
    
    str_series=pd.Series(string)
    
    mass=str_series.str.extract(r'(\d+)').values.flatten()
    element=str_series.str.extract(r'([A-Z][a-z]*)').values.flatten()
    
    #join the mass and element arrays to make isotope
    isotope=mass+element
    
    #extract only the text after the last underscore in the series of strings
    gas_mode=np.array([])
    for s in str_series:
        gas_mode=np.append(gas_mode, s.split('_')[-1])

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
    

def unarchive_replicates(rep_list):
    pattern=r'(\d*\.\d+|[PAU])'
    rep_df=rep_list.str.extractall(pattern).unstack()
    rep_df=rep_df.droplevel(0, axis=1)
    rep_df.rename(columns={i: i+1 for i in rep_df.columns}, inplace=True)
    return rep_df


def pivot_isotopes(df, var, index=['run_order', 'sample_name']):
    df_piv=df.pivot_table(index=index, columns='isotope_gas', values=var, sort=False)
    df_piv.reset_index(inplace=True)
    return df_piv
    
def make_empty_batch():
    default_columns=['run_name', 'run_order', 'time','sample_name', 'total_reps',
                     'isotope_gas', 'cps_mean', 'cps_std', 
                     'rep_list', 'sample_type', 'brkt_stnd', 'cali_curve', 'ratio_iso']     



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
    
    #POTENTIALLY NEED TO SPECIFY TIME FORMAT
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
        batch_df['time']=pd.to_datetime(batch_df['time'], format="%d-%b-%y %I:%M:%S %p") 
        
    
    
    batch_df=batch_df.loc[(batch_df['Acquisition Result']=='Pass') & 
                          (batch_df["Sample Type"].str.contains("Tune")==False) &
                          (~(batch_df["Vial#"]=="-"))]

    batch_df.reset_index(drop=True, inplace=True)
    
    #Get a list of the sample names, make them into directories and put them into the main df
    subfolder_list=[path/Path(x).name for x in batch_df["File Name"]]
    batch_df['directory']=subfolder_list

    #Setup run info table
    smpl_info=pd.DataFrame(np.repeat(path.name, len(batch_df)), columns=['run_name'])
    smpl_info[['time', 'sample_name', 'vial']]=batch_df[['time', 'Sample Name', 'Vial#']]

    #give error if no samples found
    if len(batch_df)==0:
        raise ValueError('No valid samples found in batch log.')
    
    #Get the total elapsed time since first sample
    smpl_info['session_time']=batch_df['time']-batch_df.loc[0,'time']
    #Convert to seconds
    smpl_info['session_time']=smpl_info['session_time'].dt.total_seconds()
    
    smpl_info['run_order']=np.arange(0, len(smpl_info))
    
    #This speeds up the processing to find the gas modes and number of repeats
    from concurrent.futures import ThreadPoolExecutor
    import csv
    def extract_gas_mode(file_path):
        with open(file_path, newline='') as f:
            reader = csv.reader(f)
            row1 = next(reader)[0].rsplit('/')[-1].strip('\n ')
        return row1
    
    #Start iterating through samples
    for s_num, subfolder in enumerate(subfolder_list):   

        #Get list of subfolders containing replicates and gas modes. Exclude quickscan
        csvlist = [s for s in os.listdir(subfolder) if ".csv" in s and "quickscan" 
                not in s and subfolder.name[0:-2] in s]
        file_paths = [subfolder/c for c in csvlist]
        
        #Find out how many repeats and gas modes there are by reading first sample
        testmode=[]
        with ThreadPoolExecutor() as executor:
            testmode = list(executor.map(extract_gas_mode, file_paths))
        

        #Get the number of repeats and gases by counting occurrences of gas modes
        total_reps=testmode.count(list(set(testmode))[0])
        numgases=len(set(testmode))
        compile_df=pd.DataFrame()
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
                
                
            single_rep_df=pd.DataFrame(np.array([list(smpl_info.loc[s_num])]*len(allgas_df)), 
                                       columns=smpl_info.columns)
            
            single_rep_df['run_order']=s_num
            single_rep_df['replicate']=r+1
            
            single_rep_df[['element', 'isotope_gas', 'mass', 'gas_mode', 'total_reps', 'det_mode', 'int_time', 
                           'cps']]=allgas_df[['Element', 'isotope_gas', 'mass', 'gas_mode', 'n', 'det_mode', 'Time(Sec)', 
                           'CPS']]

            single_rep_df['total_reps']=total_reps
            compile_df=pd.concat([compile_df, single_rep_df], axis=0)
    
    run_name=path.name
    
    compile_df['isotope_gas']=pd.Categorical(compile_df['isotope_gas'], categories=pd.unique(compile_df['isotope_gas']))
    rep_df=compile_df[['run_order', 'isotope_gas', 'replicate',  'cps', 'det_mode']].copy()
    rep_df.sort_values(by=['run_order','isotope_gas', 'replicate'], inplace=True)
    
    analytes=single_rep_df[['isotope_gas', 'mass', 'element', 'mass', 'gas_mode', 'int_time']]
    
    batch=Batch(run_name, smpl_info, total_reps, analytes, rep_df)

    return batch
    

    
    
            

## Classes


class Batch:   
    
    def __init__(self, run_name=None, smpl_info=None, total_reps=None, analytes=None, rep_df=None, 
                 cps_mean=None, cps_sd=None, cps_ratio=None, cps_ratio_se=None, 
                 calibrated=None, calibrated_se=None, cov=None, 
                 cali_stnd_df=None, curve_mdl=None, blk_order=[], brkt_order=[], 
                 brkt_stnd=None, cali_mode=None, ratio_iso=None, 
                 cali_order={}, stnd_df=None):
        self.run_name=run_name
        self.smpl_info=smpl_info
        self.total_reps=total_reps
        self.analytes=analytes
        self.rep_df=rep_df
        self.cps_mean=cps_mean
        self.cps_sd=cps_sd
        self.cps_ratio=cps_ratio
        self.cps_ratio_se=cps_ratio_se
        self.calibrated=calibrated
        self.calibrated_se=calibrated_se
        self.cov=cov
        self.cali_stnd_df=cali_stnd_df
        self.curve_mdl=curve_mdl
        self.blk_order=blk_order
        self.brkt_order=brkt_order
        self.brkt_stnd=brkt_stnd
        self.cali_mode=cali_mode
        self.ratio_iso=ratio_iso
        self.cali_order=cali_order
        self.stnd_df=stnd_df
    
    def set_cali_mode(self, mode):
        
        modes=['ratio curve', 'ratio single', 'conc curve', 'conc single']
        Ca_check=['ca check', 'ca_check','check', 'conc check']
        if mode.lower() in Ca_check:
            warnings.warn('Conc check mode selected. Calibration mode will be set to conc single.')
            self.cali_mode = 'conc single'
        if mode.lower() not in modes:
            raise ValueError('Invalid calibration mode. Please select from the following: ratio curve, ratio single, conc curve, conc single.')
        
        self.cali_mode = mode
        
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
    
    
    def process(self):
        #fully process the batch using the calibration mode specified
        pass
    
    

    
    def save_to_csv(self, path):
        self.df.to_csv(path, index=False)
        
    def save_to_excel(self, path):
        self.df.to_excel(path, index=False)
        
    def save_to_pickle(self, path):
        self.df.to_pickle(path)
        
    def save_to_sql(self, path, table_name):
        self.df.to_sql(table_name, path, index=False, if_exists='replace')



