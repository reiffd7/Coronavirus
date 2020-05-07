



class AnimatedBase(object):

    def __init__(self, fig):
        self.createUpdateMenus()
        self.createSliders()
        self.fig = fig


    def createUpdateMenus(self):
        self.updatemenus = [
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

    def createSliders(self):
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

    def setInitial(self, plots):
        for plot, r, c in plots:
            self.fig.add_trace(plot, row=r, col=c)

    def addSliderStep(self, date):
        slider_step = {"args": [
        [date],
        {"frame": {"duration": 300, "redraw": True},
         "mode": "immediate",
         "transition": {"duration": 100}}
    ],
        "label": date,
        "method": "animate"}
        self.sliders_dict["steps"].append(slider_step)


    def finalizeSliders(self):
        self.fig.update_layout(updatemenus=self.updatemenus, sliders=[self.sliders_dict])
