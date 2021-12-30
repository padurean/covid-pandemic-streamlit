import pandas as pd
import streamlit as st
import altair as alt

DATE_COLUMN = 'date'
LOCATION_COLUMN = 'location'
NEW_DEATHS_COLUMN = 'new_deaths'
NEW_DEATHS_PER_MILLION_COLUMN = 'new_deaths_per_million'

"""### COVID Pandemic - Visual Data Explorer
Data is retrieved from [OurWorldInData.org](https://github.com/owid/covid-19-data/tree/master/public/data)"""

# --> data
# cache the data for 3 hours
@st.experimental_memo(ttl=3*60*60)
def load_data():
  return pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv', parse_dates=[DATE_COLUMN])

df = load_data()
# <-- data

# --> user inputs and filtered data
# countries multiselect input
all_countries = df[LOCATION_COLUMN].unique()
countries = st.sidebar.multiselect("Countries", all_countries, default=['Germany', 'Sweden', 'Romania'])

# filter data
df = df[df[LOCATION_COLUMN].isin(countries)]
# df
df_deaths = df[[DATE_COLUMN,LOCATION_COLUMN,NEW_DEATHS_PER_MILLION_COLUMN,NEW_DEATHS_COLUMN]]
df_deaths = df_deaths[
  # df_deaths[DATE_COLUMN].notnull() &
  df_deaths[NEW_DEATHS_PER_MILLION_COLUMN].notnull()
  # df_deaths[NEW_DEATHS_COLUMN].notnull()
]
# df_deaths

# dates range input
dates = sorted(pd.to_datetime(df_deaths[DATE_COLUMN]).dt.date.unique().tolist())
start_date, end_date = st.sidebar.select_slider(
  'Show for period',
  options=dates,
  value=(dates[-200], dates[-1]),
  format_func=(lambda x: x.strftime("%Y/%m")))
# <-- user inputs

# --> chart
df_deaths_in_range = df_deaths[
  (df_deaths[DATE_COLUMN] >= pd.Timestamp(start_date)) &
  (df_deaths[DATE_COLUMN] <= pd.Timestamp(end_date))
]
deaths_lines = alt.Chart().mark_line(point=True).encode(
  x=alt.X(DATE_COLUMN, title="Date"),
  y=alt.Y(NEW_DEATHS_PER_MILLION_COLUMN, title='New Deaths per Million'),
  color=alt.Color(LOCATION_COLUMN, title='Country'),
  tooltip=[DATE_COLUMN, LOCATION_COLUMN, NEW_DEATHS_PER_MILLION_COLUMN, NEW_DEATHS_COLUMN]
)
deaths_mean_lines = alt.Chart().mark_rule(strokeDash=[5,1]).encode(
  y='mean('+NEW_DEATHS_PER_MILLION_COLUMN+')',
  color=LOCATION_COLUMN,
  size=alt.SizeValue(2),
  tooltip=[
    alt.Tooltip('mean('+NEW_DEATHS_PER_MILLION_COLUMN+')', title="Mean"),
    alt.Tooltip(LOCATION_COLUMN, title="Country")
  ])
chart = alt.layer(
  deaths_lines,
  deaths_mean_lines,
  data=df_deaths_in_range
).properties(
  width=750,
  height=350
).interactive()

st.altair_chart(chart)
# <-- chart
