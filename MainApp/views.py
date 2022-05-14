# from os import startfile, stat
from typing import ChainMap, get_args
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django_pandas.io import read_frame
from django.contrib.sessions.models import Session
from django import db
import sqlite3
import time
from pandas.core.frame import DataFrame
from plotly.offline import plot
# Import libraries for datahub request
from datetime import date
from urllib.error import HTTPError

from collections import OrderedDict, defaultdict
from django.forms.models import model_to_dict

import pandas as pd

# Import external functions
from .models import TenureData
from .models import AllApps

from .Views_functions import Planning_Datahub_Get_Data
from .Views_functions import Planning_Datahub_Get_Res_Units_Data_Cleaning
from .Views_functions import Planning_Datahub_geometry_functions
from .Views_functions import Planning_Datahub_Save_to_Database
from .Views_functions import Views_Graph_Objects 

from .Dash_apps import Dash_search_for_application

from MyProjects.models import created_projects



### ------------------------------------------------------------------------------------------------------ ###
### ------------------------------------- Functions  ----------------------------------------------------- ###
### ------------------------------------------------------------------------------------------------------ ###

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


def change_column_names(df):
    # Get proper columns names

    df_app_details = df.copy()

    df_app_details.rename(columns={
        'app_det_left_total_no_proposed_residential_affordable_units': 'affordable_units',
        'app_det_left_total_no_proposed_residential_units_market_for_sale': 'market_for_sale',
        'app_det_left_total_no_proposed_residential_units_market_for_rent': 'market_for_rent',
        'app_det_left_total_no_proposed_residential_units_starter_homes': 'starter_homes',

        'app_det_left_total_no_proposed_residential_units_intermediate': 'intermediate',
        'app_det_left_total_no_proposed_residential_units_social_rent': 'sociat_rent_units',
        'app_det_left_total_no_proposed_residential_units_london_living_rent': 'london_living_rent',
        'app_det_left_total_no_proposed_residential_units_affordable_rent': 'affordable_rent',
        'app_det_left_total_no_proposed_residential_units_london_affordable_rent': 'london_affordable_rent',
        'app_det_left_total_no_proposed_residential_units_discount_market_rent': 'discount_market_rent',
        'app_det_left_total_no_proposed_residential_units_discount_market_sale': 'discount_market_sale',
        'app_det_left_total_no_proposed_residential_units_discount_market_rent_charged_at_london_rents': 'market_rent_charged_london_rents',
        'app_det_left_total_no_proposed_residential_units_self_build_and_custom_build': 'self_build_and_custom_build',
        'app_det_left_total_no_existing_residential_affordable_units': 'Existing_residential_affordable_units',
        'app_det_left_habitable_rooms_density' : 'habitable_rooms_density',
        'app_det_left_total_no_existing_residential_units_affordable_rent': 'Existing_residential_affordable_rent',
        'app_det_left_total_no_existing_residential_units_london_shared_ownership' : 'Existing_residential_London_shared_ownership',
        'app_det_left_total_no_existing_residential_units_london_affordable_rent': 'Existing_residential_London_affordable_rent',
        'app_det_left_dwelling_density': "Dwelling_density", 
        'app_det_left_site_area': "Site_Ares",
        'app_det_left_total_no_existing_residential_units': 'Existing_residential_units',
        'NO storeys': 'NO_storeys',
        'NO proposed residential units': 'NO_proposed_residential_units',
        'Affordable Percentage': 'Affordable_Percentage',
        'Unit type: Studio Bedsit': 'Unit_type_Studio_Bedsit',
        'Unit type: Flat Apartment Maisonette': 'Unit_type_Flat_Apartment_Maisonette', 
        'Provider: Local Authority': 'Provider_Local_Authority',
        'Provider: Private rented sector': 'Provider_Private_rented_sector', 
        'Provider: Private': 'Provider_Private',
        'Provider: Housing Association': 'Provider_Housing_Association', 
        'Development type: New Build': 'Development_type_New_Build',
        'Development type: Change of Use': 'Development_type_Change_of_Use',

        }, inplace=True)

    return df_app_details

 
# FloorSpace details line plot
# Floorspace GIA plot
# floorspace_detail_gia_gained
# floorspace_detail_gia_lost
def GIA_plot_data(df, app_id):

    if float(df[df['App_ID'] == app_id]['floorspace_detail_gia_gained']) > float(df[df['App_ID'] == app_id]['floorspace_detail_gia_lost']):
        y_values = [float(df[df['App_ID'] == app_id]['floorspace_detail_gia_existing']), float(df[df['App_ID'] == app_id]['floorspace_detail_gia_gained'])]
    
    elif float(df[df['App_ID'] == app_id]['floorspace_detail_gia_gained']) < float(df[df['App_ID'] == app_id]['floorspace_detail_gia_lost']):
        y_values = [float(df[df['App_ID'] == app_id]['floorspace_detail_gia_lost']), float(df[df['App_ID'] == app_id]['floorspace_detail_gia_existing'])]
    
    x_values = [1, 2]
    
    return  x_values, y_values


##############################################################################################################
### ------------------------------------- Main Views ----------------------------------------------------- ###
##############################################################################################################
# How to save to database faster? Maybe use database only for all application (as in all_apps function), 
#   and Tenure data save in dataframe (?)
#
# Now -> if data is given in filtrating form, we use SQL query to get data between given dates (line 191),
#   maybe faster aproach will be to get all data, and filtrate this using pandas df (.loc for example)
#
# How to save faster to database? maybe as mentioned in point 1st. we could use only dataframe, 
#   not saving do sql 
#
# --------------------------------------------------------------------
# ----------------- VIEW - Search for application  -------------------
# --------------------------------------------------------------------
class search_for_application(View):
    
    Session.objects.all().delete()

    def get(self, request):
        print("---- GET SEARCH FOR APPLICATION FILTER ----")
        db.connections.close_all()

        qs = TenureData.objects.all()
        df_tenure_data = read_frame(qs)
        
        tenure_data = TenureData.objects.all()

        projects_database = list(created_projects.objects.values_list('App_ID', flat = True))

        Dash_search_for_application.dash_app(df_tenure_data)

        return render(request, 'front/search_for_application.html', {'projects_database': projects_database,
                                                                    'tenure_data' : tenure_data})

    def post(self, request):
        
        if 'search_filter' in request.POST:
            #---------------------------- GET DATAHUB DATA ------------------------------------------

            # SAVE TO DATABASE : 16 s
            # DB TO DF 9 s
            # Delete db 3 s

            date_from = request.POST.get('date_from')
            date_to = request.POST.get('date_to')

            status = request.POST.getlist('choose_status')

            
            # Clearing data from database
            TenureData.objects.all().delete()

            # WORKING:
            # qs = AllApps.objects.filter(decision_date__range = [date_from_range, date_to_range])
            # df_tenure_data = read_frame(qs)
            if date_from == '' or date_to == '':
                start_time = time.time()
                cnx = sqlite3.connect('db.sqlite3')
                df_tenure_data = pd.read_sql_query("SELECT * from  MainApp_allapps", cnx)
                cnx.commit()
                cnx.close()
                print("Read from Db do DF : {}".format(time.time() - start_time))
            else:
                date_from_m_d_y = date_from.split('/')
                date_to_m_d_y = date_to.split('/')

                date_from_range = pd.Timestamp(day = int(date_from_m_d_y[1]),
                                                month = int(date_from_m_d_y[0]),
                                                year = int(date_from_m_d_y[2]))

                date_to_range = pd.Timestamp(day = int(date_to_m_d_y[1]),
                                                month = int(date_to_m_d_y[0]),
                                                year = int(date_to_m_d_y[2]))

                start_time = time.time()
                cnx = sqlite3.connect('db.sqlite3')
                df_tenure_data = pd.read_sql_query("SELECT * from  MainApp_allapps WHERE decision_date BETWEEN '{}'  AND '{}'".format(date_from_range, date_to_range), cnx)
                cnx.commit()
                cnx.close()
                print("Read from Db do DF : {}".format(time.time() - start_time))
            # Save to database
            Planning_Datahub_Save_to_Database.save_to_database(TenureData, df_tenure_data)

            tenure_data = TenureData.objects.all()

            projects_database = list(created_projects.objects.values_list('App_ID', flat = True))

            Dash_search_for_application.dash_app(df_tenure_data)

            return render(request, 'front/search_for_application.html',{'projects_database': projects_database,
                                                                        'tenure_data': tenure_data})  
            
        elif "all_apps" in request.POST:
            #---------------------------- GET DATAHUB DATA ------------------------------------------
            # Clearing data from database
            AllApps.objects.all().delete()
            
            site_area = '0,100'
            units_filter = '0,100000'



            date_from = '01/01/2010'
            date_to = '12/31/2011'
            
            for i in range(18, 19):
                print("Searching for application in range: 01/01/20{}  TO  12/31/20{}".format(i, i))
                date_from = '01/01/20{}'.format(i)
                date_to = '12/31/20{}'.format(i)

                status = request.POST.getlist('choose_status')

                ### Functions call
                lpa_name = "*"
            
                df_raw_data = Planning_Datahub_Get_Data.get_data(site_area, units_filter, date_from, date_to, status, lpa_name)
                df_cleaned_data = Planning_Datahub_Get_Res_Units_Data_Cleaning.cleaning_data(df_raw_data)

                #---------------------------- DELETED FOR NOW ------------------------------------------
                #df_transformed_coords = Planning_Datahub_geometry_functions.transform_coordinates(df_cleaned_data)
                #---------------------------------------------------------------------------------------

                df = Planning_Datahub_geometry_functions.get_centroid_data(df_cleaned_data)
                df['Polygon_coords'] = df['polygon']

                df_tenure_data = change_column_names(df)

                df_tenure_data = get_status_color(df_tenure_data)
                print(df_tenure_data['decision_date'][4])
                df_tenure_data['decision_date'] = df_tenure_data['decision_date'].apply(lambda x: pd.Timestamp(day = int(x.split("/")[0]), 
                                                                                                            month = int(x.split("/")[1]), 
                                                                                                            year = int(x.split("/")[2])))
                print(df_tenure_data['decision_date'][4])
                # Save to database
                Planning_Datahub_Save_to_Database.save_to_database(AllApps, df_tenure_data)



            ### LOOP END ###
            tenure_data = TenureData.objects.all()

            projects_database = list(created_projects.objects.values_list('App_ID', flat = True))

            Dash_search_for_application.dash_app(df_tenure_data)

            return render(request, 'front/search_for_application.html',{'projects_database': projects_database,
                                                                        'tenure_data': tenure_data})
            

    
        
# --------------------------------------------------------------------
# ----------------- VIEW - Application details  ----------------------
# --------------------------------------------------------------------
class application_details(View):

    def get(self, request, word):

        # Get database data to pandas dataframe
        qs = TenureData.objects.all()
        df = read_frame(qs)
        
        # Get parking values from database and convert to dictionary to filtrate in "app_details.html" 
        parking_fields = [k for k in TenureData.objects.filter(App_ID = word).values()[0] if 'parking' in k]
        parking_dict = dict()

        for i in parking_fields:
            parking_dict[i] = TenureData.objects.filter(App_ID = word).values()[0][i]


        details = TenureData.objects.filter(App_ID = word)

        tenure_pie_chart = Views_Graph_Objects.tenure_pie_chart(word)

        app_map_location = Views_Graph_Objects.map_locations_all_appls(df[df['App_ID'] == word], 13, 
                                                             "rgb(255, 0, 0)", 
                                                             float(df.loc[df['App_ID'] == word, ['latitude']].values[0][0]), 
                                                             float(df.loc[df['App_ID'] == word, ['longitude']].values[0][0]))
        app_map_location_plot = app_map_location.print_plot()
        app_map_location_plot = plot(figure_or_data=app_map_location_plot, 
                                output_type='div')

        # --------------------------------------------------------------------
        # ------------------ Affordable units details plot -------------------
        # --------------------------------------------------------------------

        if df[df['App_ID'] == word]['Affordable_Percentage'].iloc[0] != '0.0 %':

            affortable_units_details = ['london_living_rent', 'london_affordable_rent',
                                    'sociat_rent_units', 'intermediate', 'market_rent_charged_london_rents',
                                    'self_build_and_custom_build', 'discount_market_sale', 'market_for_rent']

            affordable_details = Views_Graph_Objects.bar_plot_details(word, affortable_units_details, 'Affordable types')
            affordable_details_plot = affordable_details.print_plot()

        else:
            affordable_details_plot = "No data to show"

        # --------------------------------------------------------------------
        # ------------------------- Units type plot --------------------------
        # --------------------------------------------------------------------

        units_types_details = ['Unit_type_Studio_Bedsit', 'Unit_type_Flat_Apartment_Maisonette',
                               'Provider_Housing_Association', 'Provider_Private_rented_sector',
                               'Provider_Private', 'Development_type_Change_of_Use', 'Development_type_New_Build']
        units_types = Views_Graph_Objects.bar_plot_details(word, units_types_details, 'Units type')
        units_types_plot = units_types.print_plot()
        
        
        # --------------------------------------------------------------------
        # ------------- GIA existing/ proposed/ lost change ------------------
        # --------------------------------------------------------------------
        try:
            x_values, y_values = GIA_plot_data(df, word)
            GIA_data_plot = Views_Graph_Objects.line_plot("Change", "GIA values", False, False, 275, word)
            GIA_data_plot.add_trace_to_fig(x_values, y_values, "GIA")
            line_GIA_plot = GIA_data_plot.print_plot()
            line_GIA_plot = plot(figure_or_data=line_GIA_plot, 
                                output_type='div')
        except UnboundLocalError:
            line_GIA_plot = "No data to show"

        # --------------------------------------------------------------------

        return render(request, 'front/app_details.html', {'details' : details, 
                                                          'tenure_pie_chart' : tenure_pie_chart,
                                                          'app_map_location' : app_map_location_plot,
                                                          'affordable_units_plot': affordable_details_plot,
                                                          'units_types_plot': units_types_plot,
                                                          'line_GIA_plot' : line_GIA_plot,
                                                          'parking_dict' : parking_dict
                                                          })

class home(View):

    def get(self, request):

        return render(request, 'front/home.html')



# def post(self, request):
        
#         if 'search_filter' in request.POST:
#             #---------------------------- GET DATAHUB DATA ------------------------------------------
#             site_area = request.POST.get('site_area')
#             units_filter = request.POST.get('units_filter')

#             date_from = request.POST.get('date_from')
#             date_to = request.POST.get('date_to')

#             status = request.POST.getlist('choose_status')

#             ### Functions call
#             lpa_name = "*"
        
#             df_raw_data = Planning_Datahub_Get_Data.get_data(site_area, units_filter, date_from, date_to, status, lpa_name)
#             df_cleaned_data = Planning_Datahub_Get_Res_Units_Data_Cleaning.cleaning_data(df_raw_data)

#             #---------------------------- DELETED FOR NOW ------------------------------------------
#             #df_transformed_coords = Planning_Datahub_geometry_functions.transform_coordinates(df_cleaned_data)
#             #---------------------------------------------------------------------------------------

#             df = Planning_Datahub_geometry_functions.get_centroid_data(df_cleaned_data)
#             df['Polygon_coords'] = df['polygon']

#             df_tenure_data = change_column_names(df)

#             df_tenure_data = get_status_color(df_tenure_data)

#             # Clearing data from database
#             TenureData.objects.all().delete()

#             # Save to database
#             Planning_Datahub_Save_to_Database.save_to_database(TenureData, df_tenure_data)

#             tenure_data = TenureData.objects.all()

#             projects_database = list(created_projects.objects.values_list('App_ID', flat = True))

#             Dash_search_for_application.dash_app(df_tenure_data)

#             return render(request, 'front/search_for_application.html',{'projects_database': projects_database,
#                                                                         'tenure_data': tenure_data})  
            
#         elif "all_apps" in request.POST:
#             #---------------------------- GET DATAHUB DATA ------------------------------------------
#             site_area = '0,100'
#             units_filter = '0,100000'

#             date_from = '01/01/2018'
#             date_to = '01/31/2018'

#             status = request.POST.getlist('choose_status')

#             ### Functions call
#             lpa_name = "*"
        
#             df_raw_data = Planning_Datahub_Get_Data.get_data(site_area, units_filter, date_from, date_to, status, lpa_name)
#             df_cleaned_data = Planning_Datahub_Get_Res_Units_Data_Cleaning.cleaning_data(df_raw_data)

#             #---------------------------- DELETED FOR NOW ------------------------------------------
#             #df_transformed_coords = Planning_Datahub_geometry_functions.transform_coordinates(df_cleaned_data)
#             #---------------------------------------------------------------------------------------

#             df = Planning_Datahub_geometry_functions.get_centroid_data(df_cleaned_data)
#             df['Polygon_coords'] = df['polygon']

#             df_tenure_data = change_column_names(df)

#             df_tenure_data = get_status_color(df_tenure_data)

#             # Clearing data from database
#             AllApps.objects.all().delete()

#             # Save to database
#             Planning_Datahub_Save_to_Database.save_to_database(AllApps, df_tenure_data)

#             tenure_data = TenureData.objects.all()

#             projects_database = list(created_projects.objects.values_list('App_ID', flat = True))

#             Dash_search_for_application.dash_app(df_tenure_data)

#             return render(request, 'front/search_for_application.html',{'projects_database': projects_database,
#                                                                         'tenure_data': tenure_data})