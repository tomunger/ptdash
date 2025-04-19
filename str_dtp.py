import typing as t
import os
import datetime
import time
import pandas as pd

import streamlit as st
import data_trump_polls as dtp
import data_fred
import altair as alt

VERSION = "0.3.4"
DATE_RANGE = t.Tuple[datetime.datetime, datetime.datetime]


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

HOUR_AS_SECONDS = 60 * 60
UPDATE_INTERVAL = get_env_int('UPDATE_INTERVAL', int(HOUR_AS_SECONDS / 2))  
UPDATE_POLLS_INTERVAL = get_env_int('UPDATE_POLLS_INTERVAL', 2 * HOUR_AS_SECONDS) 
UPDATE_STOCKS_INTERVAL = get_env_int('UPDATE_STOCKS_INTERVAL', 2 * HOUR_AS_SECONDS) 
DAYS_OF_HISTORY = get_env_int('DAYS_OF_HISTORY', 4*30)  




@st.cache_data(ttl=UPDATE_POLLS_INTERVAL)
def presidential_approval_read(sheet_id: str, sheet_name:str)  -> pd.DataFrame:
    ''' Cash the polling data. '''
    return dtp.read_nyt_dataset()



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
        x=alt.X('end_date:T', title="Date", scale=date_scale),
        y=alt.Y('value:Q', title='Percentage'),
        color=alt.Color('variable:N', scale=color_scale, legend=alt.Legend(title="Legend", orient="top")),
        href=alt.Href('url_article:N', title='URL'),            # Make each point a link to the article.
        tooltip=['end_date:T', 'value:Q', 'pollster:N', 'sponsors:N', 'sample_size:Q', 'url_article:N']
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
    # poll_credit = "Mary Radcliffe [public database of polls](https://docs.google.com/spreadsheets/d/1_y0_LJmSY6sNx8qd51T70n0oa_ugN50AVFKuJmXO1-s/edit?usp=sharing)"
    poll_credit = 'NY Times [Trump poll tracking](https://www.nytimes.com/interactive/polls/donald-trump-approval-rating-polls.html)'
    #st.markdown(f"**Last Poll**: {last_row['end_date']:%Y-%m-%d} by {last_row['pollster']} ({last_row['sponsors']}).  **Last check:** {last_update:%Y-%m-%d %H:%M:%S}, **next:** {next_update:%Y-%m-%d %H:%M:%S}"
    st.markdown(f"(Poll data from {poll_credit})")



@st.cache_data(ttl=UPDATE_STOCKS_INTERVAL)
def load_fred_data(date_range: DATE_RANGE, series: str) -> pd.DataFrame:
    return data_fred.download_from_fred(
        start_date=date_range[0].strftime("%Y-%m-%d"),
        end_date=date_range[1].strftime("%Y-%m-%d"),
        series_id=series
    )

def graph_fred_series(date_range: DATE_RANGE, series: str, title: str, y_label: str, height: int = 500, y_inset: int = 0):
    # Load the S&P 500 data
    df_fred = load_fred_data(date_range, series=series)

    st.write(f"### [{title}](https://fred.stlouisfed.org/series/{series})")
    if df_fred.empty:
        st.write(f"No data available for {series} in the specified date range.")
        return


    # Create an Altair chart for visualization
    # Define a scale for the y-axis based on the min and max values of the Close column
    y_scale = alt.Scale(domain=[df_fred["value"].min()-y_inset, df_fred["value"].max()+y_inset])
    date_scale = alt.Scale(domain=[date_range[0], date_range[1]])
    
    
    chart = alt.Chart(df_fred).mark_line().encode(
        x=alt.X("date:T", title="Date", scale=date_scale),
        y=alt.Y("value:Q", title=y_label, scale=y_scale),
        tooltip=["date:T", "value:Q"]
    ).properties(
        width='container',  # Automatically adjust width to container
        height=height          # Set an initial height (can be adjusted dynamically)
    ).interactive()

    # Display the chart
    st.altair_chart(chart, use_container_width=True)





# Dates we cover
date_range = whole_day_range(DAYS_OF_HISTORY)

# Streamlit app title
st.set_page_config(page_title="Approval Ratings Dashboard", layout="wide")
st.title("Political Climate Dashboard")

presidential_approval_polls(date_range)
graph_fred_series(date_range, series="SP500", title="S&P 500 Close of Day", y_label='S&P 500 Close', y_inset=200)
graph_fred_series(date_range, series="USEPUINDXD", title="FRED Uncertainty Index", y_label='Uncertainty')
graph_fred_series(date_range, series="CPIAUCNS", title="FRED Consumer Price Index", y_label='CPI', y_inset=10)
graph_fred_series(date_range, series="CORESTICKM159SFRBATL", title="FRED Sticky Price Consumer Price Index less Food and Energy", y_label='CPI % Change', y_inset=10)
graph_fred_series(date_range, series="UNRATE", title="FRED Unemployment Rate", y_label='Unemployment Rate', y_inset=0.5)
graph_fred_series(date_range, series="GDP", title="FRED GDP", y_label='GDP', y_inset=0.5)

st.markdown(f"version: {VERSION}")

time.sleep(60*60)  # Sleep for 1 hour (3600 seconds)
st.rerun()