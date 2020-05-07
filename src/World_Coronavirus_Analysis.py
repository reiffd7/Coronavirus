import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio
import chart_studio
import chart_studio.plotly as py
chart_studio.tools.set_credentials_file(username='daniel.reiff', api_key='jhEpBS6888O1FEbZI8M4')


class World(object):

    def __init__(self, df):
        self.df = df
        self.transpose_df()

    def transpose_df(self):
        countryAgg = self.df.drop(columns=['Lat', 'Long']).groupby('Country/Region').sum().reset_index()
        self.df = countryAgg.set_index('Country/Region').stack().reset_index(level=1).reset_index().rename(columns={'level_1': 'Date', 0:'Confirmed'})

    def _addCountry(self, country, fig, i):
        df = self.df[self.df['Country/Region'] == country]
        df['NewCases'] = df.Confirmed.diff()
        df = df.fillna(0)
        df['NewCasesInLastWeek'] = df['NewCases'].rolling(7).sum()
        df = df.fillna(0)
        df["Date"] = df["Date"].apply(lambda x: x.replace("/20", ""))
        fig.add_trace(go.Scatter(x=np.log(df['Confirmed']), y=np.log(df['NewCasesInLastWeek']), text=df['Date'], mode='lines+markers', name=country), row=1, col=2)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Confirmed"], text=df['Date'], mode='lines+markers', name=country), row=i+1, col=1)
        if country == 'Korea, South':
            fig.add_trace(go.Scatter(x= np.log(df[df['Date'] == '3/4']["Confirmed"]), y = np.log(df[df['Date'] == '3/4']["NewCasesInLastWeek"]), name="Inflection Point"), row=1, col=2)
            fig.add_trace(go.Scatter(x= df[df['Date'] == '3/4']['Date'], y = df[df['Date'] == '3/4']["Confirmed"], name="Inflection Point"), row=2, col=1)

    def plotCountries(self, countries, filename):
        titles = ["{} Logistic Curve".format(country) for country in countries]
        titles.insert(1, "Existing Cases vs. New Cases")
        fig = make_subplots(
            rows=3, cols=2,
            specs=[[{}, {"rowspan":3}],
                [{}, None],
                [{}, None]],
            subplot_titles=titles)

        for i, country in enumerate(countries):
            # print(i)
            self._addCountry(country, fig, i)
        fig.update_layout(
            title="Coronavirus in Countries: Confirmed Growth",
            xaxis_title="Log(Confirmed Cases)",
            yaxis_title="Log(Total New Cases in Last Week)",
            )

        py.iplot(fig, filename = filename)



if __name__ == '__main__':
    df = pd.read_csv('../local_data/time_series_covid19_confirmed_global.csv')
    comparison = World(df)
    comparison.plotCountries(["US", "Korea, South", "Italy"], filename)
