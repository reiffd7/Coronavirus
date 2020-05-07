import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import folium
import plotly.express as px
import plotly.io as pio
import chart_studio
import chart_studio.plotly as py
chart_studio.tools.set_credentials_file(username='daniel.reiff', api_key='jhEpBS6888O1FEbZI8M4')


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






if __name__ == '__main__':
    date = '4_19'
    data_path = '../local_data/covid-19-data-master {}/us-states.csv'.format(date)
    df = pd.read_csv(data_path, index_col=0)

    df.sort_values(by=['state', 'date'], inplace=True)
    df = df.reset_index()
    df['state'] = df['state'].apply(lambda x: us_state_abbrev[x])
    df['NewCases'] = df.groupby(['state', 'fips'])['cases'].diff(1).fillna(0)
    df['NewCasesInLastWeek'] = df.groupby(['state', 'fips'])['NewCases'].apply(lambda x: x.rolling(7, min_periods=0).sum())
    df['slope'] = (df['NewCasesInLastWeek'] - df.groupby(['state', 'fips'])['NewCasesInLastWeek'].shift(1))/(df['cases'] - df.groupby(['state', 'fips'])['cases'].shift(1))
    df['same'] = 'same'
    df.sort_values(by='date', inplace=True)
    dates = df[['date', 'slope']][10:]['date'].unique()

    
    fig_dict = {
    "data": [],
    "layout": {},
    "frames": []
}
    fig_dict["layout"]["sliders"] = {
    "args": [
        "transition", {
            "duration": 400,
            "easing": "cubic-in-out"
        }
    ],
    "initialValue": "01/26",
    "plotlycommand": "animate",
    "values": dates,
    "visible": True
}
    fig_dict["layout"]["updatemenus"] = [
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
    sliders_dict = {
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

    
    fig_dict['data'].append(go.Choropleth(
        locations = df[df['date'] == '2020-01-26']['state'],
        z = df[df['date'] == '2020-01-21']['slope'],
        zmin = -1,
        zmax = 1,
        locationmode = 'USA-states',
        colorscale = 'Hot',
        reversescale = True,
        colorbar_title = 'Slope'
    ))

    
    


    for x in dates:

        frame_dict = dict(
                    name = x,
                    data = [go.Choropleth(locations = df[df['date'] == x]['state'],
                                                z = df[df['date'] == x]['slope'],
                                                locationmode = 'USA-states',
                                                colorscale = 'Hot',
                                                autocolorscale=False,
                                                colorbar_title = 'Slope')]
    )
        fig_dict['frames'].append(frame_dict)
        slider_step = {"args": [
        [x],
        {"frame": {"duration": 500, "redraw": True},
         "mode": "immediate",
         "transition": {"duration": 300}}
    ],
        "label": x,
        "method": "animate"}
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"]["sliders"] = [sliders_dict]
    fig = go.Figure(fig_dict).update_layout(geo_scope='usa')
    py.iplot(fig, filename="Go animated plot")