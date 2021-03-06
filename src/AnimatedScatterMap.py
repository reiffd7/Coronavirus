import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import folium
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import date
import plotly.io as pio
import chart_studio
import chart_studio.plotly as py
from AnimatedBase import AnimatedBase
chart_studio.tools.set_credentials_file(username='daniel.reiff', api_key='jhEpBS6888O1FEbZI8M4')
pio.renderers.default = "iframe_connected"

np.seterr(divide = 'ignore') 


class ScatterMap(object):

    def __init__(self, df, r, c, color_criteria, today):
        self.df = df
        print('prepping df')
        self.prepDF()
        self.color_criteria = color_criteria
        self.dates = self.df['date'].unique()
        self.states = self.df['state'].unique()
        print('initialzing the plot')
        fig = make_subplots(rows=r, cols=c, 
                    subplot_titles = ('US Map', 'Existing Cases vs. New Cases'),
                    specs = [[{"type": "choropleth"}, {"type": "xy"}]])
        self.Animate = AnimatedBase(fig) 
        self.scatter1_dict = {
            "x" : list(range(0, 15)),
            "y" : list(range(0, 15)),
            "mode" : "lines",
            "name" : "Exponential Growth",
            "text" : " ",
            "textposition" : "Upper Right",
            "line" : dict(color='black', dash='dash'),
            "textfont" : None,
            "marker" : None,
            "showlegend" : True,
            "ids" : None
        }

        self.scatter2_dict = {
            "x" : None,
            "y" : None,
            "mode" : "markers+text",
            "name" : None,
            "text": None,
            "textposition" : "top center",
            "line" : None,
            "textfont" : {"size": 12},
            "marker" : {
            "sizemode": "area",
            "size": 7},
            "showlegend" : False,
            "ids": None
        }
        print('setting the initial state')
        self.initialState()
        self.Animate.fig.update_yaxes(range=[0, 14])
        self.Animate.fig.update_xaxes(range=[0, 14])
        self.Animate.fig.update_xaxes(title_text = "Log(Existing Cases)")
        self.Animate.fig.update_yaxes(title_text = "Log(New Cases)")
        self.Animate.fig.update_layout(geo_scope='usa')

        print('creating frames')
        self.createFrames()
        self.Animate.finalizeSliders()

        print('sending to the cloud')
        py.iplot(self.Animate.fig, filename = "animated scatter map {}".format(today))
        
        

    
    def prepDF(self):
        self.df.sort_values(by=['state', 'date'], inplace=True)
        self.df = df.reset_index()
        self.df['NewCases'] = self.df.groupby(['state', 'fips'])['positive'].diff(1).fillna(0)
        self.df['NewCasesInLastWeek'] = self.df.groupby(['state', 'fips'])['NewCases'].apply(lambda x: x.rolling(7, min_periods=0).sum())
        self.df['slope'] = (self.df['NewCasesInLastWeek'] - self.df.groupby(['state', 'fips'])['NewCasesInLastWeek'].shift(1))/(self.df['positive'] - self.df.groupby(['state', 'fips'])['positive'].shift(1))
        self.df['sensitive_slopeBH'] = self.df.groupby(['state', 'fips'])['slope'].apply(lambda x: x.rolling(10, win_type='blackmanharris', min_periods=0).mean())
        self.df['sensitive_slopeTriang'] = self.df.groupby(['state', 'fips'])['slope'].apply(lambda x: x.rolling(10, win_type='triang', min_periods=0).mean())
        self.df['sensitive_slopeBox'] = self.df.groupby(['state', 'fips'])['slope'].apply(lambda x: x.rolling(10, win_type='boxcar', min_periods=0).mean())
        self.df.sort_values(by='date', inplace=True)

    def choro(self, date):
        return go.Choropleth(
        locations = self.df[self.df['date'] == date]['state'],
        z = self.df[self.df['date'] == date][self.color_criteria],
        zmin = -1,
        zmax = 1,
        locationmode = 'USA-states',
        colorscale = [[0.0, 'blue'], [0.5, 'white'], [1.0, 'red']],
        colorbar_title = 'Growth',
        colorbar={"x" : 0}
    )

    def scatter(self, x, y, mode, name, text, textposition, line, textfont, marker, showlegend, ids):
        return go.Scatter(
            x = x,
            y = y,
            mode = mode,
            name = name,
            text = text,
            # textposition = textpostition,
            line = line,
            textfont = textfont,
            marker = marker,
            showlegend = showlegend,
            ids = ids
    )

    def initialState(self):
        self.scatter2_dict['x'] = np.log(self.df[self.df['date'] == self.dates[0]]['positive'].to_numpy())
        self.scatter2_dict['y'] = np.log(self.df[self.df['date'] == self.dates[0]]['NewCasesInLastWeek'].to_numpy())
        self.scatter2_dict['text'] = self.df[self.df['date'] == self.dates[0]]['state'].to_numpy()
        self.scatter2_dict['ids'] = self.df[self.df['date'] == self.dates[0]]['state'].to_numpy()
        plots = [[self.choro(self.dates[0]), 1, 1], [self.scatter(**self.scatter1_dict), 1, 2], [self.scatter(**self.scatter2_dict), 1, 2]]
        self.Animate.setInitial(plots)

    def createFrames(self):
        frames = []
        for date in self.dates:
            frames_dict = dict(
                    name = str(date),
                    data = [],
                    traces = list(range(3))
        )
            self.scatter2_dict['x'] = np.log(self.df[self.df['date'] == date]['positive'].to_numpy())
            self.scatter2_dict['y'] = np.log(self.df[self.df['date'] == date]['NewCasesInLastWeek'].to_numpy())
            self.scatter2_dict['text'] = self.df[self.df['date'] == date]['state'].to_numpy()
            self.scatter2_dict['ids'] = self.df[self.df['date'] == date]['state'].to_numpy()
            frames_dict['data'].append(self.choro(date))
            frames_dict['data'].append(self.scatter(**self.scatter1_dict))
            frames_dict['data'].append(self.scatter(**self.scatter2_dict))
            self.Animate.addSliderStep(str(date))
            frames.append(frames_dict)
        self.Animate.fig.update(frames=frames)



if __name__ == '__main__':
    url = 'https://covidtracking.com/api/v1/states/daily.csv'

    date = str(date.today())
    df = pd.read_csv(url, parse_dates=['date'], index_col=['date']).sort_index()
    df = df[['state', 'fips', 'positive', 'death', 'hospitalizedCumulative', 'onVentilatorCumulative']]
    AnimatedScatterMap = ScatterMap(df, 1, 2, 'sensitive_slopeBox', date)
    

