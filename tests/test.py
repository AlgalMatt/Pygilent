import Pygilent as pyg
import os
from pathlib import Path
import pandas as pd
import numpy as np

stndvals=pyg.stnds.get_default_stndvals()
new_batch_path=Path(r"C:\Users\mdumo\OneDrive - University of St Andrews\Agilent\Matt\Full agilent data\Carbonates_STDS_1block_1M_JB_20231211b.b")
old_batch_path=Path(r"C:\Users\mdumo\OneDrive - University of St Andrews\Agilent\Matt\Full agilent data\Carbonates_STDS_CS13_8301F_1mM_JCB_20211015.b")

new_batch=pyg.pygilent.import_batch(new_batch_path)


new_batch.set_blks(how='auto')
#new_batch.check_blks()
new_batch.set_brkt_stnds(how='auto', keyword='stgfrm')
new_batch.cali_mode='ratio curve'
new_batch.set_ratio_iso(how='auto', keyword='Ca48')
new_batch.set_cali_stnds(stndvals, how='ui')

new_batch.initialise()
new_batch.blank_correction()
new_batch.ratio_correction()
#Why does bracket correction produce non 1's for STGFrm??
new_batch.bracket_correction()
new_batch.calibrate()

