
from  importlib import resources
import pandas as pd
import numpy as np
from Pygilent.Pygilent import iso_to_el

def get_default_stndvals():
    """Get path to example "Flatland" [1]_ text file.

    Returns
    -------
    pathlib.PosixPath
        Path to file.

    References
    ----------
    .. [1] E. A. Abbott, "Flatland", Seeley & Co., 1884.
    """
    with resources.path("Pygilent.data", "stndvals.csv") as f:
        stndvals_default_df = pd.read_csv(f, index_col=0)
    return stndvals_default_df


def make_stndvals_df(df, stnd_names, isotopes):
    new_df=pd.DataFrame()
    for iso in isotopes:
        vals=np.array(df.loc[iso_to_el(iso), stnd_names])
        vals_df=pd.DataFrame(dict(zip(stnd_names, vals)), index=[iso])
        units=df.loc[iso_to_el(iso), 'Units']
        vals_df.insert(0, 'Units', units)
        new_df=pd.concat([new_df, vals_df], axis=0)
    return new_df

