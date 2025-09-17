import pandas as pd
import plotly.express as px
import os

BASE = os.path.join(os.path.dirname(__file__), '..')
CSV = os.path.join(BASE, 'data', 'farmer_deaths.csv')
OUT_DIR = os.path.join(BASE, 'preview_images')
os.makedirs(OUT_DIR, exist_ok=True)

def main():
    df = pd.read_csv(CSV, parse_dates=['date'])
    df = df.sort_values('date')

    ts = df.groupby('date', as_index=False).agg({'deaths':'sum'})
    fig = px.line(ts, x='date', y='deaths', title='Monthly deaths over time')
    fig.write_image(os.path.join(OUT_DIR, 'timeseries.png'), scale=2)

    area = df.groupby(['date','cause'], as_index=False).agg({'deaths':'sum'})
    fig2 = px.area(area, x='date', y='deaths', color='cause', title='Cause breakdown')
    fig2.write_image(os.path.join(OUT_DIR, 'stacked_area.png'), scale=2)

    heat = df.groupby(['year','month'], as_index=False).agg({'deaths':'sum'})
    heat_pivot = heat.pivot(index='year', columns='month', values='deaths').fillna(0)
    fig3 = px.imshow(heat_pivot, labels=dict(x='Month', y='Year', color='Deaths'))
    fig3.write_image(os.path.join(OUT_DIR, 'heatmap.png'), scale=2)

    print('Wrote preview images to', OUT_DIR)

if __name__ == '__main__':
    main()
