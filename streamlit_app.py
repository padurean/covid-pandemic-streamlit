import pandas as pd
import streamlit as st
import altair as alt

# column names constants
DATE_COL = 'date'
LOCATION_COL = 'location'
POPULATION_COL = 'population'
# deaths columns
NEW_DEATHS_COL = 'new_deaths'
NEW_DEATHS_PER_MILLION_COL = 'new_deaths_per_million'
NEW_DEATHS_SMOOTHED_PER_MILLION_COL = 'new_deaths_smoothed_per_million'
TOTAL_DEATHS_COL = 'total_deaths'
TOTAL_DEATHS_PER_MILLION_COL = 'total_deaths_per_million'
# ICU patients
ICU_PATIENTS_COL = 'icu_patients'
ICU_PATIENTS_PER_MILLION_COL = 'icu_patients_per_million'
# Hospitalized patients
HOSP_PATIENTS_COL = 'hosp_patients'
HOSP_PATIENTS_PER_MILLION_COL = 'hosp_patients_per_million'
# cases columns
NEW_CASES_COL = 'new_cases'
NEW_CASES_PER_MILLION_COL = 'new_cases_per_million'
NEW_CASES_SMOOTHED_PER_MILLION_COL = 'new_cases_smoothed_per_million'
# vaccinations columns
PEOPLE_FULLY_VACCINATED_COL = 'people_fully_vaccinated'
PEOPLE_FULLY_VACCINATED_PER_HUNDRED_COL = 'people_fully_vaccinated_per_hundred'
# booster vaccinations columns
TOTAL_BOOSTERS_COL = 'total_boosters'
TOTAL_BOOSTERS_PER_HUNDRED_COL = 'total_boosters_per_hundred'
# reproduction rate
REPRODUCTION_RATE_COL = 'reproduction_rate'

# set wide mode by default - i.e. occupy as much page width as possible
st.set_page_config(layout='wide')

# page header
st.markdown(
  '''
  ### <span style="font-size: 2em;line-height:1em;vertical-align:middle;">🦠</span> COVID Pandemic :mag_right: Visual Data Explorer
  <small>_data is refreshed each 3 hours from
  [OurWorldInData.org](https://github.com/owid/covid-19-data/tree/master/public/data)_</small>
  ''',
  unsafe_allow_html=True)

#===> functions definitions
# loads the data (cached for 3 hours)
@st.experimental_memo(ttl=3*60*60)
def load_data():
  return pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv', parse_dates=[DATE_COL])

# create and shows a chart
def show_chart(kind_label, rel_unit, df, smoothed, show_mean, abs_col, rel_col, rel_col_smoothed, abs_format, extra_tooltips):
  # configure column and labels depending on the smoothing option
  col = rel_col_smoothed
  smoothed_label = ' (smoothed)'
  if not smoothed:
    if rel_col != '':
      col = rel_col
    else:
      col = abs_col
    smoothed_label = ''

  abs_title = kind_label
  rel_title = abs_title + ' ' + rel_unit
  smoothed_title = rel_title + ' (smoothed)'
  if rel_col != '':
    title = rel_title + smoothed_label
  else:
    title = abs_title

  # data lines tooltips
  tooltips = [
    alt.Tooltip(DATE_COL, title='Date', format=('%-d %b %Y')),
    alt.Tooltip(LOCATION_COL, title='Location'),
    alt.Tooltip(POPULATION_COL, title='Population', format='~s'),
    alt.Tooltip(abs_col, title=abs_title, format=abs_format),
  ]
  if rel_col != '':
    tooltips.append(alt.Tooltip(rel_col, title=rel_title))
  if rel_col_smoothed != '':
    tooltips.append(alt.Tooltip(rel_col_smoothed, title=smoothed_title))
  if bool(extra_tooltips):
    for extra_col, title_and_fmt in extra_tooltips.items():
      tooltips.append(alt.Tooltip(extra_col, title=title_and_fmt['title']+":", format=title_and_fmt['fmt']))
  # data lines
  lines = alt.Chart(title=title).mark_line(point=True).encode(
    x=alt.X(DATE_COL+':T', title='', axis=alt.Axis(format = ("%-d %b"))),
    y=alt.Y(col, title=title),
    color=alt.Color(LOCATION_COL, title='Location'),
    tooltip=tooltips)
  all_lines = [lines]

  # data mean lines
  if show_mean:
    mean_col = rel_col
    if mean_col == '':
      mean_col = rel_col
    not_smoothed_suffix = ''
    if smoothed:
      not_smoothed_suffix = ' (not smoothed)'
    mean_lines = alt.Chart().mark_rule(strokeDash=[5,1]).encode(
      y='mean('+mean_col+')',
      color=LOCATION_COL,
      size=alt.SizeValue(2),
      tooltip=[
        alt.Tooltip('mean('+mean_col+')', title='Mean'+not_smoothed_suffix),
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
  kinds = ['deaths', 'ICU patients', 'hospital patients', 'cases', 'vaccinations', 'boosters', 'reproduction rate']
  kind = st.selectbox("Data:", kinds, index=0, format_func=lambda x: "%s%s" % (x[0].upper(), x[1:]))
  # locations multiselect input
  locations = st.multiselect('Locations:', all_locations, default=['Germany', 'Sweden', 'Romania'])
  if not locations:
    ':no_entry: Please select at least one location.'
    st.stop()

# filter data
rel_col=''
rel_col_smoothed=''
extra_cols = []
extra_tooltips = {}
if kind == 'deaths':
  abs_col=NEW_DEATHS_COL
  rel_col=NEW_DEATHS_PER_MILLION_COL
  rel_col_smoothed=NEW_DEATHS_SMOOTHED_PER_MILLION_COL
  extra_cols = [TOTAL_DEATHS_COL, TOTAL_DEATHS_PER_MILLION_COL]
  extra_tooltips = {
    TOTAL_DEATHS_COL: {'title':'Total deaths', 'fmt':'~s'},
    TOTAL_DEATHS_PER_MILLION_COL: {'title':'Total deaths per million', 'fmt':'~f'}
  }
elif kind == 'ICU patients':
  abs_col=ICU_PATIENTS_COL
  rel_col=ICU_PATIENTS_PER_MILLION_COL
elif kind == 'hospital patients':
  abs_col=HOSP_PATIENTS_COL
  rel_col=HOSP_PATIENTS_PER_MILLION_COL
elif kind == 'cases':
  abs_col=NEW_CASES_COL
  rel_col=NEW_CASES_PER_MILLION_COL
  rel_col_smoothed=NEW_CASES_SMOOTHED_PER_MILLION_COL
elif kind == 'vaccinations':
  abs_col=PEOPLE_FULLY_VACCINATED_COL
  rel_col=PEOPLE_FULLY_VACCINATED_PER_HUNDRED_COL
elif kind == 'boosters':
  abs_col=TOTAL_BOOSTERS_COL
  rel_col=TOTAL_BOOSTERS_PER_HUNDRED_COL
elif kind == 'reproduction rate':
  abs_col=REPRODUCTION_RATE_COL

df = df[df[LOCATION_COL].isin(locations)]
if rel_col_smoothed != '':
  df_sub = df[[DATE_COL,LOCATION_COL,POPULATION_COL,abs_col,rel_col,rel_col_smoothed]+extra_cols]
  df_sub = df_sub[df_sub[rel_col].notnull()]
elif rel_col != '':
  df_sub = df[[DATE_COL,LOCATION_COL,POPULATION_COL,abs_col,rel_col]+extra_cols]
  df_sub = df_sub[df_sub[rel_col].notnull()]
else:
  df_sub = df[[DATE_COL,LOCATION_COL,POPULATION_COL,abs_col]+extra_cols]
  df_sub = df_sub[df_sub[abs_col].notnull()]

dates = sorted(pd.to_datetime(df_sub[DATE_COL]).dt.date.unique().tolist())
if not dates:
  ":no_entry: It looks like **no %s data** is available for the selected location(s) :man-shrugging:" % kind
  st.stop()
with config_expander:
  # dates range input
  start_date, end_date = st.select_slider(
    'Period:',
    options=dates,
    value=(dates[-90], dates[-1]),
    format_func=(lambda x: x.strftime("%b'%y")))

  smoothed = False
  show_mean = False
  if (kind == 'deaths') | (kind == 'cases'):
    col1, col2 = st.columns(2)
    with col1:
      # 7-day smoothed option
      smoothed = st.checkbox('7-day smoothed', value=True)
    with col2:
      # show/hide mean option
      show_mean = st.checkbox('Show mean', value=False)
  elif (kind == 'ICU patients') | (kind == 'hospital patients'):
    # show/hide mean option
    show_mean = st.checkbox('Show mean', value=False)
#<--

#--> filter data and show charts
# filter data for selected dates
df_in_range = df_sub[
  (df_sub[DATE_COL] >= pd.Timestamp(start_date)) &
  (df_sub[DATE_COL] <= pd.Timestamp(end_date))
]
# show the relative chart
kind_label = kind
rel_unit = 'per million'
abs_format = '~f'
if (kind == 'deaths') | (kind == 'cases'):
  kind_label = 'New ' + kind
elif (kind == 'ICU patients') | (kind == 'hospital patients'):
  kind_label = 'Total ' + kind
elif kind == 'vaccinations':
  kind_label = 'People fully vaccinated'
  rel_unit = '%'
  abs_format = '~s'
elif kind == 'boosters':
  kind_label = 'Total boosters'
  rel_unit = '%'
  abs_format = '~s'
elif kind == 'reproduction rate':
  kind_label = 'Reproduction rate'
  rel_unit = ''

show_chart(
  kind_label=kind_label,
  rel_unit=rel_unit,
  df=df_in_range,
  smoothed=smoothed,
  show_mean=show_mean,
  abs_col=abs_col,
  rel_col=rel_col,
  rel_col_smoothed=rel_col_smoothed,
  abs_format=abs_format,
  extra_tooltips=extra_tooltips)
#<--
#<===
