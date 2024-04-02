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


