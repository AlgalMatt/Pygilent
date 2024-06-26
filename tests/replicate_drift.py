import Pygilent as pyg
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

folders_old=['240610_MD_update_Nicones_preclean_50sweeps.b',
             '240403_update_Nicones_preclean_50sweeps.b', 
          '240403_update_Nicones_postclean_50sweeps.b',
         ]

folders=['240611_MD_updates_10secondO2.b', 
         '240611_MD_updates_30secondO2.b', 
         '240611_MD_updates_30secondO2_2.b', 
         '240611_MD_updates_40secondO2.b', 
         '240611_MD_updates_40secondO2_2.b', 
         '240611_MD_updates_40secondO2_3.b',
          '240611_MD_updates_50secondO2.b']

folders2=['240403_update_Ptcones_postclean_50sweeps.b', 
          '240403_update_Ptcones_preclean_50sweeps.b',
          '240610_MD_update_Ptcones_postclean_50sweeps.b',
          '240610_MD_update_Ptcones_preclean_50sweeps.b']

ag8800=['2024-03-15_Matt_solution_test_2.b']


isolated_gases=['231103_MD_drift_STGFrm_fullelements_O2only.b', 
                '231103_MD_drift_STGFrm_fullelements_NoGasonly.b']



## import data
all_folders=folders_old+folders+folders2+ag8800+isolated_gases
folder_prefix=Path(r"C:\Users\mdumo\OneDrive - University of St Andrews\Agilent\Matt\Full agilent data")
batch_dict={}
for folder in all_folders:
    batch_path=folder_prefix/folder
    batch=pyg.pygilent.import_batch(batch_path)
    batch_dict[folder]=batch


## sort isotopes
isotopes=['Ca43_No Gas', 'Ca43_43_H2',  'Ca43_43_O2', 'Ca48_No Gas', 'Ca48_48_H2', 'Ca48_48_O2']
rep_data_dict={}
for iso in isotopes:
    iso_df=pd.DataFrame()
    for folder in all_folders:
        batch=batch_dict[folder]
        df=batch.rep_df.loc[batch.rep_df['isotope_gas']==iso]
        df_piv=df.pivot_table(index=['replicate'], columns='run_order', values='cps', sort=False, aggfunc='first', observed=False)
        df_piv_norm=df_piv/df_piv.mean()
        df_piv_norm.reset_index(inplace=True, drop=False)
        df_melt=df_piv_norm.melt(id_vars='replicate', var_name='run_order', value_name='cps_norm')
        df_melt.insert(0, 'batch', folder)        
        
        iso_df=pd.concat([iso_df, df_melt])
    rep_data_dict[iso]=iso_df
            


## plotting

#8800 data uses 10 second stabilisation time

output_folder=Path(r"C:\Users\mdumo\OneDrive - University of St Andrews\Agilent\Drift runs\240626_figs")

for iso in isotopes:
    f1=folders_old+folders2+isolated_gases+ag8800
    df=rep_data_dict[iso].loc[rep_data_dict[iso]['batch'].isin(f1)]
    p1=sns.catplot(data=df, kind='point', col='batch', 
                col_wrap=3, sharex=True, sharey=True, hue='run_order', x='replicate', y='cps_norm', 
                palette='Set2', markers=None)
    p1.map(sns.pointplot, 'replicate', 'cps_norm', color='black')
    plt.ylim([0.95, 1.05])
    plt.suptitle(iso) 
    plt.savefig(output_folder/f'{iso}_drift_assorted_similar_stabilisation.png', dpi=300)


    df=rep_data_dict[iso].loc[rep_data_dict[iso]['batch'].isin(folders+isolated_gases+ag8800)]
    p1=sns.catplot(data=df, kind='point', col='batch', 
                col_wrap=3, sharex=True, sharey=True, hue='run_order', x='replicate', y='cps_norm', 
                palette='Set2', markers=None)
    p1.map(sns.pointplot, 'replicate', 'cps_norm', color='black')
    plt.ylim([0.95, 1.05])
    plt.suptitle(iso) 
    plt.savefig(output_folder/f'{iso}_drift_varying_stabilisation.png', dpi=300)






