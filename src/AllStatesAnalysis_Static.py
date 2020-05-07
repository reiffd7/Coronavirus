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

Regions = {
        'AK': 'Other',
        'AL': 'South',
        'AR': 'South',
        'AS': 'Other',
        'AZ': 'West',
        'CA': 'West',
        'CO': 'West',
        'CT': 'Northeast',
        'DC': 'Northeast',
        'DE': 'Northeast',
        'FL': 'South',
        'GA': 'South',
        'GU': 'Other',
        'HI': 'Other',
        'IA': 'Midwest',
        'ID': 'West',
        'IL': 'Midwest',
        'IN': 'Midwest',
        'KS': 'Midwest',
        'KY': 'South',
        'LA': 'South',
        'MA': 'Northeast',
        'MD': 'Northeast',
        'ME': 'Northeast',
        'MI': 'West',
        'MN': 'Midwest',
        'MO': 'Midwest',
        'MP': 'Other',
        'MS': 'South',
        'MT': 'West',
        'NA': 'Other',
        'NC': 'South',
        'ND': 'Midwest',
        'NE': 'West',
        'NH': 'Northeast',
        'NJ': 'Northeast',
        'NM': 'West',
        'NV': 'West',
        'NY': 'Northeast',
        'OH': 'Midwest',
        'OK': 'South',
        'OR': 'West',
        'PA': 'Northeast',
        'PR': 'Other',
        'RI': 'Northeast',
        'SC': 'South',
        'SD': 'Midwest',
        'TN': 'South',
        'TX': 'South',
        'UT': 'West',
        'VA': 'South',
        'VI': 'Other',
        'VT': 'Northeast',
        'WA': 'West',
        'WI': 'Midwest',
        'WV': 'South',
        'WY': 'West'
}

statePops = {'California': 39557045,
 'Texas': 28701845,
 'Florida': 21299325,
 'New York': 19542209,
 'Pennsylvania': 12807060,
 'Illinois': 12741080,
 'Ohio': 11689442,
 'Georgia': 10519475,
 'North Carolina': 10383620,
 'Michigan': 9995915,
 'New Jersey': 8908520,
 'Virginia': 8517685,
 'Washington': 7535591,
 'Arizona': 7171646,
 'Massachusetts': 6902149,
 'Tennessee': 6770010,
 'Indiana': 6691878,
 'Missouri': 6126452,
 'Maryland': 6042718,
 'Wisconsin': 5813568,
 'Colorado': 5695564,
 'Minnesota': 5611179,
 'South Carolina': 5084127,
 'Alabama': 4887871,
 'Louisiana': 4659978,
 'Kentucky': 4468402,
 'Oregon': 4190713,
 'Oklahoma': 3943079,
 'Connecticut': 3572665,
 'Puerto Rico': 3195153,
 'Utah': 3161105,
 'Iowa': 3156145,
 'Nevada': 3034392,
 'Arkansas': 3013825,
 'Mississippi': 2986530,
 'Kansas': 2911505,
 'New Mexico': 2095428,
 'Nebraska': 1929268,
 'West Virginia': 1805832,
 'Idaho': 1754208,
 'Hawaii': 1420491,
 'New Hampshire': 1356458,
 'Maine': 1338404,
 'Montana': 1062305,
 'Rhode Island': 1057315,
 'Delaware': 967171,
 'South Dakota': 882235,
 'North Dakota': 760077,
 'Alaska': 737438,
 'District of Columbia': 702455,
 'Vermont': 626299,
 'Wyoming': 577737,
 'American Samoa': 55465,
 'Guam': 165768,
 'Northern Mariana Islands': 56882,
 'Virgin Islands': 106977}


class Grapher(object):

    def __init__(self, df):
        self.df = df
        self.assignRegions()

    def assignRegions(self):
        self.df['region'] = self.df['state'].apply(lambda x: Regions[us_state_abbrev[x]])
        self.df = self.df.sort_values(by=['region', 'state', 'date'])
        regions = ['Northeast', 'Midwest', 'South', 'West', 'Other']
        self.regional_data = {region:self.df.query("region == '%s'" %region) for region in regions}
        self.region_colors = {'Northeast': 'rgba(44, 130, 201, 1)', 'Midwest': 'rgba(0, 132, 122, .8)', 'South': 'rgba(152, 0, 0, .8)', 'West': 'rgba(244, 179, 80, 1)', 'Other': 'rgba(35, 0, 34, .8)'}


    def _addState(self, state, df, fig, region):
        self.state_dictLATEST[state] = {}
        self.state_dictLATEST[state]['state'] = state
        self.state_dictLATEST[state]['region'] = region
        df = df.drop(columns=['fips', 'deaths'])
        df['NewCases'] = df.cases.diff()
        df = df.fillna(0)
        df['NewCasesInLastWeek'] = df['NewCases'].rolling(7).sum()
        df = df.fillna(0)
        mostRecentRecord = df.tail(1)
        self.state_dictLATEST[state]['normalized total cases'] = mostRecentRecord['cases'].values[0]/statePops[state]
        self.state_dictLATEST[state]['normalized new cases'] = mostRecentRecord['NewCases'].values[0]/statePops[state]
        self.state_dictLATEST[state]['normalized new cases last week'] = mostRecentRecord['NewCasesInLastWeek'].values[0]/statePops[state]
        return go.Scatter(
                x=np.log(df['cases']), 
                y=np.log(df['NewCasesInLastWeek']), 
                mode='markers+lines',
                text='date', 
                marker = dict(
                        size=7,
                        color=self.region_colors[region], #set color equal to a variable
                    
                    ),
                name=state)
        # fig.update_layout(xaxis_type="log", yaxis_type="log")


    def plotGrowth(self):
        fig = go.Figure()
        self.state_dictLATEST = {}
        data = []
        for region_name, region in self.regional_data.items():
            
            for state, stateDF in region.groupby('state'):  
                data.append(self._addState(state, stateDF, fig, region_name))





        py.iplot(data, filename = 'states exponential growth')
        fig.update_layout(
            title="Coronavirus in States: Confirmed Growth",
            xaxis_title="Log(Confirmed Cases)",
            yaxis_title="Log(Total New Cases in Last Week)",
            )

        fig.show()
        self.state_dfLATEST = pd.DataFrame(list(self.state_dictLATEST.values()))
        self.state_dfLATEST['state'] = self.state_dfLATEST['state'].apply(lambda x: us_state_abbrev[x])


    def plotChoropleth(self):
        fig = px.choropleth(locations=self.state_dfLATEST['state'], 
                        locationmode="USA-states", 
                        title= "States By Normalized Total Cases (Total)", 
                        color=self.state_dfLATEST['normalized total cases'], 
                        scope="usa")
        py.iplot(fig, filename = "states by normalized total cases")

        fig = px.choropleth(locations=self.state_dfLATEST['state'], 
                        locationmode="USA-states", 
                        title= "States By Normalized New Cases (Last Week)", 
                        color=self.state_dfLATEST['normalized new cases last week'], 
                        scope="usa")
        py.iplot(fig, filename = "states by normalized new cases last week")

        fig = px.choropleth(locations=self.state_dfLATEST['state'], 
                        locationmode="USA-states", 
                        title= "States By Normalized New Cases (Last Day)", 
                        color=self.state_dfLATEST['normalized new cases'], 
                        scope="usa")
        py.iplot(fig, filename = "states by normalized new cases last day")


if __name__ == '__main__':
    date = '5_03'
    data_path = '../local_data/covid-19-data-master {}/us-states.csv'.format(date)
    df = pd.read_csv(data_path, index_col=0)

    coronaUS = Grapher(df)
    coronaUS.plotGrowth()
    # coronaUS.plotChoropleth()

