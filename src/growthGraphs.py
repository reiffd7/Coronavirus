import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import folium
import plotly.express as px

np.seterr(divide = 'ignore') 

def transposeCountries(df, criteria):
    countryAgg = df.drop(columns=['Lat', 'Long']).groupby('Country/Region').sum().reset_index()
    df1 = countryAgg.set_index('Country/Region').stack().reset_index(level=1).reset_index().rename(columns={'level_1': 'Date', 0:criteria})
    return df1

def addState(state, df, fig):
    df = df.drop(columns=['fips', 'deaths'])
    df['NewCases'] = df.cases.diff()
    df = df.fillna(0)
    df['NewCasesInLastWeek'] = df['NewCases'].rolling(3).sum()
    df = df.fillna(0)
    fig.add_trace(go.Scatter(x=df['cases'], y=df['NewCasesInLastWeek'], mode='lines+markers', name=x, hoverinfo='name'))
    fig.update_layout(xaxis_type="log", yaxis_type="log")


def addStateDeath(state, fig):
    df = dfStates[dfStates['state'] == state]
    df = df.drop(columns=['fips', 'cases'])
    df['NewCases'] = df.deaths.diff()
    df = df.fillna(0)
    df['NewCasesInLastWeek'] = df['NewCases'].rolling(7).sum()
    df = df.fillna(0)
    fig.add_trace(go.Scatter(x=df['deaths'], y=df['NewCasesInLastWeek'], mode='lines+markers', name=state))
    fig.update_layout(xaxis_type="log", yaxis_type="log")


def addCountry(country, fig, period):
    df = df1[df1['Country/Region'] == country]
    df['NewCases'] = df.Confirmed.diff()
    df = df.fillna(0)
    df['NewCasesInLastWeek'] = df['NewCases'].rolling(period).sum()
    df = df.fillna(0)
    fig.add_trace(go.Scatter(x=df['Confirmed'], y=df['NewCasesInLastWeek'], text=df['Date'], mode='lines+markers', name='{} Confirmed: {}'.format(country, period)))
    fig.update_layout(xaxis_type="log", yaxis_type="log")


def addCountryDeath(country, fig, period):
    df = df1Deaths[df1Deaths['Country/Region'] == country]
    df['NewDeaths'] = df.Deaths.diff()
    df = df.fillna(0)
    df['NewDeathsInLastWeek'] = df['NewDeaths'].rolling(period).sum()
    df = df.fillna(0)
    fig.add_trace(go.Scatter(x=df['Deaths'], y=df['NewDeathsInLastWeek'], text=df['Date'], mode='lines+markers', name='{} Death: {}'.format(country, period)))
    fig.update_layout(xaxis_type="log", yaxis_type="log")



if __name__ == '__main__':
    df = pd.read_csv('../local_data/time_series_covid19_confirmed_global.csv')
    dfCountriesDeaths = pd.read_csv('../local_data/time_series_covid19_deaths_global.csv')
    dfStates = pd.read_csv('../local_data/covid-19-data-master 4_12/us-states.csv')

    states = dfStates['state'].unique()
    countries = df['Country/Region'].unique()


    df1 = transposeCountries(df, 'Confirmed')
    df1Deaths = transposeCountries(dfCountriesDeaths, 'Deaths')



    fig = go.Figure()
    for country in countries:
        addCountry(country, fig, 7)
    fig.update_layout(xaxis_type="log", yaxis_type="log")
    fig.update_layout(
        title="Coronavirus in Countries: Confirmed Growth",
        xaxis_title="Log(Confirmed Cases)",
        yaxis_title="Log(Total New Cases in Last Week)",
        )


    fig.show()