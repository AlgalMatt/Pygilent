import Pygilent as pyg
import os
from pathlib import Path
import pandas as pd
import numpy as np

stndvals=pyg.stnds.get_default_stndvals()

isotopes=['Li7_No Gas', 'B11_No Gas', 'Mg24_No Gas', 'Al27_No Gas']



cwd=Path(os.getcwd())
archive_path=cwd.parent/'Agilent_EDA'/'data'/'bigdf_240226.csv'
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




new_batch_path=Path(r"C:\Users\mdumo\OneDrive - University of St Andrews\Agilent\Matt\Full agilent data\Carbonates_STDS_1block_1M_JB_20231211b.b")
old_batch_path=Path(r"C:\Users\mdumo\OneDrive - University of St Andrews\Agilent\Matt\Full agilent data\Carbonates_STDS_CS13_8301F_1mM_JCB_20211015.b")

new_batch=pyg.pygilent.import_batch(new_batch_path)


new_batch.set_blk_order(how='auto')
#new_batch.check_blks()
new_batch.set_brkt_order(how='auto', keyword='stgfrm')
new_batch.cali_mode='ratio curve'
new_batch.set_ratio_iso(how='ui')

new_batch.set_cali_stnds(stndvals, how='ui')

