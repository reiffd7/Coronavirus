import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import folium
import plotly.express as px
from plotly.subplots import make_subplots

import plotly.io as pio
import chart_studio
import chart_studio.plotly as py
from AnimatedBase import AnimatedBase
chart_studio.tools.set_credentials_file(username='daniel.reiff', api_key='jhEpBS6888O1FEbZI8M4')
pio.renderers.default = "iframe_connected"

np.seterr(divide = 'ignore') 

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}


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
        self.df['state'] = self.df['state'].apply(lambda x: us_state_abbrev[x])
        self.df['NewCases'] = self.df.groupby(['state', 'fips'])['cases'].diff(1).fillna(0)
        self.df['NewCasesInLastWeek'] = self.df.groupby(['state', 'fips'])['NewCases'].apply(lambda x: x.rolling(7, min_periods=0).sum())
        self.df['slope'] = (self.df['NewCasesInLastWeek'] - self.df.groupby(['state', 'fips'])['NewCasesInLastWeek'].shift(1))/(self.df['cases'] - self.df.groupby(['state', 'fips'])['cases'].shift(1))
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
        self.scatter2_dict['x'] = np.log(self.df[self.df['date'] == self.dates[0]]['cases'].to_numpy())
        self.scatter2_dict['y'] = np.log(self.df[self.df['date'] == self.dates[0]]['NewCasesInLastWeek'].to_numpy())
        self.scatter2_dict['text'] = self.df[self.df['date'] == self.dates[0]]['state'].to_numpy()
        self.scatter2_dict['ids'] = self.df[self.df['date'] == self.dates[0]]['state'].to_numpy()
        plots = [[self.choro(self.dates[0]), 1, 1], [self.scatter(**self.scatter1_dict), 1, 2], [self.scatter(**self.scatter2_dict), 1, 2]]
        self.Animate.setInitial(plots)

    def createFrames(self):
        frames = []
        for date in self.dates:
            frames_dict = dict(
                    name = date,
                    data = [],
                    traces = list(range(3))
        )
            self.scatter2_dict['x'] = np.log(self.df[self.df['date'] == date]['cases'].to_numpy())
            self.scatter2_dict['y'] = np.log(self.df[self.df['date'] == date]['NewCasesInLastWeek'].to_numpy())
            self.scatter2_dict['text'] = self.df[self.df['date'] == date]['state'].to_numpy()
            self.scatter2_dict['ids'] = self.df[self.df['date'] == date]['state'].to_numpy()
            frames_dict['data'].append(self.choro(date))
            frames_dict['data'].append(self.scatter(**self.scatter1_dict))
            frames_dict['data'].append(self.scatter(**self.scatter2_dict))
            self.Animate.addSliderStep(date)
            frames.append(frames_dict)
        self.Animate.fig.update(frames=frames)



if __name__ == '__main__':
    date = '5_03'
    data_path = '../local_data/covid-19-data-master {}/us-states.csv'.format(date)
    df = pd.read_csv(data_path, index_col=0)
    AnimatedScatterMap = ScatterMap(df, 1, 2, 'sensitive_slopeBox', date)
    

#     fig_dict = {
#     "data": [],
#     "layout": {},
#     "frames": []
# }

    

#     fig_dict["layout"]["xaxis"] = {"range": [0, 14], "title": "Log(Existing"}
#     fig_dict["layout"]["yaxis"] = {"range": [0, 12], "title": "Log(New Cases in The Last Week"}
#     fig_dict["layout"]["hovermode"] = "closest"
#     fig_dict["layout"]["sliders"] = {
#     "args": [
#         "transition", {
#             "duration": 400,
#             "easing": "cubic-in-out"
#         }
#     ],
#     "initialValue": "01/21",
#     "plotlycommand": "animate",
#     "values": dates,
#     "visible": True
# }

    

    
    ## initial data
    # date = '2020-01-21'

    # fig.add_trace(go.Choropleth(
    #     locations = df[df['date'] == '2020-01-21']['state'],
    #     z = df[df['date'] == '2020-01-21']['sensitive_slopeBox'],
    #     zmin = -1,
    #     zmax = 1,
    #     locationmode = 'USA-states',
    #     colorscale = [[0.0, 'blue'], [0.5, 'white'], [1.0, 'red']],
    #     colorbar_title = 'Growth',
    #     colorbar={"x" : 0}
    # ), row=1, col=1)

    # fig.add_trace(go.Scatter(
    #         x = list(range(0, 15)),
    #         y = list(range(0, 15)),
    #         mode = "lines",
    #         name = "Exponential Growth",
    #         line = dict(color='black', dash='dash'),
    #         showlegend = True
    # ), row = 1, col = 2)

    
    
    # fig.add_trace(go.Scatter(
    #     x = np.log(df[df['date'] == '2020-01-21']['cases'].to_numpy()),
    #     y = np.log(df[df['date'] == '2020-01-21']['NewCasesInLastWeek'].to_numpy()),
    #     mode = "markers+text",
    #     text = df[df['date'] == '2020-01-21']['state'].to_numpy(),
    #     textposition = "top center",
    #     textfont = {"size": 12},
    #     marker = {
    #         "sizemode": "area",
    #         "size": 7},
    #     showlegend = False,
    #     ids = df[df['date'] == '2020-01-21']['state'].to_numpy()

    # ), row = 1, col =2 )

        # data_dict = {
        #     "x" : list(np.log(dataset_by_state_and_day["cases"])),
        #     "y" : list(np.log(dataset_by_state_and_day["NewCasesInLastWeek"])),
        #     "mode" : "lines+markers+text",
        #     "text": state,
        #     "marker": {
        #         "sizemode": "area",
        #         "size": 7
                
        #                 },
        #     "name": state,
        #     "showlegend": False
        #     }
        # fig_dict["data"].append(data_dict)

    # fig.update_yaxes(range=[0, 14])
    # fig.update_xaxes(range=[0, 14])
    # fig.update_xaxes(title_text = "Log(Existing Cases)")
    # fig.update_yaxes(title_text = "Log(New Cases)")
    # fig.update_layout(geo_scope='usa')
    ## make frames
    # frames = []
    
    
    # for date in dates:
    #     frames_dict = dict(
    #                 name = date,
    #                 data = [],
    #                 traces = list(range(3))
    #     )
    #     # frame = {"data": [], "name": str(date)}
        
    #     frames_dict['data'].append(go.Choropleth(locations = df[df['date'] == date]['state'],
    #                                             z = df[df['date'] == date]['sensitive_slopeBox'],
    #                                             locationmode = 'USA-states',
    #                                             colorscale = [[0.0, 'rgb(0,0,255)'], [0.5, 'rgb(255,255,255)'], [1.0, 'rgb(255,0,0)']],
    #                                             colorbar_title = 'Growth',
    #                                             colorbar={"x" : 0}))

    #     frames_dict['data'].append(go.Scatter(
    #         x = list(range(0, 15)),
    #         y = list(range(0, 15)),
    #         mode = "lines",
    #         name = "Exponential Growth",
    #         line = dict(color='black', dash='dash'),
    #         showlegend = True
    # ))

    #     frames_dict['data'].append(go.Scatter(
    #     x = np.log(df[df['date'] == date]['cases'].to_numpy()),
    #     y = np.log(df[df['date'] == date]['NewCasesInLastWeek'].to_numpy()),
    #     mode = "markers+text",
    #     text = df[df['date'] == date]['state'].to_numpy(),
    #     textposition = "top center",
    #     textfont = {"size": 12},
    #     marker = {
    #         "sizemode": "area",
    #         "size": 7},
    #     showlegend = False,
    #     ids = df[df['date'] == date]['state'].to_numpy()

    # ))
    #     # fig_dict["frames"].append(frame)
    #     slider_step = {"args": [
    #     [date],
    #     {"frame": {"duration": 300, "redraw": True},
    #      "mode": "immediate",
    #      "transition": {"duration": 100}}
    # ],
    #     "label": date,
    #     "method": "animate"}
    #     sliders_dict["steps"].append(slider_step)
    #     frames.append(frames_dict)

    # fig.update(frames=frames)
    # fig.update_layout(updatemenus=updatemenus, sliders=[sliders_dict])
    # py.iplot(fig, filename = "animated scatter map 4_30")
    # # fig_dict["layout"]["sliders"] = [sliders_dict]
    # # fig = go.Figure(fig_dict)
    # fig.show()

