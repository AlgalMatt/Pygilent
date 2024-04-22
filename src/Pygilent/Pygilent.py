import numpy as np
import pandas as pd
import os
from pathlib import Path
import warnings
from Pygilent.stnds import get_default_stndvals, make_stndvals_df

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
    
    str_series=pd.Series(input)
    
    mass=str_series.str.extract(r'(\d+)').values.flatten()
    element=str_series.str.extract(r'([A-Z][a-z]*)').values.flatten()
    gas_mode=str_series.str.split('_').str[-1].values
    if type(input) is str:
        mass=mass[0]
        element=element[0]
        gas_mode=gas_mode[0]
        
        
    
    #join the mass and element arrays to make isotope
    isotope=mass+element
    

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

def create_entry_window(string_list, default_values):
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("User Input Window")

    # Dictionary to store user inputs
    user_inputs = {}

    # Function to handle 'OK' button click
    def ok_button_click():
        for idx, string in enumerate(string_list):
            user_input = entry_fields[idx].get()
            try:
                float_value = float(user_input)
                user_inputs[string] = float_value
            except ValueError:
                show_error_message("Error", "Please enter a valid number for '{}'.".format(string))
                return
            
        root.destroy()
        
    def show_error_message(title, message):
        tk.messagebox.showerror(title, message)
    
    #title
    instructions_label = tk.Label(root, text="Enter conc scalings")
    instructions_label.grid(row=0, column=0, columnspan=2, pady=5)
        
    # Create labels and entry fields with default values
    entry_fields = []
    for idx, string in enumerate(string_list):
        label = tk.Label(root, text=string)
        label.grid(row=idx + 1, column=0, padx=10, pady=5, sticky="w")
        default_value = default_values[idx] if default_values and idx < len(default_values) else ""
        entry = tk.Entry(root)
        entry.insert(0, default_value)
        entry.grid(row=idx + 1, column=1, padx=10, pady=5, sticky="e")
        entry_fields.append(entry)

    # Create 'OK' button
    ok_button = tk.Button(root, text="OK", command=ok_button_click)
    ok_button.grid(row=len(string_list) + 1, column=0, columnspan=2, pady=10)

    # Run the Tkinter main loop
    root.mainloop()

    return user_inputs



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
        batch_df['time']=pd.to_datetime(batch_df['time'], format="%d-%b-%y %I:%M:%S %p") 
        
    
    
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
    total_reps=testmode.count(list(set(testmode))[0])
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
        
    analytes=single_rep_df[['isotope_gas', 'mass', 'element', 'mass', 'gas_mode', 'int_time']]
    
    return Batch(run_name, batch_info, total_reps, analytes, rep_df, cps_mean, cps_sd, det_mode)
    

    
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




## Classes


class Batch:   
    modes=('ratio curve', 'ratio single', 'conc curve', 'conc single')
    
    def __init__(self, run_name=None, batch_info=None, total_reps=None, analytes=None, rep_df=None, 
                 cps_mean=None, cps_sd=None, det_mode=None, cps_ratio=None, cps_ratio_se=None, 
                 calibrated=None, calibrated_se=None, cov=None, 
                 cali_stnd_df=None, curve_mdl=None, blk_order=np.array([], dtype=int), brkt_order=np.array([], dtype=int), 
                 brkt_stnd=None, cali_mode=None, ratio_iso=None, 
                 cali_order={}, stnd_df=None):
        self.run_name=run_name
        self.batch_info=batch_info
        self.total_reps=total_reps
        self.analytes=analytes
        self.rep_df=rep_df
        self.cps_mean=cps_mean
        self.cps_sd=cps_sd
        self.det_mode=det_mode
        self.cps_ratio=cps_ratio
        self.cps_ratio_se=cps_ratio_se
        self.calibrated=calibrated
        self.calibrated_se=calibrated_se
        self.cov=cov
        self.cali_stnd_df=cali_stnd_df
        self.curve_mdl=curve_mdl
        if not np.all(np.isin(blk_order, self.batch_info['run_order'].values)):
            raise ValueError(f'Invalid bracket order. Must be from array of run orders: ({self.batch_info['run_order'].values.min()} - {self.batch_info['run_order'].values.max()}).')
        self.blk_order=np.array(blk_order, dtype=int)
        if not np.all(np.isin(brkt_order, self.batch_info['run_order'].values)):
            raise ValueError(f'Invalid bracket order. Must be from array of run orders: ({self.batch_info['run_order'].values.min()} - {self.batch_info['run_order'].values.max()}).')
        self.brkt_order=np.array(brkt_order, dtype=int)

        
        self.brkt_stnd=brkt_stnd
        
        if cali_mode is not None:
            if cali_mode.lower() in ['ca check', 'ca_check','check', 'conc check']:
                warnings.warn('Conc check mode selected. Calibration mode will be set to conc single.')
                self.cali_mode = 'conc single'
            if cali_mode.lower() not in self.modes:
                raise ValueError(f'Invalid calibration mode. Please select from the following: {self.modes}.')
        self.cali_mode=cali_mode
        
        self.ratio_iso=ratio_iso
        self.cali_order=cali_order
        self.stnd_df=stnd_df
    
    
    def identify_blks(self, blk_order=np.array([], dtype=int), how='auto', keyword='blk', case=False):
        
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
        self.batch_info.loc[self.blk_order, 'sample_type']='blank'


    def identify_brkt_stnds(self, brkt_order=np.array([], dtype=int), how='manual', keyword=None, case=False):
        if how not in ['auto', 'manual', 'ui']:
            raise ValueError('Invalid method. Please select from: auto, manual, ui.')

        #reset the original bracket order
        self.batch_info.loc[self.brkt_order, 'sample_type']='sample'
        sample_type='bracket'
        self.brkt_order=select_run_order(self, brkt_order, how, keyword, case, sample_type)
        self.batch_info.loc[self.brkt_order, 'sample_type']=sample_type
    
    
    def identify_cali_stnds(self, stnd_vals_df, cali_run_order=np.array([], dtype=int), cali_order={}, 
                            how='manual', keyword=None, cali_stnd_df=None):
        if how not in ['auto', 'manual', 'ui']:
            raise ValueError('Invalid method. Please select from: auto, manual, ui.')
        
        if self.cali_mode is None:
            raise ValueError('Calibration mode not set. Please set calibration mode.')
        
        
        
        if how =='ui':
            from Pygilent.uitools import fancycheckbox, fancycheckbox_2window
        
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
                                                   associate_defaults, 'Associate bracket standards with standards list')
            else:
                bracket_dict=associate_defaults
            
            cali_order={}
            for k, v in bracket_dict.items():
                if np.any(v):
                    name=bracket_names[v]
                    idx=np.isin(self.batch_info.loc[cali_run_order, 'sample_name'] , name)
                    self.cali_order[k]=cali_run_order[idx]
            #make cali_stnd_df
            self.cali_stnd_df=make_stndvals_df(stnd_vals_df, list(self.cali_order.keys()), 
                                               self.analytes['isotope_gas'].values)
        elif self.cali_mode == 'ratio curve':
            if how =='auto' & keyword is None:
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
            cali_order={k: self.batch_info.loc[v, 'run_order'] for k, v in cali_dict.items() if np.any(v)}
            self.cali_stnd_df=make_stndvals_df(stnd_vals_df, list(self.cali_order.keys()), self.analytes['isotope_gas'].values)
        
        elif self.cali_mode == 'conc curve': 
            if how =='auto' & keyword is None:
                raise ValueError('Keyword required for auto method.')
            if keyword is not None:
                if type(keyword) is not str:
                    raise ValueError('Keyword must be a single standard name for conc curve mode.')
                associate_defaults={keyword: self.batch_info['sample_name'].str.contains(keyword, case=False)}
            else:
                associate_defaults=None
            if how=='ui':
                cali_dict=fancycheckbox_2window(self.batch_info['sample_name'], stnd_vals_names, associate_defaults,
                                                'Associate calibration standards with standards list', single=True)
            else:
                cali_dict=associate_defaults
            
            stnd_name=list(cali_dict.keys())[0]
            cali_rows=self.batch_info.loc[cali_dict[stnd_name], 'run_order'].values
            

            unique_stnd_names=pd.unique(self.batch_info.loc[cali_dict[stnd_name], 'sample_name'])

            stnd_conc_defaults=[extract_float_substring(s) for s in unique_stnd_names]

            if how == 'ui':
                stnd_conc_dict = create_entry_window(list(unique_stnd_names), 
                                                     default_values=stnd_conc_defaults)
            else:
                stnd_conc_dict=dict(zip(unique_stnd_names, np.array(stnd_conc_defaults).astype(float)))

            cali_order={val:[] for val in stnd_conc_dict.values()}

            for key, val in stnd_conc_dict.items():
                key_rows=cali_rows[self.batch_info.loc[cali_rows, 'sample_name']==key]
                cali_order[val].extend(list(key_rows))
            self.cali_stnd_df=make_stndvals_df(stnd_vals_df, [stnd_name], self.analytes['isotope_gas'].values)

            
                
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



