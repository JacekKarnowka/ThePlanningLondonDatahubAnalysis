import pandas as pd
import ast
import numpy as np

# 
# Get informations about residential units
#

def get_dictionary_residential_units_data(tmp):
    
    if 'residential_details' not in tmp['application_details']:
        return "NO DATA"

    residential_details = tmp['application_details']['residential_details']

    tmp_dict = {}

    change_type = []
    unit_type = []
    unit_development_type = []
    provider = []
    tenure = []

    for i in residential_details['residential_units']:
        change_type.append(i['change_type'])
        unit_type.append(i['unit_type'])
        unit_development_type.append(i['unit_development_type'])
        provider.append(i['provider'])
        tenure.append(i['tenure'])

    tmp_dict['change_type'] = change_type
    tmp_dict['unit_type'] = unit_type
    tmp_dict['unit_development_type'] = unit_development_type 
    tmp_dict['provider'] = provider
    tmp_dict['tenure'] = tenure
    tmp_dict2 = {}

    df2 = pd.DataFrame.from_dict(tmp_dict)
    tmp_dict2['change_type'] = dict(df2['change_type'].value_counts())
    tmp_dict2['unit_type'] = dict(df2['unit_type'].value_counts())
    tmp_dict2['unit_development_type'] = dict(df2['unit_development_type'].value_counts())
    tmp_dict2['provider'] = dict(df2['provider'].value_counts())
    tmp_dict2['tenure'] = dict(df2['tenure'].value_counts())

    return tmp_dict2

#
# Get residential units data directly from source['application_details']['residential_details'] 
#
def get_more_residential_units_data(df):
    values = ['total_no_proposed_bedrooms',
                'total_no_proposed_residential_units',
                'total_no_proposed_residential_units_london_living_rent',
                'total_no_proposed_residential_units_london_affordable_rent',
                'total_no_proposed_residential_units_affordable_rent',
                'total_no_proposed_residential_affordable_units',
                'total_no_proposed_residential_units_market_for_sale',
                'total_no_proposed_residential_units_social_rent',
                'total_no_proposed_residential_units_intermediate',
                'total_no_proposed_residential_units_discount_market_rent_charged_at_london_rents',
                'total_no_proposed_residential_units_market_for_rent',
                'total_no_proposed_residential_units_discount_market_sale',
                'total_no_proposed_residential_units_self_build_and_custom_build',
                'total_no_proposed_residential_units_starter_homes',
                'total_no_proposed_residential_units_discount_market_rent',
                'total_no_existing_residential_affordable_units',
                'habitable_rooms_density',
                'total_no_existing_residential_units_affordable_rent',
                'total_no_existing_residential_units_london_shared_ownership',
                'total_no_existing_residential_units_london_affordable_rent',
                'dwelling_density',
                'site_area',
                'affordable_percentage',
                'total_no_existing_residential_units',
                ]

    # Get more residential details data from columns name listed above. 
    for i in values:
        df['app_det_left_{}'.format(i)] = df['source'].apply(
            lambda x: float(x['application_details']['residential_details'][i]) if x['application_details']['residential_details'][i] != None else 0)

    return df

#
# Get floorspace details, if empty write 'nan' value to df
#
def get_floorspace_details(df):

    floorspace_details = ['actual_commencement_date', 'actual_completion_date', 'gia_existing', 'gia_gained',
                          'gia_lost', 'superseded_by_lpa_app_no', 'superseded_date', 'use_class']

    
    for det in floorspace_details:
        df['floorspace_detail_{}'.format(det)] = df['source'].apply(lambda x: x['application_details']['existing_proposed_floorspace_details'][0][det] 
                                                                            if ('existing_proposed_floorspace_details' in x['application_details']) and 
                                                                                (len(x['application_details']['existing_proposed_floorspace_details']) > 0) and
                                                                                (det in x['application_details']['existing_proposed_floorspace_details'][0])
                                                                            else "nan")
    return df

# 
# Get details about units such as types, provider and tenure
#
def get_units_info_details(df):
    units_info_details = ['change_type', 'unit_type', 'unit_development_type', 'provider', 'tenure']

    for det in units_info_details:
        df['app_det_res_units_{}'.format(det)] = df['Units_info'].apply(lambda x: x[det] if det in x else "nan")

    # --------------- algorithm for 'unit types', 'providers' and 'development type' ---------------------
    # values are saved as a list of dictionary (1 key, 1 item)
    # 1. Create set with all keys from list of dictionary (set to avoid repeating types, we are looking for all unique types in df column)
    # 2. Create list from set
    # 3. Create new column in df with proper type name, assign proper value, if empty or none assing '0')
    # -----------------------------------------------------------------------------------------------------

    # Get all uniques 'units types' types and values
    # Create new columns in df_res_det DataFrame with values as number of specific units type
    unit_type_set = []

    #df['app_det_res_units_unit_type'] = df['app_det_res_units_unit_type'].apply(lambda x: ast.literal_eval(str(x)))
    for i in range(0, len(df['app_det_res_units_unit_type'])):
        for k, v in df['app_det_res_units_unit_type'][i].items():
            unit_type_set.append(k)
    unit_type_list = list(unit_type_set)

    # Create new columns with specified number of units types as a column
    for new_col in unit_type_list:
        df['Unit type: {}'.format(new_col)] = df['app_det_res_units_unit_type'].apply(
            lambda x: x[new_col] if new_col in x else 0)

    df.drop(columns=['app_det_res_units_unit_type'], inplace=True)


    # Get all uniques 'providers' types and values
    # Create new columns in df_res_det DataFrame with values as number of specific providers
    provider_set = set()

    for i in range(0, len(df['app_det_res_units_provider'])):
        for k, v in df['app_det_res_units_provider'][i].items():
            provider_set.add(k)
    provider_list = list(provider_set)

    # Create new columns with specified number of providers for each application
    for new_col in provider_list:
        df['Provider: {}'.format(new_col)] = df['app_det_res_units_provider'].apply(
            lambda x: x[new_col] if new_col in x else 0)
    df.drop(columns=['app_det_res_units_provider'], inplace=True)


    # Get all uniques 'development_type' types and values
    # Create new columns in df_res_det DataFrame with values as number of specific development_type
    development_type_set = set()

    for i in range(0, len(df['app_det_res_units_unit_development_type'])):
        for k, v in df['app_det_res_units_unit_development_type'][i].items():
            development_type_set.add(k)
    development_type_list = list(development_type_set)

    # Create new columns with specified number of providers for each application
    for new_col in development_type_list:
        df['Development type: {}'.format(new_col)] = df['app_det_res_units_unit_development_type'].apply(
            lambda x: x[new_col] if new_col in x else 0)

    df.drop(columns=['app_det_res_units_unit_development_type'], inplace=True)

    return df

def get_parking_details(df):
    df['Parking'] = df['source'].apply(lambda x: x['parking_details'])

                            
    parking_details_list= ['net_bluebadge', 'net_bus', 'net_carclub', 'net_cycle', 'net_lgv', 
                           'net_car', 'net_motorcycle', 'net_other', 'net_resi_offstreet', 
                           'no_existing_bluebadge', 'no_existing_bus', 'no_existing_car', 'no_existing_carclub', 
                           'no_existing_cycle', 'no_existing_lgv', 'no_existing_motorcycle', 'no_existing_other', 
                           'no_existing_resi_offstreet', 'no_proposed_bluebadge', 'no_proposed_bus', 
                           'no_proposed_car', 'no_proposed_carclub', 'no_proposed_cycle', 'no_proposed_lgv', 
                           'no_proposed_motorcycle', 'no_proposed_other', 'no_proposed_resi_offstreet']

    for details in parking_details_list:
        try:
            df['parking_{}'.format(details)] = df['Parking'].apply(lambda x: x[details] 
                                                               if (details in x) and (x[details] != 'nan')  else 0)
        except TypeError:
            print()
            df['parking_{}'.format(details)] = 'nan'


    return df
# 
#
#
#
#

def cleaning_data(df):
    #df.drop(columns=['Unnamed: 0'], inplace=True)

    # Create new DF with _source and convert to dictionary
    new_df = pd.DataFrame(columns=['source'])


    #new_df['source'] = np.where(df['_source'], ast.literal_eval(str(df['_source'].values)))
    #print(type(df['_source'][0]))
    #new_df['source'] = df['_source'].apply(lambda x: ast.literal_eval(str(x)))

    new_df['source'] = df['_source']
    new_df['Units_info'] = new_df['source'].apply(lambda x: get_dictionary_residential_units_data(x))
    
    new_df['Site_area'] = new_df['source'].apply(lambda x: x['application_details']['site_area'] 
                                                 if ('site_area' in x['application_details']) else 'nan')
    
    new_df['NO storeys'] = new_df['source'].apply(lambda x: x['application_details']['building_details'][0]['no_storeys'] 
                                                    if 'building_details' in x['application_details'] and x['application_details']['building_details'] != None and len(x['application_details']['building_details']) > 0 else 'NAN')

    

    new_df = get_floorspace_details(new_df)

    new_df = get_units_info_details(new_df)
    new_df = get_more_residential_units_data(new_df)
    new_df = get_parking_details(new_df)

    new_df['Status'] = new_df['source'].apply(lambda x: x['status'])
    
    # Get data directly from _source
    #
    new_df['centroid'] = new_df['source'].apply(lambda x: x['centroid'])
    new_df['polygon'] = new_df['source'].apply(lambda x: x['polygon'])
    new_df['ward'] = new_df['source'].apply(lambda x: x['ward'])
    new_df['decision_agency'] = new_df['source'].apply(lambda x: x['decision_agency'])
    new_df['site_name'] = new_df['source'].apply(lambda x: x['site_name'])
    new_df['lpa_app_no'] = new_df['source'].apply(lambda x: x['lpa_app_no'])
    new_df['decision_date'] = new_df['source'].apply(lambda x: x['decision_date'])
    new_df['PostCode'] = new_df['source'].apply(lambda x: x['postcode'])
    

    new_df['app_det_left_affordable_percentage'] = new_df['app_det_left_affordable_percentage'].apply(
        lambda x: str(round(float(x), 2))+" %")

    new_df['ID'] = df['_id']
    new_df['Borough'] = new_df['ID'].apply(lambda x: str(x).split('-')[0])
    new_df['App_ID'] = new_df['ID'].apply(lambda x: str(x).split('-')[1])
    new_df.drop(columns=['ID'], inplace=True)

    new_df['app_det_left_dwelling_density'] = new_df['app_det_left_dwelling_density'].apply(lambda x: str(round(float(x), 2)))

    new_df.rename(columns={'app_det_left_total_no_proposed_residential_units': 'NO proposed residential units',
                               'app_det_left_affordable_percentage': 'Affordable Percentage'}, inplace=True)
    #print(new_df.columns)

    return new_df