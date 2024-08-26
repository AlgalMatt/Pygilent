import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd

def select_folder(title="Select a folder"):
    """
    Opens a dialog box to select a folder.

    Parameters:
    - title (str): The title of the dialog box. Defaults to 'Select a folder'.

    Returns:
    - str: The path of the selected folder.

    Usage:
    - Call the function with an optional title parameter to open a dialog box.
    - The user can select a folder using the dialog box.
    - The function returns the path of the selected folder.

    Example:
    folder_path = select_folder("Select the folder containing the data files")
    print(f"Selected folder: {folder_path}")

    """
    from tkinter import filedialog
    root=tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_select=filedialog.askdirectory(title=title)
    root.destroy()
    return folder_select


def create_entry_window(string_list, default_values):
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("User Input Window")

    # Dictionary to store user inputs
    user_inputs = {}

    # Function to handle 'OK' button click
    def ok_button_click():
        for idx, string in enumerate(string_list):
            user_input = entry_fields[idx].get()
            try:
                float_value = float(user_input)
                user_inputs[string] = float_value
            except ValueError:
                show_error_message("Error", "Please enter a valid number for '{}'.".format(string))
                return
            
        root.destroy()
        
    def show_error_message(title, message):
        tk.messagebox.showerror(title, message)
    
    #title
    instructions_label = tk.Label(root, text="Enter conc scalings")
    instructions_label.grid(row=0, column=0, columnspan=2, pady=5)
        
    # Create labels and entry fields with default values
    entry_fields = []
    for idx, string in enumerate(string_list):
        label = tk.Label(root, text=string)
        label.grid(row=idx + 1, column=0, padx=10, pady=5, sticky="w")
        default_value = default_values[idx] if default_values and idx < len(default_values) else ""
        entry = tk.Entry(root)
        entry.insert(0, default_value)
        entry.grid(row=idx + 1, column=1, padx=10, pady=5, sticky="e")
        entry_fields.append(entry)

    # Create 'OK' button
    ok_button = tk.Button(root, text="OK", command=ok_button_click)
    ok_button.grid(row=len(string_list) + 1, column=0, columnspan=2, pady=10)

    # Run the Tkinter main loop
    root.mainloop()

    return user_inputs


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
    
    def select_all():
        global selected   
        if np.all(selected):
            for cb in cb_list:
                cb.deselect()
        else:
            for cb in cb_list:
                cb.select()
        
        
    
    # Create a list to store the checkbox variables
    cb_vars = []

    #The title of the window
    label=tk.Label(window, text=title, font=("Helvetica", 10))
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


def fancycheckbox_2window(items_1, items_2,  title_1="", title_2="", 
                          defaults=None, single_1=False, single_2=False, unique=True):
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
    global selected_1, selected_2
    #if no defaults used, create a list of False to implement defaults.
    if defaults is None:
        defaults={key: [False]*len(items_1) for key in items_2}
    #Otherwise fill in the remainder of the dictionary with False
    else:
        for key in np.setdiff1d(items_2, list(defaults.keys())): 
            defaults[key]=[False]*len(items_1)
    
    selected_1=defaults.copy()
    selected_2=np.append([True], [False]*(len(items_2)-1))

    # Create the main window
    window = tk.Tk()
    #Keep the window at the front of other apps.
    window.lift()
    window.attributes("-topmost", True)
    
    
    
    w = 700 # width for the Tk root
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

    # Function to update the list of selected items 1
    def update_selected_1(var):
        global selected_1
        
        if single_1:
            for i in range(len(cb_vars_1)):
                if i != var:
                    cb_vars_1[i].set(False)
                    cb_list_1[i]['bg']='white'
        
        item_2_selected=np.array(items_2)[selected_2][0]
        selected_1[item_2_selected] = [cb_vars_1[i].get() for i in range(len(cb_vars_1))]
        if cb_vars_1[var].get():
            cb_list_1[var]['bg']='yellow'
        else:
            cb_list_1[var]['bg']='white'
        
        if unique:
            #make sure only one item 2 is associated with each item 1
            for key, value in selected_1.items():
                if item_2_selected!=key:
                    idx=np.array(selected_1[item_2_selected]) & np.array(value)
                    array=np.array(selected_1[key])
                    array[idx]=False
                    selected_1[key]=list(array)
            
        #if single_2 is True, only one item 2 can be selected
        if single_2:
            for key, value in selected_1.items():
                if item_2_selected!=key:
                    selected_1[key]=[False]*len(items_1)
    
        # Function to update the list of selected items 2 
    def update_selected_2(var2):
        global selected_2   
        #only allow one to be selected     
        for i in range(len(cb_vars_2)):
            if i != var2:
                cb_vars_2[i].set(False)
                cb_list_2[i]['bg']='white'
        selected_2 = [cb_vars_2[i].get() for i in range(len(cb_vars_2))]
        if cb_vars_2[var2].get():
            cb_list_2[var2]['bg']='yellow'
        else:
            cb_list_2[var2]['bg']='white'
        item_2_selected=np.array(items_2)[selected_2][0]
        
        for i, booleon in enumerate(selected_1[item_2_selected]):
            if booleon:
                booleon=True
            else:
                booleon=False
            cb_vars_1[i].set(booleon)
            if booleon:
                cb_list_1[i]['bg']='yellow'
            else:
                cb_list_1[i]['bg']='white'
        


    #The title of the 1st window
    label=tk.Label(window, text=title_1, font=("Helvetica", 10))
    label.grid(row=0, column=0, pady=5)
    #The title of the 2nd window
    label=tk.Label(window, text=title_2, font=("Helvetica", 10))
    label.grid(row=0, column=1, pady=5)

    #make the window scrollable
    textframe=ScrolledText(window, width=40, height=50)
    textframe.grid(row=1, column=0, sticky='nsw', rowspan=2)
    # Create a list to store the checkbox variables
    cb_vars_1 = []
    cb_list_1=[]
    
    
    item_selected=np.array(items_2)[selected_2][0]
    # Create checkboxes for window 1
    for i, item in enumerate(items_1):
        
        cb_var = tk.BooleanVar()
        cb = tk.Checkbutton(textframe, text=item, variable=cb_var,
                            command=lambda var=i: update_selected_1(var), 
                            font=("Arial",10),fg="black", bg="white")
        
        cb_list_1.append(cb)
        textframe.window_create('end', window=cb)
        textframe.insert('end', '\n')
        cb_vars_1.append(cb_var)
        if defaults[item_selected][i]:
            cb.select()
            cb['bg']='yellow'
    
    
    
    # create second textframe window
    textframe2=ScrolledText(window, width=40, height=50)
    textframe2.grid(row=1, column=1, sticky='nse', rowspan=2)
    cb_vars_2 = []
    cb_list_2=[]
    for j, item2 in enumerate(items_2):
        cb_var2 = tk.BooleanVar()
        cb2 = tk.Checkbutton(textframe2, text=item2, variable=cb_var2,
                            command=lambda var2=j: update_selected_2(var2), 
                            font=("Arial",10),fg="black", bg="white")
        
        cb_list_2.append(cb2)
        textframe2.window_create('end', window=cb2)
        textframe2.insert('end', '\n')
        cb_vars_2.append(cb_var2)
        if j==0:
            cb2.select()
            cb2['bg']='yellow'
    
    
    

    # Create a "Submit" button
    submit_button = tk.Button(window, text="Submit", command=lambda: window.destroy())
    submit_button.grid(row=3, column=0, columnspan=2)
    
    
    # Run the main loop
    window.mainloop()
    #selected_indexes = np.array([i for i, x in enumerate(selected) if x])
    return selected_1



def cali_block_select(batch_info, title_1="Cali standards", title_2="Samples"):

    #defaults is a list of dictionaries    
    
    global selected_1, selected_2
    #if no defaults used, create a list of False to implement defaults.
    #if defaults is None:
        
    #    defaults={key: [False]*len(items_1) for key in items_2}
    #Otherwise fill in the remainder of the dictionary with False
    #else:
    #    for key in np.setdiff1d(items_2, list(defaults.keys())): 
    #        defaults[key]=[False]*len(items_1)
    
    
    
    
    selected_1=defaults.copy()
    selected_2=np.append([True], [False]*(len(items_2)-1))

    # Create the main window
    window = tk.Tk()
    #Keep the window at the front of other apps.
    window.lift()
    window.attributes("-topmost", True)
    
    
    
    w = 700 # width for the Tk root
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

    # Function to update the list of selected items 1
    def update_selected_1(var):
        global selected_1
        
        if single_1:
            for i in range(len(cb_vars_1)):
                if i != var:
                    cb_vars_1[i].set(False)
                    cb_list_1[i]['bg']='white'
        
        item_2_selected=np.array(items_2)[selected_2][0]
        selected_1[item_2_selected] = [cb_vars_1[i].get() for i in range(len(cb_vars_1))]
        if cb_vars_1[var].get():
            cb_list_1[var]['bg']='yellow'
        else:
            cb_list_1[var]['bg']='white'
        
        if unique:
            #make sure only one item 2 is associated with each item 1
            for key, value in selected_1.items():
                if item_2_selected!=key:
                    idx=np.array(selected_1[item_2_selected]) & np.array(value)
                    array=np.array(selected_1[key])
                    array[idx]=False
                    selected_1[key]=list(array)
            
        #if single_2 is True, only one item 2 can be selected
        if single_2:
            for key, value in selected_1.items():
                if item_2_selected!=key:
                    selected_1[key]=[False]*len(items_1)
    
        # Function to update the list of selected items 2 
    def update_selected_2(var2):
        global selected_2   
        #only allow one to be selected     
        for i in range(len(cb_vars_2)):
            if i != var2:
                cb_vars_2[i].set(False)
                cb_list_2[i]['bg']='white'
        selected_2 = [cb_vars_2[i].get() for i in range(len(cb_vars_2))]
        if cb_vars_2[var2].get():
            cb_list_2[var2]['bg']='yellow'
        else:
            cb_list_2[var2]['bg']='white'
        item_2_selected=np.array(items_2)[selected_2][0]
        
        for i, booleon in enumerate(selected_1[item_2_selected]):
            if booleon:
                booleon=True
            else:
                booleon=False
            cb_vars_1[i].set(booleon)
            if booleon:
                cb_list_1[i]['bg']='yellow'
            else:
                cb_list_1[i]['bg']='white'
        


    #The title of the 1st window
    label=tk.Label(window, text=title_1, font=("Helvetica", 10))
    label.grid(row=0, column=0, pady=5)
    #The title of the 2nd window
    label=tk.Label(window, text=title_2, font=("Helvetica", 10))
    label.grid(row=0, column=1, pady=5)

    #make the window scrollable
    textframe=ScrolledText(window, width=40, height=50)
    textframe.grid(row=1, column=0, sticky='nsw', rowspan=2)
    # Create a list to store the checkbox variables
    cb_vars_1 = []
    cb_list_1=[]
    
    
    item_selected=np.array(items_2)[selected_2][0]
    # Create checkboxes for window 1
    for i, item in enumerate(items_1):
        
        cb_var = tk.BooleanVar()
        cb = tk.Checkbutton(textframe, text=item, variable=cb_var,
                            command=lambda var=i: update_selected_1(var), 
                            font=("Arial",10),fg="black", bg="white")
        
        cb_list_1.append(cb)
        textframe.window_create('end', window=cb)
        textframe.insert('end', '\n')
        cb_vars_1.append(cb_var)
        if defaults[item_selected][i]:
            cb.select()
            cb['bg']='yellow'
    
    
    
    # create second textframe window
    textframe2=ScrolledText(window, width=40, height=50)
    textframe2.grid(row=1, column=1, sticky='nse', rowspan=2)
    cb_vars_2 = []
    cb_list_2=[]
    for j, item2 in enumerate(items_2):
        cb_var2 = tk.BooleanVar()
        cb2 = tk.Checkbutton(textframe2, text=item2, variable=cb_var2,
                            command=lambda var2=j: update_selected_2(var2), 
                            font=("Arial",10),fg="black", bg="white")
        
        cb_list_2.append(cb2)
        textframe2.window_create('end', window=cb2)
        textframe2.insert('end', '\n')
        cb_vars_2.append(cb_var2)
        if j==0:
            cb2.select()
            cb2['bg']='yellow'
    
    
    

    # Create a "Submit" button
    submit_button = tk.Button(window, text="Submit", command=lambda: window.destroy())
    submit_button.grid(row=3, column=0, columnspan=2)
    
    
    # Run the main loop
    window.mainloop()
    #selected_indexes = np.array([i for i, x in enumerate(selected) if x])
    return selected_1


def textinputbox(title=""):
    """
    Creates a simple text input box window.

    Parameters:
    - title (str): The title of the input box window. Defaults to an empty string.

    Returns:
    - str: The user-inputted text when the 'Save' button is clicked.

    Usage:
    - Call the function with an optional title parameter to create a text input box window.
    - The user can input text in the provided text area.
    - Clicking the 'Save' button retrieves the inputted text and closes the window.
    - The function returns the entered text.

    Example:
    user_input = textinputbox("Enter your name")
    print(f"Hello, {user_input}!")
    
    """
    
    
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
    root.title(title)
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

def pickfig(df, xvar, title):
    
    """
    Creates an interactive plot for selecting data points in a scatter plot.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the data.
    - xvar (str): The column in df representing the x-axis values.
    - title (str): The title of the Tkinter window.

    Returns:
    - np.array: An array of indices corresponding to the selected data points.

    Usage:
    - Call the function with the DataFrame, x-axis variable, and window title.
    - The function opens a Tkinter window with an interactive scatter plot.
    - Clicking on data points toggles between 'Remove' and 'Keep' status.
    - Select the y-axis variable using the dropdown menu.
    - Click 'Submit' to close the window and return the indices of the selected data points.

    Example:
    import pandas as pd

    # Create a DataFrame
    data = {'Time': [1, 2, 3, 4, 5],
            'Value1': [10, 15, 7, 20, 12],
            'Value2': [5, 8, 12, 18, 10]}

    df = pd.DataFrame(data)

    # Select data points interactively
    selected_indices = pickfig(df, xvar='Time', title='Interactive Plot')
    print(f"Selected indices: {selected_indices}")
    
    """
    
    
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
    ax.set_xlabel(xvar)
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
    
    
    # Create the dropdown menu
    dropdown_var = tk.StringVar(window)
    dropdown_var.set("Choose an isotope")  # Set default value
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

def display_dataframe_with_option(df):


    
    """
    Display a Tkinter window with a Treeview widget to visualize a DataFrame and prompt a user option.

    Parameters:
    - df (pd.DataFrame): The DataFrame to be displayed.

    Returns:
    - bool or None: The result of the user's choice ('Yes', 'No') or None if the window is closed.

    This function creates a Tkinter window to visualize the contents of a DataFrame using a Treeview widget.
    The user is prompted with a question and provided with 'Yes' and 'No' buttons to make a choice.
    The function returns the user's choice once a button is clicked, or None if the window is closed.

    Example:
    import pandas as pd

    # Assuming a DataFrame 'my_dataframe' is defined
    user_choice = display_dataframe_with_option(my_dataframe)
    if user_choice is not None:
        print(f"User chose {'Yes' if user_choice else 'No'}.")

    """
    
    df.reset_index(inplace=True)
    result = None  # Initialize result variable
    
    def yes_clicked():
        nonlocal result  # Use nonlocal to modify the outer variable
        result = True
        root.destroy()
    
    def no_clicked():
        nonlocal result  # Use nonlocal to modify the outer variable
        result = False
        root.destroy()

    # Create the main window
    root = tk.Tk()
    root.title("DataFrame Viewer")
    
    #Keep the window at the front of other apps.
    root.lift()
    root.attributes("-topmost", True)

    # Create a Treeview widget
    tree = ttk.Treeview(root)

    # Define columns based on DataFrame columns
    tree['columns'] = list(df.columns)

    # Set column headings
    for col in df.columns:
        #Find the width of the columns so that they can be adjusted to fit
        max_len = max(df[col].astype(str).apply(len).max(), len(col))
        tree.column(col, width=max_len * 10)  # Adjust the factor (10) as needed for proper sizing
        tree.heading(col, text=col, command=lambda c=col: sortby(tree, c, 0))

    # Create vertical scrollbar
    vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    # Create horizontal scrollbar
    hsb = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
    hsb.pack(side='bottom', fill='x')
    tree.configure(xscrollcommand=hsb.set)

    # Insert data from DataFrame
    for index, row in df.iterrows():
        tree.insert(parent='', index='end', iid=index, text=index, values=list(row))

    # Pack the Treeview widget
    tree.pack()

    # Create label
    label = ttk.Label(root, text="Automatically remove P/A outliers?")
    label.pack(pady=5)

    # Create a frame to contain the buttons
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=5)
    
    # Create 'Yes' and 'No' buttons
    yes_button = ttk.Button(button_frame, text='Yes', command=yes_clicked)
    yes_button.pack(side='left', padx=10)
    no_button = ttk.Button(button_frame, text='No', command=no_clicked)
    no_button.pack(side='left', padx=10)

    # Start the tkinter main loop
    root.mainloop()
    
    return result  # Return the result after the window is destroyed

def stndblk_picker(cps_df, sd_df, pa_df, table_df, title, outmod, isotopes):
    
    from Pygilent.pygilent import find_outliers
    
    global selected_ind, variable
    xvar=cps_df['session_time'].values/3600
    cps_df_modified=cps_df.copy()
    variable=cps_df['isotope_gas'].values[0]
    selected_ind={k: np.array([], dtype=int) for k in cps_df['isotope_gas'].values}
    df_index=cps_df.index.values
    
    def on_pick(event):
        global ind, selected_ind
        ind = event.ind

        newind=np.setdiff1d(ind, selected_ind[variable])
        
        #If the user has selected a new unselected point
        if newind.size>0:
            #Save the data index to the dictionary of isotopes
            selected_ind[variable]=np.append(selected_ind[variable], newind)
            cps_df_modified.loc[df_index[ind], variable]=np.nan    
        #If the user has clicked on an already selected point    
        else:
            selected_ind[variable]=np.setdiff1d(selected_ind[variable], ind)
            cps_df_modified.loc[df_index[ind], variable]=cps_df.loc[df_index[ind], variable]
        #Re-calculate means, standard deviations, and quartiles    
        iso_mean=np.nanmean(cps_df_modified.loc[df_index[ind], variable])
        iso_sd=np.nanstd(cps_df_modified.loc[df_index[ind], variable])
        q75, q25 = np.percentile(cps_df_modified.loc[df_index[ind], variable], [75 ,25])
        
        #Re-draw the figure
        scatter2.set_data(xvar, cps_df_modified.loc[df_index[ind], variable])
        mean_line.set_ydata([iso_mean, iso_mean])
        sd_line_upper.set_ydata([iso_mean+iso_sd*2, iso_mean+iso_sd*2])
        out_line_upper.set_ydata([q75+(q75-q25)*outmod, q75+(q75-q25)*outmod])
        sd_line_lower.set_ydata([iso_mean-iso_sd*2, iso_mean-iso_sd*2])
        out_line_lower.set_ydata([q25-(q75-q25)*outmod, q25-(q75-q25)*outmod])
        fig.canvas.draw_idle()
    
    
    # Create the initial plot without showing the figure
    fig, ax = plt.subplots()
    scatter1, = ax.plot([], [], linestyle='None', marker='o', color='red', picker=5, mec='r')
    scatter2, = ax.plot([], [], linestyle='None', marker='o', color='blue', mec='b')
    scatter_outs, = ax.plot([], [], linestyle='None', marker='o', 
                            mfc='none', mec='r', mew=1)
    mean_line=ax.axhline(y=0, ls='-', color='black')
    sd_line_upper=ax.axhline(y=0, ls='--', color='black')
    out_line_upper=ax.axhline(y=0, ls=':', color='black')
    sd_line_lower=ax.axhline(y=0, ls='--', color='black')
    out_line_lower=ax.axhline(y=0, ls=':', color='black')
    PA_annotate_ls=[ax.text(0, 0, [], fontsize=12, ha='right', va='bottom') 
                    for i in df_index]
    
    ax.set_xlabel('Analysis time (hours)')
    ax.set_ylabel(variable+ ' cps')
    ax.legend(['Remove', 'Keep', 'Recommend (outlier)', 'Mean', '2$\sigma$', 'outlier threshold'])
    
    # Register the pick event
    fig.canvas.mpl_connect('pick_event', on_pick)
    
    plt.close(fig)  # Close the figure to prevent it from being displayed
    
    
    
    # Define the update function for the dropdown (changing isotopes)
    def update_y_axis(*args):
        global variable
        variable = dropdown_var.get()
        
        #Show the outliers recommended for removal
        outs=find_outliers(cps_df.loc[df_index, variable].astype(float), mod=outmod)
        
        #calculate the means, sd and quartiles
        iso_mean=np.nanmean(cps_df_modified.loc[df_index, variable])
        iso_sd=np.nanstd(cps_df_modified.loc[df_index, variable])
        q75, q25 = np.percentile(cps_df_modified.loc[df_index, variable], [75 ,25])
        
        #Re-draw the figure
        scatter1.set_data(xvar, cps_df.loc[df_index, variable])
        scatter2.set_data(xvar, cps_df_modified.loc[df_index, variable])
        scatter_outs.set_data(xvar[outs], cps_df_modified.loc[df_index[outs], variable])
        mean_line.set_ydata([iso_mean, iso_mean])
        sd_line_upper.set_ydata([iso_mean+iso_sd*2, iso_mean+iso_sd*2])
        out_line_upper.set_ydata([q75+(q75-q25)*outmod, q75+(q75-q25)*outmod])
        sd_line_lower.set_ydata([iso_mean-iso_sd*2, iso_mean-iso_sd*2])
        out_line_lower.set_ydata([q25-(q75-q25)*outmod, q25-(q75-q25)*outmod])
        
        for i, txt in enumerate(PA_annotate_ls):
            txt.set_position((xvar[i], cps_df.loc[df_index[i], variable].astype(float)))
            PA_text=pa_df.loc[df_index[i], variable]
            txt.set_text(PA_text)
        
        ax.set_ylabel(variable)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()
        

    # Create the Tkinter window
    window = tk.Tk()
    window.title(title)
    
    #Keep the window at the front of other apps.
    window.lift()
    window.attributes("-topmost", True)
    
    plot_frame = ttk.Frame(window)
    plot_frame.grid(row=0, column=0, sticky='nsew')
    
    table_frame = ttk.Frame(window)
    table_frame.grid(row=0, column=1, sticky='nsew')
    
    
        # Create a treeview widget for the table
    outlier_table = ttk.Treeview(table_frame, columns=table_df.columns, show='headings')
    
        # Define columns based on DataFrame columns
    outlier_table['columns'] = list(table_df.columns)

    # Set column headings
    for col in table_df.columns:
        outlier_table.heading(col, text=col)
    
    # Insert data from DataFrame
    for index, row in table_df.iterrows():
        outlier_table.insert(parent='', index='end', iid=index, values=list(row))

    # Pack the table
    outlier_table.pack(expand=tk.YES, fill=tk.BOTH)
    
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=outlier_table.yview)
    vsb.pack(side='right', fill='y')
    outlier_table.configure(yscrollcommand=vsb.set)


    # Configure grid weights to make the frames resizable
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    
    
    # Create the dropdown menu
    dropdown_var = tk.StringVar(plot_frame)
    dropdown_var.set('Choose an isotope')  
    dropdown = tk.OptionMenu(plot_frame, dropdown_var, *isotopes, command=update_y_axis)
    dropdown.pack(padx=10, pady=10)
    
    
    submit_button = tk.Button(plot_frame, text="Submit", command=lambda: window.destroy())
    submit_button.pack(side = tk.BOTTOM)


    # Create the FigureCanvasTkAgg object
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    
    # Run the Tkinter event loop
    window.mainloop()
    
    
    return cps_df_modified

def pickfig_cross(dfy, dfx, variables, title=None, fitted=None):
    
    """
    Creates an interactive scatter plot for selecting data points in multiple y-axis variables.

    Parameters:
    - dfy (pd.DataFrame): The DataFrame containing the y-axis data.
    - dfx (pd.DataFrame): The DataFrame containing the x-axis and variable data.
    - variables (list): List of variable names to be plotted on the y-axis.
    - title (str): The title of the Tkinter window. Defaults to None.
    - fitted (pd.DataFrame): The DataFrame containing fitted values. Defaults to None.

    Returns:
    - dict: A dictionary containing selected indices for each variable.

    Usage:
    - Call the function with the y-axis DataFrame, x-axis DataFrame, list of variables,
      optional title, and optional fitted values.
    - The function opens a Tkinter window with an interactive scatter plot for each variable.
    - Clicking on data points toggles between 'Remove' and 'Keep' status.
    - Select the variable using the dropdown menu.
    - Click 'Submit' to close the window and return the selected indices for each variable.

    Example:
    import pandas as pd

    # Create DataFrames
    dfx = pd.DataFrame({'Time': [1, 2, 3, 4, 5],
                        'Value1': [10, 15, 7, 20, 12],
                        'Value2': [5, 8, 12, 18, 10]})
    
    dfy = pd.DataFrame({'Value1': [20, 25, 15, 30, 18],
                        'Value2': [15, 18, 22, 28, 20]})
    
    # Select data points interactively for multiple variables
    selected_indices = pickfig_cross(dfy, dfx, variables=['Value1', 'Value2'], title='Interactive Plot')
    print(f"Selected indices: {selected_indices}")
    """
    
    global selected_ind, variable
    dfx2=dfx.copy()
    variable=variables[0]
    selected_ind={k: np.array([], dtype=int) for k in variables}
    
    
    def on_pick(event):
        global ind, selected_ind
        ind = dfx.index[event.ind]
        
    
        newind=np.setdiff1d(ind, selected_ind[variable])
        
        if newind.size>0:
            selected_ind[variable]=np.append(selected_ind[variable], newind)
            dfx2.loc[ind, variable]=np.nan
            scatter2.set_data(dfx2[variable], dfy[variable])
            fig.canvas.draw_idle()
            
        else:
            selected_ind[variable]=np.setdiff1d(selected_ind[variable], ind)
            dfx2.loc[ind, variable]=dfx.loc[ind, variable]
            scatter2.set_data(dfx2[variable], dfy[variable])
            fig.canvas.draw_idle()
            
 
 
    # Create the initial plot without showing the figure
    fig, ax = plt.subplots()
    scatter1, = ax.plot([], [], linestyle='None', marker='o', color='red', picker=True)
    scatter2, = ax.plot([], [], linestyle='None', marker='o', color='blue')
    if all(fitted!=None):
        fit1=ax.plot([], [], linestyle='-', marker=None, color='black')
    ax.set_xlabel(variable)
    ax.set_ylabel(variable)
    ax.legend(['Remove', 'Keep'])
    
    
    
    # Register the pick event
    fig.canvas.mpl_connect('pick_event', on_pick)
    
    plt.close(fig)  # Close the figure to prevent it from being displayed
    
    
    # Define the update function for the dropdown
    def update_y_axis(*args):
        global variable
        variable = dropdown_var.get()
        scatter1.set_data(dfx[variable], dfy[variable])
        scatter2.set_data(dfx2[variable], dfy[variable])
        if all(fitted!=None):
            fit1[0].set_data(dfx[variable], fitted[variable])
        ax.set_ylabel(variable)
        ax.set_xlabel(variable)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()
        
    
    # Create the Tkinter window
    window = tk.Tk()
    window.title(title)
    
    
    # Create the dropdown menu
    dropdown_var = tk.StringVar(window)
    dropdown_var.set("Choose an isotope")  # Set default value
    dropdown = tk.OptionMenu(window, dropdown_var, *variables, 
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
    
    
    return selected_ind

def blankfigsaver(df1, df2, iso_vars, variable='cps_mean',  title='Blanks CPS',  
                  xvar='time', figpath='.'):
    
    """
    Creates an interactive plot for saving figures of archive and batch data for selected isotopes.

    Parameters:
    - df1 (pd.DataFrame): Archive data DataFrame.
    - df2 (pd.DataFrame): Batch data DataFrame.
    - iso_vars (list): List of isotope names.
    - variable (str): Variable to be plotted on the y-axis. Defaults to 'CPS mean'.
    - title (str): Title of the Tkinter window. Defaults to 'Blanks CPS'.
    - xvar (str): Variable for the x-axis. Defaults to 'Acq. Date-Time'.

    Returns:
    - None

    Usage:
    - Call the function with archive and batch DataFrames, list of isotope names,
      optional y-axis variable, optional title, and optional x-axis variable.
    - The function opens a Tkinter window with an interactive plot.
    - Select the isotope using the dropdown menu.
    - Click 'Save' to save the figure for the current isotope.
    - Click 'Save all' to save figures for all isotopes.
    - Click 'Exit' to close the window.

    Example:
    import pandas as pd

    # Create DataFrames
    df1 = pd.DataFrame({'isotope_gas': ['A', 'B', 'A', 'B'],
                        'Acq. Date-Time': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04'],
                        'CPS mean': [10, 15, 7, 20]})
    
    df2 = pd.DataFrame({'isotope_gas': ['A', 'B', 'A', 'B'],
                        'Acq. Date-Time': ['2023-01-05', '2023-01-06', '2023-01-07', '2023-01-08'],
                        'CPS mean': [5, 8, 12, 18]})
    
    # Save figures interactively
    blankfigsaver(df1, df2, iso_vars=['A', 'B'])
    """
    
    from Pygilent.pygilent import find_outliers
    
    global iso
    iso=iso_vars[0]
    
    #Isolate one element
    df1_el=df1.loc[df1['isotope_gas']==iso]
    if df1_el.size>0:
        outs=find_outliers(np.array(df1_el[variable]))
        df1_el=df1_el.loc[~outs]
    df2_el=df2.loc[df2['isotope_gas']==iso]
    
    def saveonefig():        
        #Save the current figure
        fig.savefig(figpath+'/'+title+iso+'.png')
        
    def saveallfig():   
        
         #reset the progressbar
         progressbar['value']=0  
         progressbar.update()
         
         for j, el in enumerate(iso_vars):
            
            #increment the progressbar
            progressbar['value']=(j+1)/len(iso_vars)*100
            progressbar.update()
                 
            #get the specific isotope data 
            df1_elb=df1.loc[df1['isotope_gas']==el]
            #remove outliers from archive
            if df1_elb.size>0:
                outs=find_outliers(np.array(df1_elb[variable]))
                df1_elb=df1_elb.loc[~outs]
            df2_elb=df2.loc[df2['isotope_gas']==el]
               
            #plot figure
            figall, ax = plt.subplots()
            figall.set_figheight(6)
            figall.set_figwidth(12)
            #Archive data 
            scatter1 = ax.scatter(df1_elb[xvar].astype('datetime64[ns]'), 
                            df1_elb[variable],
                            linestyle='None', marker='o', color='blue', s=4)
            #Batch data 
            scatter2 = ax.scatter(df2_elb[xvar].astype('datetime64[ns]'), 
                            df2_elb[variable], 
                            linestyle='None', marker='o', color='red', s=4)
                                    
            ax.xaxis.set_tick_params(rotation=45)
            ax.set_xlabel(xvar)
            ax.set_ylabel(variable+' '+el)
            ax.legend(['Archive', 'This run'])
            figall.savefig(figpath+'/'+title+el+'.png')
            plt.close(figall)
              
     
              
     
    #turn off interactive plotting
    plt.ioff()

    
    # Create the initial plot without showing the figure
    fig, ax = plt.subplots()   
    #Archive data
    scatter1 = ax.scatter(df1_el[xvar].astype('datetime64[ns]'), 
                    df1_el[variable],
                    linestyle='None', marker='o', color='blue', s=4)
    #Batch data
    scatter2 = ax.scatter(df2_el[xvar].astype('datetime64[ns]'), 
                    df2_el[variable],
                    linestyle='None', marker='o', color='red', s=4)
    ax.xaxis.set_tick_params(rotation=45)
    ax.set_xlabel(xvar)
    ax.set_ylabel(variable+' '+iso)
    ax.legend(['Archive', 'This run'])
    
    plt.close(fig)  # Close the figure to prevent it from being displayed
    
    
    # Define the update function for the dropdown
    def update_y_axis(*args):
        global iso
        iso = dropdown_var.get()
        #Get specific isotope data, remove outliers from archive   
        df1_el=df1.loc[df1['isotope_gas']==iso]
        if df1_el.size>0:
            outs=find_outliers(np.array(df1_el[variable]))
            df1_el=df1_el.loc[~outs]        
        
        df2_el=df2.loc[df2['isotope_gas']==iso]
        
        #clear the old data from the plot
        ax.cla()
        #add new data from selected isotope
        scatter1 = ax.scatter(df1_el[xvar].astype('datetime64[ns]'), 
                        df1_el[variable], 
                        linestyle='None', marker='o', color='blue', s=4)
        
        scatter2 = ax.scatter(df2_el[xvar].astype('datetime64[ns]'), 
                        df2_el[variable],
                        linestyle='None', marker='o', color='red', s=4)
        ax.xaxis.set_tick_params(rotation=45)
        plt.xticks(rotation = 45)
        ax.set_xlabel(xvar)
        ax.set_ylabel(variable+' '+iso)
        ax.legend(['Archive', 'This run'])
        fig.canvas.draw_idle()
    
    # Create the Tkinter window
    window = tk.Tk()
    window.geometry("1000x800")
    window.title(title)
       
    
    button_frame = tk.Frame(window)
    button_frame.pack(side=tk.TOP, padx=10, pady=10)
    
    
    # Create the dropdown menu
    dropdown_var = tk.StringVar(window)
    dropdown_var.set("Choose the isotope")  # Set default value
    dropdown = tk.OptionMenu(button_frame, dropdown_var, *iso_vars, 
                             command=update_y_axis)
    dropdown.pack(side=tk.LEFT)
    
    button_frame2 = tk.Frame(window)
    button_frame2.pack(side=tk.BOTTOM)
    
    figure_frame = tk.Frame(window)
    figure_frame.pack(fill=tk.BOTH,  side=tk.TOP)
    
    
    # Create the FigureCanvasTkAgg object
    canvas = FigureCanvasTkAgg(fig, master=figure_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, ipady=20)
    
    
    #progress bar
    progressbar = ttk.Progressbar(window, orient=tk.HORIZONTAL, length=400)
    progressbar.pack(side=tk.BOTTOM)
  
    
    Save_button = tk.Button(button_frame2, text="Save", 
                              command=saveonefig)
    SaveAll_button = tk.Button(button_frame2, text="Save all", 
                              command=saveallfig)
    Exit_button = tk.Button(button_frame2, text="Exit", 
                              command=lambda: window.destroy())
    
    Save_button.pack(side=tk.LEFT)
    SaveAll_button.pack(side=tk.LEFT)
    Exit_button.pack(side=tk.LEFT)

    # Run the Tkinter event loop
    window.mainloop()

def stdfigsaver(df1, df2, title, iso_vars, expected,
                variables=['cali_single', 'cali_curve'],  
                errors=['cali_single_se', 'cali_curve_se'],  
             xvar='time', figpath='.'):
    
    """
    Creates an interactive plot for saving figures of calibration data for selected isotopes.

    Parameters:
    - df1 (pd.DataFrame): Archive data DataFrame.
    - df2 (pd.DataFrame): Batch data DataFrame.
    - title (str): Title of the Tkinter window.
    - iso_vars (list): List of isotope names.
    - expected (dict): Dictionary with expected values for each isotope.
    - variables (list): List of variables to be plotted on the y-axis. Defaults to ['cali_single', 'cali_curve'].
    - errors (list): List of error variables corresponding to each variable. Defaults to ['cali_single_se', 'cali_curve_se'].
    - xvar (str): Variable for the x-axis. Defaults to 'time'.

    Returns:
    - None

    Usage:
    - Call the function with archive and batch DataFrames, title, list of isotope names, dictionary of expected values,
      optional list of y-axis variables, optional list of error variables, and optional x-axis variable.
    - The function opens a Tkinter window with an interactive plot.
    - Select the isotope using the dropdown menu.
    - Click 'Save' to save the figure for the current isotope.
    - Click 'Save all' to save figures for all isotopes.
    - Click 'Exit' to close the window.

    Example:
    import pandas as pd

    # Create DataFrames
    df1 = pd.DataFrame({'isotope_gas': ['A', 'B', 'A', 'B'],
                        'brkt_stnd': ['Bracket1', 'Bracket2', 'Bracket1', 'Bracket2'],
                        'Acq. Date-Time': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04'],
                        'cali_single': [10, 15, 7, 20],
                        'cali_curve': [25, 30, 22, 35],
                        'cali_single_se': [1, 1.5, 0.7, 2],
                        'cali_curve_se': [2, 2.5, 1.2, 3]})
    
    df2 = pd.DataFrame({'isotope_gas': ['A', 'B', 'A', 'B'],
                        'Acq. Date-Time': ['2023-01-05', '2023-01-06', '2023-01-07', '2023-01-08'],
                        'cali_single': [5, 8, 12, 18],
                        'cali_curve': [22, 28, 18, 30],
                        'cali_single_se': [0.5, 0.8, 1.2, 1.8],
                        'cali_curve_se': [1, 1.2, 1.5, 2]})
    
    expected_values = {'A': 15, 'B': 25}
    
    # Save figures interactively
    stdfigsaver(df1, df2, title='Calibration Figures', iso_vars=['A', 'B'],
                expected=expected_values, variables=['cali_single', 'cali_curve'])
    """
    
    global iso
    #set default value for the isotope
    iso=iso_vars[0]
    
    #Make a colour map to for shading different bracketing standards
    cmap = matplotlib.colormaps['rainbow'].resampled(len(pd.unique(df1['brkt_stnd'])))
    
    
    #this will be a list of the archive dataframes with each entry corresponding
    #to a different bracketing standard used.
    df1_ls=[]
    #cycle through the different bracketing standards
    for brk in pd.unique(df1['brkt_stnd']):
         
        #Subset the dataframe for the given isotope and bracketing standard
        df1_el=df1.loc[(df1['isotope_gas']==iso)&(df1['brkt_stnd']==brk)]
        #If dataframe isn't empty, remove outliers in single-point data 
        if (df1_el[variables[0]].size>0) & (any(~np.isnan(df1_el[variables[0]]))):
            outs_s=outsbool(np.array(df1_el[variables[0]]))
            outs_s=outs_s | outsbool(np.array(df1_el[errors[0]]))
            df1_el.loc[outs_s, variables[0]]=np.nan       
            #If cali-curve isn't empty, remove outliers in cali-curve data 
            if (df1_el[variables[1]].size>0) & (any(~np.isnan(df1_el[variables[1]]))):
                outs_c=outsbool(np.array(df1_el[variables[1]]))
                outs_c=outs_c | outsbool(np.array(df1_el[errors[1]]))
                df1_el.loc[outs_c, variables[1]]=np.nan
        #add to the dataframe list
        df1_ls.append(df1_el)
        
    #subset the run dataframe for the given isotope 
    df2_el=df2.loc[df2['isotope_gas']==iso]
    
    
    
    #Save the current figure
    def saveonefig():        
        fig.savefig(figpath+'/'+title+'_'+iso+'.png')
    
    #Save all figures
    def saveallfig():  
         
        #reset the progressbar
        progressbar['value']=0  
        progressbar.update()
                
        #cycle through each isotope
        for j, el in enumerate(iso_vars):

            #increment the progressbar
            progressbar['value']=(j+1)/len(iso_vars)*100
            progressbar.update()
                
                
            #adjust the dataframes
            #this will be a list of the archive dataframes with each entry corresponding
            #to a different bracketing standard used.
            df1_ls=[]
            #cycle through the different bracketing standards
            for brk in pd.unique(df1['brkt_stnd']):
                 
                #Subset the dataframe for the given isotope and bracketing standard
                df1_el=df1.loc[(df1['isotope_gas']==el)&(df1['brkt_stnd']==brk)]
                #If dataframe isn't empty, remove outliers in single-point data 
                if (df1_el[variables[0]].size>0) & (any(~np.isnan(df1_el[variables[0]]))):
                    outs_s=outsbool(np.array(df1_el[variables[0]]))
                    outs_s=outs_s | outsbool(np.array(df1_el[errors[0]]))
                    df1_el.loc[outs_s, variables[0]]=np.nan       
                    #If cali-curve isn't empty, remove outliers in cali-curve data 
                    if (df1_el[variables[1]].size>0) & (any(~np.isnan(df1_el[variables[1]]))):
                        outs_c=outsbool(np.array(df1_el[variables[1]]))
                        outs_c=outs_c | outsbool(np.array(df1_el[errors[1]]))
                        df1_el.loc[outs_c, variables[1]]=np.nan
                #add to the dataframe list
                df1_ls.append(df1_el)
                
                #subset the run dataframe for the given isotope 
                df2_el=df2.loc[df2['isotope_gas']==el]
            
      
            # Create the initial plot without showing the figure
            figall, ax = plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True)   
            figall.set_figheight(6)
            figall.set_figwidth(12)
                
            #Cycle through bracketing standards in the archive data
            for i, brk in enumerate(pd.unique(df1['brkt_stnd'])):
                
                #Single-point calibration archive data
                if any(~np.isnan(df1_ls[i][variables[0]])):
                    
                    #shaded area showing +/-2SD
                    ystdev2=df1_ls[i][variables[0]].std()*2
                    ymean=df1_ls[i][variables[0]].mean()
                    ax[0].axhspan(ymean-ystdev2, ymean+ystdev2, 
                                  alpha=0.2, color=cmap(i), 
                                  label='Archive calibrated by '+brk+r'$\mu \pm2\sigma$')
                    #Archive data with +/-1SE errorbars
                    scatter1_s = ax[0].errorbar(df1_ls[i][xvar].astype('datetime64[ns]'), 
                                    df1_ls[i][variables[0]], yerr=df1_ls[i][errors[0]],
                                    linestyle='None', marker='.', 
                                    color=cmap(i), ms=4, 
                                    label='Archive calibrated by '+brk+r'$ \pm1\sigma$')
                 
                #Calibation curve archive data    
                if any(~np.isnan(df1_ls[i][variables[1]])):    
                    
                    #shaded area showing +/-2SD
                    ystdev2=df1_ls[i][variables[1]].std()*2
                    ymean=df1_ls[i][variables[1]].mean()
                    ax[1].axhspan(ymean-ystdev2, ymean+ystdev2, 
                                  alpha=0.2, color=cmap(i), 
                                  label='Archive calibrated by '+brk+r'$\mu \pm2\sigma$')
                    #Archive data with +/-1SE errorbars
                    scatter1_c = ax[1].errorbar(df1_ls[i][xvar].astype('datetime64[ns]'), 
                                    df1_ls[i][variables[1]], yerr=df1_ls[i][errors[1]],
                                    linestyle='None', marker='.', 
                                    color=cmap(i), ms=4, 
                                    label='Archive calibrated by '+brk+r'$ \pm1\sigma$')
                
            #Single-point run data with +/-1SE errorbars       
            scatter2_s = ax[0].errorbar(df2_el[xvar].astype('datetime64[ns]'), 
                                df2_el[variables[0]], yerr=df2_el[errors[0]],
                                linestyle='None', marker='s', color='black', ms=4, 
                                label='This run'+r'$ \pm1\sigma$')

            
            if any(df2_el.columns == variables[1]):
                #Calibration curve run data with +/-1SE errorbars
                scatter2_c = ax[1].errorbar(df2_el[xvar].astype('datetime64[ns]'), 
                                df2_el[variables[1]], yerr=df2_el[errors[1]],
                                linestyle='None', marker='s', color='black', ms=4, 
                                label='This run'+r'$ \pm1\sigma$')
                
            
            
            #draw expected values
            if ~np.isnan(expected[el]):
                ax[0].axhline(expected[el], color='black', label='Expected', ls='--')
                ax[1].axhline(expected[el], color='black', label='Expected', ls='--')
            
            #Legend    
            handles,labels = ax[0].get_legend_handles_labels()
            ax[0].legend(handles, labels)
            handles,labels = ax[1].get_legend_handles_labels()
            ax[1].legend(handles, labels)
            
            #Titles and tick marks
            ax[0].title.set_text('Single-point')
            ax[1].title.set_text('Calibration curve')
            ax[0].xaxis.set_tick_params(rotation=45)
            ax[1].xaxis.set_tick_params(rotation=45)
            #Axes labels
            ax[0].set_xlabel(xvar)
            ax[1].set_xlabel(xvar)
            ax[0].set_ylabel(el)
            #Main title
            figall.suptitle(title)
            
            
            figall.savefig(figpath+'/'+title+'_'+el+'.png')
            plt.close(figall)
            #plt.show()   
    
 
    #turn off interactive plotting
    plt.ioff()
    
    
    # Create the initial plot without showing the figure
    fig, ax = plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True)   
    
    #Cycle through bracketing standards in the archive data
    for i, brk in enumerate(pd.unique(df1['brkt_stnd'])):
        
        #Single-point calibration archive data
        if any(~np.isnan(df1_ls[i][variables[0]])):
            
            #shaded area showing +/-2SD
            ystdev2=df1_ls[i][variables[0]].std()*2
            ymean=df1_ls[i][variables[0]].mean()
            ax[0].axhspan(ymean-ystdev2, ymean+ystdev2, 
                          alpha=0.2, color=cmap(i), 
                          label='Archive calibrated by '+brk+r'$\mu \pm2\sigma$')
            #Archive data with +/-1SE errorbars
            scatter1_s = ax[0].errorbar(df1_ls[i][xvar].astype('datetime64[ns]'), 
                            df1_ls[i][variables[0]], yerr=df1_ls[i][errors[0]],
                            linestyle='None', marker='.', 
                            color=cmap(i), ms=4, 
                            label='Archive calibrated by '+brk+r'$ \pm1\sigma$')
         
        #Calibation curve archive data    
        if any(~np.isnan(df1_ls[i][variables[1]])):    
            
            #shaded area showing +/-2SD
            ystdev2=df1_ls[i][variables[1]].std()*2
            ymean=df1_ls[i][variables[1]].mean()
            ax[1].axhspan(ymean-ystdev2, ymean+ystdev2, 
                          alpha=0.2, color=cmap(i), 
                          label='Archive calibrated by '+brk+r'$\mu \pm2\sigma$')
            #Archive data with +/-1SE errorbars
            scatter1_c = ax[1].errorbar(df1_ls[i][xvar].astype('datetime64[ns]'), 
                            df1_ls[i][variables[1]], yerr=df1_ls[i][errors[1]],
                            linestyle='None', marker='.', 
                            color=cmap(i), ms=4, 
                            label='Archive calibrated by '+brk+r'$ \pm1\sigma$')
        
    #Single-point run data with +/-1SE errorbars       
    scatter2_s = ax[0].errorbar(df2_el[xvar].astype('datetime64[ns]'), 
                        df2_el[variables[0]], yerr=df2_el[errors[0]],
                        linestyle='None', marker='s', color='black', ms=4, 
                        label='This run'+r'$ \pm1\sigma$')

    
    if any(df2_el.columns == variables[1]):
        #Calibration curve run data with +/-1SE errorbars
        scatter2_c = ax[1].errorbar(df2_el[xvar].astype('datetime64[ns]'), 
                        df2_el[variables[1]], yerr=df2_el[errors[1]],
                        linestyle='None', marker='s', color='black', ms=4, 
                        label='This run'+r'$ \pm1\sigma$')
        
    
    
    #draw expected values
    if ~np.isnan(expected[iso]):
        ax[0].axhline(expected[iso], color='black', label='Expected', ls='--')
        ax[1].axhline(expected[iso], color='black', label='Expected', ls='--')
    
    #Legend    
    handles,labels = ax[0].get_legend_handles_labels()
    ax[0].legend(handles, labels)
    handles,labels = ax[1].get_legend_handles_labels()
    ax[1].legend(handles, labels)
    
    #Titles and tick marks
    ax[0].title.set_text('Single-point')
    ax[1].title.set_text('Calibration curve')
    ax[0].xaxis.set_tick_params(rotation=45)
    ax[1].xaxis.set_tick_params(rotation=45)
    #Axes labels
    ax[0].set_xlabel(xvar)
    ax[1].set_xlabel(xvar)
    ax[0].set_ylabel(iso)
    #Main title
    fig.suptitle(title)

    plt.close(fig)  # Close the figure to prevent it from being displayed
    
    
    
    
    
    
    # Define the update function for the dropdown
    def update_y_axis(*args):
        global iso
            
        
        #set the isotope
        iso = dropdown_var.get()
        
      
        #this will be a list of the archive dataframes with each entry corresponding
        #to a different bracketing standard used.
        df1_ls=[]
        #cycle through the different bracketing standards
        for brk in pd.unique(df1['brkt_stnd']):
             
            #Subset the dataframe for the given isotope and bracketing standard
            df1_el=df1.loc[(df1['isotope_gas']==iso)&(df1['brkt_stnd']==brk)]
            #If dataframe isn't empty, remove outliers in single-point data 
            if (df1_el[variables[0]].size>0) & (any(~np.isnan(df1_el[variables[0]]))):
                outs_s=outsbool(np.array(df1_el[variables[0]]))
                outs_s=outs_s | outsbool(np.array(df1_el[errors[0]]))
                df1_el.loc[outs_s, variables[0]]=np.nan       
                #If cali-curve isn't empty, remove outliers in cali-curve data 
                if (df1_el[variables[1]].size>0) & (any(~np.isnan(df1_el[variables[1]]))):
                    outs_c=outsbool(np.array(df1_el[variables[1]]))
                    outs_c=outs_c | outsbool(np.array(df1_el[errors[1]]))
                    df1_el.loc[outs_c, variables[1]]=np.nan
            #add to the dataframe list
            df1_ls.append(df1_el)
            
        #subset the run dataframe for the given isotope 
        df2_el=df2.loc[df2['isotope_gas']==iso]

        #clear the axes
        ax[0].cla()
        ax[1].cla()
        
        
        
      
        #Cycle through bracketing standards in the archive data
        for i, brk in enumerate(pd.unique(df1['brkt_stnd'])):
            
            #Single-point calibration archive data
            if any(~np.isnan(df1_ls[i][variables[0]])):
                
                #shaded area showing +/-2SD
                ystdev2=df1_ls[i][variables[0]].std()*2
                ymean=df1_ls[i][variables[0]].mean()
                ax[0].axhspan(ymean-ystdev2, ymean+ystdev2, 
                              alpha=0.2, color=cmap(i), 
                              label='Archive calibrated by '+brk+r'$\mu \pm2\sigma$')
                #Archive data with +/-1SE errorbars
                scatter1_s = ax[0].errorbar(df1_ls[i][xvar].astype('datetime64[ns]'), 
                                df1_ls[i][variables[0]], yerr=df1_ls[i][errors[0]],
                                linestyle='None', marker='.', 
                                color=cmap(i), ms=4, 
                                label='Archive calibrated by '+brk+r'$ \pm1\sigma$')
             
            #Calibation curve archive data    
            if any(~np.isnan(df1_ls[i][variables[1]])):    
                
                #shaded area showing +/-2SD
                ystdev2=df1_ls[i][variables[1]].std()*2
                ymean=df1_ls[i][variables[1]].mean()
                ax[1].axhspan(ymean-ystdev2, ymean+ystdev2, 
                              alpha=0.2, color=cmap(i), 
                              label='Archive calibrated by '+brk+r'$\mu \pm2\sigma$')
                #Archive data with +/-1SE errorbars
                scatter1_c = ax[1].errorbar(df1_ls[i][xvar].astype('datetime64[ns]'), 
                                df1_ls[i][variables[1]], yerr=df1_ls[i][errors[1]],
                                linestyle='None', marker='.', 
                                color=cmap(i), ms=4, 
                                label='Archive calibrated by '+brk+r'$ \pm1\sigma$')
            
        #Single-point run data with +/-1SE errorbars       
        scatter2_s = ax[0].errorbar(df2_el[xvar].astype('datetime64[ns]'), 
                            df2_el[variables[0]], yerr=df2_el[errors[0]],
                            linestyle='None', marker='s', color='black', ms=4, 
                            label='This run'+r'$ \pm1\sigma$')

        
        if any(df2_el.columns == variables[1]):
            #Calibration curve run data with +/-1SE errorbars
            scatter2_c = ax[1].errorbar(df2_el[xvar].astype('datetime64[ns]'), 
                            df2_el[variables[1]], yerr=df2_el[errors[1]],
                            linestyle='None', marker='s', color='black', ms=4, 
                            label='This run'+r'$ \pm1\sigma$')
            
        
        
        #draw expected values
        if ~np.isnan(expected[iso]):
            ax[0].axhline(expected[iso], color='black', label='Expected', ls='--')
            ax[1].axhline(expected[iso], color='black', label='Expected', ls='--')
        
        #Legend    
        handles,labels = ax[0].get_legend_handles_labels()
        ax[0].legend(handles, labels)
        handles,labels = ax[1].get_legend_handles_labels()
        ax[1].legend(handles, labels)
        
        #Titles and tick marks
        ax[0].title.set_text('Single-point')
        ax[1].title.set_text('Calibration curve')
        ax[0].xaxis.set_tick_params(rotation=45)
        ax[1].xaxis.set_tick_params(rotation=45)
        #Axes labels
        ax[0].set_xlabel(xvar)
        ax[1].set_xlabel(xvar)
        ax[0].set_ylabel(iso)
        #plt.show()
        
        fig.canvas.draw_idle()
        
  
    
    # Create the Tkinter window
    window = tk.Tk()
    
    width= window.winfo_screenwidth()*0.9               
    height= window.winfo_screenheight()*0.85               
    window.geometry("%dx%d" % (width, height))
    window.title(title)
    
    
    
    
    button_frame = tk.Frame(window)
    button_frame.pack(side=tk.TOP, padx=10, pady=10)
    
    
    # Create the dropdown menu
    dropdown_var = tk.StringVar(window)
    dropdown_var.set("Choose the isotope")  # Set default value
    dropdown = tk.OptionMenu(button_frame, dropdown_var, *iso_vars, 
                             command=update_y_axis)
    dropdown.pack(side=tk.LEFT)
    
    button_frame2 = tk.Frame(window)
    button_frame2.pack(side=tk.BOTTOM)
    
    figure_frame = tk.Frame(window)
    figure_frame.pack(fill=tk.BOTH,  side=tk.TOP)
    
    
    # Create the FigureCanvasTkAgg object
    canvas = FigureCanvasTkAgg(fig, master=figure_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, ipady=20)
    
    
    Save_button = tk.Button(button_frame2, text="Save", 
                              command=saveonefig)
    SaveAll_button = tk.Button(button_frame2, text="Save all", 
                              command=saveallfig)
    Exit_button = tk.Button(button_frame2, text="Exit", 
                              command=lambda: window.destroy())
    
    Save_button.pack(side=tk.LEFT)
    SaveAll_button.pack(side=tk.LEFT)
    Exit_button.pack(side=tk.LEFT)


    #progress bar
    progressbar = ttk.Progressbar(window, orient=tk.HORIZONTAL, length=400)
    progressbar.pack(side=tk.BOTTOM)
    
    # Run the Tkinter event loop
    window.mainloop()

def repeditor(df, pa, title, table_df, id, repnames, repPA_all_df, outmod=1.5):
    
    """
    Open a Tkinter GUI for interactive editing of data points in a DataFrame.

    Parameters:
    - df (pd.DataFrame): The main DataFrame containing data points.
    - pa (pd.DataFrame): DataFrame with additional information for annotations.
    - title (str): The title of the Tkinter window.
    - table_df (pd.DataFrame): DataFrame to display in a table in the GUI.
    - id (int): Identifier for the current instance.

    Returns:
    - pd.DataFrame: A modified DataFrame after user interaction.

    This function opens a Tkinter window with an embedded Matplotlib plot, allowing
    users to interactively select and edit data points. The user can choose an isotope
    from a dropdown menu, click on points in the plot to mark them for removal or restoration,
    and view additional information in tables.

    The function utilizes global variables for efficiency and includes a nested function
    for handling pick events on the plot. It provides functionality for updating the plot,
    handling dropdown menu changes, and displaying tables with updated data.

    The GUI consists of a scatter plot with different markers for removal, keeping, and
    recommended outliers. Tables are displayed alongside the plot, showing data and annotations.

    Note: The function relies on the Matplotlib, Pandas, and Tkinter libraries.

    Example:
    import pandas as pd
    import numpy as np
    import tkinter as tk
    from tkinter import ttk
    import matplotlib.pyplot as plt

    # Assuming necessary variables are defined (e.g., repnames, repPA_all_df)
    modified_df = repeditor(df, pa, "Interactive Editor", table_df, 1)
    """
    
    from Pygilent.pygilent import find_outliers
    
    global selected_ind, variable
    xvar=np.arange(len(repnames))+1
    df2=df.copy()
    variable=df['isotope_gas'].values[0]
    selected_ind={k: np.array([], dtype=int) for k in df['isotope_gas'].values}
    
    def on_pick(event):
        global ind, selected_ind
        ind = event.ind

        newind=np.setdiff1d(ind, selected_ind[variable])
        
        #If the user has selected a new unselected point
        if newind.size>0:
            #Save the data index to the dictionary of isotopes
            selected_ind[variable]=np.append(selected_ind[variable], newind)
            df2.loc[variable, repnames[ind]]=np.nan    
        #If the user has clicked on an already selected point    
        else:
            selected_ind[variable]=np.setdiff1d(selected_ind[variable], ind)
            df2.loc[variable, repnames[ind]]=df.loc[variable, repnames[ind]]
        #Re-calculate means, standard deviations, and quartiles    
        iso_mean=np.nanmean(df2.loc[variable,repnames])
        iso_sd=np.nanstd(df2.loc[variable,repnames])
        q75, q25 = np.percentile(df2.loc[variable, repnames], [75 ,25])
        
        #Re-draw the figure
        scatter2.set_data(xvar, df2.loc[variable, repnames])
        mean_line.set_ydata([iso_mean, iso_mean])
        sd_line_upper.set_ydata([iso_mean+iso_sd*2, iso_mean+iso_sd*2])
        out_line_upper.set_ydata([q75+(q75-q25)*outmod, q75+(q75-q25)*outmod])
        sd_line_lower.set_ydata([iso_mean-iso_sd*2, iso_mean-iso_sd*2])
        out_line_lower.set_ydata([q25-(q75-q25)*outmod, q25-(q75-q25)*outmod])
        fig.canvas.draw_idle()
    
    
    # Create the initial plot without showing the figure
    fig, ax = plt.subplots()
    scatter1, = ax.plot([], [], linestyle='None', marker='o', color='red', picker=5, mec='r')
    scatter2, = ax.plot([], [], linestyle='None', marker='o', color='blue', mec='b')
    scatter_outs, = ax.plot([], [], linestyle='None', marker='o', 
                            mfc='none', mec='r', mew=1)
    mean_line=ax.axhline(y=0, ls='-', color='black')
    sd_line_upper=ax.axhline(y=0, ls='--', color='black')
    out_line_upper=ax.axhline(y=0, ls=':', color='black')
    sd_line_lower=ax.axhline(y=0, ls='--', color='black')
    out_line_lower=ax.axhline(y=0, ls=':', color='black')
    PA_annotate_ls=[ax.text(0, 0, [], fontsize=12, ha='right', va='bottom') 
                    for rep in repnames]
    
    ax.set_xlabel('Replicate number')
    ax.set_ylabel(variable)
    ax.legend(['Remove', 'Keep', 'Recommend (outlier)', 'Mean', '2$\sigma$', 'outlier threshold'])
    
    # Register the pick event
    fig.canvas.mpl_connect('pick_event', on_pick)
    
    plt.close(fig)  # Close the figure to prevent it from being displayed
    
    
    
    # Define the update function for the dropdown (changing isotopes)
    def update_y_axis(*args):
        global variable
        variable = dropdown_var.get()
        
        #Show the outliers recommended for removal
        outs=find_outliers(df.loc[variable, repnames].astype(float), mod=outmod)
        
        #calculate the means, sd and quartiles
        iso_mean=np.nanmean(df2.loc[variable,repnames])
        iso_sd=np.nanstd(df2.loc[variable,repnames])
        q75, q25 = np.percentile(df2.loc[variable, repnames], [75 ,25])
        
        #Re-draw the figure
        scatter1.set_data(xvar, df.loc[variable, repnames])
        scatter2.set_data(xvar, df2.loc[variable, repnames])
        scatter_outs.set_data(xvar[outs], df2.loc[variable, repnames[outs]])
        mean_line.set_ydata([iso_mean, iso_mean])
        sd_line_upper.set_ydata([iso_mean+iso_sd*2, iso_mean+iso_sd*2])
        out_line_upper.set_ydata([q75+(q75-q25)*outmod, q75+(q75-q25)*outmod])
        sd_line_lower.set_ydata([iso_mean-iso_sd*2, iso_mean-iso_sd*2])
        out_line_lower.set_ydata([q25-(q75-q25)*outmod, q25-(q75-q25)*outmod])
        
        for i, txt in enumerate(PA_annotate_ls):
            txt.set_position((xvar[i], df.loc[variable, repnames[i]].astype(float)))
            PA_text=pa.loc[variable, repnames[i]]
            txt.set_text(PA_text)
        
        ax.set_ylabel(variable)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()
        
        new_PA_run_df=repPA_all_df[['sample_name', variable]].copy()
        new_PA_run_df.insert(0, 'Index', np.arange(len(repPA_all_df)))
        
        #Change the 2nd table contents
        for iid in list(PA_run_table.get_children()):
            PA_run_table.delete(iid)
        
        PA_run_table.heading(col, text=col)
        
        for index, row in new_PA_run_df.iterrows():
            if index==id:
                PA_run_table.insert(parent='', index='end', 
                                    iid=index, values=list(row), tags='sample') 
            else:
                PA_run_table.insert(parent='', index='end', iid=index, values=list(row))
        PA_run_table.tag_configure('sample', background='yellow')
        
        
        
    
    # Create the Tkinter window
    window = tk.Tk()
    window.title(title)
    
    #Keep the window at the front of other apps.
    window.lift()
    window.attributes("-topmost", True)
    
    plot_frame = ttk.Frame(window)
    plot_frame.grid(row=0, column=0, sticky='nsew', rowspan=2)
    
    table_frame = ttk.Frame(window)
    table_frame.grid(row=0, column=1, sticky='new')
    
    table_2_frame = ttk.Frame(window)
    table_2_frame.grid(row=1, column=1, sticky='sew')    
    
    
        # Create a treeview widget for the table
    outlier_table = ttk.Treeview(table_frame, columns=table_df.columns, show='headings')
    
        # Define columns based on DataFrame columns
    outlier_table['columns'] = list(table_df.columns)

    # Set column headings
    for col in table_df.columns:
        outlier_table.heading(col, text=col)
    
    # Insert data from DataFrame
    for index, row in table_df.iterrows():
        outlier_table.insert(parent='', index='end', iid=index, values=list(row))

    # Pack the table
    outlier_table.pack(expand=tk.YES, fill=tk.BOTH)
    
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=outlier_table.yview)
    vsb.pack(side='right', fill='y')
    outlier_table.configure(yscrollcommand=vsb.set)
    
    #Start table
    
    PA_template_df=pd.DataFrame({'Index': np.arange(len(repPA_all_df)), 
                                 'sample_name': repPA_all_df['sample_name'].values, 
                                    'Isotope': np.array(['']*len(repPA_all_df))})

    
        # Create a treeview widget for the table
    PA_run_table = ttk.Treeview(table_2_frame, columns=PA_template_df.columns, show='headings')
    
        # Define columns based on DataFrame columns
    PA_run_table['columns'] = list(PA_template_df.columns)

    # Set column headings
    for col in PA_template_df.columns:
        PA_run_table.heading(col, text=col)
    
    # Insert data from DataFrame
    for index, row in PA_template_df.iterrows():
        if index==id:
            PA_run_table.insert(parent='', index='end', 
                                iid=index, values=list(row), tags='sample') 
        else:
            PA_run_table.insert(parent='', index='end', iid=index, values=list(row))
    PA_run_table.tag_configure('sample', background='yellow')

    # Pack the table
    PA_run_table.pack(expand=tk.YES, fill=tk.BOTH)
    
    vsb = ttk.Scrollbar(table_2_frame, orient="vertical", command=PA_run_table.yview)
    vsb.pack(side='right', fill='y')
    PA_run_table.configure(yscrollcommand=vsb.set)
    

    # Configure grid weights to make the frames resizable
    window.grid_rowconfigure(0, weight=1)
    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    

    
    # Create the dropdown menu
    dropdown_var = tk.StringVar(plot_frame)
    dropdown_var.set('Choose an isotope')  
    dropdown = tk.OptionMenu(plot_frame, dropdown_var, *df['isotope_gas'].values, 
                             command=update_y_axis)
    dropdown.pack(padx=10, pady=10)
    
    
    submit_button = tk.Button(plot_frame, text="Submit", 
                              command=lambda: window.destroy())
    submit_button.pack( side = tk.BOTTOM)


    # Create the FigureCanvasTkAgg object
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    
    # Run the Tkinter event loop
    window.mainloop()
    
    
    return df2

def ratioel_rep_removal(df, repnames, ratioels, isotopes, Gasmodes):
    
    """
    Remove data points corresponding to certain ratio elements (ratioels) from a DataFrame.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing data points.

    Returns:
    - pd.DataFrame: A modified DataFrame after removing specified ratio elements.

    This function identifies and removes data points in the DataFrame where the isotope_gas
    corresponds to specific ratio elements defined in the global variable ratioels. The removal
    is based on the presence of NaN values in the columns specified by the global variable repnames.
    The function iterates through the identified points and updates the DataFrame accordingly.

    Parameters such as repnames, ratioels, isotopes, Gasmodes, and rep_cps_long_df are assumed
    to be defined globally.

    Example:
    import pandas as pd
    import numpy as np

    # Assuming necessary variables are defined (e.g., repnames, ratioels, isotopes, Gasmodes)
    modified_df = ratioel_rep_removal(df)
    """
    
    out_idx=np.any(np.isnan(df[repnames]), axis=1)
    out_iso=df.loc[out_idx, 'isotope_gas']
    if np.any(np.isin(out_iso, list(ratioels.values()))):
        ratioel_out_idx=out_iso.loc[np.isin(out_iso, list(ratioels.values()))].index
        for i in ratioel_out_idx:
            out_ratio_el=df.loc[i, 'isotope_gas']
            out_gasmode=Gasmodes[i%len(isotopes)]
            isos_in_gasmode=isotopes[Gasmodes==out_gasmode]
            idx=(np.isin(df['isotope_gas'], isos_in_gasmode)
                    &(df['run_order']==df.loc[i, 'run_order']))
            
            
            
            out_array=np.array([list(pd.isna(df.loc[i, repnames]))]*len(isos_in_gasmode))
            
            df.loc[idx, repnames]= np.where(out_array, np.nan, df.loc[idx, repnames])
    
    return df

def setup_progress_bar(text=''):
    
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

    l = tk.Label(root, text = text)
    l.pack(side=tk.TOP)
    progressbar.pack(side=tk.BOTTOM)
    progressbar['value']=0  
    progressbar.update()
    return root, progressbar
