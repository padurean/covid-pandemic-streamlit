import pandas as pd
import streamlit as st
import altair as alt

# column names constants
DATE_COL = 'date'
LOCATION_COL = 'location'
# deaths columns
NEW_DEATHS_COL = 'new_deaths'
NEW_DEATHS_PER_MILLION_COL = 'new_deaths_per_million'
NEW_DEATHS_SMOOTHED_PER_MILLION_COL = 'new_deaths_smoothed_per_million'
# cases columns
NEW_CASES_COL = 'new_cases'
NEW_CASES_PER_MILLION_COL = 'new_cases_per_million'
NEW_CASES_SMOOTHED_PER_MILLION_COL = 'new_cases_smoothed_per_million'

# page header
st.markdown(
  """### COVID Pandemic :mag_right: Visual Data Explorer
  <small>_data is refreshed each 3 hours from
  [OurWorldInData.org](https://github.com/owid/covid-19-data/tree/master/public/data)_</small>""",
  unsafe_allow_html=True)

#===> functions definitions
# loads the data (cached for 3 hours)
@st.experimental_memo(ttl=3*60*60)
def load_data():
  return pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv', parse_dates=[DATE_COL])

# create and shows a chart
def show_rel_chart(kind, rel_unit, df, smoothed, show_mean, abs_col, rel_col, rel_col_smoothed):
  # configure column and labels depending on the smoothing option
  col = rel_col_smoothed
  smoothed_label = ' (smoothed)'
  if not smoothed:
    col = rel_col
    smoothed_label = ''

  abs_title = 'New '+ kind
  rel_title = abs_title +' per ' + rel_unit
  smoothed_title = rel_title + ' (smoothed)'
  title = rel_title + smoothed_label

  # data lines
  lines = alt.Chart(title=title).mark_line(point=True).encode(
    x=alt.X(DATE_COL+':T', title='', axis=alt.Axis(format = ("%-d %b"))),
    y=alt.Y(col, title=title),
    color=alt.Color(LOCATION_COL, title='Location'),
    tooltip=[
      alt.Tooltip(DATE_COL, title='Date', format=('%-d %b %Y')),
      alt.Tooltip(LOCATION_COL, title='Location'),
      alt.Tooltip(abs_col, title=abs_title),
      alt.Tooltip(rel_col, title=rel_title),
      alt.Tooltip(rel_col_smoothed, title=smoothed_title),
    ])
  all_lines = [lines]

  # data mean lines
  if show_mean:
    mean_lines = alt.Chart().mark_rule(strokeDash=[5,1]).encode(
      y='mean('+rel_col+')',
      color=LOCATION_COL,
      size=alt.SizeValue(2),
      tooltip=[
        alt.Tooltip('mean('+rel_col+')', title='Mean (not smoothed)'),
        alt.Tooltip(LOCATION_COL, title='Location')
      ])
    all_lines.append(mean_lines)

  # create and show chart with all lines
  chart = alt.layer(*all_lines, data=df).configure_legend(orient='bottom')
  st.altair_chart(chart, use_container_width=True)
#<===

#===> main script
# load data
df = load_data()

#--> show user inputs and filter data
config_expander = st.expander('⚙️ Configure', expanded=False)

all_locations = sorted(df[LOCATION_COL].unique())
with config_expander:
  # data kind
  kind = st.selectbox("Data:", ('deaths', 'cases'), index=0, format_func=lambda x: x.capitalize())
  # locations multiselect input
  locations = st.multiselect('Locations:', all_locations, default=['Germany', 'Sweden', 'Romania'])
  if not locations:
    ':no_entry: Please select at least one location.'
    st.stop()

# filter data
abs_col=NEW_DEATHS_COL
rel_col=NEW_DEATHS_PER_MILLION_COL
rel_col_smoothed=NEW_DEATHS_SMOOTHED_PER_MILLION_COL
if kind == 'cases':
  abs_col=NEW_CASES_COL
  rel_col=NEW_CASES_PER_MILLION_COL
  rel_col_smoothed=NEW_CASES_SMOOTHED_PER_MILLION_COL

df = df[df[LOCATION_COL].isin(locations)]
df_sub = df[[DATE_COL,LOCATION_COL,abs_col,rel_col,rel_col_smoothed]]
df_sub = df_sub[df_sub[rel_col].notnull()]

dates = sorted(pd.to_datetime(df_sub[DATE_COL]).dt.date.unique().tolist())
with config_expander:
  # dates range input
  start_date, end_date = st.select_slider(
    'Period:',
    options=dates,
    value=(dates[-90], dates[-1]),
    format_func=(lambda x: x.strftime("%b'%y")))

  col1, col2, _ = st.columns(3)
  with col1:
    # 7-day smoothed option
    smoothed = st.checkbox('7-day smoothed', value=True)
  with col2:
    # show/hide mean option
    show_mean = st.checkbox('Show mean', value=True)
#<--

#--> filter data and show charts
# filter data for selected dates
df_in_range = df_sub[
  (df_sub[DATE_COL] >= pd.Timestamp(start_date)) &
  (df_sub[DATE_COL] <= pd.Timestamp(end_date))
]
# show the relative chart
show_rel_chart(
  kind=kind,
  rel_unit='million',
  df=df_in_range,
  smoothed=smoothed,
  show_mean=show_mean,
  abs_col=abs_col,
  rel_col=rel_col,
  rel_col_smoothed=rel_col_smoothed)
#<--
#<===
