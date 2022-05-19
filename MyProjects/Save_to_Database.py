# from The_Planning_London_Datahub_web import Create_App
from .models import created_projects


def save_to_database(dictionary):
    b = created_projects(  # source,
        # Units_info,
        # source = dictionary[source],
        App_ID=dictionary["App_ID"],
        Borough=dictionary["Borough"],
        PostCode=dictionary["PostCode"],
        latitude=dictionary["latitude"],
        longitude=dictionary["longitude"],
        NO_storeys=dictionary["NO_storeys"],
        Dwelling_density=dictionary["Dwelling_density"],
        NO_proposed_residential_units=dictionary["NO_proposed_residential_units"],
        # Main information about building
        Site_area=dictionary["Site_area"],
        # Site_Ares = dictionary['App_ID'],
        # Affordable percengage and unts
        Affordable_Percentage=dictionary["Affordable_Percentage"],
        market_for_sale=dictionary["market_for_sale"],
        market_for_rent=dictionary["market_for_rent"],
        affordable_units=dictionary["affordable_units"],
        starter_homes=dictionary["starter_homes"],
        # Affordable units details:
        london_living_rent=dictionary["london_living_rent"],
        london_affordable_rent=dictionary["london_affordable_rent"],
        sociat_rent_units=dictionary["sociat_rent_units"],
        intermediate=dictionary["intermediate"],
        market_rent_charged_london_rents=dictionary["market_rent_charged_london_rents"],
        self_build_and_custom_build=dictionary["self_build_and_custom_build"],
        discount_market_rent=dictionary["discount_market_rent"],
        discount_market_sale=dictionary["discount_market_sale"],
        # Units types
        Unit_type_Studio_Bedsit=dictionary["Unit_type_Studio_Bedsit"],
        Unit_type_Flat_Apartment_Maisonette=dictionary[
            "Unit_type_Flat_Apartment_Maisonette"
        ],
        Provider_Local_Authority=dictionary["Provider_Local_Authority"],
        Provider_Private_rented_sector=dictionary["Provider_Private_rented_sector"],
        Provider_Private=dictionary["Provider_Private"],
        Provider_Housing_Association=dictionary["Provider_Housing_Association"],
        Development_type_New_Build=dictionary["Development_type_New_Build"],
        Development_type_Change_of_Use=dictionary["Development_type_Change_of_Use"],
        # Units types
        floorspace_detail_actual_completion_date=dictionary[
            "floorspace_detail_actual_completion_date"
        ],
        floorspace_detail_gia_existing=dictionary["floorspace_detail_gia_existing"],
        floorspace_detail_gia_gained=dictionary["floorspace_detail_gia_gained"],
        floorspace_detail_gia_lost=dictionary["floorspace_detail_gia_lost"],
        floorspace_detail_superseded_by_lpa_app_no=dictionary[
            "floorspace_detail_superseded_by_lpa_app_no"
        ],
        floorspace_detail_superseded_date=dictionary[
            "floorspace_detail_superseded_date"
        ],
        floorspace_detail_use_class=dictionary["floorspace_detail_use_class"],
        ##app_det_res_units_change_type,
        ##app_det_res_units_tenure,
        ##Status,
        ##app_det_left_total_no_proposed_bedrooms,
        ##NO_proposed_residential_units,
        ##affordable_rent,
        ##Existing_residential_affordable_units,
        ##habitable_rooms_density,
        ##Existing_residential_affordable_rent,
        ##Existing_residential_London_shared_ownership,
        ##Existing_residential_London_affordable_rent,
        ##Existing_residential_units,
        ##centroid,
        ##polygon,
        ##ward,
        ##decision_agency,
        ##site_name,
        ##lpa_app_no,
        ##Polygon_coords,
        ##color,
        ##parking_net_bluebadge,
        ##parking_net_bus,
        ##parking_net_carclub,
        ##parking_net_cycle,
        ##parking_net_lgv,
        ##parking_net_car,
        ##parking_net_motorcycle,
        ##parking_net_other,
        ##parking_net_resi_offstreet,
        ##parking_no_existing_bluebadge,
        ##parking_no_existing_bus,
        ##parking_no_existing_car,
        ##parking_no_existing_carclub,
        ##parking_no_existing_cycle,
        ##parking_no_existing_lgv,
        ##parking_no_existing_motorcycle,
        ##parking_no_existing_other,
        ##parking_no_existing_resi_offstreet,
        ##parking_no_proposed_bluebadge,
        ##parking_no_proposed_bus,
        ##parking_no_proposed_car,
        ##parking_no_proposed_carclub,
        ##parking_no_proposed_cycle,
        ##parking_no_proposed_lgv,
        ##parking_no_proposed_motorcycle,
        ##parking_no_proposed_other,
        ##parking_no_proposed_resi_offstreet
    )
    b.save()
