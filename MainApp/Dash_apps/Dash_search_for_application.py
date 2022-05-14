import pandas as pd
import json
import geopy.distance

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
import dash_html_components as html
import dash_table

from django_plotly_dash import DjangoDash

from ..Views_functions import Views_Graph_Objects
from ..models import TenureData
from django_pandas.io import read_frame
import datetime
from MyProjects.models import created_projects
# --------------------------------------------------------------------
# ------------Total number of residential units by date --------------
# --------------------------------------------------------------------
def total_no_res_units_by_date(df):
    # Total number of residential units by date    
    # df['decision_date'] = df['decision_date'].apply(lambda x: pd.Timestamp(day = int(x.split("/")[0]), 
    #                                                                         month = int(x.split("/")[1]), 
    #                                                                         year = int(x.split("/")[2])))
    boroughs = df['Borough'].unique()
    allowed_status = ['Approved', 'Completed', 'Commenced', 'Allowed']

    total_df = df.copy()

    total_df = total_df[(total_df['Status'].isin(allowed_status))]

    total_res_units = Views_Graph_Objects.line_plot("Date", 'Number of residential units', True, True, 450)

    for borough in boroughs:
        
        # For each unique borough get 'decision_date' as x_value for trace
        x_values = sorted(list(total_df[total_df['Borough'] == borough]['decision_date']))

        # For each unique borough get 'proposed residential units' value 
        tmp = list(float(i) for i in total_df[total_df['Borough'] == borough]['NO_proposed_residential_units'])

        y_sum = [0]

        # for each borough sum list of proposed residential units -> every next number is sum of previous ones
        for i in range(0, len(tmp)):
            y_sum.append(y_sum[i] + tmp[i])
        
        del y_sum[0]

        # Create trace, x_value is date, y_value is summed list of proposed residential units 
        total_res_units.add_trace_to_fig(x_values,
                                            y_sum,
                                            borough,
                                            )

        res_units_by_date = total_res_units.print_plot()
        
    return res_units_by_date


# --------------------------------------------------------------------
# --------------------- Status pie charts and table ------------------
# --------------------------------------------------------------------
def status_pie_chart(df):
    # PIE CHART- different status and procentage value

    # Create new dataframe based on df_tenure_data, copy only "status".lower() column
    status_df_all = pd.DataFrame().reset_index(drop = True)
    status_df_all['Status'] = df['Status']
    status_df_all = delete_my_project_status(status_df_all)

    status_df_all['Status'] = status_df_all['Status'].apply(lambda x: str(x).lower())

    # Delete status from created projects
    status_df_all = delete_my_project_status(status_df_all)

    # Add column "count" to dataframe and group by Status -> count columns show how many different status are in df
    status_df_all['count'] = 1
    status_df_all = status_df_all.groupby('Status').sum().reset_index(drop = False)

    plot_data = Views_Graph_Objects.status_pie_chart(status_df_all)
    status_pie_chart_plot = plot_data.create_plot()

    # Create status and counts dictionary
    status_dict = dict()

    for i in range(len(status_df_all['Status'])):
        status_dict[status_df_all['Status'][i]] = (status_df_all['count'][i])

    return status_pie_chart_plot, status_df_all


# --------------------------------------------------------------------
# --------------------- Delete my project status -- ------------------
# --------------------------------------------------------------------
def delete_my_project_status(df):

    df = df[df['Status'] != "my_project"]

    return df


# --------------------------------------------------------------------
# ------------- CALCULATE DISTANCE BASED ON COORDS -------------------
# --------------------------------------------------------------------

# Calculate distance between comparased project coords and other applications and return 
# dataframe where every application is less or equal this distance
def comparsion_form_radius_filter(df, radius):
    try:
        comp_latitude = float(df[df['New'] == 1]['latitude'])
        comp_longitude = float(df[df['New'] == 1]['longitude'])

    except KeyError:
        comp_latitude = 51.508530
        comp_longitude = -0.076132

    except TypeError:
        comp_latitude = 51.508530
        comp_longitude = -0.076132

    df['distance'] = df.apply(lambda row: geopy.distance.geodesic((float(row['latitude']), float(row['longitude'])), (comp_latitude, comp_longitude)).km, axis = 1)
            
    df = df[df['distance'] <= float(radius)]
    
    return df



# ----------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------- DASH APPLICATION SEARCH FOR APPLICATION ----------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------

def dash_app(df_tenure_data):

    all_apps_loc = Views_Graph_Objects.map_locations_all_appls(df_tenure_data, size = 10)
    all_app_plot = all_apps_loc.print_plot()

    try:
        res_units_by_date = total_no_res_units_by_date(df_tenure_data)
    except UnboundLocalError:
        res_units_by_date = "No data"

    density_NO_units_bar_chart = Views_Graph_Objects.density_and_NO_units_bar_chart(df_tenure_data)

    density_affordable_types_bar_chart = Views_Graph_Objects.density_and_affordable_types_bar_chart(df_tenure_data)

    density_NO_storeys_bar_chart = Views_Graph_Objects.density_and_NO_storeys_bar_chart(df_tenure_data)
    status_pie_chart_plot, status_table = status_pie_chart(df_tenure_data)

    app = DjangoDash('SimpleExample', add_bootstrap_links=True)
    # app.css.append_css({ "external_url" : "/static/front/css" })
    app.css.append_css({ "external_url" : "/static/back/css/main.css" })

    projects_options = [{"label": "No selected", "value": 'No selected'}]
    projects_database = list(created_projects.objects.values_list('App_ID', flat = True))
    
    for proj_name in projects_database:
        projects_options.append({"label": proj_name, "value": proj_name})


    app.layout = html.Div([

        ########## MAP LOCATIONS WITH SLIDER
        html.Div([
            
            html.Div([
                html.Div([
                    html.H2(children = "Choose created project for comparison", id = 'dropdown_text')
                    ], className= "block-title"),
                        dcc.Dropdown(id="projects_dropdown", 
                                    multi=False,
                                    options = projects_options),
                ], className = "block full"),


            html.Div([
                html.Div([
                    html.H2(children = "Map locations with slider")
                    ], className= "block-title"),
                        dcc.Slider(min = 0, max=50, step=1, value=30, 
                                    id = 'map_loc_slider', 
                                    tooltip = {'allways_visible' : True, 'placement': 'bottom'},
                                    dots = True),

                        dcc.Graph(id = "map_location",
                                    figure = all_app_plot),
                ], className = "block full"),

            ########## RESIDENTIAL UNITS BY DATE

            
            html.Div([
                html.Div([
                    html.H2(children = "Residential units by date")
                    ], className= "block-title"),

                        dcc.Graph(id = "res_units_by_date",
                                figure= res_units_by_date),

                ], className = "block full"),
            


            ########## STATUS PIE PLOT WITH TABLE

            html.Div([
                html.Div([
                    html.H2(children = "Status pie chart and table")
                    ], className= "block-title"),
                    html.Div([
                            html.Div(id = "status_table_div", 
                                    children = dash_table.DataTable(data = status_table.to_dict("rows"), 
                                                                    columns = [{"name": i, "id": i} for i in status_table.columns], 
                                                                    id = "status_table",
                                                                    style_data={
                                                                            'text-align': 'left',
                                                                            },
                                                                    style_header={
                                                                            'text-align': 'left',
                                                                            },
                                                                    )
                                    ),
                    
                                    html.Button("clear selection", id="clear")
                                ],
                                style={
                                    'display': 'inline-block',
                                    'vertical-align': 'bottom',
                                    'width': '49%',
                                    'height': '100%',

                                }
                                ),
                        html.Div([
                                    dcc.Graph(id = "status_pie_chart",
                                    figure= status_pie_chart_plot),
                                ], style={
                                    'display': 'inline-block',
                                    'vertical-align': 'bottom',
                                    'width': '49%',
                                    'height': '100%',
                                }),  

                ], className = "block full"),


            ########## Density and number of units bar chart

            html.Div([
                html.Div([
                    html.H2(children = "Density and number of units bar chart")
                    ], className= "block-title"),

                        html.Div([
                            dcc.Graph(id = "density_NO_units",
                            figure= density_NO_units_bar_chart),
                        ]),

                ], className = "block full"),

            

            ########## Density affordable types

            html.Div([
                html.Div([
                    html.H2(children = "Density affordable types")
                    ], className= "block-title"),

                        html.Div([
                            dcc.Graph(id = "density_affordable",
                            figure= density_affordable_types_bar_chart),
                        ]),

                ], className = "block full"),

            
            ########## Density and number of storeys


            html.Div([
                html.Div([
                    html.H2(children = "Density and number of storeys")
                    ], className= "block-title"),

                        html.Div([
                            dcc.Graph(id = "density_no_storeys",
                            figure= density_NO_storeys_bar_chart),
                        ]),

                ], className = "block full"),


        
        ])
    ], style={'backgroundColor':'#ededed', "overflowY": "auto"})

    #####################################################################################
    ############################## CALLBACKS ############################################
    #####################################################################################

    ### --------------------------------------------------------------------------
    ### ---------------------- MAP LOCATIONS -------------------------------------
    ### --------------------------------------------------------------------------
    ### CHANGE MAP LOCATION WITH FILTER AS A SELECTED STATUS FROM STATUS TABLE
    @app.callback(
        Output('map_location', 'figure'),
        [Input('map_loc_slider', 'value'),
        Input('status_table', 'active_cell'),
        Input('status_table', 'data')
        ],
        
        )
    def callback_radius(value, active_cell, table_data):

        if active_cell != None:
            cell = json.dumps(active_cell, indent=2)    
            row = active_cell['row']
            col = active_cell['column_id']
            status = str(table_data[row][col]).title()

            df_tenure_data2 = comparsion_form_radius_filter(df_tenure_data, value)

            df_tenure_data3 = df_tenure_data2[df_tenure_data2['Status'] == status]


            all_apps_loc = Views_Graph_Objects.map_locations_all_appls(df_tenure_data3, size = 11)
            all_app_plot = all_apps_loc.print_plot()
            
            return all_app_plot

        df_tenure_data2 = comparsion_form_radius_filter(df_tenure_data, value)
        all_apps_loc = Views_Graph_Objects.map_locations_all_appls(df_tenure_data2, size = 11)
        all_app_plot = all_apps_loc.print_plot()
        
        return all_app_plot

    ### --------------------------------------------------------------------------
    ### --------------- RES UNITS BY DATE LINE PLOT ------------------------------
    ### --------------------------------------------------------------------------

    ### CHANGE DATA BASED ON SLIDER VALUE
    @app.callback(
        Output('res_units_by_date', 'figure'),
        [Input('map_loc_slider', 'value'),
        Input('status_table', 'active_cell'),
        Input('status_table', 'data')])
    def callback_radius(value, active_cell, table_data):

        if active_cell != None:

            cell = json.dumps(active_cell, indent=2)    
            row = active_cell['row']
            col = active_cell['column_id']
            status = str(table_data[row][col]).title()

            df_tenure_data2 = comparsion_form_radius_filter(df_tenure_data, value)

            df_tenure_data_updated = df_tenure_data2[df_tenure_data2['Status'] == status]

            updated = total_no_res_units_by_date(df_tenure_data_updated)
            
            return updated

        df_tenure_data_updated = comparsion_form_radius_filter(df_tenure_data, value)
        updated = total_no_res_units_by_date(df_tenure_data_updated)
        return updated

    ### --------------------------------------------------------------------------
    ### ---------------------- STATUS TABLE --------------------------------------
    ### --------------------------------------------------------------------------

    ### RESET SELECTED TABLE CELL
    @app.callback(
        Output("status_table", "selected_cells"),
        Output("status_table", "active_cell"),
        Input("clear", "n_clicks"),    
    )
    def clear(n_clicks):
        return [], None


    ### UPDATE TABLE STATUS COUNT VALUES
    @app.callback(Output("status_table_div", "children"),
                Input("map_loc_slider", 'value'))
    def change_table_data(slider_value):

        df_tenure_data2 = comparsion_form_radius_filter(df_tenure_data, slider_value)

        status_plot, status_table = status_pie_chart(df_tenure_data2)

        return html.Div(dash_table.DataTable(data = status_table.to_dict("rows"), 
                                                    columns = [{"name": i, "id": i} for i in status_table.columns], 
                                                    id = "status_table",
                                                    style_data={
                                                            'text-align': 'left',
                                                            },
                                                    style_header={
                                                            'text-align': 'left',
                                                            },
                                                    )), 
            
    ### --------------------------------------------------------------------------
    ### ---------------------- STATUS PIE CHART ----------------------------------
    ### --------------------------------------------------------------------------

    ### UPDATE STATUS PIE CHART BASED ON SLIDER RADIUS VALUE
    @app.callback(Output("status_pie_chart", 'figure'),
                Input("map_loc_slider", 'value'))
    def change_table_data(slider_value):

        df_tenure_data_updated = comparsion_form_radius_filter(df_tenure_data, slider_value)

        status_pie_chart_plot, status_table = status_pie_chart(df_tenure_data_updated)

        return status_pie_chart_plot 


    ### --------------------------------------------------------------------------
    ### ------------ DWELLING DENSITY AND TOTAL NUMBER OF UNITS ------------------
    ### --------------------------------------------------------------------------

    ### CHANGE MAP LOCATION BASED ON SLIDER (RADIUS) VALUE (DISTANCE IN KM)
    @app.callback(
        Output('density_NO_units', 'figure'),
        [Input('map_loc_slider', 'value'),
        Input('status_table', 'active_cell'),
        Input('status_table', 'data')]
        )
    def dwell_density_total_number_units(value, active_cell, table_data):

        if active_cell != None:

            cell = json.dumps(active_cell, indent=2)    
            row = active_cell['row']
            col = active_cell['column_id']
            status = str(table_data[row][col]).title()

            df_tenure_data2 = comparsion_form_radius_filter(df_tenure_data, value)

            df_tenure_data_updated = df_tenure_data2.loc[(df_tenure_data2['Status'] == status) | (df_tenure_data2['New'] == 1)] 


            updated = Views_Graph_Objects.density_and_NO_units_bar_chart(df_tenure_data_updated)
            
            return updated

        df_tenure_data_updated = comparsion_form_radius_filter(df_tenure_data, value)
        updated = Views_Graph_Objects.density_and_NO_units_bar_chart(df_tenure_data_updated)

        return updated


    ### --------------------------------------------------------------------------
    ### -------------- DWELLING DENSITY AND AFFORDABLE PERCENTAGE ----------------
    ### --------------------------------------------------------------------------

    ### CHANGE DATA BASED ON SLIDER VALUE
    @app.callback(
        Output('density_affordable', 'figure'),
        [Input('map_loc_slider', 'value'),
        Input('status_table', 'active_cell'),
        Input('status_table', 'data')])
    def dwell_density_aff_percentage(value, active_cell, table_data):

        if active_cell != None:

            cell = json.dumps(active_cell, indent=2)    
            row = active_cell['row']
            col = active_cell['column_id']
            status = str(table_data[row][col]).title()

            df_tenure_data2 = comparsion_form_radius_filter(df_tenure_data, value)

            df_tenure_data_updated = df_tenure_data2.loc[(df_tenure_data2['Status'] == status) | (df_tenure_data2['New'] == 1)] 

            updated = Views_Graph_Objects.density_and_affordable_types_bar_chart(df_tenure_data_updated)
            
            return updated

        df_tenure_data_updated = comparsion_form_radius_filter(df_tenure_data, value)
        updated = Views_Graph_Objects.density_and_affordable_types_bar_chart(df_tenure_data_updated)
        return updated


    ### --------------------------------------------------------------------------
    ### --------------- RES UNITS AND AFFORDABLE PERCENTAGE ----------------------
    ### --------------------------------------------------------------------------

    ### CHANGE DATA BASED ON SLIDER VALUE
    @app.callback(
        Output('density_no_storeys', 'figure'),
        [Input('map_loc_slider', 'value'),
        Input('status_table', 'active_cell'),
        Input('status_table', 'data')])
    def dwell_density_and_NO_storeys(value, active_cell, table_data):

        if active_cell != None:

            cell = json.dumps(active_cell, indent=2)    
            row = active_cell['row']
            col = active_cell['column_id']
            status = str(table_data[row][col]).title()

            df_tenure_data2 = comparsion_form_radius_filter(df_tenure_data, value)

            df_tenure_data_updated = df_tenure_data2.loc[(df_tenure_data2['Status'] == status) | (df_tenure_data2['New'] == 1)] 

            updated = Views_Graph_Objects.density_and_NO_storeys_bar_chart(df_tenure_data_updated)
            
            return updated

        df_tenure_data_updated = comparsion_form_radius_filter(df_tenure_data, value)
        updated = Views_Graph_Objects.density_and_NO_storeys_bar_chart(df_tenure_data_updated)

        return updated


    @app.callback(
    # Output('dropdown_text', 'children'),
    Output('map_loc_slider', 'value'),
    [Input('projects_dropdown', 'value'),
    Input('map_loc_slider', 'value')])
    def dropdown(value, slider_value):

        # Get all data from TenureData database and write to df
        # Add column "NEW" as a flag to targer database (to differentiate old from new project)
        qs = TenureData.objects.all()
        df_tenure_data = read_frame(qs)
        df_tenure_data['New'] = 0
        if value == "No selected":
            dash_app(df_tenure_data)
            return slider_value

        # Get data from created_projects database filtrated by choosen App_ID
        # Creat columns in dataframe with different color, decision date as the nowest from tenure data
        # Add column "NEW" as a flag to targer database (to differentiate old from new project)
        qa = created_projects.objects.filter(App_ID = value)
        df_projects = read_frame(qa)

        df_projects['color'] = "rgb(255,0,0)"
        df_projects['decision_date'] = df_tenure_data['decision_date'].min()
        df_projects['New'] = 1

        df_tenure_data = pd.concat([df_tenure_data, df_projects], ignore_index=True, sort=False)

        dash_app(df_tenure_data)
        return slider_value