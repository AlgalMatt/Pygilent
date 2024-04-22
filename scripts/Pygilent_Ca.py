import os
import pandas as pd
import numpy as np
from tkinter import filedialog
import tkinter as tk
import csv
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter.scrolledtext import ScrolledText

####### Functions ################
#function for finding occurrences of substring (or a selection of substrings) 
#within an array of strings
def contains1d(array1, string1, ret_array=True, case_sensitive=False):
    """
    Looks for occurrences of substring(s) within an array of strings, returning
    a boolean array. This is essentially the Pandas series.str.contains method, 
    but slightly adapted.
    
    Parameters
    ----------
    array1 : 1d array (list, numpy array)
        array to search.
    string1 : string, or 1d array of strings (list or numpy array)
        substrings used to search for within array1.
    ret_array : boolean, optional
        If true, then the output will be a 1d array of the same size as array1, 
        providing True/False values for each element that contains/does not 
        contain any of the substrings within string1. 
        If false, then the output will be a matrix of len(array1) by
        len(string1) with each column being a separate boolean array of 
        occurrences of each substring in string1 within array1.
        The default is True.
    case_sensitive : boolean, optional
        If true, the search will be case-sensitive. The default is False.

    Returns
    -------
    retarray : numpy array or matrix of len(array1)
        An array of boolean values where True values indicate the presence of the 
        substring, string1, at the same index of array1. An element-wise 
        string1 in array1.

    """
    
    #vectorize lower cases
    nlower=np.vectorize(str.lower)
    
    retarray=[]
    #if argument string1 is a single string
    if type(string1)==str:
        #lower all cases
        if case_sensitive==False:
            array1=nlower(array1)
            string1=string1.lower()
        for i in array1:
            retarray.append(string1 in i)   
    #if string1 is a list of strings             
    else:
        #lower all cases
        if case_sensitive==False:
            array1=nlower(array1)
            string1=nlower(string1)
        retarray=np.full((len(array1), len(string1)), False)
        #iterate over the list of substrings
        for j, s in enumerate(string1):
            #iterate over the array of strings a check if the iterated 
            #substring is in it            
            for i, a in enumerate(array1):
                retarray[i, j]=s in a
        #if true, return a 1D array, else it returns a len(array1) by 
        #len(string1) matrix of occurrences of each substring within the array
        if ret_array:
            retarray=np.any(retarray, axis=1)           
    return retarray




def fancycheckbox(items,  title="", defaults=None, single=False):
    """    
    Creates a pop-up simple checkbox from a list of items. Returns indexes of 
    the checked items.

    Parameters
    ----------
    items : 1d array (list or numpy array)
        list of items to fill the checkbox.
    title : string, optional
        Descriptive title of the checkbox window. The default is "".
    defaults : boolean array, optional
        Indexes which items to have check boxes ticked by default. 
        The default is None.
    single : boolean, optional
        If true, only one checkbox can be selected. The default is False.

    Returns
    -------
    selected_indexes : numpy.array
        array of indexes of checked items.

    """
    global selected
    #if no defaults used, create a list of False to implement defaults.
    if defaults is None:
        defaults=[False]*len(items)
    # Create the main window
    window = tk.Tk()
    window.title(title)
    #Keep the window at the front of other apps.
    window.lift()
    window.attributes("-topmost", True)
    
    
    w = 400 # width for the Tk root
    h = 700 # height for the Tk root
    
    # get screen width and height
    ws = window.winfo_screenwidth() # width of the screen
    hs = window.winfo_screenheight() # height of the screen
    
    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    
    # set the dimensions of the screen 
    # and where it is placed
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
    #make sure scrolling area always fills the window area
    window.rowconfigure(1, weight=1)
    window.columnconfigure(0, weight=1)
    
    # Create a list of booleans to store the state of each checkbox
    selected = defaults
    
    # Function to update the list of selected items
    def update_selected(var):
        global selected        
        if single:
            for i in range(len(cb_vars)):
                if i != var:
                    cb_vars[i].set(False)
                    cb_list[i]['bg']='white'
        selected = [cb_vars[i].get() for i in range(len(cb_vars))]
        if cb_vars[var].get():
            cb_list[var]['bg']='yellow'
        else:
            cb_list[var]['bg']='white'
    

    
    # Create a list to store the checkbox variables
    cb_vars = []
       
    #The title of the window
    label=tk.Label(window, text=title, font=("Helvetica", 14))
    label.grid(row=0, column=0, pady=5)
    
    textframe=ScrolledText(window, width=40, height=50)
    textframe.grid(row=1, column=0, sticky='ewns')
    cb_list=[]
    # Create a 4-column grid of checkboxes
    for i, item in enumerate(items):
        cb_var = tk.BooleanVar()
        cb = tk.Checkbutton(textframe, text=item, variable=cb_var,
                            command=lambda var=i: update_selected(var), 
                            font=("Arial",10),fg="black", bg="white")
        
        cb_list.append(cb)
        textframe.window_create('end', window=cb)
        textframe.insert('end', '\n')
        cb_vars.append(cb_var)
        if defaults[i]:
            cb.select()
            cb['bg']='yellow'

    # Create a "Submit" button
    submit_button = tk.Button(window, text="Submit", command=lambda: window.destroy())
    submit_button.grid(row=2, column=0)
    
    # Run the main loop
    window.mainloop()
    selected_indexes = np.array([i for i, x in enumerate(selected) if x])
    return selected_indexes






#function for calling unique values with order retained.
def unique(list1):
    array1=np.array(list1)
    indx=np.unique(array1, return_index=True)[1]
    indx.sort()
    uarray=array1[indx]
    return uarray



#Enter name for file
def textinputbox(title=""):
    #setup the window
    root=tk.Tk()
    
    w = 200 # width for the Tk root
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
    
    #make sure scrolling area always fills the window area
    root.rowconfigure(1, weight=3)
    root.rowconfigure(0, weight=2)
    root.columnconfigure(0, weight=1)
    
    #The title of the window
    label=tk.Label(root, text=title, font=("Helvetica", 14))
    label.grid(row=0, column=0, pady=5)
    
    #Button function that saves input value and closes the window
    def retrieve_input():
        global inputValue
        inputValue=textBox.get("1.0","end-1c")
        root.destroy()
    #Text input
    textBox=tk.Text(root, height=2, width=10)
    textBox.grid(row=1, column=0, sticky='ewns')
    #Save button (see function above)
    buttonSave=tk.Button(root, height=1, width=10, text="Save", 
                        command=lambda: retrieve_input())
    buttonSave.grid(row=2, column=0)  
    
    tk.mainloop()   
    return inputValue   


#Ca data entry
def Cacheckinput(labels, defaults):
    root=tk.Tk()
    
    w = 700 # width for the Tk root
    h = 500 # height for the Tk root
    
    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen
    
    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    
    # set the dimensions of the screen 
    # and where it is placed
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
    #make sure scrolling area always fills the window area
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)
    root.rowconfigure(3, weight=1)
    root.rowconfigure(4, weight=1)
    root.rowconfigure(5, weight=1)
    root.columnconfigure(0, weight=1)   
    root.columnconfigure(1, weight=1)   
    
    def save_entries():
        global entries
        entries=[]
        for ent in entrylist:
            entries.append(ent.get())
        
       
        entries=np.array(entries)
        entries=entries.astype(float)
        root.destroy()
        
    # Create the main window
    root.title("Enter sample prep and target conc data",)
    
    # Create and place labels
    
    for i, label_text in enumerate(labels):
        label = tk.Label(root, text=label_text)
        label.grid(row=i, column=0, padx=10, pady=10, sticky='ens')
    
    
    
    # Create and place text entry boxes
    entrylist=[]
    for i, lab in enumerate(labels):
        entry=tk.Entry(root)
        entry.grid(row=i, column=1, sticky='wns')
        entry.insert(-1, defaults[i])
        entrylist.append(entry)
    
    
    
    # Create and place a button to save entries
    save_button = tk.Button(root, text="Submit", command=save_entries)
    save_button.grid(row=len(labels)+1, column=0, pady=20, padx=10, 
                     columnspan=2)
    
    # Start the Tkinter event loop
    root.mainloop()  
    return entries    
        



def pickfig(df, xvar, title):
    global selected_ind, variable
    df[xvar]=df[xvar]/3600
    df2=df.copy()
    variable=df.columns[df.columns!=xvar][0]
    selected_ind=np.array([], dtype=int)
          
    def on_pick(event):
        global ind, selected_ind
        ind = event.ind
    
        newind=np.setdiff1d(ind, selected_ind)
        
        if newind.size>0:
            selected_ind=np.append(selected_ind, newind)
            df2.iloc[ind]=np.nan
            scatter2.set_data(df2[xvar], df2[variable])
            fig.canvas.draw_idle()
            
        else:
            selected_ind=np.setdiff1d(selected_ind, ind)
            df2.iloc[ind]=df.iloc[ind]
            scatter2.set_data(df2[xvar], df2[variable])
            fig.canvas.draw_idle()
    
    
 
    # Create the initial plot without showing the figure
    fig, ax = plt.subplots()
    scatter1, = ax.plot([], [], linestyle='None', marker='o', color='red', picker=5)
    scatter2, = ax.plot([], [], linestyle='None', marker='o', color='blue')
    ax.set_xlabel('Analysis time (hours)')
    ax.set_ylabel(variable)
    ax.legend(['Remove', 'Keep'])
    
    
    
    # Register the pick event
    fig.canvas.mpl_connect('pick_event', on_pick)
    
    plt.close(fig)  # Close the figure to prevent it from being displayed
    
    
    # Define the update function for the dropdown
    def update_y_axis(*args):
        global variable
        variable = dropdown_var.get()
        scatter1.set_data(df[xvar], df[variable])
        scatter2.set_data(df2[xvar], df2[variable])
        ax.set_ylabel(variable)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()
    
    # Create the Tkinter window
    window = tk.Tk()
    window.title(title)
    
    
    # Create a label for the dropdown menu
    label = tk.Label(window, text="Choose an isotope")
    label.pack(padx=10, pady=5)
    
    # Create the dropdown menu
    dropdown_var = tk.StringVar(window)
    dropdown_var.set(df.columns[df.columns!=xvar][0])  # Set default value
    dropdown = tk.OptionMenu(window, dropdown_var, *df.columns[df.columns!=xvar], 
                             command=update_y_axis)
    dropdown.pack(padx=10, pady=10)
    
    
    submit_button = tk.Button(window, text="Submit", 
                              command=lambda: window.destroy())
    submit_button.pack( side = tk.BOTTOM)


    
    
    # Create the FigureCanvasTkAgg object
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    # Run the Tkinter event loop
    window.mainloop()
    
    
    return np.array(df.index[selected_ind])



#############Import data #################

#Select directory
root=tk.Tk()
root.withdraw()
root.attributes('-topmost', True)
folder_select=filedialog.askdirectory()
root.destroy()

#reads batch file
folder_list=os.listdir(folder_select)
Batchlogloc=folder_select+'/BatchLog.csv'
batch_raw=pd.read_csv(folder_select+'/BatchLog.csv') 
#convert string dates into datetime
batch_raw["Acq. Date-Time"]=pd.to_datetime(batch_raw["Acq. Date-Time"])
#Remove non-run (errors, restarts etc) rows from raw batch file
batch_t=batch_raw.loc[(batch_raw['Acquisition Result']=='Pass'
                 ) &(batch_raw["Sample Type"].str.contains("Tune")==False)].copy()


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
Run_df=pd.DataFrame(np.repeat(runname, len(batch_t)), columns=['Run Name'])
Run_df=pd.concat([Run_df, batch_t[['Acq. Date-Time', 'Sample Name', 'Vial#']]],
                 axis=1)
Run_df['Elapse']=batch_t['Acq. Date-Time']-batch_t['Acq. Date-Time'][0]

Run_df['Elapse']=Run_df['Elapse'].dt.total_seconds()


#empty dataframes
repCPS_all_df=pd.DataFrame()
repPA_all_df=pd.DataFrame()
repSD_all_df=pd.DataFrame()


#Start iterating through samples
for folder in batch_t['Sample Folder']:
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
            gas_df=pd.read_csv(fileloc, skiprows=list(range(0, 7)), header=0) 
            #remove print info                             
            gas_df=gas_df.drop(gas_df.tail(1).index) 
            #get the current gas mode
            gasmodetxt=testmode[i+j*numrepeats].strip(' ') 
            #Make df of current gas mode
            #Combine mass and element to make isotope column
            gas_df["Isotope_gas"]=gas_df["Element"]+\
                gas_df.iloc[:, 0]+"_"+gasmodetxt 
            gas_df["Gas mode"]=gasmodetxt
                        
            #PA column often wrongly named, so need to rename it.
            #first find the column next to CPS            
            idx=np.where(gas_df.columns == 'CPS')[0]+1
            gas_df['PA']=gas_df.iloc[:, idx]
            #Concat all gas modes of this repeat
            allgas_df=pd.concat([allgas_df, gas_df], ignore_index=True)
        #extract cps, PA and stdev info from all gas modes of this repeat
        listCPS.append((np.array(allgas_df['CPS']))) 
        listPA.append((np.array(allgas_df['PA'])))
        #listSD.append((np.array(allgas_df['SD'])))
    
    #arrays of isotopes and gas modes used
    isotopes=np.array(allgas_df['Isotope_gas'])    
    Gasmodes=np.array(allgas_df['Gas mode']) 
    
    #Create nested list of CPS, PA and stdev replicates
    repCPS=[list(s) for s in np.vstack(listCPS).T]
    repPA=[list(s) for s in np.vstack(listPA).T]
    #repSD=[list(s) for s in np.vstack(listSD).T]
               
    #Form above lists into df
    repCPS_df=pd.DataFrame([repCPS], columns=isotopes)
    repPA_df=pd.DataFrame([repPA], columns=isotopes)
   # repSD_df=pd.DataFrame([repSD], columns=isotopes)
        
    #Concatenate all samples
    repCPS_all_df=pd.concat([repCPS_all_df, repCPS_df], ignore_index=True)       
    repPA_all_df=pd.concat([repPA_all_df, repPA_df], ignore_index=True)  
    #repSD_all_df=pd.concat([repSD_all_df, repSD_df], ignore_index=True) 
   

         
# Add in the info    
repCPS_all_df=pd.concat([Run_df, repCPS_all_df], axis=1)            
repPA_all_df=pd.concat([Run_df, repPA_all_df], axis=1)                 

#Create means and stdevs.
CPSmean=np.array([])
CPSstd=np.array([])
for lab, row in repCPS_all_df.iterrows():    
    bb=np.array([np.array([np.array(b).mean(), np.array(b).std()]) for
                 b in row[isotopes]])
    CPSmean=np.concatenate([CPSmean, bb[:, 0]])
    CPSstd=np.concatenate([CPSstd, bb[:, 1]])
CPSmean=CPSmean.reshape([-1, len(bb)])
CPSstd=CPSstd.reshape([-1, len(bb)])

#Make dataframes
CPSmean_df=pd.DataFrame(CPSmean, columns=isotopes)
CPSstd_df=pd.DataFrame(CPSstd, columns=isotopes)
    
# Add in the info 
CPSmean_df=pd.concat([Run_df, CPSmean_df], axis=1)            
CPSstd_df=pd.concat([Run_df, CPSstd_df], axis=1) 

#Create average P/A table
PAarray=[]
for lab, row in repPA_all_df[isotopes].iterrows(): #iterate over rows of df
    els=np.array(list(row))
    PAlist=[]
    for x in els: #iterate through elements
        if all(x=='P') | all(x=='A'):
            PAlist.append(str(x[0]))
        else:
            PAlist.append('M')
    PAarray.append(PAlist) #list of lists
    
    
PA_df=pd.DataFrame(np.array(PAarray), columns=isotopes) #make the df
PA_df=pd.concat([Run_df, PA_df], axis=1) #add the info



######### Options ########

#Assign default blank indexes based off sample names    
blkdefaults=list(batch_t['Sample Name'].str.contains('blk',
                                                     case=False).astype(int))

#Checkbox for selecting blanks
namelist=[str(i+1)+')  '+s for i, s in enumerate(list(batch_t['Sample Name']))]

blkrows=np.array([])
while blkrows.size<1:
    blkrows=fancycheckbox(namelist, defaults=blkdefaults, 
                          title=("Check the blanks are selected"))


#Figure de-select outlier blanks based of counts
cpsblank=CPSmean_df.loc[blkrows, np.append('Elapse', isotopes)]
deblank=pickfig(cpsblank, 'Elapse', 'Click on blanks to remove outliers')
blkrows=blkrows[~np.in1d(blkrows, deblank)]



#Assign default bracket standard indexes based off sample names    
brktdefaults=list(batch_t['Sample Name'].str.contains('stgfrm',
                                                     case=False).astype(int))

#Use the most-common occurrence of 'STGFrm'
if sum(brktdefaults)>0:
    countbrkt=batch_t.loc[batch_t['Sample Name'].str.contains('stgfrm',case=False), 
            'Sample Name'].value_counts()   
    brktdefaults=batch_t['Sample Name']==countbrkt.index[0]
    brktdefaults=list(brktdefaults.astype(int))



#Checkbox for selecting bracketing standards
brktrows=np.array([])
while brktrows.size<1:
    brktrows=fancycheckbox(namelist, defaults=brktdefaults, 
                       title=("Check the bracketing standards are selected"))


#De-select outlier bracketing standards based of counts
cpsbrkt=CPSmean_df.loc[brktrows, np.append('Elapse', isotopes)]
debrkt=pickfig(cpsbrkt, 'Elapse', 
               'Click on bracketing standards to remove outliers')
brktrows=brktrows[~np.in1d(brktrows, debrkt)]


#Select the concentration isotope(s)
ratioel_default=contains1d(isotopes, 'Ca48')

ratioels=np.array([])
while ratioels.size<1:
    ratioels=isotopes[fancycheckbox(isotopes, defaults=ratioel_default, 
                                 single=False, 
                                 title=("Select isotope of interest (Ca)"))]





#Assign a column that describes the type of sample or standard
#first assign all as 'Sample'
Run_df['Type']=['Sample']*len(Run_df)
#Then assign the blanks
Run_df.loc[blkrows, 'Type']=['Blank_'+str(x) 
                             for x in np.arange(len(blkrows))+1]
#Then the bracketing standards
Run_df.loc[brktrows, 'Type']=['Bracket_'+str(x) 
                             for x in np.arange(len(brktrows))+1]     






#User entry Ca check options

#default values
defaults=['1', '3', '197', '350', '1']        
labels = [
    "Standard conc (mM)",
    "Vol of sample pipetted (ul)",
    "Vol of acid pipetted (ul)",
    "Desired vol (ul)",
    "Desired conc (mM)"
]

entries=Cacheckinput(labels, defaults)
entries_dict=dict(zip(labels, entries))
entries_df=pd.DataFrame(entries_dict, index=[0])
#################Processing ##################

#create array of Ca counts using different gases
y_df=Run_df.copy() #mean Ca cps
s_y_df=Run_df.copy() #sd Ca
repCPS_y_df=Run_df.copy() #replicate Ca cps
    


#Initialise final data frames using an array of NaN values
nanarray=np.full((len(Run_df),len(isotopes)),np.nan)
RunNaN_df=Run_df.copy()
RunNaN_df[isotopes]=nanarray

blkcorr_df=RunNaN_df.copy()
CaConc_df=RunNaN_df.copy()
undiluted_df=RunNaN_df.copy()
VolSmpl_df=RunNaN_df.copy()
VolAcid_df=RunNaN_df.copy()
exPA_df=RunNaN_df.copy()



#Cycle through sample by sample to blank correct then bracket
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
    brktorder=np.vstack((brktrows, np.abs(brktrows-i)))
    brktorder=np.vstack((brktorder, brktrows-i))
    brktorder = brktorder[:, np.argsort(brktorder[1,:], axis=0)]
    #If sample is before or after all stnds, use just one closest stnd
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
     
    
    #Assign fractional distance between two blanks
    if blk_r[0]==blk_r[1]:
        #If not between two blanks, then distance is 0
        Dtb=0
        Dts1b=0
        Dts2b=0
    else:
        #Sample
        Dtb=(row['Elapse']-Run_df.loc[blk_r[0], 'Elapse'])/(
            Run_df.loc[blk_r[1], 'Elapse']-Run_df.loc[blk_r[0], 'Elapse'])
        #Bracketing standard 1
        Dts1b=(Run_df.loc[brkt_r[0], 'Elapse']
               -Run_df.loc[blk_r[0], 'Elapse'])/(
                   Run_df.loc[blk_r[1], 'Elapse']
                   -Run_df.loc[blk_r[0], 'Elapse'])
        #Bracketing standard 2
        Dts2b=(Run_df.loc[brkt_r[1], 'Elapse']
               -Run_df.loc[blk_r[0], 'Elapse'])/(
                   Run_df.loc[blk_r[1], 'Elapse']
                   -Run_df.loc[blk_r[0], 'Elapse'])   
    
    #Assign fractional distance between bracketing standards
    if brkt_r[0]==brkt_r[1]:
        Dts=0
    else:
        Dts=(row['Elapse']-Run_df.loc[brkt_r[0], 'Elapse'])/(
            Run_df.loc[brkt_r[1], 'Elapse']-Run_df.loc[brkt_r[0], 'Elapse'])    
    
    
    #Blank correction
    #Sample
    blkcorr=(row[isotopes]-Dtb*CPSmean_df.loc[blk_r[0], isotopes]
     +CPSmean_df.loc[blk_r[0], isotopes]*(Dtb-1))
    #Standards
    s1=(CPSmean_df.loc[brkt_r[0],isotopes]-Dts1b*CPSmean_df.loc[blk_r[0], isotopes]
     +CPSmean_df.loc[blk_r[0], isotopes]*(Dts1b-1))
    s2=(CPSmean_df.loc[brkt_r[1],isotopes]-Dts2b*CPSmean_df.loc[blk_r[1], isotopes]
     +CPSmean_df.loc[blk_r[1], isotopes]*(Dts2b-1))
    
    blkcorr_brkt=s2*Dts+s1*(1-Dts)
    
    #bracketting  
    brkt_smpl=blkcorr/blkcorr_brkt
    
    #Use given conc value for calibration
    """ entries
   0 "Standard conc (mM)",
   1 "Vol of sample pipetted (ul)",
   2 "Vol of acid pipetted (ul)",
   3 "Desired vol (ul)",
   4 "Desired conc (mM)"
    """
    #convert from object dtype
    brkt_smpl=brkt_smpl.convert_dtypes()
    
    #Calculate pipetting vols
    CaConc_smpl=brkt_smpl*entries[0]
    undiluted_smpl=CaConc_smpl/entries[1]*(entries[2]+entries[1])
    VolSmpl_smpl=entries[3]*entries[4]/undiluted_smpl
    #Adjust pipetting volume so that minimum is 2ul    
    VolSmpl_smpl.loc[VolSmpl_smpl<2]=2
    VolSmpl_smpl=np.round(VolSmpl_smpl, decimals=1)
    VolAcid_smpl=VolSmpl_smpl*undiluted_smpl/entries[4] - VolSmpl_smpl
    VolAcid_smpl=np.round(VolAcid_smpl, decimals=1)

    
    #blkcorr_df=RunNaN_df.copy()
    CaConc_df.loc[i, isotopes]=CaConc_smpl
    undiluted_df.loc[i, isotopes]=undiluted_smpl
    VolSmpl_df.loc[i, isotopes]=VolSmpl_smpl
    VolAcid_df.loc[i, isotopes]=VolAcid_smpl
    
    
    
    #expected PA   
    exPA_ls=np.array(['A']*len(isotopes))    
    exPA_ls[row[isotopes]<1000000]='P'   
    exPA_df.loc[i, isotopes]=exPA_ls



rep_CPS_arr=np.array(repCPS_all_df[isotopes].values.tolist())
rep_CPS_arr_reshaped=np.reshape(rep_CPS_arr, (-1, numrepeats))

s_names=[y for x in Run_df['Sample Name'].values for y in [x]*len(isotopes)]
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
rep_cps_long_df['rep_list']=rep_cps_long_df[repnames].apply(list, axis=1)
rep_cps_long_df['cps_mean']=np.nanmean(rep_cps_long_df[repnames], axis=1)
rep_cps_long_df['cps_std']=np.nanstd(rep_cps_long_df[repnames], axis=1, ddof=1)


## FIX Unecessary?
#Expand the replicates so that can be viewable in an excel file (one cell per
# rep)
reps_expand_df=Run_df.copy()
#cycle through elements
for col in repCPS_all_df.columns[5:]:
    #convert element column of reps into matrix of reps and samples
    elarray=np.array(list(repCPS_all_df[col]))    
    #create new column names for the replicate columns
    colnames=[m+'_rep'+str(n) for m,n in zip([col]*5,np.arange(numrepeats)+1)]
    #build into dataframe
    eldf=pd.DataFrame(elarray, columns=colnames)
    reps_expand_df=pd.concat([reps_expand_df, eldf], axis=1)   




###### Saving ######

savepath=folder_select+'/Pygilent_out/'
isExist = os.path.exists(savepath)

if not isExist:
    os.makedirs(savepath)    

savename=textinputbox(title="Enter save name")
tstamp=str(round(time.time()))


#Make a dataframes containing only selected isotopes
dflist=[]
for r in ratioels:
    temp_df=Run_df.copy()
    temp_df['CPS']=CPSmean_df[r]
    temp_df['PA']=PA_df[r]
    temp_df['expected PA']=exPA_df[r]
    temp_df['CaConc (mM)']=CaConc_df[r]
    temp_df['undiluted Ca (mM)']=undiluted_df[r]
    temp_df['Vol smpl (ul)']=VolSmpl_df[r]
    temp_df['Vol acid (ul)']=VolAcid_df[r]
    
    temp_df.drop(blkrows, inplace=True)
    temp_df=temp_df.sort_values('Type')
    
    dflist.append(temp_df)


with pd.ExcelWriter(savepath+savename +'_Ca_'+ tstamp +'.xlsx') as writer:
    rep_cps_long_df.to_excel(writer, sheet_name='Reps')
    CPSmean_df.to_excel(writer, sheet_name='CPS')
    PA_df.to_excel(writer, sheet_name='PA') 
    CaConc_df.to_excel(writer, sheet_name='CaConc (mM)') 
    undiluted_df.to_excel(writer, sheet_name='Undiluted CaConc (mM)') 
    VolSmpl_df.to_excel(writer, sheet_name='Vol smpl (ul)')  
    VolAcid_df.to_excel(writer, sheet_name='Vol acid (ul)')  
    for r, df in zip(ratioels, dflist):
        df.to_excel(writer, sheet_name=r)  
    entries_df.to_excel(writer, sheet_name="parameters")
        
#Finished message box
tk.messagebox.showinfo("", "Processing complete")