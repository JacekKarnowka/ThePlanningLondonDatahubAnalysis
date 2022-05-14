from os import name
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot
import pandas as pd
from plotly.subplots import make_subplots
import itertools
from datetime import datetime

from ..models import TenureData
from .. import views
from django_pandas.io import read_frame

pd.options.mode.chained_assignment = None  # default='warn'

### ------------------------------------------------------------------------------------------------------ ###
### -------------------------------- Sort by dwelling density  ------------------------------------------- ###
### ------------------------------------------------------------------------------------------------------ ###

def sort_df_density(df):

    # Sort df by dwelling density
    df['Dwelling_density'] = df['Dwelling_density'].apply(lambda x: float(x))

    df.sort_values(by = ['Dwelling_density'], ascending = False, inplace = True)
    df = df.reset_index()

    try: 
        new_project_index = df.index[df['New'] == 1].tolist()
    except KeyError:
        return df[0:50]
    if new_project_index == []:
        return df[0:50]
    if new_project_index[0] > 25:

        df_cut = df[new_project_index[0] - 25 : new_project_index[0] + 25]

    elif new_project_index[0] < 25:
        
        df_cut = df[0: 50]

    else:

        df_cut = df[0:50]

    return df_cut


### ------------------------------------------------------------------------------------------------------ ###
### -------------------------- APP DETAILS AND SEARCH FOR APPLICATION ------------------------------------ ###
### ------------------------------------------------------------------------------------------------------ ###

class line_plot():
    def __init__(self,  x_title, y_title, legend_bool, xaxis_title_bool, height, app_id = None):
        self.app_id = app_id
        self.x_title = x_title
        self.y_title = y_title
        self.legend_bool = legend_bool
        self.xaxis_title_bool = xaxis_title_bool
        self.fig = go.Figure()
        self.height = height

    def add_trace_to_fig(self, x_values, y_values, name):

        self.x_values = x_values
        self.y_values = y_values
        self.name = name

        self.fig.add_trace(go.Scatter(x = self.x_values, 
                                      y = self.y_values,
                                      name = self.name
                                      ))


    def print_plot(self):
    
        self.fig.update_layout(autotypenumbers='convert types',
                                yaxis=dict(title = self.y_title,
                                            showgrid=True,
                                            showline=True,
                                            showticklabels=True),
                                xaxis=dict(title = self.x_title, 
                                           showticklabels=self.xaxis_title_bool),
                                showlegend = self.legend_bool,
                                font={"color": "gray",
                                  'family': 'sans-serif',
                                  'size': 12
                                  },

                                   margin = {
                                              'b' : 0,
                                              'l' : 0,
                                              'r' : 0,
                                              't' : 0,
                                              },
                                   legend = dict(
                                      orientation = 'h',
                                      y = -0.3,
                                      ),
                                   height = self.height
                                )

        return self.fig


class status_pie_chart():

    def __init__(self, plot_1):
        self.plot_1 = plot_1

    def create_plot(self):
        fig = go.Figure()

        fig.add_trace(go.Pie(
            values=self.plot_1['count'],
            labels=self.plot_1['Status']))


        fig.update_layout( autotypenumbers='convert types',

                     coloraxis=dict(colorscale='Bluered_r'), 
                      legend = dict(
                          orientation = 'v',
                          y = 0,
                          ),
                      margin = {
                                'b' : 0,
                                'l' : 0,
                                'r' : 0,
                                't' : 0,
                                },

                        height = 250
                        )


        return fig

    
### ------------------------------------------------------------------------------------------------------ ###
### ------------------------------------- APP DETAILS  --------------------------------------------------- ###
### ------------------------------------------------------------------------------------------------------ ###

class bar_plot_details():

    def __init__(self, app_id, data_to_plot, y_name):
        self.app_id = app_id
        self.data_to_plot = data_to_plot
        self.y_name = y_name

    def print_plot(self):

        qs = TenureData.objects.all()
        df = read_frame(qs)

        fig = go.Figure()

        for detail in self.data_to_plot:

            fig.add_trace(go.Bar( x = [detail],
                                  y = df[df['App_ID'] == self.app_id][detail],
                                  hoverinfo='text',
                                  hovertext = df[df['App_ID'] == self.app_id][detail],
                                  name = detail)
                )
        fig.update_layout(autotypenumbers='convert types',
                            yaxis=dict(title = self.y_name,
                                        showgrid=True,
                                        showline=True,
                                        showticklabels=True),
                            xaxis=dict(showticklabels=False),
                            font={"color": "gray",
                                  'family': 'sans-serif',
                                  'size': 12
                                  },

                            showlegend = True,
                               margin = {
                                          'b' : 0,
                                          'l' : 0,
                                          'r' : 0,
                                          't' : 0,
                                          },
                               legend = dict(
                                  orientation = 'h',
                                  y = 0,
                                  ),
                               height = 335
                            )

        plot_div = plot(figure_or_data=fig, output_type='div')

        return plot_div

def get_status_color(df):
    df['color'] = df['Status'].apply(lambda x: 
                                     "rgb(124,98,78)" if x == "Allowed"
                                     else "rgb(226,207,190)" if x == "Approved"
                                     else "rgb(109,148,198)" if x == "Commenced"
                                     else "rgb(3,100,110)" if x == "Completed"
                                     else "rgb(241,234,226)" if x == "Lapsed"
                                     else "rgb(217,50,34)" if x == "Submited"
                                     else "rgb(155,153,155)")


    return df

def tenure_pie_chart(app_id):

    qs = TenureData.objects.all()
    df = read_frame(qs)

    df_tenure_data = views.change_column_names(df)

    df_tenure_data = views.get_status_color(df_tenure_data)

    df_tmp = df_tenure_data[df_tenure_data['App_ID'] == app_id].copy().reset_index()
    
    datails = df_tmp[[
        'affordable_units',
        'market_for_sale',
        'market_for_rent',
        'starter_homes',
    ]].T.reset_index()

    datails.rename(columns={'index': 'key', 0: 'value'}, inplace=True)

    fig_4 = px.pie(datails,
                   values='value',
                   names='key',
                   labels='value',

                   )
    fig_4.update_traces(textposition='inside', textinfo='percent+label')

    fig_4.update_layout(
                        font={"color": "gray",
                              'family': 'sans-serif',
                              'size': 12
                              },
                       showlegend = True,
                       legend = dict(
                          orientation = 'v',
                          y = 0, x = 0
                          ),
                       margin = {
                          'b' : 0,
                          'l' : 0,
                          'r' : 0,
                          't' : 0,
                          },
                       height = 230
                       )

    plot_div = plot(figure_or_data=fig_4, output_type='div')

    return plot_div


# -----------------------------------------------------------------------------------------------------
# ------------------------------- SEARCH_FOR_APPLICATION ----------------------------------------------
# -----------------------------------------------------------------------------------------------------

class map_locations_all_appls():
    def __init__(self, df, size, color = None, lat = 51.509865, lon = -0.118092):
        self.mapbox_access_token = 'pk.eyJ1IjoiamFjZWtrYXJub3drIiwiYSI6ImNrenZsajFpOTFvYjQyb29objA3dTYzNjYifQ.qDY3-VZu6GfWci1dVbibpA'
        self.scatter_size = size
        self.df = df
        self.color = color
        self.lat = lat
        self.long = lon
        #self.sel_type = sel_type

    def print_plot(self):
        self.df['size'] = self.scatter_size

        if self.color == None:
            marker = {
                'color' : self.df.color,
                'size' : self.df['size'],
                'opacity' : 0.9
                }
        else:
            marker = {
                'color' : self.color,
                'size' : self.df['size'],
                'opacity' : 0.9
                }

        fig = go.Figure()
        fig.add_trace(go.Scattermapbox(
            name = "Map location plot",
            lat = self.df['latitude'],
            lon = self.df['longitude'],
            marker = go.scattermapbox.Marker(
                marker)
            ))

        fig.update_layout(
            uirevision = True,
            mapbox = {
                        'style': "light",
                        'accesstoken': self.mapbox_access_token,
                        "zoom": 9.3,
                        'pitch': 10,
                        "center": {
                            "lat": self.lat,
                            "lon": self.long,
                        }
            },
            margin= {"r": 0, "t": 0, "l": 0, "b": 0},
            height = 550
            )
        return fig


# SUBPLOTS: 
# first plot: Y: 'Dwelling_density', X: 'App_ID',
# secoung plot: Y: NO_proposed_residential_units
def density_and_NO_units_bar_chart(df):

    fig = make_subplots(rows=2, cols=1, shared_xaxes= False, vertical_spacing = 0.28)

    df['color_gray'] = "rgb(155,153,155)"

    status_set = set()

    df = sort_df_density(df)

    app_list = list(df['App_ID'])

    for app in app_list:
        fig.append_trace(go.Bar(
                            x=[str(app)], 
                            y=df[df['App_ID'] == app]['Dwelling_density'],
                            marker={'color': df[df['App_ID'] == app]['color'], 
                                    'showscale': False},
                            hoverinfo='text',
                            
                            hovertext = df[df['App_ID'] == app]['Dwelling_density'],
                            name = df.loc[df['App_ID'] == app, ['Status']].values[0][0],
                            showlegend = True if df.loc[df['App_ID'] == app, ['Status']].values[0][0] not in status_set else False,

                            ), 1, 1)
        status_set.add(df.loc[df['App_ID'] == app, ['Status']].values[0][0]),


        fig.add_trace(go.Bar(
                            x=df['App_ID'], 
                            y=df['NO_proposed_residential_units'],
                            marker={'color': df[df['App_ID'] == app]['color_gray']},
                            showlegend = False,
                            #text = df['NO_proposed_residential_units'],
                            hoverinfo='text',
                            hovertext = df['NO_proposed_residential_units']
                            ), 2, 1)

    fig.update_layout( autotypenumbers='convert types',

                     coloraxis=dict(colorscale='Bluered_r'), 
                      legend = dict(
                          orientation = 'h',
                          y = -0.3,
                          ),
                        yaxis=dict(title = "Dwelling density",
                                    showgrid=True,
                                    showline=True,
                                    showticklabels=True),
                        yaxis2=dict(title = "Total number of units",
                                    showgrid=True,
                                    showline=True,
                                    showticklabels=True),

                        title = dict(text = "Dwellig density and total number of units",
                                     y = 0.95,
                                     x = 0.5,
                                     xanchor = 'center',
                                     yanchor = 'top'
                            ),

                        height = 800
                        )

    return fig


# 
# Affordable unit types and dwelling density
#
def density_and_affordable_types_bar_chart(df):

    fig = make_subplots(rows=2, cols=1, shared_xaxes= False, vertical_spacing = 0.28)

    df = sort_df_density(df)

    affordable = ['affordable_units',
                    'market_for_sale',
                    'market_for_rent',
                    'starter_homes',
                    ]

    for name in affordable:
        fig.append_trace(go.Bar(
                                x = df['App_ID'],
                                y = df[name],
                                hoverinfo='text',
                                hovertext = df['Affordable_Percentage'],
                                name = name), 1, 1)

    fig.add_trace(go.Bar(
                        x=df['App_ID'], 
                        y=df['Dwelling_density'],
                        marker={'color': "rgb(155,153,155)", 
                                'showscale': False},
                        showlegend = False,
                        hoverinfo='text',
                        hovertext = df['Dwelling_density'],
                        name = "Dwelling Density Plot"
                        ),2,1)
    

    fig.update_layout( autotypenumbers='convert types',

                      barmode = 'stack',
                      legend = dict(
                          orientation = 'h',
                          y = -0.3,
                          ),
                      title = dict(text = "Dwellig density and affordable percentage (with specified type)",
                                     y = 0.95,
                                     x = 0.5,
                                     xanchor = 'center',
                                     yanchor = 'top'
                            ),

                      yaxis1=dict(title = "Number of units (affordable types)",
                                    showgrid=True,
                                    showline=True,
                                    showticklabels=True),

                        yaxis2=dict(title = "Dwelling density",
                                    showgrid=True,
                                    showline=True,
                                    showticklabels=True),


                        height = 800
                        )

    return fig


# 
# Dwelling density with no storyes
#
def density_and_NO_storeys_bar_chart(df):

    fig = make_subplots(rows=2, cols=1, shared_xaxes= False, vertical_spacing = 0.28)

    df = sort_df_density(df)

    try:
        df['NO_storeys'] = df['NO_storeys'].apply(lambda x: float(x) if x != 'nan' else 0)
    except TypeError:
        df['NO_storeys'] = 0

    fig.add_trace(go.Bar(x = df['App_ID'],
                         y = df['NO_storeys'],
                         marker={'color': df['color'], 
                                #'colorscale': 'matter',
                                'showscale': False},
                         hoverinfo='text',
                         hovertext = df['NO_storeys'],
                         ), 1, 1)

    fig.add_trace(go.Bar(
                        x=df['App_ID'], 
                        y=df['Dwelling_density'],
                        marker={'color': "rgb(155,153,155)", 
                                     'showscale': False},
                        hoverinfo='text',
                        hovertext = df['Dwelling_density'],
                        ),2,1)

    fig.update_layout( autotypenumbers='convert types',
                        coloraxis=dict(colorscale='Bluered_r'), 
                        showlegend=False,

                        yaxis=dict(title = "Number of storeys",
                                    showgrid=True,
                                    showline=True,
                                    showticklabels=True),
                        yaxis2=dict(title = "Dwelling density",
                                    showgrid=True,
                                    showline=True,
                                    showticklabels=True),

                        title = dict(text = "Number of storeys and dwelling density",
                                     y = 0.95,
                                     x = 0.5,
                                     xanchor = 'center',
                                     yanchor = 'top'
                            ),

                        height = 800

                        )

    return fig

