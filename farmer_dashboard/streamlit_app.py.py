import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os
import calendar
from io import BytesIO

DATA_CSV = os.path.join(os.path.dirname(__file__), 'data', 'farmer_deaths.csv')

st.set_page_config(layout='wide', page_title='Farmer Deaths Dashboard')

@st.cache_data
def load_data():
    return pd.read_csv(DATA_CSV, parse_dates=['date'])

st.title('Farmer Deaths Dashboard (Synthetic Data 2000-2025)')

if not os.path.exists(DATA_CSV):
    st.error('Data file not found. Run data/generate_data.py to create the dataset.')
    st.stop()

df = load_data()

with st.sidebar:
    st.header('Filters')
    years = sorted(df['year'].unique())
    year_range = st.slider('Year range', min_value=int(years[0]), max_value=int(years[-1]), value=(years[0], years[-1]))
    regions = ['All'] + sorted(df['region'].unique())
    region = st.selectbox('Region', regions)
    causes = ['All'] + sorted(df['cause'].unique())
    cause = st.selectbox('Cause', causes)
    months = st.multiselect('Select months (leave empty = all)', options=list(range(1,13)), format_func=lambda m: calendar.month_name[m], default=list(range(1,13)))
    normalize = st.checkbox('Show per 100k (normalized)', value=False)
    st.markdown('---')
    st.subheader('Normalization population')
    # default population per region (synthetic). Change as needed or enter total population for the filter.
    default_pops = {
        'North': 1200000,
        'South': 1500000,
        'East': 900000,
        'West': 800000,
        'Central': 1000000
    }
    if region == 'All':
        default_total_pop = sum(default_pops.values())
    else:
        default_total_pop = default_pops.get(region, 1000000)
    population_for_norm = st.number_input('Population used for normalization (total)', min_value=1, value=int(default_total_pop))

q = df.copy()
q = q[(q['year'] >= year_range[0]) & (q['year'] <= year_range[1])]
if region != 'All':
    q = q[q['region'] == region]
if cause != 'All':
    q = q[q['cause'] == cause]
if months:
    q = q[q['month'].isin(months)]

st.markdown('---')

col1, col2 = st.columns([2,1])

with col1:
    st.subheader('Total deaths over time (monthly)')
    ts = q.groupby('date', as_index=False).agg({'deaths':'sum'})
    ts_display = ts.copy()
    if normalize and population_for_norm > 0:
        scale = 100000.0 / population_for_norm
        ts_display['deaths'] = ts_display['deaths'] * scale
        y_title = 'Deaths per 100k'
    else:
        y_title = 'Deaths'
    fig = px.line(ts, x='date', y='deaths', title='Monthly deaths over time')
    st.plotly_chart(fig.update_yaxes(title=y_title), use_container_width=True)
    # download button for timeseries
    def fig_to_bytes(fig_obj):
        return fig_obj.to_image(format='png', scale=2)
    st.download_button('Download timeseries PNG', data=fig_to_bytes(fig), file_name='timeseries.png', mime='image/png')

    st.subheader('Cause breakdown (stacked area)')
    area = q.groupby(['date','cause'], as_index=False).agg({'deaths':'sum'})
    fig2 = px.area(area, x='date', y='deaths', color='cause', title='Cause breakdown over time')
    st.plotly_chart(fig2, use_container_width=True)
    st.download_button('Download stacked area PNG', data=fig_to_bytes(fig2), file_name='stacked_area.png', mime='image/png')

with col2:
    st.subheader('Summary metrics')
    total = int(q['deaths'].sum())
    avg_month = round(q.groupby(['year','month']).agg({'deaths':'sum'})['deaths'].mean(),1)
    st.metric('Total deaths (filtered)', total)
    st.metric('Avg deaths / month', avg_month)

    st.subheader('Top causes')
    top = q.groupby('cause', as_index=False).agg({'deaths':'sum'}).sort_values('deaths', ascending=False)
    st.table(top.head(10))

st.markdown('---')

st.subheader('Monthly heatmap (year vs month)')
heat = q.groupby(['year','month'], as_index=False).agg({'deaths':'sum'})
heat_pivot = heat.pivot(index='year', columns='month', values='deaths').fillna(0)
fig3 = px.imshow(heat_pivot, labels=dict(x='Month', y='Year', color='Deaths'), x=[calendar.month_abbr[m] for m in range(1,13)], y=heat_pivot.index)
st.plotly_chart(fig3, use_container_width=True)
st.download_button('Download heatmap PNG', data=fig3.to_image(format='png', scale=2), file_name='heatmap.png', mime='image/png')

st.markdown('---')

st.subheader('Cause distribution')
pie = q.groupby('cause', as_index=False).agg({'deaths':'sum'})
fig4 = px.pie(pie, names='cause', values='deaths', title='Deaths by cause')
st.plotly_chart(fig4, use_container_width=True)
st.download_button('Download cause pie PNG', data=fig4.to_image(format='png', scale=2), file_name='cause_pie.png', mime='image/png')

st.markdown('---')

st.subheader('Data explorer & download')
st.dataframe(q.sort_values(['date','region','cause']).reset_index(drop=True))

@st.cache_data
def to_csv_bytes(df_in):
    b = BytesIO()
    df_in.to_csv(b, index=False)
    b.seek(0)
    return b

csv_b = to_csv_bytes(q)
st.download_button('Download filtered CSV', data=csv_b, file_name='farmer_deaths_filtered.csv')

st.markdown('---')
st.subheader('Yearly aggregation')
yearly = q.groupby('year', as_index=False).agg({'deaths':'sum'})
fig_year = px.bar(yearly, x='year', y='deaths', title='Total deaths by year')
st.plotly_chart(fig_year, use_container_width=True)
st.download_button('Download yearly PNG', data=fig_year.to_image(format='png', scale=2), file_name='yearly.png', mime='image/png')

st.subheader('Average by month (across selected years)')
by_month = q.groupby('month', as_index=False).agg({'deaths':'sum'})
by_month = by_month.sort_values('month')
fig_month = px.bar(by_month, x='month', y='deaths', title='Total deaths by month (selected years)')
fig_month.update_xaxes(tickvals=list(range(1,13)), ticktext=[calendar.month_abbr[m] for m in range(1,13)])
st.plotly_chart(fig_month, use_container_width=True)
st.download_button('Download month PNG', data=fig_month.to_image(format='png', scale=2), file_name='by_month.png', mime='image/png')
