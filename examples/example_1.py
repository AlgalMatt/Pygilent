import Pygilent as pyg
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import os

#get the default standard values
stndvals=pyg.stnds.get_default_stndvals()

#import the batch from folder
dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
new_batch=pyg.pygilent.import_batch(dir_path/'example_batch_TEratio.b')

new_batch.set_blks(how='auto')
new_batch.set_brkt_stnds(how='auto', keyword='stgfrm')
new_batch.cali_mode='ratio curve'
new_batch.set_internal_stnd(how='auto', keyword='Ca48')
new_batch.set_cali_stnds(stndvals, how='ui')
new_batch.initialise()
new_batch.blank_correction()
new_batch.ratio_correction()
new_batch.bracket_correction()
new_batch.calibrate()