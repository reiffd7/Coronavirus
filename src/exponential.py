import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import folium
import plotly.express as px
import plotly.io as pio
import chart_studio
import chart_studio.plotly as py
chart_studio.tools.set_credentials_file(username='daniel.reiff', api_key='jhEpBS6888O1FEbZI8M4')
pio.renderers.default = "browser"

## plotly subplots and animations with sigmoid curve 

def sigmoid(x):
  return 10000 / (1 + math.exp(-(1/24)*(x-100)))

x_vals = np.linspace(1, 250, 1000)
sigmoid_vals = np.array([sigmoid(x) for x in x_vals])

diff_sigmoid_vals = np.diff(sigmoid_vals)
y = [0] + [c + n for c, n in zip(diff_sigmoid_vals, diff_sigmoid_vals[1:])]


fig = make_subplots(rows=1, cols=2, subplot_titles=("Logistic Curve", "Existing Values vs. New Values"))
# fig = go.Figure()

fig.add_trace(
    go.Scatter(x=x_vals, y=sigmoid_vals)
)
fig.add_trace(go.Scatter(x=[x_vals[500]], y = [sigmoid_vals[500]]))

fig.add_trace(
    go.Scatter(x=np.log(sigmoid_vals), y=np.log(diff_sigmoid_vals)),
    row=1, col=2
)
fig.add_trace(
    go.Scatter(x=[np.log(sigmoid_vals)[500]], y=[np.log(diff_sigmoid_vals)[500]]),
    row=1, col=2
)

number_frames = 99
frames = [dict(
               name = k,
               data = [go.Scatter(x = [x_vals[k]], y = [sigmoid_vals[k]]),#update the trace 1 in (1,1)
                       go.Scatter(x = [np.log(np.cumsum(sigmoid_vals))[k]], y = [np.log(np.diff(sigmoid_vals))[k]])]
            #    traces =[0, 1] # the elements of the list [0,1,2] give info on the traces in fig.data
                                      # that are updated by the above three go.Scatter instances
              ) for k in range(number_frames-1)]


updatemenus = [dict(type='buttons',
                    buttons=[dict(label='Play',
                                  method='animate',
                                  args=[[f'{k}' for k in range(98)], 
                                         dict(frame=dict(duration=500, redraw=False), 
                                              transition=dict(duration=0),
                                              easing='linear',
                                              fromcurrent=True,
                                              mode='immediate'
                                                                 )])],
                    direction= 'left', 
                    pad=dict(r= 10, t=85), 
                    showactive =True, x= 0.1, y= 0, xanchor= 'right', yanchor= 'top')
            ]

sliders = {
    "active": 0,
    "yanchor": "top",
    "xanchor": "left",
    "currentvalue": {
        "font": {"size": 20},
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

for x in range(number_frames - 1): 
    slider_step = {"args": [
            [x],
            {"frame": {"duration": 300, "redraw": False},
            "mode": "immediate",
            "transition": {"duration": 300}}
        ],
            "label": x,
            "method": "animate"}

    sliders["steps"].append(slider_step)

fig.update_layout(height=600, width=800, title_text="Side By Side Subplots")
# fig.update(frames=frames)
# fig.update_layout(updatemenus=updatemenus,
#                   sliders=[sliders])
fig.show()
py.plot(fig, filename = "fat logistic")