### ------------------------------------------------------------ ###
# Get The Planning London Datahub data, based on choosen settings

import pandas as pd
import requests
import copy


def get_data(
    site_area_filter, units_filter, date_from, date_to, status="*", lpa_name="*"
):
    site_area_range = site_area_filter.split(",")
    units_filter_range = units_filter.split(",")

    date_from_m_d_y = date_from.split("/")
    date_to_m_d_y = date_to.split("/")

    date_from_m_d_y[0], date_from_m_d_y[1] = date_from_m_d_y[1], date_from_m_d_y[0]
    date_to_m_d_y[0], date_to_m_d_y[1] = date_to_m_d_y[1], date_to_m_d_y[0]

    date_from_range = "/".join(date_from_m_d_y)
    date_to_range = "/".join(date_to_m_d_y)

    # print("site area: {} + type {}".format(site_area_range, type(site_area_range)))
    # print("units filter: {} + type {}".format(units_filter_range, type(units_filter_range)))
    # print("date_from: {} + type {}".format(date_from_range, type(date_from_range)))
    # print("date_to: {} + type {}".format(date_to_range, type(date_to_range)))

    url = "https://planningdata.london.gov.uk/api-guest/applications/_search?"
    url += "size=10000"
    url += "&sort=_doc"

    ### FEATURES
    source_ = []
    source_ = source_ + [
        "lpa_name",
        "ward",
        "street_name",
        "postcode",
        "polygon",
        "centroid",
    ]
    source_ = source_ + ["lpa_app_no", "site_name"]

    source_ = source_ + [
        "appeal_decision",
        "appeal_status",
        "application_type",
        "application_type_full",
        "decision",
        "decision_agency",
        "decision_process",
        "development_type",
        "status",
    ]

    source_ = source_ + ["valid_date", "decision_date"]

    source_ = source_ + ["application_details"]

    source_ = source_ + ["parking_details"]

    print(source_)
    url += "&_source={}".format(",".join(source_))

    ### FILTERS
    lpa_name_filter = "lpa_name:{}".format(",".join(lpa_name))
    url += "&q={}".format(lpa_name_filter)

    try:
        sitearea_filter = (
            "application_details.residential_details.site_area:[{} TO {}]".format(
                site_area_range[0], site_area_range[1]
            )
        )
        url += " AND {}".format(sitearea_filter)
    except IndexError:
        sitearea_filter = "*"

    try:
        units_filter = "application_details.residential_details.total_no_proposed_residential_units:[{} TO {}]".format(
            units_filter_range[0], units_filter_range[1]
        )
        url += " AND {}".format(units_filter)
    except IndexError:
        units_filter = "*"

    decision_date_filter = "decision_date:[{} TO {}]".format(
        date_from_range, date_to_range
    )
    url += " AND {}".format(decision_date_filter)

    if len(status) == 0 or status[0] == "All options":
        pass
    else:
        status_filter = "status:{}".format(",".join(status))
        url += " AND {}".format(status_filter)

    print(url)

    ### REQUEST
    headers = {"X-API-AllowRequest": "be2rmRnt&"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    else:
        print("!!! Success !!!")
    jsonData = response.json()

    json_data_copy = copy.deepcopy(jsonData["hits"]["hits"])

    df = pd.DataFrame.from_dict(json_data_copy)

    # df.drop(columns = ['_index', '_type', '_ignored', '_score'], inplace= True)

    return df
