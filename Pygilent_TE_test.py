import os
import pandas as pd
import numpy as np
import sympy as sym
from tkinter import filedialog
import tkinter as tk
import csv
import math
import warnings
import statsmodels.api as sm
import time
import statistics
from tkinter import ttk
import agilent.Pygilent as pyg





########Directories###########

#Select directory for new data import
root=tk.Tk()
root.withdraw()
root.attributes('-topmost', True)
folder_select=filedialog.askdirectory()
root.destroy()


#Standard data
stndpath=(r"stndvals.csv")
#Archived data
archivepath=(r"AgilentArchive.csv")



#Flicker value determined from fit (used for theoretical errors)
flick=0.003



#############Import data #################

#load archive data and set datetimes
if os.path.exists(archivepath):
    archive_df=pd.read_csv(archivepath, index_col=0)  
    archive_df['time']=pd.to_datetime(archive_df['time'], 
                                            dayfirst=True)
    archive_df['session_time']=pd.to_timedelta(archive_df['session_time']).dt.total_seconds()



#New data import
#reads batch file
folder_list=os.listdir(folder_select)
Batchlogloc=folder_select+'/BatchLog.csv'
batchdf=pd.read_csv(folder_select+'/BatchLog.csv') 
#gets time string and converts to datetime
batchdf['time']=pd.to_datetime(batchdf.iloc[:, 1]) 
batch_t=batchdf[(batchdf['Acquisition Result']=='Pass') & \
                (batchdf["Sample Type"].str.contains("Tune")==False)].copy()


#Get the runname
fsplit=folder_select.split('/')
runname=fsplit[-1]

#Get a list of the sample names, make them into directories and put them into the main df
values=[]
for i in batch_t["File Name"]:
    sfsplit=i.split('\\')    
    values.append(folder_select+'/'+sfsplit[-1])
   # print(sfsplit[-1])
batch_t['Sample Folder']=values
batch_t=batch_t.reset_index()
#Setup run info table
Run_df=pd.DataFrame(np.repeat(runname, len(batch_t)), columns=['run_name'])

#rename columns to be pythonic
batch_t.rename(columns={'Sample Name':'sample_name','Vial#':'vial'}, 
               inplace=True)

Run_df=pd.concat([Run_df, batch_t[['time', 'sample_name', 'vial']]],
                 axis=1)

#Get the total elapsed time since first sample
Run_df['session_time']=batch_t['time']-batch_t.loc[0,'time']
#Convert to seconds
Run_df['session_time']=Run_df['session_time'].dt.total_seconds()

#empty dataframes
repCPS_all_df=pd.DataFrame()
repPA_all_df=pd.DataFrame()
repSD_all_df=pd.DataFrame()

#set up the progressbar
root=tk.Tk()
progressbar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400)
root.title('Progress')

#Keep the window at the front of other apps.
root.lift()
root.attributes("-topmost", True)


w = 300 # width for the Tk root
h = 100 # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# set the dimensions of the screen 
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

l = tk.Label(root, text = "Importing data, please wait...")
l.pack(side=tk.TOP)
progressbar.pack(side=tk.BOTTOM)
progressbar['value']=0  
progressbar.update()


#Start iterating through samples
for i, folder in enumerate(batch_t['Sample Folder']):   
       
    #increment the progressbar
    progressbar['value']=(i+1)/len(batch_t['Sample Folder'])*100
    progressbar.update()

    
    #Get list of subfolders containing replicates and gas modes. Exclude quickscan
    csvlist = [s for s in os.listdir(folder) if ".csv" in s and "quickscan" 
               not in s]
    
    #Find out how many repeats and gas modes there are by reading first sample
    testmode=[]
    headlist=[]
    #iterate through all files in sample directory
    for c in csvlist:
        #open each file and take the gas mode by stripping other content
        with open(folder+'/'+c, newline='') as f:
            reader = csv.reader(f)
            row1 = next(reader)[0].rsplit('/')[-1].strip('\n ')
            testmode.append(row1)
    
    #Get the number of repeats and gases by counting occurrences of gas modes
    numrepeats=testmode.count(list(set(testmode))[0])
    numgases=len(set(testmode))
    
    #Extract all data from all samples
    #Create empty lists      
    listCPS=[]
    listPA=[]
    listSD=[]
    #iterate through replicates  
    for i in range(numrepeats):
        #Empty dataframe for each repeat
        allgas_df=pd.DataFrame()
        #iterate through gas modes
        for j in range(numgases):
            fileloc=folder+'/'+csvlist[i+j*numrepeats] #directory of file
            #Read the data
            gas_df=pd.read_csv(fileloc, skiprows=list(range(0, 7)), header=0) 
            #remove print info                               
            gas_df=gas_df.drop(gas_df.tail(1).index) 
            #get the current gas mode
            gasmodetxt=testmode[i+j*numrepeats].strip(' ') 
            
            #Get the element and mass info, which is printed differently in csv
            #depending on whether using single or double quads.
            if np.all(np.any(pyg.contains1d(gas_df.columns, ['Q1', 'Q2'], 
                                        ret_array=False), axis=0)):
                
                 gas_df["isotope_gas"]=(gas_df["Element"]
                                        +np.array(gas_df['Q1'], 
                                                  dtype=int).astype('str')
                                        +"_"+np.array(gas_df['Q2'], 
                                                      dtype=int).astype('str')
                                        +"_"+gasmodetxt)   
                
            else:                    
                #Make df of current gas mode
                #Combine mass and element to make isotope column
                gas_df["isotope_gas"]=(gas_df["Element"]
                                       +gas_df.iloc[:, 0]+"_"+gasmodetxt) 
                    
                    
            gas_df["gas_mode"]=gasmodetxt
                        
            #PA column often wrongly named, so need to rename it.
            #first find the column next to CPS            
            idx=np.where(gas_df.columns == 'CPS')[0]+1
            gas_df['PA']=gas_df.iloc[:, idx]
            #Concat all gas modes of this repeat
            allgas_df=pd.concat([allgas_df, gas_df], ignore_index=True)
        #extract cps and PA from all gas modes
        listCPS.append((np.array(allgas_df['CPS']))) 
        listPA.append((np.array(allgas_df['PA'])))
        
    
    #arrays of isotopes and gas modes used
    isotopes=np.array(allgas_df['isotope_gas'])    
    Gasmodes=np.array(allgas_df['gas_mode']) 
    
    #Create nested list of CPS and PA replicates
    repCPS=[list(s) for s in np.vstack(listCPS).T]
    repPA=[list(s) for s in np.vstack(listPA).T]
    

    #Form above lists into df
    repCPS_df=pd.DataFrame([repCPS], columns=isotopes)
    repPA_df=pd.DataFrame([repPA], columns=isotopes)

        
    #Concatenate all samples
    repCPS_all_df=pd.concat([repCPS_all_df, repCPS_df], ignore_index=True)       
    repPA_all_df=pd.concat([repPA_all_df, repPA_df], ignore_index=True)  

            

#close the progress bar
root.destroy()

# Add in the info    
repCPS_all_df=pd.concat([Run_df, repCPS_all_df], axis=1)            
repPA_all_df=pd.concat([Run_df, repPA_all_df], axis=1)    


#Make a long dataframe with a column for each rep
#reshape the replicates to make one column for each
rep_CPS_arr=np.array(repCPS_all_df[isotopes].values.tolist())
rep_CPS_arr_reshaped=np.reshape(rep_CPS_arr, (-1, numrepeats))

repPA_arr=np.array(repPA_all_df[isotopes].values.tolist()) 
repPA_arr_reshaped=np.reshape(repPA_arr, (-1, numrepeats))

s_names=[y for x in Run_df['sample_name'].values for y in [x]*len(isotopes)]
s_idx=[y for x in np.arange(len(repCPS_all_df)) for y in [x]*len(isotopes)]

s_isos=[]
for i in range(len(Run_df)):
    s_isos.extend(isotopes)

rep_num=[numrepeats]*len(s_idx)
run_long_df=pd.DataFrame(list(zip(s_idx, s_names, rep_num, s_isos)), 
                            columns=['run_order', 'sample_name', 'rep_num', 'isotope_gas'])
#rep col names
repnames=np.array([f"rep_{i}" for i in np.arange(numrepeats)+1])
rep_cps_long_df=pd.concat([run_long_df, 
                            pd.DataFrame(rep_CPS_arr_reshaped, columns=repnames)], axis=1)
rep_PA_long_df=pd.concat([run_long_df, 
                            pd.DataFrame(repPA_arr_reshaped, columns=repnames)], axis=1)




####Select the ratio element
#iterate through gas modes to select each ratio element and store as dict
ratioels={}
isotopes_bygas={}
isotopes_bygas_element={}
for gas in pd.unique(Gasmodes):
    gasels=isotopes[Gasmodes==gas]
    #Use Ca48 by default, second preference is Ca43
    ratioel_default=pyg.contains1d(gasels, 'Ca48')   
    if sum(ratioel_default)<1:
        ratioel_default=pyg.contains1d(gasels, 'Ca43')
    
    #User select the ratio isotope
    ratioel=gasels[pyg.fancycheckbox(gasels, defaults=ratioel_default, 
                                 single=True, title=("Select ratio isotope"
                                                     ))][0]
    #dict of ratio elements
    ratioels[gas]=ratioel
    #dict of measured full isotope names
    isotopes_bygas[gas]=gasels
    #dict of measured isotope names as element only (no mas or gas mode)
    #This is for referencing with the stndvals_df.
    isotopes_bygas_element[gas]=[
        s.split('_')[0].strip('1234567890') for s in gasels] 
  






########Open the replicate editor?
options = {'icon': 'question', 'type': 'yesno', 'default': 'no'}
answer = tk.messagebox.askyesno(title=None, 
                                message='Open replicate editor? (Not recommended)', **options)

if answer:
    #Remove the same rep(s) from all samples?
    answer = tk.messagebox.askyesno(title=None, 
                                message='Do you want to remove the same replicate from all samples?', 
                                **options)
    if answer:
        #Select which reps to remove
        rep_edit_idx=pyg.fancycheckbox(repnames, 
                                   title=("Select the replicate(s) you want to remove (FROM ALL SAMPLES)")) 
        if len(rep_edit_idx)>0:
            #Remove the reps from all samples
            #rep_cps_long_df.drop(labels=np.array(repnames)[rep_edit_idx], axis=1, inplace=True)
            #rep_PA_long_df.drop(labels=np.array(repnames)[rep_edit_idx], axis=1, inplace=True)
            rep_cps_long_df[repnames[rep_edit_idx]]=np.nan
            rep_cps_long_df['rep_num']=numrepeats-len(rep_edit_idx)
            rep_PA_long_df[repnames[rep_edit_idx]]=np.nan
            rep_PA_long_df['rep_num']=numrepeats-len(rep_edit_idx)
            

    #P/A outlier determination
    pa_outliers=np.array(rep_PA_long_df[repnames].apply(lambda x: 
        (x.values!=x.value_counts().index[0])&(~pd.isna(x.values)), 
        axis=1).tolist())

    if len(rep_PA_long_df.loc[pa_outliers]) > 0:
        # Display the P/A outliers and ask whether to auto remove?
        answer=pyg.display_dataframe_with_option(rep_PA_long_df.loc[pa_outliers])
    
        if answer:
            #Are any of the outliers the ratio element? 
            #If so, must remove that rep from all isotopes in that sample
            #Automatically remove P/A outlers
            rep_cps_long_df[repnames] = np.where(pa_outliers, np.nan, rep_cps_long_df[repnames])
            rep_cps_long_df=pyg.ratioel_rep_removal(rep_cps_long_df, repnames, ratioels, isotopes, Gasmodes)
            rep_cps_long_df['rep_num']=numrepeats-np.isnan(rep_cps_long_df[repnames]).sum(axis=1)
            rep_PA_long_df[repnames] = np.where(pa_outliers, np.nan, rep_PA_long_df[repnames])
            rep_PA_long_df['rep_num']=numrepeats-pd.isna(rep_PA_long_df[repnames]).sum(axis=1)
        
    
    
    #CPS outliers
    #Set to mod = 20 arbitrarily to only highlight very clear outliers (normally use mod=1.5)
    outmod=20
    cps_outliers=np.array(rep_cps_long_df[repnames].apply(pyg.outsbool, mod=outmod, axis=1).tolist())
    #omit NaNs
    cps_outliers=cps_outliers & (~pd.isna(rep_cps_long_df[repnames]))
    
    cps_outlier_samples=rep_cps_long_df.loc[np.any(cps_outliers, axis=1)]
    pa_outlier_samples=rep_PA_long_df.loc[np.any(pa_outliers, axis=1)]
    
    cps_outlier_samples_short=pd.unique(cps_outlier_samples['run_order'].values)
    out_defaults=np.array([False]*len(Run_df))
    out_defaults[cps_outlier_samples_short]=True
    
    sample_edit_idx=pyg.fancycheckbox(repCPS_all_df['sample_name'].values, defaults=out_defaults , 
                  title=("Select the samples from which you want to edit replicates"))
    
    #cycle through each sample and edit
    for id in sample_edit_idx:
        
        sample_df=rep_cps_long_df.loc[rep_cps_long_df['run_order']==id]
        sample_pa_df=rep_PA_long_df.loc[rep_PA_long_df['run_order']==id]
        sample_outlier_cps_isos=cps_outlier_samples.loc[
            cps_outlier_samples['run_order']==id, 'isotope_gas'].values
        sample_outlier_pa_isos=pa_outlier_samples.loc[
            pa_outlier_samples['run_order']==id, 'isotope_gas'].values

        pa_padding=np.array(['']*max([
            0, len(sample_outlier_cps_isos)-len(sample_outlier_pa_isos)]))
        cps_padding=np.array(['']*max([
            0, len(sample_outlier_pa_isos)-len(sample_outlier_cps_isos)]))
        
        cps_pa_dict={'CPS outlier isotopes': np.concatenate((sample_outlier_cps_isos, cps_padding)), 
                     'PA outliers isotopes': np.concatenate((sample_outlier_pa_isos, pa_padding))}
        
        cps_col=np.concatenate((sample_outlier_cps_isos, cps_padding))
        pa_col=np.concatenate((sample_outlier_pa_isos, pa_padding))
        
        
        cps_pa_table=pd.DataFrame(cps_pa_dict)
        
        
        
        title=str(id)+': '+repCPS_all_df.loc[id, 'sample_name']
        
        sample_df.loc[:, 'old_index']=sample_df.index.values
        sample_pa_df.loc[:, 'old_index']=sample_pa_df.index.values
        
        sample_df=sample_df.set_index('isotope_gas', drop=False)
        sample_pa_df=sample_pa_df.set_index('isotope_gas', drop=False)
        
        new_sample_df=pyg.repeditor(sample_df, sample_pa_df, title, cps_pa_table, id, repnames, 
                                repPA_all_df=repPA_all_df)
        
        new_sample_df=new_sample_df.set_index('old_index')
        
        rep_cps_long_df.loc[new_sample_df.index]=new_sample_df.copy()
        


#Are any of the outliers the ratio element? 
#If so, must remove that rep from all isotopes in that sample
rep_cps_long_df=pyg.ratioel_rep_removal(rep_cps_long_df, repnames, ratioels, isotopes, Gasmodes)

rep_cps_long_df['rep_num']=(numrepeats-np.sum(np.isnan(rep_cps_long_df[repnames]), axis=1))
rep_cps_long_df['rep_list']=rep_cps_long_df[repnames].apply(list, axis=1)


#Create means and stdevs.
rep_cps_long_df['cps_mean']=np.nanmean(rep_cps_long_df[repnames], axis=1)
rep_cps_long_df['cps_std']=np.nanstd(rep_cps_long_df[repnames], axis=1, ddof=1)
CPSmean_df=pd.pivot_table(rep_cps_long_df, values='cps_mean', index='run_order'
                          , columns=['isotope_gas'], sort=False)
CPSmean_df.reset_index(inplace=True)
CPSmean_df=pd.concat([Run_df, CPSmean_df], axis=1)
CPSstd_df=pd.pivot_table(rep_cps_long_df, values='cps_std', index='run_order'
                          , columns=['isotope_gas'], sort=False)
CPSstd_df.reset_index(inplace=True)
CPSstd_df=pd.concat([Run_df, CPSstd_df], axis=1)


#Make df of lists of all reps
reps_pivoted_sorted = rep_cps_long_df.pivot(index='run_order', columns=['isotope_gas'], 
                        values='rep_list')
repCPS_all_df[isotopes]=reps_pivoted_sorted[isotopes]

#####Create average P/A table
#make sure any reps chosen in the rep editor are assigned as nan in PA df
mask=np.isnan(rep_cps_long_df[repnames])
rep_PA_long_df[repnames] = np.where(mask, np.nan, rep_PA_long_df[repnames])
rep_PA_long_df['rep_num']=rep_cps_long_df['rep_num']

rep_PA_long_df['PA_all_digi'] = (np.nansum(rep_PA_long_df[repnames]=='P', axis=1)
                                 /rep_PA_long_df['rep_num'])
PA_digi_df=pd.pivot_table(rep_PA_long_df, values='PA_all_digi', index='run_order'
                          , columns=['isotope_gas'], sort=False)
PA_df=PA_digi_df.copy()
PA_df[isotopes]='M'
PA_df[isotopes] = np.where(PA_digi_df[isotopes]==1, 
                                    'P', PA_df[isotopes] ) 
PA_df[isotopes]  = np.where(PA_digi_df[isotopes] ==0, 
                                    'A', PA_df[isotopes] ) 
PA_df.reset_index(inplace=True)
PA_df=pd.concat([Run_df, PA_df], axis=1)


#Create table of rep numbers (n)
n_df=pd.pivot_table(rep_cps_long_df, values='rep_num', index='run_order'
                          , columns=['isotope_gas'], sort=False)
n_df.reset_index(inplace=True)
n_df=pd.concat([Run_df, n_df], axis=1)




########## Setup processing equations ########


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

#TE/Ca ratio equation
R_sym=(x_sym - Dtb_sym*xb2_sym + xb1_sym*(Dtb_sym - 1)
       )/(y_sym - Dtb_sym*yb2_sym + yb1_sym*(Dtb_sym - 1))
#Make into function    
R_f = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, 
                    Dtb_sym), R_sym)  

#Variance in R
R_var_sym=(s_x_sym**2*R_sym.diff(x_sym)**2+s_y_sym**2*R_sym.diff(y_sym)**2
    +s_xb1_sym**2*R_sym.diff(xb1_sym)**2+s_xb2_sym**2*R_sym.diff(xb2_sym)**2
    +s_yb1_sym**2*R_sym.diff(yb1_sym)**2+s_yb2_sym**2*R_sym.diff(yb2_sym)**2
    +2*cov_xy_sym*R_sym.diff(x_sym)*R_sym.diff(y_sym)
    +2*cov_xb1yb1_sym*R_sym.diff(xb1_sym)*R_sym.diff(yb1_sym)
    +2*cov_xb2yb2_sym*R_sym.diff(xb2_sym)*R_sym.diff(yb2_sym))
#Make into function
R_var_f = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, 
                        Dtb_sym, cov_xy_sym, cov_xb1yb1_sym, cov_xb2yb2_sym, 
                        s_x_sym, s_y_sym, s_xb1_sym, s_xb2_sym, s_yb1_sym, 
                        s_yb2_sym), R_var_sym)    


#Bracketed sample equation                    
B_sym=-((x_sym - Dtb_sym*xb2_sym + xb1_sym*(Dtb_sym - 1))/((((Dts_sym - 1)
    *(xs1_sym - Dts1b_sym*xb2_sym + xb1_sym*(Dts1b_sym - 1)))
    /(ys1_sym - Dts1b_sym*yb2_sym + yb1_sym*(Dts1b_sym - 1))
    -(Dts_sym*(xs2_sym - Dts2b_sym*xb2_sym + xb1_sym*(Dts2b_sym - 1)))
    /(ys2_sym - Dts2b_sym*yb2_sym + yb1_sym*(Dts2b_sym - 1)))
    *(y_sym - Dtb_sym*yb2_sym + yb1_sym*(Dtb_sym - 1))))

#Make into function       
B_f = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, Dtb_sym, 
              xs1_sym, ys1_sym, Dts1b_sym, xs2_sym, ys2_sym, Dts2b_sym, 
              Dts_sym), B_sym)       
    
#Variance in B    
B_var_sym=(s_x_sym**2*B_sym.diff(x_sym)**2+s_y_sym**2*B_sym.diff(y_sym)**2
    +s_xb1_sym**2*B_sym.diff(xb1_sym)**2+s_xb2_sym**2*B_sym.diff(xb2_sym)**2
    +s_xs1_sym**2*B_sym.diff(xs1_sym)**2+s_xs2_sym**2*B_sym.diff(xs2_sym)**2
    +s_yb1_sym**2*B_sym.diff(yb1_sym)**2+s_yb2_sym**2*B_sym.diff(yb2_sym)**2
    +s_ys1_sym**2*B_sym.diff(ys1_sym)**2+s_ys2_sym**2*B_sym.diff(ys2_sym)**2
    +2*cov_xy_sym*B_sym.diff(x_sym)*B_sym.diff(y_sym)
    +2*cov_xb1yb1_sym*B_sym.diff(xb1_sym)*B_sym.diff(yb1_sym)
    +2*cov_xb2yb2_sym*B_sym.diff(xb2_sym)*B_sym.diff(yb2_sym)
    +2*cov_xs1ys1_sym*B_sym.diff(xs1_sym)*B_sym.diff(ys1_sym)
    +2*cov_xs2ys2_sym*B_sym.diff(xs2_sym)*B_sym.diff(ys2_sym))


#Make into function
B_var_f = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, 
                        Dtb_sym, xs1_sym, ys1_sym, Dts1b_sym, xs2_sym, ys2_sym
                        ,Dts2b_sym, Dts_sym, cov_xy_sym, cov_xb1yb1_sym, 
                        cov_xb2yb2_sym, cov_xs1ys1_sym, cov_xs2ys2_sym, 
                        s_x_sym, s_y_sym, s_xb1_sym, s_xb2_sym,
                        s_yb1_sym, s_yb2_sym, s_xs1_sym, s_ys1_sym, s_xs2_sym, 
                        s_ys2_sym), B_var_sym)



#Counts per cycle for theoretical error
inttime_dict=dict(zip(allgas_df['isotope_gas'], allgas_df['Time(Sec)']))
CPC_df=CPSmean_df.copy()
for iso in isotopes:
    CPC_df[iso]=CPSmean_df[iso]*inttime_dict[iso]





######### User Options #########################

#Assign default blank indexes based off sample names    
blkdefaults=list(batch_t['sample_name'].str.contains('blk',
                                                     case=False).astype(int))

#Checkbox for selecting blanks
namelist=[str(i+1)+')  '+s for i, s in enumerate(list(batch_t['sample_name']))]
blkrows=np.array([])
#Don't allow the window to close unless at least one blank is selected
while blkrows.size<1:
    blkrows=pyg.fancycheckbox(namelist, defaults=blkdefaults, 
                          title=("Check the blanks are selected"))

#Figure de-select outlier blanks based of counts
cpsblank=CPSmean_df.loc[blkrows, np.append('session_time', isotopes)]
deblank=pyg.pickfig(cpsblank, 'session_time', 'Click on blanks to remove outliers')
blkrows=blkrows[~np.in1d(blkrows, deblank)]




#Assign default bracket standard indexes based off sample names    
brktdefaults=list(batch_t['sample_name'].str.contains('stgfrm',
                                                     case=False).astype(int))

#Use the most-common occurrence of 'STGFrm'
if sum(brktdefaults)>0:
    countbrkt=batch_t.loc[batch_t['sample_name'].str.contains('stgfrm',case=False), 
            'sample_name'].value_counts()   
    brktdefaults=batch_t['sample_name']==countbrkt.index[0]
    brktdefaults=list(brktdefaults.astype(int))




brktrows=np.array([])
#Don't allow the window to close unless at least one brkt stnd is selected
while brktrows.size<1:
    brktrows=pyg.fancycheckbox(namelist, defaults=brktdefaults, 
                       title=("Check the bracketing standards are selected"))

#De-select outlier bracketing standards based of counts
cpsbrkt=CPSmean_df.loc[brktrows, np.append('session_time', isotopes)]
debrkt=pyg.pickfig(cpsbrkt, 'session_time', 
               'Click on bracketing standards to remove outliers')
brktrows=brktrows[~np.in1d(brktrows, debrkt)]


    
    
    
    
#Select calibration method
calistyle_list=['Single-point', 'Calibration curve']
calistyle=calistyle_list[pyg.fancycheckbox(calistyle_list, defaults=[True, False],
                                       single=True, title=("Select calibration"
                                                           " method"))[0]]

calinames=pd.unique(batch_t['sample_name'][brktrows])
calirows=[]
if calistyle=='Calibration curve':
    #Select cali standards
    unique_names=pd.unique(batch_t['sample_name'])
    #default cali standard names
    calidefaults=pyg.contains1d(unique_names, ['stgfrm', 'stgcco', 'stglim',
                                        'stgcrl'])
    #remove dummy standard at beginning
    calidefaults[pyg.contains1d(unique_names, 'stgfrmx')]=False
    
    #Choose calibration standards
    #Make sure the user chooses at least 2
    calinamebool=np.array([])
    while calinamebool.size<2:
        calinamebool=pyg.fancycheckbox(unique_names, defaults=calidefaults, 
                                             title=("Select names of the "
                                                    "calibration standards"))
    calinames=unique_names[calinamebool]
    #Find them in the sequence and get the index
    calindx_default=batch_t['sample_name'].isin(calinames)
    #Removes extra bracketing standards (those that aren't adjacent)
    #Only include as many bracketing standards in the calibration
    #as there are copies of each of the other calibration standards
    
    #find the most common calibrant quantity
    numcali=statistics.mode(batch_t['sample_name'].value_counts()[calinames])
    
    
      
    calirows=[]
    
    #Find only adjacent calibration standards in the sequence
    for i, c in enumerate(calindx_default):
        if c and calindx_default[max([i-1, 0])]==False and \
            calindx_default[min([i+1, len(calindx_default)-1])]==False:
            calindx_default[i]=False
            
    #User select the cali stnds from sequence
    calindx=np.array([])
    while calindx.size<len(calinames):
        calindx=pyg.fancycheckbox(namelist, defaults=calindx_default, 
                              title=("Check that the correct calibration standards"
                                     " are selected"))
else:
    calinames=pd.unique(Run_df.loc[brktrows, 'sample_name'])
        
                
#load in the standard values set 
stndvals_df=pd.read_csv(stndpath)  
stndvals_df=stndvals_df.set_index('Element')
stndval_names=stndvals_df.columns[1:]

#make dict for elements and isotopes
isoel_dict=dict(zip(allgas_df['isotope_gas'], allgas_df['Element']))

#Assign measured isotope names to the standard values dataframe
calivals_df=pd.DataFrame()

for i, iso in enumerate(isotopes):
    #Check if isotope is included in standard spreadsheet, if not then skip
    if all(stndvals_df.index!=isoel_dict[iso]):       
        continue
        
    #Create dataframe with standard values
    row_df=stndvals_df.loc[isoel_dict[iso], :].copy()
    row_df['isotope']=iso
    row_df=pd.DataFrame(row_df).transpose().reset_index() 
    row_df.rename(columns={'index':'element'}, inplace=True)
    row_df.set_index("isotope", inplace=True)  
    calivals_df=pd.concat([calivals_df,row_df])
    
  
#Manually associate each bracketing or cali standard to one in stndvals.
stnd_dict={}
for cali in calinames:    
    associate_default=[x in cali for x in stndval_names]
    cal_associate=stndval_names[pyg.fancycheckbox(stndval_names, 
                                              defaults=associate_default,
                                              single=True, 
                                              title=("Link {} to the correct " 
                                              "standard name".format(cali)))]   
    stnd_dict[cali]=calivals_df[cal_associate].dropna()


#this will be a dictionary with isotopes to not be included in the calibration
#as keys, the values are the column indexes for the isotopes when all data is 
#an array
missing={}

brkt_df=stnd_dict[Run_df.loc[brktrows[0], 'sample_name']]      
for i, iso in enumerate(isotopes):   
    if all(brkt_df.index!=iso):
        #note the missing isotopes for later
        missing[iso]=i

#get the calibration isotopes
sing_isos=isotopes.copy()
sing_isos=isotopes[~pyg.contains1d(isotopes, list(missing.keys()))].copy()



#Assign a column that describes the type of sample, standard or blank

#first assign all as 'Sample'
Run_df['sample_type']=['Sample']*len(Run_df)
#Then assign the blanks
Run_df.loc[blkrows, 'sample_type']=['Blank_'+str(x) 
                             for x in np.arange(len(blkrows))+1]
#Then the bracketing standards
Run_df.loc[brktrows, 'sample_type']=['Bracket_'+str(x) 
                             for x in np.arange(len(brktrows))+1]
#Then the calibration standards, if any. 
if calistyle=='Calibration curve':   
    for i, row in enumerate(calindx):
        if any(row==np.intersect1d(calindx, brktrows)):
            Run_df.loc[row, 'sample_type']=Run_df.loc[
                row, 'sample_type']+' & Calibrant_'+str(i+1)
        else:
            Run_df.loc[row, 'sample_type']='Calibrant_'+str(i+1)
        

        


#Ensure that all cali standards are using the same detector mode (P/A)
#Find the P/A of the bracketing standard, remove standards from cali curve that
#aren't the same P/A. 
PA_bracket_bad_index={}
if calistyle=='Calibration curve':
    PA_df_cali=PA_df.loc[calindx, :]
    for i, iso in enumerate(isotopes):   
        #The P/A of the bracketing standard       
        PAbracket=PA_df.loc[brktrows, iso]
        
        #if more than one P/A, then remove them from calibration
        if len(PAbracket.value_counts())>1:                       
            PA_bracket_bad_index[iso]=PAbracket.index[PAbracket!=PAbracket.value_counts().index[0]].values
            
        PA_df_cali[iso]==PAbracket.value_counts().index[0]  
        PAcounts=PA_df_cali[iso].value_counts()
        #list of sample names that have a different P/A to the bracketing stnd
        PA_outlier=PA_df_cali.loc[PA_df_cali[iso]!=PAbracket.value_counts(
            ).index[0], 'sample_name']
        #Remove those stnds from the calibation curve
        if PA_outlier.shape[0]>0:       
            for st in PA_outlier:
                stnd_dict[st].loc[iso]=np.NaN
    
#Isotopes to be used in the calibration curve approach (possibly different
#from the single-point isotopes (sing_isos))
curve_isos=isotopes[~pyg.contains1d(isotopes, list(missing.keys()))].copy()





#################Processing ##################

#create array of Ca counts using different gases
y_df=Run_df.copy() #mean Ca cps
s_y_df=Run_df.copy() #sd Ca
repCPS_y_df=Run_df.copy() #replicate Ca cps
CPC_y_df=Run_df.copy() #for theoretical errors (Ca counts per cycle)
   
for gas in list(ratioels.keys()):
    #Create matrix of Ca cps values
    rat_mat=np.tile(np.array(CPSmean_df[ratioels[gas]]), 
                    [len(isotopes_bygas[gas]), 1])
    sd_mat=np.tile(np.array(CPSstd_df[ratioels[gas]]), 
                    [len(isotopes_bygas[gas]), 1])
    
    rep_mat=np.tile(np.array(repCPS_all_df[ratioels[gas]]), 
                    [len(isotopes_bygas[gas]), 1])
    #convert to data frame
    rat_df=pd.DataFrame(rat_mat.T, columns=isotopes_bygas[gas])
    y_df=pd.concat([y_df, rat_df], axis=1)
    
    sd_df=pd.DataFrame(sd_mat.T, columns=isotopes_bygas[gas])
    s_y_df=pd.concat([s_y_df, sd_df], axis=1)
    
    rep_df=pd.DataFrame(rep_mat.T, columns=isotopes_bygas[gas])
    repCPS_y_df=pd.concat([repCPS_y_df, rep_df], axis=1)
    
    CPC_y_df=pd.concat([CPC_y_df, rat_df*inttime_dict[ratioels[gas]]], axis=1)
    
    


#Generate covariances dataframe    
cov_df=pd.DataFrame([])
#cycle through samples with nested loop of isotopes to get covariances
for i, row in repCPS_all_df.iterrows():
    cov_array=np.array([])
    for iso in isotopes:
        #array of numerator isotopes
        rep_x_array=np.array(list(row[iso]))
        #array of denominators (Ca)
        rep_y_array=np.array(list(repCPS_y_df.loc[i, iso]))   
        
        #remove any NaNs
        rep_y_array=rep_y_array[~np.isnan(rep_x_array)]
        rep_x_array=rep_x_array[~np.isnan(rep_x_array)]

        #covariances
        cov_array=np.append(cov_array, 
                         np.cov(np.vstack((rep_x_array, rep_y_array)))[0, 1])
    #make into dataframe   
    cov_row=pd.DataFrame([cov_array], columns=isotopes)   
    cov_df=pd.concat([cov_df, cov_row], ignore_index=True)        

#Initialise final data frames using an array of NaN values
nanarray=np.full((len(Run_df),len(isotopes)),np.nan)
RunNaN_df=Run_df.copy()
RunNaN_df[isotopes]=nanarray

ratio_smpl_df=RunNaN_df.copy()
brkt_smpl_df=RunNaN_df.copy()
ratio_smpl_se_df=RunNaN_df.copy()
brkt_smpl_se_df=RunNaN_df.copy()
cali_sing_df=RunNaN_df.copy()
cali_sing_se_df=RunNaN_df.copy()
cali_curv_df=RunNaN_df.copy()
cali_curv_se_df=RunNaN_df.copy()
blkcorr_df=RunNaN_df.copy()
theo_R_rse_df=RunNaN_df.copy()
theo_Rbc_rse_df=RunNaN_df.copy()
theo_B_rse_df=RunNaN_df.copy()
theo_Bbc_rse_df=RunNaN_df.copy()

#Initialize index lists
blk_index_1_ls=[]
blk_index_2_ls=[]
brkt_index_1_ls=[]
brkt_index_2_ls=[]
Dtb_ls=[]
Dts_ls=[]
Dts1b_ls=[]
Dts2b_ls=[]


indexes_dict={'blk_1_run_order':np.full((len(Run_df)),np.nan), 
              'blk_2_run_order':np.full((len(Run_df)),np.nan), 
              'brkt_1_run_order':np.full((len(Run_df)),np.nan),
              'brkt_2_run_order':np.full((len(Run_df)),np.nan), 
              'time_fraction_between_blks':np.full((len(Run_df)),np.nan),
              'time_fraction_between_brkts':np.full((len(Run_df)),np.nan),
              'brkt_1_time_fraction_between_blks':np.full((len(Run_df)),np.nan),
              'brkt_2_time_fraction_between_blks':np.full((len(Run_df)),np.nan)}


#Cycle through sample by sample to calculate R and B
for i, row in CPSmean_df.iterrows():
    #If a blank, skip
    if any(i==blkrows):
        continue
    
    #Number of blanks and stnds used for the corrections
    #find closest blank(s)
    blkorder=np.vstack((blkrows, np.abs(blkrows-i)))
    blkorder=np.vstack((blkorder, blkrows-i))
    blkorder = blkorder[:, np.argsort(blkorder[1,:], axis=0)]
    #If sample is before or after all blanks, use just one closest blank
    if np.all(blkrows-i>=0) or np.all(blkrows-i<=0):
        blk_r=np.array([blkorder[0, 0],blkorder[0, 0]])        
    #Otherwise use the two closest (braketing blanks)
    #If the first blank is before the sample in the run find one after
    elif blkorder[2, 0]<0:
        #get the next nearest blk that is of opposite sign direction away
        blk2=blkorder[0, np.where(blkorder[2, 1:]>0)[0][0]+1]          
        blk_r=np.array([blkorder[0, 0], blk2])
    #otherwise find a blank before the sample
    else:
        blk2=blkorder[0, np.where(blkorder[2, 1:]<0)[0][0]+1]          
        blk_r=np.array([blk2,blkorder[0, 0]])
           
    #find closest bracketing standard(s)
    #Make an array where the first row is the run positions of the closest 
    #bracketing standards
    #The second row is the absolute distance between the sample and the 
    #bracketing standard given in row 1
    brktorder=np.vstack((brktrows, np.abs(brktrows-i)))
    #The third row is the distance between the sample and standard with the
    #sign maintained to help determine whether they are 'bracketed'
    brktorder=np.vstack((brktorder, brktrows-i))
    #order the columns w.r.t the absolute distance
    brktorder = brktorder[:, np.argsort(brktorder[1,:], axis=0)]
    if np.all(brktrows-i>=0) or np.all(brktrows-i<=0) or any(brktrows-i==0):
        brkt_r=np.array([brktorder[0, 0],brktorder[0, 0]])
    #Otherwise use the two closest (braketing standards)
    #If the first stnd is before the sample in the run find one after
    elif brktorder[2, 0]<0:
        #get the next nearest stnd that is of opposite sign direction away
        brk2=brktorder[0, np.where(brktorder[2, 1:]>0)[0][0]+1]          
        brkt_r=np.array([brktorder[0, 0], brk2])
    #otherwise find a stnd before the sample
    else:
        brk2=brktorder[0, np.where(brktorder[2, 1:]<0)[0][0]+1]          
        brkt_r=np.array([brk2,brktorder[0, 0]])
        
        

    
          
    #Assign components of processing
    x=np.array(row[isotopes]) #TE sample
    y=np.array(y_df.loc[i, isotopes]) #Ca sample
    xb1=np.array(CPSmean_df.loc[blk_r[0], isotopes]) #TE blank 1
    yb1=np.array(y_df.loc[blk_r[0], isotopes])#Ca blank 1
    xb2=np.array(CPSmean_df.loc[blk_r[1], isotopes])#TE blank 2
    yb2=np.array(y_df.loc[blk_r[1], isotopes])#Ca blank 2
    
    xs1=np.array(CPSmean_df.loc[brkt_r[0], isotopes])#TE stnd 1
    ys1=np.array(y_df.loc[brkt_r[0], isotopes])#Ca stnd 1
    xs2=np.array(CPSmean_df.loc[brkt_r[1], isotopes])#TE stnd 2
    ys2=np.array(y_df.loc[brkt_r[1], isotopes])#Ca stnd 2
    
    #Assign fractional distance between two blanks
    if blk_r[0]==blk_r[1]:
        #If not between two blanks, then distance is 0
        Dtb=0
        Dts1b=0
        Dts2b=0
    else:
        #Sample
        Dtb=(row['session_time']-Run_df.loc[blk_r[0], 'session_time'])/(
            Run_df.loc[blk_r[1], 'session_time']-Run_df.loc[blk_r[0], 'session_time'])
        #Bracketing standard 1
        Dts1b=(Run_df.loc[brkt_r[0], 'session_time']
               -Run_df.loc[blk_r[0], 'session_time'])/(
                   Run_df.loc[blk_r[1], 'session_time']
                   -Run_df.loc[blk_r[0], 'session_time'])
        #Bracketing standard 2
        Dts2b=(Run_df.loc[brkt_r[1], 'session_time']
               -Run_df.loc[blk_r[0], 'session_time'])/(
                   Run_df.loc[blk_r[1], 'session_time']
                   -Run_df.loc[blk_r[0], 'session_time'])   
    
    #Assign fractional distance between bracketing standards
    if brkt_r[0]==brkt_r[1]:
        Dts=0
    else:
        Dts=(row['session_time']-Run_df.loc[brkt_r[0], 'session_time'])/(
            Run_df.loc[brkt_r[1], 'session_time']-Run_df.loc[brkt_r[0], 'session_time'])  
        
               
    #Find the blank-corrected values. Only necessary for LoD calulcation
    blkcorr=(row[isotopes]-Dtb*CPSmean_df.loc[blk_r[0], isotopes]
     +CPSmean_df.loc[blk_r[0], isotopes]*(Dtb-1)) 
    blkcorr_df.loc[i, isotopes]=blkcorr
    
    #Assign errors   
    s_x=np.array(CPSstd_df.loc[i, isotopes])
    s_y=np.array(s_y_df.loc[i, isotopes])
    s_xb1=np.array(CPSstd_df.loc[blk_r[0], isotopes])
    s_yb1=np.array(s_y_df.loc[blk_r[0], isotopes])
    s_xb2=np.array(CPSstd_df.loc[blk_r[1], isotopes])
    s_yb2=np.array(s_y_df.loc[blk_r[1], isotopes])
    s_xs1=np.array(CPSstd_df.loc[brkt_r[0], isotopes])
    s_ys1=np.array(s_y_df.loc[brkt_r[0], isotopes])
    s_xs2=np.array(CPSstd_df.loc[brkt_r[1], isotopes])
    s_ys2=np.array(s_y_df.loc[brkt_r[1], isotopes])
    
    #Assign covariances        
    cov_xy=np.array(cov_df.loc[i])
    cov_xb1yb1=np.array(cov_df.loc[blk_r[0]])
    cov_xb2yb2=np.array(cov_df.loc[blk_r[1]])
    cov_xs1ys1=np.array(cov_df.loc[brkt_r[0]])
    cov_xs2ys2=np.array(cov_df.loc[brkt_r[1]])
    
    
    
    
    
    #record blank indexes, brkt indexes, Dtb, Dts, Dts1b, Dts2b
    indexes_dict['blk_1_run_order'][i]=blk_r[0]
    indexes_dict['blk_2_run_order'][i]=blk_r[1]
    indexes_dict['brkt_1_run_order'][i]=brkt_r[0]
    indexes_dict['brkt_2_run_order'][i]=brkt_r[1]
    indexes_dict['time_fraction_between_blks'][i]=Dtb
    indexes_dict['time_fraction_between_brkts'][i]=Dts
    indexes_dict['brkt_1_time_fraction_between_blks'][i]=Dts1b
    indexes_dict['brkt_2_time_fraction_between_blks'][i]=Dts2b

    
    
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        #TE count ratio and variance
        ratio_smpl=R_f(x, xb2, xb1, y, yb2, yb1, Dtb)
        ratio_smpl_var=R_var_f(x, xb2, xb1, y, yb2, yb1, Dtb, cov_xy, 
                               cov_xb1yb1, cov_xb2yb2, s_x, s_y, s_xb1, s_xb2, 
                               s_yb1, s_yb2)
        #Bracketed count ratio and variance
        brkt_smpl = B_f(x, xb2, xb1, y, yb2, yb1, Dtb, xs1, ys1, Dts1b, xs2, 
                        ys2, Dts2b, Dts)
        brkt_smpl_var=B_var_f(x, xb2, xb1, y, yb2, yb1, Dtb, xs1, ys1, Dts1b, 
                              xs2, ys2, Dts2b, Dts, cov_xy, cov_xb1yb1, 
                              cov_xb2yb2, cov_xs1ys1, cov_xs2ys2, s_x, s_y,
                              s_xb1, s_xb2, s_yb1, s_yb2, s_xs1, s_ys1, s_xs2, 
                              s_ys2)
        
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        num_rep_arr=n_df.loc[i, isotopes].values.astype(int)
    
        #c4 function for adjusting se for low number of measurements    
        c4=np.array([math.gamma(x/2)/math.gamma((x-1)/2)*(
            2/(x-1))**0.5 if x>1 else np.nan for x in num_rep_arr])
        
        #convert variance into standard deviation
        ratio_smpl_se=ratio_smpl_var**0.5/c4/numrepeats**0.5
        brkt_smpl_se=brkt_smpl_var**0.5/c4/numrepeats**0.5
    
        #put into dataframes
        ratio_smpl_df.loc[i, isotopes]=ratio_smpl
        brkt_smpl_df.loc[i, isotopes]=brkt_smpl
        ratio_smpl_se_df.loc[i, isotopes]=ratio_smpl_se
        brkt_smpl_se_df.loc[i, isotopes]=brkt_smpl_se
    
         
        #calibration (single point)
        #delete the elements missing from the cali standard list
        b1=np.delete(brkt_smpl, list(missing.values()))
        b1_se=np.delete(brkt_smpl_se, list(missing.values()))  
         
        #make standard array based on the bracketing standard
        #Note, this does mean that different bracketing standards can be used
        #throughout the run
        cali_array=np.array(stnd_dict[Run_df.loc[brkt_r[0], 'sample_name']])
        
        #calibrate sample to known standard values by single-point calibration
        cali_sing=b1*np.squeeze(cali_array)
        cali_sing_se=(b1_se/b1)*cali_sing
        cali_sing_df.loc[i, sing_isos]=cali_sing
        cali_sing_se_df.loc[i, sing_isos]=cali_sing_se
        
        
        
        ############Theoretical error    
        
        #Sample R
        neff=((CPC_df.loc[i, isotopes]*CPC_y_df.loc[i, isotopes])
              / (CPC_df.loc[i, isotopes]+CPC_y_df.loc[i, isotopes]))
        
        
        interp_blank_cpc=(CPC_df.loc[blk_r[0], isotopes]*(1-Dtb)
                          +CPC_df.loc[blk_r[1], isotopes]*Dtb)
        interp_blank_cpc_y=(CPC_y_df.loc[blk_r[0], isotopes]*(1-Dtb)
                          +CPC_y_df.loc[blk_r[1], isotopes]*Dtb)
        
        neffbc=(((CPC_df.loc[i, isotopes]-interp_blank_cpc)
                 *(CPC_y_df.loc[i, isotopes]-interp_blank_cpc_y))
              / ((CPC_df.loc[i, isotopes]-interp_blank_cpc)
                       +(CPC_y_df.loc[i, isotopes]-interp_blank_cpc_y)))
        
        neff_rsd=neff**-0.5
        neffbc_rsd=neffbc**-0.5
        
        theo_R_rsd=(neff_rsd**2+flick**2)**0.5
        theo_Rbc_rsd=(neffbc_rsd**2+flick**2)**0.5
        theo_R_rse=theo_R_rsd/c4/numrepeats**0.5
        theo_Rbc_rse=theo_Rbc_rsd/c4/numrepeats**0.5
        
        
        
        #Brkt 1 R    
        neff=((CPC_df.loc[brkt_r[0], isotopes]*CPC_y_df.loc[brkt_r[0], isotopes])
              / (CPC_df.loc[brkt_r[0], isotopes]+CPC_y_df.loc[brkt_r[0], isotopes]))
           
        interp_blank_cpc=(CPC_df.loc[blk_r[0], isotopes]*(1-Dts1b)
                          +CPC_df.loc[blk_r[1], isotopes]*Dts1b)
        interp_blank_cpc_y=(CPC_y_df.loc[blk_r[0], isotopes]*(1-Dts1b)
                          +CPC_y_df.loc[blk_r[1], isotopes]*Dts1b)    
        
        neffbc=(((CPC_df.loc[brkt_r[0], isotopes]-interp_blank_cpc)
                 *(CPC_y_df.loc[brkt_r[0], isotopes]-interp_blank_cpc_y))
              / ((CPC_df.loc[brkt_r[0], isotopes]-interp_blank_cpc)
                       +(CPC_y_df.loc[brkt_r[0], isotopes]-interp_blank_cpc_y)))
            
        neff_rsd_s1=neff**-0.5
        neffbc_rsd_s1=neffbc**-0.5
        
        theo_R_rsd_s1=(neff_rsd**2+flick**2)**0.5
        theo_Rbc_rsd_s1=(neffbc_rsd**2+flick**2)**0.5
        
        
        
        
        
        
        
        #Brkt 2 R   
        neff=((CPC_df.loc[brkt_r[1], isotopes]*CPC_y_df.loc[brkt_r[1], isotopes])
              / (CPC_df.loc[brkt_r[1], isotopes]+CPC_y_df.loc[brkt_r[1], isotopes]))
            
        interp_blank_cpc=(CPC_df.loc[blk_r[0], isotopes]*(1-Dts2b)
                          +CPC_df.loc[blk_r[1], isotopes]*Dts2b)
        interp_blank_cpc_y=(CPC_y_df.loc[blk_r[0], isotopes]*(1-Dts2b)
                          +CPC_y_df.loc[blk_r[1], isotopes]*Dts2b)
           
        neffbc=(((CPC_df.loc[brkt_r[1], isotopes]-interp_blank_cpc)
                 *(CPC_y_df.loc[brkt_r[1], isotopes]-interp_blank_cpc_y))
              / ((CPC_df.loc[brkt_r[1], isotopes]-interp_blank_cpc)
                       +(CPC_y_df.loc[brkt_r[1], isotopes]-interp_blank_cpc_y)))   
        
        neff_rsd_s2=neff**-0.5
        neffbc_rsd_s2=neffbc**-0.5
        
        theo_R_rsd_s2=(neff_rsd**2+flick**2)**0.5
        theo_Rbc_rsd_s2=(neffbc_rsd**2+flick**2)**0.5
          
        
        theo_B_rsd=(theo_R_rsd**2
                    +(Dts*theo_R_rsd_s2)**2
                    +((Dts-1)*theo_R_rsd_s1)**2)**0.5
        
        theo_Bbc_rsd=(theo_Rbc_rsd**2
                    +(Dts*theo_Rbc_rsd_s2)**2
                    +((Dts-1)*theo_Rbc_rsd_s1)**2)**0.5
        
        theo_B_rse=theo_B_rsd/c4/numrepeats**0.5
        theo_Bbc_rse=theo_Bbc_rsd/c4/numrepeats**0.5
        
    
        theo_R_rse_df.loc[i, sing_isos]=theo_R_rse[sing_isos]
        theo_Rbc_rse_df.loc[i, sing_isos]=theo_Rbc_rse[sing_isos]
        theo_B_rse_df.loc[i, sing_isos]=theo_B_rse[sing_isos]
        theo_Bbc_rse_df.loc[i, sing_isos]=theo_Bbc_rse[sing_isos]
        
        


        
        
        
        
        
    
#calibration (cali curve)   
if calistyle=='Calibration curve':
    #make a df of known standard values
    stnd_array=np.empty((0, len(curve_isos)))  
    stnd_df=Run_df.loc[calindx]
    for c in calindx:
        s_array=np.array(stnd_dict[Run_df.loc[c, 'sample_name']]).T
        stnd_array=np.append(stnd_array, s_array, axis=0)    
    stnd_df[curve_isos]=stnd_array
    
    
    #Remove bracketing standards that exhibit different PA
    
    for iso in PA_bracket_bad_index.keys():
        idx=np.intersect1d(stnd_df.index.values, PA_bracket_bad_index[iso])
        if len(idx)>0:
            stnd_df.loc[idx, iso]=np.nan
    
    
    #make dataframes containing information from the calibration curve fit
    #including: x values, y values, r_sq, fit parameters
    caliy=stnd_df.copy()
    
    params_df=pd.DataFrame(np.full((len(brkt_smpl_df)*3+5,
                                    brkt_smpl_df.shape[1]),np.nan), 
                           columns=[brkt_smpl_df.columns])
    
    
    
    caliy=['Calibrant_y_'+str(x) for x in np.arange(len(stnd_df))+1]
    calix=['Calibrant_x_'+str(x)  for x in np.arange(len(stnd_df))+1]
    weightx=['Weight_x_'+str(x)  for x in np.arange(len(stnd_df))+1]
    paramnames=['r_sq', 'beta0', 'beta0_1se' , 'beta1', 'beta1_1se']
        
    #collect the fit params and variables in one df
    params_df=params_df.reindex(caliy+calix+weightx+paramnames)   
    params_df.loc[caliy, stnd_df.columns]=np.array(stnd_df)
    params_df.loc[calix, stnd_df.columns]=np.array(
        brkt_smpl_df.loc[calindx, stnd_df.columns])
    params_df.loc[weightx, Run_df.columns]=np.array(Run_df.loc[calindx])
    
    brkt_cali_df=brkt_smpl_df.loc[calindx]
    
    nanarray=np.full((len(calindx),len(curve_isos)),np.nan)
    fitted_df=pd.DataFrame(nanarray, columns=curve_isos)
    
    #perform the cali curve
    for i, iso in enumerate(curve_isos):
       #get the bracketed values of the calibration standards
        brktiso_arr=np.array(brkt_smpl_df.loc[calindx, iso])
        #and their SEs
        brktiso_se_arr=np.array(brkt_smpl_se_df.loc[calindx, iso], 
                                dtype=np.float64)
        
        #assign the true values to an array
        stndiso_arr=np.array(stnd_df[iso])
        
        #determine weights based on SE
        w=1/brktiso_se_arr**2
        
        #Reshape and add intercept to bracketed values
        X=brktiso_arr
        Xwint=np.empty(shape=(len(X), 2), dtype=np.float64)
        Xwint[:,0]=1
        Xwint[:, 1]=X
        
        
        #reshape true values
        Y=stndiso_arr.reshape(-1, 1)
        
        #put the weights into the df for storage
        params_df.loc[weightx, iso]=w
        
        #boolean array indicating what standards are missing
        missindx=~pd.isna(Y).flatten()
        #Remove any NaN's from the two variables
        Xwint=Xwint[missindx]
        w=w[missindx]
        
        Y=Y[missindx]
        
        
        #Perform weighted least squares
        mdl = sm.WLS(Y, Xwint, weights=w)
        res_wls = mdl.fit()
        
        #get R-squared of WLS
        r_sq = res_wls.rsquared
        #get parameters and their SEs of WLS (0 = intercept, 1 = slope)
        params=res_wls.params 
        params_se=res_wls.bse 
        

        #put the fit params into the df for storage
        params_df.loc[paramnames, iso]=[
            r_sq, params[0], params_se[0], params[1], params_se[1]]
        
        
        fitted_df.loc[missindx, iso]=res_wls.fittedvalues
        
        #Apply regression to samples.
        cali_curv_df[iso]=brkt_smpl_df[iso]*params[1]+params[0]
        #propagate uncertainty
        cali_curv_se_df[iso]=(((brkt_smpl_se_df[iso]/brkt_smpl_df[iso])**2 
            + (params_se[1]/params[1])**2)*(brkt_smpl_df[iso]*params[1])**2
                              +params_se[0]**2)**0.5
        

    #User remove data points from the calibration curves    
    decali=pyg.pickfig_cross(stnd_df, brkt_cali_df, curve_isos, 
                         title='Remove outliers', fitted=fitted_df)
    
    #If any data points were clicked, perform the calibration again
    if any(np.array([True for k in decali.keys() if decali[k].size>0])):
                       
       #perform the cali curve
       for i, iso in enumerate(curve_isos):
           
           stnd_df.loc[decali[iso], iso]=np.nan
           
           
          #get the bracketed values of the calibration standards
           brktiso_arr=np.array(brkt_smpl_df.loc[calindx, iso])
           #and their SEs
           brktiso_se_arr=np.array(brkt_smpl_se_df.loc[calindx, iso], 
                                   dtype=np.float64)
           
           #assign the true values to an array
           stndiso_arr=np.array(stnd_df[iso])
           
           #determine weights based on SE
           w=1/brktiso_se_arr**2
           
           #Reshape and add intercept to bracketed values
           X=brktiso_arr
           Xwint=np.empty(shape=(len(X), 2), dtype=np.float64)
           Xwint[:,0]=1
           Xwint[:, 1]=X
           
           
           #reshape true values
           Y=stndiso_arr.reshape(-1, 1)
           
           #put the weights into the df for storage
           params_df.loc[weightx, iso]=w
           
           #boolean array indicating what standards are missing
           missindx=~pd.isna(Y).flatten()
           #Remove any NaN's from the two variables and weights
           Xwint=Xwint[missindx]
           w=w[missindx]          
           Y=Y[missindx]
           
           
           #Perform weighted least squares
           mdl = sm.WLS(Y, Xwint, weights=w)
           res_wls = mdl.fit()
           
           #get R-squared of WLS
           r_sq = res_wls.rsquared
           #get parameters and their SEs of WLS (0 = intercept, 1 = slope)
           params=res_wls.params 
           params_se=res_wls.bse 
           
     
           #put the fit params into the df for storage
           params_df.loc[paramnames, iso]=[
               r_sq, params[0], params_se[0], params[1], params_se[1]]
           
           
           fitted_df.loc[missindx, iso]=res_wls.fittedvalues
           
           #Apply regression to samples.
           cali_curv_df[iso]=brkt_smpl_df[iso]*params[1]+params[0]
           #propagate uncertainty
           cali_curv_se_df[iso]=(((brkt_smpl_se_df[iso]/brkt_smpl_df[iso])**2 
               + (params_se[1]/params[1])**2)*cali_curv_df[iso]**2
                                 +params_se[0]**2)**0.5 
           
           
           
           

    
#calculate the LoD using each blank (Blank equivalent concentration)
#blank CPS + 3*blankCPS_1sd as a fraction of the bracketing standard CPS
beclist=[]       
for blk in blkrows:
       
    blankcps=CPSmean_df.loc[blk, isotopes]
    
    
    #find closest bracketing standard(s)
    #Make an array where the first row is the run positions of the closest 
    #bracketing standards
    #The second row is the absolute distance between the sample and the 
    #bracketing standard given in row 1
    brktorder=np.vstack((brktrows, np.abs(brktrows-blk)))
    #The third row is the distance between the sample and standard with the
    #sign maintained to help determine whether they are 'bracketed'
    brktorder=np.vstack((brktorder, brktrows-blk))
    #order the columns w.r.t the absolute distance
    brktorder = brktorder[:, np.argsort(brktorder[1,:], axis=0)]
    #If sample is before or after all stnds, use just one closest stnd
    if np.all(brktrows-blk>=0) or np.all(brktrows-blk<=0) or any(brktrows-blk==0):
        brkt_r=np.array([brktorder[0, 0],brktorder[0, 0]])
    #Otherwise use the two closest (braketing standards)
    #If the first stnd is before the sample in the run find one after
    elif brktorder[2, 0]<0:
        #get the next nearest stnd that is of opposite sign direction away
        brk2=brktorder[0, np.where(brktorder[2, 1:]>0)[0][0]+1]          
        brkt_r=np.array([brktorder[0, 0], brk2])
    #otherwise find a stnd before the sample
    else:
        brk2=brktorder[0, np.where(brktorder[2, 1:]<0)[0][0]+1]          
        brkt_r=np.array([brk2,brktorder[0, 0]])
    
    
    #Assign fractional distance between bracketing standards
    if brkt_r[0]==brkt_r[1]:
        Dts=0
    else:
        Dts=(Run_df.loc[blk, 'session_time']-Run_df.loc[brkt_r[0], 'session_time'])/(
            Run_df.loc[brkt_r[1], 'session_time']-Run_df.loc[brkt_r[0], 'session_time'])    
    

    #determine the interpolated standard value
    s1=blkcorr_df.loc[brkt_r[0], isotopes]
    s2=blkcorr_df.loc[brkt_r[1], isotopes]
    s_brkt=s2*Dts+s1*(1-Dts)  
    
    #blank equivalent concentration
    bec=(blankcps[pyg.contains1d(isotopes, sing_isos)]/s_brkt[pyg.contains1d(isotopes, sing_isos)]
             *np.squeeze(cali_array))
    
    beclist.append(bec)
    
    
#Calculate the LoD    
becarray=np.array(beclist, dtype=float)
LoDlist=[]
for col in becarray.T:
    outs=pyg.outsbool(col)
    outs=np.isnan(col) | outs
    LoDlist.append(col[np.where(~outs)].mean()+3*col[np.where(~outs)].std())

LoD_sing=np.array(LoDlist)        



#Calculate LoD relative to bracketing standard(s)
LoDstack=LoD_sing.copy()
for brkt in pd.unique(Run_df.loc[brktrows, 'sample_name']):
    brkt_pcntLoD=LoD_sing/np.array(stnd_dict[brkt]).flatten()*100
    LoDstack=np.vstack((LoDstack, brkt_pcntLoD))

LoDnames='mean LoD'
LoDnames=[[LoDnames]+['% of '+name] for name in pd.unique(Run_df.loc[brktrows, 
                                                           'sample_name'])][0]  
    
#make the LoD dataframe
LoD_df=pd.DataFrame()
LoD_df['Type']=LoDnames

nanarray=np.full((len(LoDstack),len(isotopes)),np.nan)
LoD_df[isotopes]=nanarray
LoD_df[sing_isos]=LoDstack    


#make the covariance dataframe
cov_run_df=pd.concat([Run_df, cov_df], axis=1)   

#Get the name of the bracketing standard
commonbrkt=Run_df.loc[brktrows, 'sample_name'].value_counts().index[0]
brktname=stnd_dict[commonbrkt].columns[0]    

#############Long-term precision#############

#Make the long-term precision dataframe
ltp_df=pd.DataFrame()

if os.path.exists(archivepath):

    #User choose which standards to get long-term precision data for
    stndnamearray=np.append(np.array(stndval_names), 'None')
    stndbool=np.array([])
    stndbool=pyg.fancycheckbox(
        stndnamearray, title=("Include long-term precision data?"))
    if len(stndbool)>0:
        stndlistchoice=stndnamearray[stndbool]
    else:
        stndlistchoice=None
    
    

    #Continue if any standards were selected by user
    if np.all(stndlistchoice!=None):
        #get the archive data from chosen stnds that uses the same brkt stnd 
        cs_all_df=archive_df.loc[(pyg.contains1d(archive_df['sample_name'], stndlistchoice))
                                & (archive_df['brkt_stnd']==brktname)] 
        

        #Need to cycle through elements and standards to remove outliers
        for iso in sing_isos:  
            iso_df=cs_all_df.loc[cs_all_df['isotope_gas']==iso]
            for cs in stndlistchoice:
                        
                cs_df=iso_df.loc[iso_df['sample_name'].str.contains(cs, case=False)]                                  
                cs_sing=cs_df['cali_single']
                cs_curv=cs_df['cali_curve']
                
                if len(cs_sing)<2:
                    continue
                
                #Remove outliers
                sing_outs=pyg.outsbool(np.array(cs_sing))
                sing_std=cs_sing[~sing_outs].std()*2
                sing_m=cs_sing[~sing_outs].mean()
                sing_rsd=sing_std/sing_m*100
                sing_n=sum(~np.isnan(cs_sing[~sing_outs]))
                
                curv_std=np.nan
                curv_m=np.nan
                curv_rsd=np.nan
                curv_n=sum(~np.isnan(cs_curv))
                if curv_n>2:            
                    curv_outs=pyg.outsbool(np.array(cs_curv))
                    curv_std=cs_curv[~curv_outs].std()*2
                    curv_m=cs_curv[~curv_outs].mean()
                    curv_rsd=curv_std/curv_m*100
                    curv_n=sum(~np.isnan(cs_curv[~curv_outs]))
                
                #Add in the expected values from the stnd_vals.csv
                expect=calivals_df.loc[iso, cs]
                    
                #Within-run data
                
                #Find the stnd in the run
                sing_run=cali_sing_df.loc[pyg.contains1d(Run_df['sample_name'], 
                                                    cs), iso].values
                sing_run_m=sing_run.mean()
                sing_run_1se=cali_sing_se_df.loc[pyg.contains1d(Run_df['sample_name'], 
                                                    cs), iso].values
                sing_run_2se_m=sing_run_1se.mean()*2
                sing_run_std=np.nan
                if len(sing_run)>2:
                    outs=pyg.outsbool(sing_run)
                    sing_run_std=sing_run[~outs].std()*2
                    sing_run_m=sing_run[~outs].mean()
                    sing_run_2se_m=sing_run_1se[~outs].mean()
                
                
                if calistyle=='Calibration curve':
                    curv_run=cali_curv_df.loc[pyg.contains1d(Run_df['sample_name'], 
                                                        cs), iso].values
                    curv_run_m=sing_run.mean()
                    curv_run_1se=cali_curv_se_df.loc[pyg.contains1d(Run_df['sample_name'], 
                                                        cs), iso].values
                    curv_run_2se_m=curv_run_1se.mean()*2
                    curv_run_std=np.nan
                    if sum(~np.isnan(curv_run))>2:
                        outs=pyg.outsbool(curv_run)
                        curv_run_std=curv_run[~outs].std()*2
                        curv_run_m=curv_run[~outs].mean()
                        curv_run_2se_m=curv_run_1se[~outs].mean()*2
                else:
                    curv_run_m=np.nan
                    curv_run_2se_m=np.nan
                    curv_run_std=np.nan
                    
                
                
                
                #Put all the data together
                cols=['stnd', 'isotope_gas', 'units', 'expected', 'Archive S-P mean', 
                        'Archive S-P 2sd', 'Archive S-P %2rsd', 'Archive S-P n',
                        'Run S-P mean', 'Run S-P 2se (mean)', 'Run S-P 2sd',                
                        'Archive curve mean', 'Archive curve 2sd' , 
                        'Archive curve %2rsd', 'Archive curve n', 
                        'Run curve mean', 'Run curve 2se (mean)', 'Run curve 2sd',]   
                var_list=[cs, iso, cs_df['units'].iloc[0], expect, sing_m, sing_std, 
                        sing_rsd, sing_n, 
                        sing_run_m, sing_run_2se_m, sing_run_std,
                        curv_m, curv_std, curv_rsd,curv_n, 
                        curv_run_m, curv_run_2se_m, curv_run_std]
                
                    
                temp_dict=dict(zip(cols, var_list))    
                        
                ltp_df=pd.concat([ltp_df, pd.DataFrame(temp_dict, index=[0])])      
            

        ltp_df=ltp_df.reset_index(drop=True)





indexes_df=pd.concat((Run_df, pd.DataFrame(indexes_dict)), axis=1)


#make units for the headings of the excel output
unit_dict={}
for iso in sing_isos:    
    unit_dict[iso]=iso+' ('+calivals_df.loc[iso, 'Units']+')'



############# Export data ###############
   
savepath=folder_select+'/Pygilent_out/'
isExist = os.path.exists(savepath)

if not isExist:
    os.makedirs(savepath)
    
savename=pyg.textinputbox(title="Enter save name")
#add a timestamp to the filename to reduce risk of accidental data overwrite
tstamp=str(round(time.time()))


#Write short output 
with pd.ExcelWriter(savepath+savename +'_short_'+ tstamp +'.xlsx') as writer:
    rep_cps_long_df.to_excel(writer, sheet_name='Reps')
    CPSmean_df.to_excel(writer, sheet_name='CPS')
    CPSstd_df.to_excel(writer, sheet_name='CPS_1sd')    

    if calistyle=='Calibration curve':
        #change column names to include units
        cali_curv_df_wunits=cali_curv_df.rename(unit_dict, axis=1)
        cali_curv_se_df_wunits=cali_curv_se_df.rename(unit_dict, axis=1)
        #export
        cali_curv_df_wunits.to_excel(writer, sheet_name='Cali')
        cali_curv_se_df_wunits.to_excel(writer, sheet_name='Cali_1se')
    else:
        #change column names to include units
        cali_sing_df_wunits=cali_sing_df.rename(unit_dict, axis=1)
        cali_sing_se_df_wunits=cali_sing_se_df.rename(unit_dict, axis=1)
        #export
        cali_sing_df_wunits.to_excel(writer, sheet_name='Cali')
        cali_sing_se_df_wunits.to_excel(writer, sheet_name='Cali_1se')
        
#Write long output      
with pd.ExcelWriter(savepath+savename +'_full_'+ tstamp +'.xlsx') as writer:
    rep_cps_long_df.to_excel(writer, sheet_name='Reps')
    CPSmean_df.to_excel(writer, sheet_name='CPS')
    CPSstd_df.to_excel(writer, sheet_name='CPS 1sd')
    PA_df.to_excel(writer, sheet_name='PA')
    cov_run_df.to_excel(writer, sheet_name='Covar')  
    indexes_df.to_excel(writer, sheet_name='indexes')  
    ratio_smpl_df.to_excel(writer, sheet_name='R')  
    ratio_smpl_se_df.to_excel(writer, sheet_name='R 1se')  
    brkt_smpl_df.to_excel(writer, sheet_name='Bracket')  
    brkt_smpl_se_df.to_excel(writer, sheet_name='Bracket 1se')  
    
    #change column names to include units
    cali_sing_df_wunits=cali_sing_df.rename(unit_dict, axis=1)
    cali_sing_se_df_wunits=cali_sing_se_df.rename(unit_dict, axis=1)
    LoD_df_wunits=LoD_df.rename(unit_dict, axis=1)
    #export
    cali_sing_df_wunits.to_excel(writer, sheet_name='S-P cali')
    cali_sing_se_df_wunits.to_excel(writer, sheet_name='S-P cali 1se')
    
    if calistyle=='Calibration curve':
        #change column names to include units
        cali_curv_df_wunits=cali_curv_df.rename(unit_dict, axis=1)
        cali_curv_se_df_wunits=cali_curv_se_df.rename(unit_dict, axis=1)
        #export
        cali_curv_df_wunits.to_excel(writer, sheet_name='Curve cali')
        cali_curv_se_df_wunits.to_excel(writer, sheet_name='Curve cali 1se')
        params_df.to_excel(writer, sheet_name='Curve params')
    LoD_df.to_excel(writer, sheet_name='LoD')
    if len(ltp_df)>0:
        ltp_df.to_excel(writer, sheet_name='Long-term precision')
    
    theo_R_rse_df.to_excel(writer, sheet_name='theo R rse')
    theo_Rbc_rse_df.to_excel(writer, sheet_name='theo Rbc rse')
    theo_B_rse_df.to_excel(writer, sheet_name='theo B rse')
    theo_Bbc_rse_df.to_excel(writer, sheet_name='theo Bbc rse')
    
            







################## Format data for archiving#############
Run_df['run_order']=np.arange(len(Run_df))+1
repCPS_all_df=pd.concat((Run_df, repCPS_all_df), axis=1)



#Melt all the data into a single dataframe
idcols=Run_df.columns

df_list=[CPSmean_df, CPSstd_df, ratio_smpl_df, ratio_smpl_se_df, 
         brkt_smpl_df, brkt_smpl_se_df, cali_sing_df, cali_sing_se_df, PA_df]
val_names=['cps_mean', 'cps_sd', 'ratio', 'ratio_se', 'brkted', 'brkted_se', 
           'cali_single', 'cali_single_se', 'PA']

Melt_df=repCPS_all_df.melt(id_vars=idcols, value_vars=isotopes, var_name='isotope_gas', 
                            value_name='cps_reps')

for df, val_name in zip(df_list, val_names):
    Melt_df[['isotope_gas', val_name]]=df.melt(
        value_vars=isotopes, var_name='isotope_gas', value_name=val_name)

Melt_df['brkt_stnd']=brktname


#create a dict of integration times and gas modes 
#so they can be added to the final data
gasmode_dict=dict(zip(isotopes, Gasmodes))  
for iso in isotopes:
    Melt_df.loc[Melt_df['isotope_gas']==iso,'lod']=float(
        LoD_df.loc[0,iso])
    Melt_df.loc[Melt_df['isotope_gas']==iso,'gas_mode']=gasmode_dict[iso]
    Melt_df.loc[Melt_df['isotope_gas']==iso,'int_time']=inttime_dict[iso]
    Melt_df.loc[Melt_df['isotope_gas']==iso, 'n']=rep_cps_long_df.loc[
        rep_cps_long_df['isotope_gas']==iso, 'rep_num'].values

for k in ratioels.keys():
    Melt_df.loc[Melt_df['gas_mode']==k,'Ratio iso']=ratioels[k]

for iso in calivals_df.index:
    Melt_df.loc[Melt_df['isotope_gas']==iso,'units'
                   ]=calivals_df.loc[iso, 'Units']
    


if calistyle=='Calibration curve':
    Melt_df[['isotope_gas', 'cali_curve']]=cali_curv_df.melt(
        value_vars=isotopes, var_name='isotope_gas', value_name='cali_curve')
    Melt_df[['isotope_gas', 'cali_curve_se']]=cali_curv_se_df.melt(
        value_vars=isotopes, var_name='isotope_gas', value_name='cali_curve_se')     
    for iso in isotopes:
        Melt_df.loc[Melt_df['isotope_gas']==iso,'r_sq']=float(
            params_df.loc['r_sq', iso])
        Melt_df.loc[Melt_df['isotope_gas']==iso,'beta0']=float(
            params_df.loc['beta0', iso])
        Melt_df.loc[Melt_df['isotope_gas']==iso,'beta0_se']=float(
            params_df.loc['beta0_1se', iso])
        Melt_df.loc[Melt_df['isotope_gas']==iso,'beta1']=float(
            params_df.loc['beta1', iso])
        Melt_df.loc[Melt_df['isotope_gas']==iso,'beta1_se']=float(
            params_df.loc['beta1_1se', iso])











###################Figures###########

answer = tk.messagebox.askyesno(title=None, message='Make figures?')

if answer:
    
    figlist=np.array(['Blanks CPS'] + list(stndval_names))
    figlistchoice=figlist[pyg.fancycheckbox(figlist, 
                                        title=("Select figures to draw"))]
    
    figpath=savepath+'/figures'
    isExist = os.path.exists(figpath)
    
    if not isExist:
        os.makedirs(figpath)
    
    
    for f in figlistchoice:    
        if f == 'Blanks CPS':
            df1=archive_df.loc[pyg.contains1d(archive_df['sample_type'], 'blank')]
            df2=Melt_df[pyg.contains1d(Melt_df['sample_type'], 'blank')]
            pyg.blankfigsaver(df1, df2, isotopes, figpath=figpath)
        else:
            df1=archive_df.loc[pyg.contains1d(archive_df['sample_name'], str(f))]
            df2=Melt_df[pyg.contains1d(Melt_df['sample_name'], str(f))]
            expected=calivals_df[f]  
                
            pyg.stdfigsaver(df1, df2, f, sing_isos, expected, figpath=figpath)        
    


if os.path.exists(archivepath):
    #Is the run already present in the archive data? 
    #If yes, ask whether the user wants to replace the existing data. 
    #If no, the data is not saved
    if any(archive_df['run_name']==Melt_df['run_name'][0]):
        answer = tk.messagebox.askyesno(title=None, 
                                        message='Overwrite data in archive?')
        if answer:
            archive_df=archive_df.loc[archive_df['run_name']!=Melt_df['run_name'][0]]
            archive_df=pd.concat([archive_df, Melt_df], ignore_index=True)
            archive_df.to_csv(archivepath)
    else:
        archive_df=pd.concat([archive_df, Melt_df], ignore_index=True)
        archive_df.to_csv(archivepath)
else:
    #If the archive doesn't already exist, then start one with this run
    Melt_df.to_csv(archivepath)



#Finished message box
tk.messagebox.showinfo("", "Processing complete")