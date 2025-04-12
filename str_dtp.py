import datetime
import time

import streamlit as st
import data_trump_polls as dtp
import altair as alt

UPDATE_INTERVAL = 60 * 60  # 1 hour in seconds

# Load the dataset
(df_polls, df_new) = dtp.read_dataset(sheet_id=dtp.SHEET_ID, sheet_name=dtp.SHEET_NAME)

# Calculate the approval column
df_polls['approval'] = df_polls['yes'] - df_polls['no']

# Streamlit app title
st.set_page_config(page_title="Approval Ratings Dashboard", layout="wide")
st.title("Approval Ratings Dashboard")


# Define a color scale 
color_scale = alt.Scale(
    domain=['yes', 'no', 'approval'],
    range=['green', 'red', 'blue']  # Blue for 'yes', Red for 'no', Green for 'approval'
)

# Create an Altair chart for visualization
st.write("### Approval Ratings Over Time")
chart = alt.Chart(df_polls).mark_circle(size=40).encode(
    x=alt.X('end_date:T', title='Date'),
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
st.write(f"Last Poll: {last_row['end_date']:%Y-%m-%d} by {last_row['pollster']} ({last_row['sponsors']}).  Last check: {last_update:%Y-%m-%d %H:%M:%S}, next: {next_update:%Y-%m-%d %H:%M:%S}.")

# Credit the data source
st.write("(Poll data from Mary Radcliffe [public database of polls](https://docs.google.com/spreadsheets/d/1_y0_LJmSY6sNx8qd51T70n0oa_ugN50AVFKuJmXO1-s/edit?usp=sharing))")


time.sleep(60*60)  # Sleep for 1 hour (3600 seconds)
st.rerun()