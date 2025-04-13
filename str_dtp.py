import typing as t
import os
import datetime
import time
import dotenv
import pandas as pd

import streamlit as st
import data_trump_polls as dtp
import data_fred
import altair as alt

VERSION = "0.3.0"
DATE_RANGE = t.Tuple[datetime.datetime, datetime.datetime]

dotenv.load_dotenv()

def get_env_int(key: str, default: int) -> int:
    """
    Get an integer from the environment variable or return the default value.
    """
    value = os.getenv(key)
    if value is not None:
        try:
            return int(value)
        except ValueError:
            pass
    return default

def whole_day_range(days_of_history: int) -> DATE_RANGE:
    """
    Get the current date range for the whole day.
    """
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end = today + datetime.timedelta(days=1)
    start = end - datetime.timedelta(days=days_of_history)
    return (start, end)

UPDATE_INTERVAL = get_env_int('UPDATE_INTERVAL', 3600)  
UPDATE_POLLS_INTERVAL = get_env_int('UPDATE_POLLS_INTERVAL', 100000) 
DAYS_OF_HISTORY = get_env_int('DAYS_OF_HISTORY', 90)  # Default to 30 days




@st.cache_data(ttl=UPDATE_POLLS_INTERVAL)
def presidential_approval_read(sheet_id: str, sheet_name:str)  -> t.Tuple[pd.DataFrame, pd.DataFrame]:
    ''' Cash the polling data. '''
    return dtp.read_dataset(sheet_id=dtp.SHEET_ID, sheet_name=dtp.SHEET_NAME)[0]



def presidential_approval_polls(date_range: DATE_RANGE):

    # Load the dataset
    df_polls = presidential_approval_read(sheet_id=dtp.SHEET_ID, sheet_name=dtp.SHEET_NAME)
    # Trim the dataframe to the specified date range
    df_polls = df_polls[(df_polls['end_date'] >= date_range[0]) & (df_polls['end_date'] < date_range[1])]
    # Calculate the approval column
    df_polls['approval'] = df_polls['yes'] - df_polls['no']


    # Define a color scale 
    color_scale = alt.Scale(
        domain=['yes', 'no', 'approval'],
        range=['green', 'red', 'blue']  # Blue for 'yes', Red for 'no', Green for 'approval'
    )

    # Default the date scale to our full date range.  This makes ageing of the latest poll more obvious.
    date_scale = alt.Scale(domain=[date_range[0], date_range[1]])

    # Create an Altair chart for visualization
    st.write("### Presidential Approval Polls")
    chart = alt.Chart(df_polls).mark_circle(size=40).encode(
        x=alt.X('end_date:T', title='Date', scale=date_scale),
        y=alt.Y('value:Q', title='Percentage'),
        color=alt.Color('variable:N', scale=color_scale, legend=alt.Legend(title="Legend")),
        tooltip=['end_date:T', 'value:Q', 'pollster:N', 'sponsors:N', 'sample_size:Q']
    ).transform_fold(
        ['yes', 'no', 'approval'],  # Columns to plot
        as_=['variable', 'value']   # Fold into variable and value columns
    ).properties(
        width='container',  # Automatically adjust width to container
        height=500          # Set an initial height (can be adjusted dynamically)
    ).interactive()

    # Display the chart
    st.altair_chart(chart, use_container_width=True)

    # Last update summary
    last_row = df_polls.iloc[-1]
    last_update = datetime.datetime.now()
    next_update = last_update + datetime.timedelta(seconds=UPDATE_INTERVAL)
    st.markdown(f"""
**Last Poll**: {last_row['end_date']:%Y-%m-%d} by {last_row['pollster']} ({last_row['sponsors']}).  **Last check:** {last_update:%Y-%m-%d %H:%M:%S}, **next:** {next_update:%Y-%m-%d %H:%M:%S}.
(Poll data from Mary Radcliffe [public database of polls](https://docs.google.com/spreadsheets/d/1_y0_LJmSY6sNx8qd51T70n0oa_ugN50AVFKuJmXO1-s/edit?usp=sharing))""")


def load_sp500(date_range: DATE_RANGE) -> pd.DataFrame:
    return data_fred.download_from_fred(
        start_date=date_range[0].strftime("%Y-%m-%d"),
        end_date=date_range[1].strftime("%Y-%m-%d"),
        series_id="SP500"
    )


def sp500_chart(date_range: DATE_RANGE):
    # Load the S&P 500 data
    df_sp500 = load_sp500(date_range)

    # Create an Altair chart for visualization
    # Define a scale for the y-axis based on the min and max values of the Close column
    y_scale = alt.Scale(domain=[df_sp500['Close'].min()-400, df_sp500['Close'].max()+400])
    date_scale = alt.Scale(domain=[date_range[0], date_range[1]])
    
    st.write("### S&P 500 Close of Day")
    
    chart = alt.Chart(df_sp500).mark_line().encode(
        x=alt.X('Date:T', title='Date', scale=date_scale),
        y=alt.Y('Close:Q', title='S&P 500 Close', scale=y_scale),
        tooltip=['Date:T', 'Close:Q']
    ).properties(
        width='container',  # Automatically adjust width to container
        height=500          # Set an initial height (can be adjusted dynamically)
    ).interactive()

    # Display the chart
    st.altair_chart(chart, use_container_width=True)





# Dates we cover
date_range = whole_day_range(DAYS_OF_HISTORY)

# Streamlit app title
st.set_page_config(page_title="Approval Ratings Dashboard", layout="wide")
st.title("Political Climate Dashboard")

presidential_approval_polls(date_range)
sp500_chart(date_range)

st.markdown(f"version: {VERSION}")

time.sleep(60*60)  # Sleep for 1 hour (3600 seconds)
st.rerun()