import Pygilent as pyg
from pathlib import Path




#replace with path of single evaporite batch folder (.b folder)
evap_batch_path=Path(r"C:\Users\mdumo\OneDrive - University of St Andrews\Agilent\Matt\Full agilent data\20240524_Evaporites\20240524_Evaporites\Evaporites_TE_11smps_HJMM_20240524_MalSWEvapExp.b")

#the following methods must be performed in order

#retrieve stock standard values
stndvals=pyg.stnds.get_default_stndvals()

#import batch folder
new_batch=pyg.pygilent.import_batch(evap_batch_path)

#(optional) identify blanks. Set how = 'auto' to label any sample 
# containing the string 'blk' (not case sensitive)
# use how = 'ui' to use a pop-up window to select blanks by hand
new_batch.set_blks(how='auto')

#set calibration mode
new_batch.cali_mode='conc curve'

#set calibration standards. Can set how='auto' with a keyword to automatically label
#all keyword matches as the standard
new_batch.set_cali_stnds(stndvals, how='ui', keyword='STGSW')

#initialise the calibration. 
new_batch.initialise()

#(optional) perform blank correction using labelled blanks
new_batch.blank_correction()

#calibrate using the labelled calibration standards
new_batch.calibrate()

#calibrated output is now retrievable as attribute: new_batch.calibrated_output 

#produces a plot of any given isotope's calibration curve
#useful for checking if any outliers in the standards. 
#Can go back to set_cali_stnds method step to change cali standards
new_batch.plot_calibration('B11_No Gas')

#save calibrated output to excel file
new_batch.save_to_excel(evap_batch_path/'output.xlsx')

