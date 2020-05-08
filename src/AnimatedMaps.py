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

class Map(object):

    def __init__(self, df, r, c, today):
        self.df = df
        print('prepping df')
        self.prepDF()
        self.criteria_lst = ['sensitive_slopeBox_positive', 'sensitive_slopeBox_negative', 'sensitive_slopeBox_death', 'sensitive_slopeBox_hospitalizedCumulative']
        self.dates = self.df['date'].unique()
        self.states = self.df['state'].unique()
        print('initialzing the plot')
        fig = make_subplots(rows=r, cols=c, 
                    subplot_titles = ('Positives', 'Negatives', 'Deaths', 'Hospitalizations'),
                    specs = [[{"type": "choropleth"}, {"type": "choropleth"}],
                            [{"type": "choropleth"}, {"type": "choropleth"}]])
        self.Animate = AnimatedBase(fig)
        print('setting the initial state')
        self.Animate.fig.update_layout(geo_scope='usa')
        self.Animate.fig.update_layout(geo2_scope='usa')
        self.Animate.fig.update_layout(geo3_scope='usa')
        self.Animate.fig.update_layout(geo4_scope='usa')
        self.initialState()

        print('creating frames')
        self.createFrames()
        self.Animate.finalizeSliders()
        print('sending to the cloud')
        py.iplot(self.Animate.fig, filename = "animated maps {}".format(today))


    def evaluateGrowth(self, criteria):
        self.df['New{}'.format(criteria)] = self.df.groupby(['state', 'fips'])[criteria].diff(1).fillna(0)
        self.df['New{}InLastWeek'.format(criteria)] = self.df.groupby(['state', 'fips'])['New{}'.format(criteria)].apply(lambda x: x.rolling(7, min_periods=0).sum())
        self.df['slope_{}'.format(criteria)] = (self.df['New{}InLastWeek'.format(criteria)] - self.df.groupby(['state', 'fips'])['New{}InLastWeek'.format(criteria)].shift(1))/(self.df[criteria] - self.df.groupby(['state', 'fips'])[criteria].shift(1))
        # self.df['sensitive_slopeBH'] = self.df.groupby(['state', 'fips'])['slope'].apply(lambda x: x.rolling(10, win_type='blackmanharris', min_periods=0).mean())
        # self.df['sensitive_slopeTriang'] = self.df.groupby(['state', 'fips'])['slope'].apply(lambda x: x.rolling(10, win_type='triang', min_periods=0).mean())
        self.df['sensitive_slopeBox_{}'.format(criteria)] = self.df.groupby(['state', 'fips'])['slope_{}'.format(criteria)].apply(lambda x: x.rolling(10, win_type='boxcar', min_periods=0).mean())
        self.df.sort_values(by='date', inplace=True)


    def prepDF(self):
        self.df.sort_values(by=['state', 'date'], inplace=True)
        self.df = self.df.reset_index()
        criteria_lst = ['positive', 'death', 'hospitalizedCumulative', 'onVentilatorCumulative', 'negative']
        for crit in criteria_lst:
            self.evaluateGrowth(crit)

    def choro(self, date, criteria):
        return go.Choropleth(
        locations = self.df[self.df['date'] == date]['state'],
        z = self.df[self.df['date'] == date][criteria],
        zmin = -1,
        zmax = 1,
        locationmode = 'USA-states',
        colorscale = [[0.0, 'blue'], [0.5, 'white'], [1.0, 'red']],
        colorbar_title = 'Growth',
        colorbar={"x" : 0}
    )


    def initialState(self):
        plots = []
        r, c = 1, 1
        for i, crit in enumerate(self.criteria_lst):
            print(r, c)
            sub = [self.choro(self.dates[0], crit), r, c]
            plots.append(sub)
            if c%2 == 0:
                c = 1
                r += 1
            else:
                c += 1
        self.Animate.setInitial(plots)

    def createFrames(self):
        frames = []
        for date in self.dates:
            frames_dict = dict(
                name = str(date),
                data = [],
                traces = list(range(4))
            )
            for crit in self.criteria_lst:
                frames_dict['data'].append(self.choro(date, crit))
            self.Animate.addSliderStep(str(date))
            frames.append(frames_dict)
        self.Animate.fig.update(frames=frames)




if __name__ == '__main__':
    url = 'https://covidtracking.com/api/v1/states/daily.csv'

    date = str(date.today())
    df = pd.read_csv(url, parse_dates=['date'], index_col=['date']).sort_index()
    df = df[['state', 'fips', 'positive', 'death', 'hospitalizedCumulative', 'onVentilatorCumulative', 'negative']]
    AnimatedMaps = Map(df, 2, 2, date)