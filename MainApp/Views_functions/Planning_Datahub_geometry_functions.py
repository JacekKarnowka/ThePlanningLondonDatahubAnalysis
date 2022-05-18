import pandas as pd
import ast
from shapely.geometry import Polygon
from pyproj import Transformer

### ------------------------------------------------------------ ###
# Transform coordinates function
# Transform crs epsg from 27700 to 4326
# return polygon data
#
def transform_coordinates_function(cords_list):
    good_list = []

    if cords_list:
        if cords_list["geometries"]:

            poly = cords_list["geometries"][0]["coordinates"][0]

            for i in poly:
                transformer = Transformer.from_crs("epsg:27700", "epsg:4326")
                tmp_poly_lat, tmp_poly_long = transformer.transform(i[0], i[1])
                good_list.append([tmp_poly_long, tmp_poly_lat])

            return Polygon(good_list)
    else:
        return 0


def transform_coordinates(df_data):

    df_test = df_data.copy()
    df_test = df_test[df_test["polygon"] != "0"]
    df_test = df_test[df_test["polygon"].notna()]

    # df_test['polygon'] = df_test['polygon'].apply(lambda x: ast.literal_eval(str(x)))
    df_test["Polygon_coords"] = df_test.apply(
        lambda row: transform_coordinates_function(row["polygon"]), axis=1
    )

    return df_test


def get_centroid_data(df):

    # print(type(df['centroid'][0]))
    # df['centroid'] = df['centroid'].apply(lambda x: ast.literal_eval(str(x)))
    df["latitude"] = df["centroid"].apply(lambda x: float(x["lat"]))
    df["longitude"] = df["centroid"].apply(lambda x: float(x["lon"]))

    return df
