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


new_batch.set_blks(how='auto')
#new_batch.check_blks()
new_batch.set_brkt_stnds(how='auto', keyword='stgfrm')
new_batch.cali_mode='ratio curve'
new_batch.set_ratio_iso(how='auto', keyword='Ca48')
new_batch.set_cali_stnds(stndvals, how='ui')

new_batch.blank_subtraction()
new_batch.initialise()




import os
import pandas as pd
import numpy as np
import sympy as sym

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

blkcorr_y_sym=(y_sym - Dtb_sym*yb2_sym + yb1_sym*(Dtb_sym - 1))

blkcorr_R_sym=blkcorr_x_sym/blkcorr_y_sym

blkcorr_R_f = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, 
                            Dtb_sym), blkcorr_R_sym)

blkcorr_R_var_sym=(s_x_sym**2*blkcorr_R_sym.diff(x_sym)**2+s_y_sym**2*blkcorr_R_sym.diff(y_sym)**2
                   +s_xb1_sym**2*blkcorr_R_sym.diff(xb1_sym)**2+s_xb2_sym**2*blkcorr_R_sym.diff(xb2_sym)**2
                   +s_yb1_sym**2*blkcorr_R_sym.diff(yb1_sym)**2+s_yb2_sym**2*blkcorr_R_sym.diff(yb2_sym)**2
                   +2*cov_xy_sym*blkcorr_R_sym.diff(x_sym)*blkcorr_R_sym.diff(y_sym)
                   +2*cov_xb1yb1_sym*blkcorr_R_sym.diff(xb1_sym)*blkcorr_R_sym.diff(yb1_sym)
                   +2*cov_xb2yb2_sym*blkcorr_R_sym.diff(xb2_sym)*blkcorr_R_sym.diff(yb2_sym))   

blkcorr_R_var_f=sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, 
                        Dtb_sym, cov_xy_sym, cov_xb1yb1_sym, cov_xb2yb2_sym, 
                        s_x_sym, s_y_sym, s_xb1_sym, s_xb2_sym, s_yb1_sym, 
                        s_yb2_sym), blkcorr_R_var_sym)

#TE/Ca ratio equation
R_sym=(x_sym - Dtb_sym*xb2_sym + xb1_sym*(Dtb_sym - 1))  \
    /(y_sym - Dtb_sym*yb2_sym + yb1_sym*(Dtb_sym - 1))
    
R_f = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, 
                    Dtb_sym), R_sym)  

#Variance in R
R_var_sym=s_x_sym**2*R_sym.diff(x_sym)**2+s_y_sym**2*R_sym.diff(y_sym)**2\
    +s_xb1_sym**2*R_sym.diff(xb1_sym)**2+s_xb2_sym**2*R_sym.diff(xb2_sym)**2\
    +s_yb1_sym**2*R_sym.diff(yb1_sym)**2+s_yb2_sym**2*R_sym.diff(yb2_sym)**2\
    +2*cov_xy_sym*R_sym.diff(x_sym)*R_sym.diff(y_sym)\
    +2*cov_xb1yb1_sym*R_sym.diff(xb1_sym)*R_sym.diff(yb1_sym)\
    +2*cov_xb2yb2_sym*R_sym.diff(xb2_sym)*R_sym.diff(yb2_sym)

R_var_f = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, 
                        Dtb_sym, cov_xy_sym, cov_xb1yb1_sym, cov_xb2yb2_sym, 
                        s_x_sym, s_y_sym, s_xb1_sym, s_xb2_sym, s_yb1_sym, 
                        s_yb2_sym), R_var_sym)    

B_sym=-(x_sym - Dtb_sym*xb2_sym + xb1_sym*(Dtb_sym - 1))/((((Dts_sym - 1)\
    *(xs1_sym - Dts1b_sym*xb2_sym + xb1_sym*(Dts1b_sym - 1)))\
    /(ys1_sym - Dts1b_sym*yb2_sym + yb1_sym*(Dts1b_sym - 1))\
    -(Dts_sym*(xs2_sym - Dts2b_sym*xb2_sym + xb1_sym*(Dts2b_sym - 1)))\
    /(ys2_sym - Dts2b_sym*yb2_sym + yb1_sym*(Dts2b_sym - 1)))\
    *(y_sym - Dtb_sym*yb2_sym + yb1_sym*(Dtb_sym - 1)))


B_blk_corr_sym=-blkcorr_x_sym/((((Dts_sym - 1)\
    *(xs1_sym - Dts1b_sym*xb2_sym + xb1_sym*(Dts1b_sym - 1)))\
    /(ys1_sym - Dts1b_sym*yb2_sym + yb1_sym*(Dts1b_sym - 1))\
    -(Dts_sym*(xs2_sym - Dts2b_sym*xb2_sym + xb1_sym*(Dts2b_sym - 1)))\
    /(ys2_sym - Dts2b_sym*yb2_sym + yb1_sym*(Dts2b_sym - 1)))\
    *blkcorr_y_sym)



x=100

y=1000

x_blk1=1
x_blk2=2
y_blk1=10
y_blk2=15

s_x=0.1
s_y=1
s_xb1=0.1
s_xb2=0.2
s_yb1=1.1
s_yb2=1.5

Dtb=0.5

cov_xy=0.1
cov_xb1yb1=0.1
cov_xyb2yb2=0.1

R=R_f(x, x_blk2, x_blk1, y, y_blk2, y_blk1, Dtb)
R_var=R_var_f(x, x_blk2, x_blk1, y, y_blk2, y_blk1, 
              Dtb, cov_xy, cov_xb1yb1, cov_xyb2yb2,
              s_x, s_y, s_xb1, s_xb2, s_yb1, s_yb2)

blkcorr_R=blkcorr_R_f(x, x_blk2, x_blk1, y, y_blk2, y_blk1, Dtb)
blkcorr_R_var=blkcorr_R_var_f(x, x_blk2, x_blk1, y, y_blk2, y_blk1, 
                        Dtb, cov_xy, cov_xb1yb1, cov_xyb2yb2, 
                        s_x, s_y, s_xb1, s_xb2, s_yb1, s_yb2)
