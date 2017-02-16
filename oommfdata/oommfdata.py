import os
import glob
import oommfodt
import numpy as np
import traitlets
import ipywidgets
import discretisedfield as df
import matplotlib.pyplot as plt
import IPython.display
from IPython.display import display, clear_output


class DataAnalysisODT:
    def __init__(self, name):
        self.dirname = os.path.join(name, "")
        
        odtfile = max(glob.iglob("{}*.odt".format(self.dirname)),
                      key=os.path.getctime)
        self.dt = oommfodt.OOMMFodt(odtfile).df
        self.time = self.dt["t"].as_matrix()/1e-12
        
        self.slider = ipywidgets.IntSlider(value=self.time[0],
                                             min=self.time[0], 
                                             max=self.time[-1],
                                             step=self.time[1]-self.time[0],
                                             description="t (ps):",
                                             readout=True,
                                             layout=ipywidgets.Layout(width="100%"))

        self.select = ipywidgets.Select(options=list(self.dt.columns.values),
                                        description="Output:")
        
        self.play = ipywidgets.Play(value=self.time[0],
                                    min=self.time[0], 
                                    max=self.time[-1],
                                    step=self.time[1]-self.time[0])
       
        ipywidgets.jslink((self.play, "value"), (self.slider, "value"))
        self.slider.observe(self.update_output_slider)
        self.select.observe(self.update_output_slider)
        self.out = ipywidgets.Output(layout=ipywidgets.Layout(width="300%"))
    
        self.update_output_slider(None)
        
    def _ipython_display_(self):
        box1 = ipywidgets.VBox([self.slider, self.out])
        box2 = ipywidgets.HBox([self.select, box1, self.play])
        display(box2)
            
    def update_output_slider(self, value):
        self.out.clear_output(wait=True)
        plt.plot(self.time, self.dt[self.select.value])
        plt.xlabel("t (ps)")
        plt.ylabel(self.select.value)
        plt.xlim([0, self.slider.value])
        plt.grid()
        with self.out:
            display(plt.gcf())
        plt.close()

        
class DataAnalysisOMF:
    def __init__(self, name):
        self.dirname = os.path.join(name, "")
        
        odtfile = max(glob.iglob("{}*.odt".format(self.dirname)),
                      key=os.path.getctime)
        self.omffiles = sorted(glob.iglob("{}*.omf".format(self.dirname)),
                               key=os.path.getctime)
        last_omf_file = max(glob.iglob("{}*.omf".format(self.dirname)),
                            key=os.path.getctime)
        self.last_field = df.read_oommf_file(last_omf_file)
        
        self.dt = oommfodt.OOMMFodt(odtfile).df
        self.stage = self.dt["stage"].as_matrix()
        
        self.slider = ipywidgets.IntSlider(value=self.stage[0],
                                           min=self.stage[0], 
                                           max=self.stage[-1],
                                           step=self.stage[1]-self.stage[0],
                                           description="Stage:",
                                           readout=True,
                                           layout=ipywidgets.Layout(width="80%"))
        
        self.slice_slider = ipywidgets.FloatSlider(value=0,
                                                   min=0, 
                                                   max=1,
                                                   step=0.01,
                                                   description="Point:",
                                                   readout=True,
                                                   layout=ipywidgets.Layout(width="75.5%"))
        
        self.play = ipywidgets.Play(value=self.stage[0],
                                          min=self.stage[0], 
                                          max=self.stage[-1],
                                          step=self.stage[1]-self.stage[0])

        self.select = ipywidgets.RadioButtons(options=["x", "y", "z"],
                                              description="Slice:")
        
        ipywidgets.jslink((self.play, "value"), (self.slider, "value"))

        self.slider.observe(self.update_plot)
        self.slice_slider.observe(self.update_plot)
        self.select.observe(self.update_plot)
        self.out = ipywidgets.Output(layout=ipywidgets.Layout(width="300%"))
    
        self.update_plot(None)
        
    def _ipython_display_(self):
        box0 = ipywidgets.HBox([self.slider, self.play])
        box1 = ipywidgets.VBox([box0, self.slice_slider, self.out])
        box2 = ipywidgets.HBox([self.select, box1])
        display(box2)
            
    def update_plot(self, value):
        self.out.clear_output(wait=True)
        omffile = self.find_omf_file()
        field = df.read_oommf_file(omffile)
        
        slice_index = {"x": 0, "y": 1, "z": 2}[self.select.value]
        point = field.mesh.pmin[slice_index] + self.slice_slider.value*field.mesh.l[slice_index]
        
        field.plot_slice(self.select.value, point, xsize=10)
        with self.out:
            display(plt.gcf())
        plt.close()
            
    def find_omf_file(self):
        for f in self.omffiles:
            if str(self.slider.value) in f[0:-7]:
                return f
