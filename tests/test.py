import Pygilent as pyg
import os
from pathlib import Path
import pandas as pd
import numpy as np

g=pyg.stnds.get_default_stndvals()

isotopes=['Li7_No Gas', 'B11_No Gas', 'Mg24_No Gas', 'Al27_No Gas']
a=pyg.stnds.make_stndvals_df(g, ['STGFrm', 'STGCco'], isotopes)





cwd=Path(os.getcwd())
archive_path=cwd.parent.parent/'Agilent_EDA'/'data'/'bigdf_240226.csv'
archive_df=pd.read_csv(archive_path, index_col=0, parse_dates=['time'])
run_name=pd.unique(archive_df['run_name'])
df=archive_df.loc[archive_df['run_name']==run_name[-1]].copy()
df.rename(columns={'type': 'sample_type', 
                   'ratio':'cps_ratio', 
                   'ratio_se':'cps_ratio_se'}, inplace=True)   

df.loc[df['sample_type'].str.contains('Cali_STGFrm'), 'sample_type']='Bracket & Cali_STGFrm'
df['cali_mode']='ratio curve'

df['gas_mode']=pd.Categorical(df['gas_mode'], categories=['No Gas', 'H2', 'O2'])

df.sort_values(by=['run_order', 'gas_mode', 'mass'], inplace=True)

df['archive_smpl_id']=df['time'].dt.strftime('%y%m%d%H%M%S').astype(np.int64)







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
#Then quickly (using ThreadPoolExecutor) get the relevant info from files.
testmode=[]
with ThreadPoolExecutor() as executor:
    testmode = list(executor.map(extract_gas_mode, file_paths))