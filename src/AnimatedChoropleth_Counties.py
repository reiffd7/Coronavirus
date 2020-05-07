import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import folium
import plotly.express as px
import plotly.io as pio
import json
from urllib.request import urlopen
import chart_studio
import chart_studio.plotly as py
chart_studio.tools.set_credentials_file(username='daniel.reiff', api_key='jhEpBS6888O1FEbZI8M4')


np.seterr(divide = 'ignore') 


class BuildAnimatedScatter(object):


    def __init__(self, df):
        self.df = df
        self.prepDF()
        with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
            self.counties = json.load(response)
        self.fig_dict = {
                "data": [],
                "layout": {},
                "frames": []
            }
        self.buildLayout()
        self.sliders_dict = {
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 20},
                    "prefix": "Day:",
                    "visible": True,
                    "xanchor": "right"
                },
                "transition": {"duration": 300, "easing": "cubic-in-out"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": []
            }
        self.buildFirstFrame()
        self.buildFrames()
        self.fig_dict["layout"]["sliders"] = [self.sliders_dict]
        self.renderFig()



    def prepDF(self):
        self.df.sort_values(by=['state', 'county', 'date'], inplace=True)
        self.df.dropna(inplace=True)
        self.df['fips'] = self.df['fips'].astype(int)
        self.df['fips'] = self.df['fips'].apply(lambda x: str(x).zfill(5))
        self.df['NewCases'] = self.df.groupby(['state', 'county', 'fips'])['cases'].diff(1).fillna(0)
        self.df['NewCasesInLastWeek'] = self.df.groupby(['state', 'county', 'fips'])['NewCases'].apply(lambda x: x.rolling(7, min_periods=0).sum())
        self.df['slope'] = (self.df['NewCasesInLastWeek'] - self.df.groupby(['state', 'county', 'fips'])['NewCasesInLastWeek'].shift(1))/(self.df['cases'] - self.df.groupby(['state', 'county', 'fips'])['cases'].shift(1))
        self.df.sort_values(by='date', inplace=True)
        self.df = self.df.reset_index()
        self.dates = self.df['date'].unique()


    def buildLayout(self):
        self.fig_dict["layout"]["sliders"] = {
            "args": [
                "transition", {
                    "duration": 400,
                    "easing": "cubic-in-out"
                }
            ],
            "initialValue": self.dates[0],
            "plotlycommand": "animate",
            "values": self.dates,
            "visible": True
        }
        self.fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": True},
                                    "fromcurrent": True, "transition": {"duration": 300,
                                                                        "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
                    ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 87},
                    "showactive": False,
                    "type": "buttons",
                    "x": 0.1,
                    "xanchor": "right",
                    "y": 0,
                    "yanchor": "top"
                }
            ]


    def buildFirstFrame(self):
        fig_dict['data'].append(go.Choropleth(
                locations = self.df[self.df['date'] == self.dates[0]]['fips'],
                z = self.df[self.df['date'] == self.dates[0]]['slope'],
                zmin = -1,
                zmax = 1,
                geojson = self.counties,
                locationmode = 'geojson-id',
                colorscale = 'Hot',
                reversescale = True,
                colorbar_title = 'Growth'
            ))

    
    def buildFrames(self):
        for x in self.dates:
            frame_dict = dict(
                        name = x,
                        data = [go.Choropleth(locations = self.df[self.df['date'] == x]['fips'],
                                                    z = self.df[self.df['date'] == x]['slope'],
                                                    geojson = self.counties,
                                                    locationmode = 'geojson-id',
                                                    colorscale = 'Hot',
                                                    autocolorscale=False,
                                                    colorbar_title = 'Growth')]
        )
            self.fig_dict['frames'].append(frame_dict)
            slider_step = {"args": [
            [x],
            {"frame": {"duration": 500, "redraw": True},
            "mode": "immediate",
            "transition": {"duration": 300}}
        ],
            "label": x,
            "method": "animate"}
            self.sliders_dict["steps"].append(slider_step)

        
    def renderFig(self):
        fig = go.Figure(self.fig_dict).update_layout(geo_scope='usa')
        fig.show()
        # py.iplot(fig, filename="counties animated plot")



if __name__ == '__main__':
    date = '4_26'
    data_path = '../local_data/covid-19-data-master {}/us-counties.csv'.format(date)
    df = pd.read_csv(data_path, index_col=0)

    
    

    
    


    

    
    
    