import Pygilent as pyg
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

folders=['240610_MD_update_Nicones_preclean_50sweeps.b', 
         '240610_MD_update_Ptcones_postclean_30secondO2.b', 
         '240610_MD_update_Ptcones_postclean_50sweeps.b', 
         '240610_MD_update_Ptcones_preclean_50sweeps.b']

folder_prefix=Path(r"C:\Users\mdumo\OneDrive - University of St Andrews\Agilent\Matt\Full agilent data")

batch_dict={}
for folder in folders:
    batch_path=folder_prefix/folder
    batch_dict[folder]=pyg.pygilent.import_batch(batch_path)
    

isotopes=['Ca48_No Gas', 'Ca48_48_H2', 'Ca48_48_O2']
for iso in isotopes:
    
    row=0
    fig, ax = plt.subplots(nrows=len(folders), figsize=(6,10), sharex=True, sharey=True)
    fig.suptitle(iso, fontsize=16)
    for k, v in batch_dict.items():
        df=v.rep_df.loc[v.rep_df['isotope_gas']==iso]
        df_piv=df.pivot_table(index=['replicate'], columns='run_order', values='cps', sort=False, aggfunc='first', observed=False)
        df_piv_norm=df_piv/df_piv.mean()
        df_piv_norm.plot(ax=ax[row], legend=False)
        ax[row].set_title(k)
        row+=1
        


    





