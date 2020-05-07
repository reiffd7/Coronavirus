import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import folium
import plotly.express as px
import json
from urllib.request import urlopen
import plotly.io as pio
pio.renderers.default = "iframe"


def fips(row):
    print(row)
    return int(str(row['STATE']) + str(row['COUNTY']).zfill(3))
    

if __name__ == '__main__':

    counties = pd.read_csv('../local_data/covid-19-data-master 4_19/us-counties.csv', index_col=0)
    countyPop = pd.read_csv('../local_data/covid-19-data-master 4_19/co-est2019-alldata.csv', encoding = "cp1252")

    ## cleaning/preprocessing county coronavirus data
    counties = counties.dropna()
    counties['fips'] = counties['fips'].astype(int)

    ## just take the elements we want from county population data
    countyPop = countyPop[['STATE', 'COUNTY', 'STNAME', 'CTYNAME', 'POPESTIMATE2019']]

    ## create fips codes from state+county codes 
    countyPop['fips'] = countyPop.apply(fips, axis=1)

    ## dict of county populations to draw into coronavirus data
    countyPopDICT = dict(zip(countyPop.fips, countyPop.POPESTIMATE2019))

    ## we only want the last record per county to get the total case tally up to date
    totalCases = counties.groupby(['county', 'state']).tail(1)
    ## normalize total case tally by county population
    totalCases['countyPop'] = totalCases['fips'].apply(lambda x: countyPopDICT[x])
    totalCases['normalized_case_total'] = (totalCases['cases']/totalCases['countyPop'])*100
    totalCases['death_pct'] = (totalCases['deaths']/totalCases['cases'])

    ## preprocessing for mapping
    totalCases = totalCases.reset_index()
    totalCases['fips'] = totalCases['fips'].apply(lambda x: str(x).zfill(5))


    ## mapping
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    fig = px.choropleth(totalCases, geojson=counties, locations='fips', color='death_pct',
                           color_continuous_scale="Viridis",
                           scope="usa",
                           labels = {'county': 'county name'},
                           hover_data = ['county', 'cases', 'countyPop']
                                        )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()