import typing as t
import pandas as pd

# Read data from 

SHEET_ID = '1_y0_LJmSY6sNx8qd51T70n0oa_ugN50AVFKuJmXO1-s'
SHEET_NAME = 'president_approval_polls'

def read_dataset(df_current: pd.DataFrame | None = None, url: str|None = None, sheet_id: str|None = None, sheet_name: str|None = None) -> t.Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Read the dataset from the Google Sheets URL and return it as a DataFrame.
    If df_current is provided, return the new rows as a separate DataFrame.


    :param df_current: Current DataFrame to compare with (optional).
    :param url: Google Sheets URL (optional).
    :param sheet_id: Google Sheets ID (optional).
    :param sheet_name: Google Sheets name (optional).
    :return: Tuple of DataFrames (current data, new data).
    
    """
    if url is None and (sheet_id is None and sheet_name is None):
        raise ValueError("Either url or both sheet_id and sheet_name must be provided.")
    if url is None:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

    # Read from a google sheet and drop empty rows.
    df = pd.read_csv(url) # parse_dates=['start_date', 'end_date'], dayfirst=True)
    df = df.dropna(subset=['end_date'])

    # Convert date columns to datetime format
    #format = "%d/%m/%y"
    format = "mixed"
    df['start_date'] = pd.to_datetime(df['start_date'], format=format, dayfirst=False)
    df['end_date'] = pd.to_datetime(df['end_date'], format=format, dayfirst=False)
    df = df.sort_values(by='end_date')


    # Create a new DF with only the new rows.
    if df_current is not None:
        # Compare to existing.
        df_new = df.merge(df_current, how='outer', indicator=True).query('_merge == "left_only"').drop(columns=['_merge'])
    else:
        # No existing DF, so create a new, empty one.
        df_new = pd.DataFrame(columns=df.columns)
    return df, df_new