from __future__ import unicode_literals
from django.db.models.aggregates import Max

from django.db import models
# Create your models here.

class created_projects(models.Model):
    def __str__(self):
        return self.App_ID
    pass
columns = ['source', 
            'Units_info', 
            'NO_storeys',
            'app_det_res_units_change_type', 
            'app_det_res_units_tenure', 
            'Status',
            'app_det_left_total_no_proposed_bedrooms',
            'NO_proposed_residential_units', 
            'london_living_rent',
            'london_affordable_rent', 
            'affordable_rent', 
            'affordable_units',
            'market_for_sale', 
            'sociat_rent_units', 
            'intermediate',
            'market_rent_charged_london_rents', 
            'market_for_rent',
            'discount_market_sale', 
            'self_build_and_custom_build', 
            'starter_homes',
            'discount_market_rent', 
            'Existing_residential_affordable_units',
            'habitable_rooms_density', 
            'Existing_residential_affordable_rent',
            'Existing_residential_London_shared_ownership',
            'Existing_residential_London_affordable_rent', 
            'Dwelling_density',
            'Site_Ares', 
            'Affordable_Percentage', 
            'Existing_residential_units',
            'centroid', 
            'polygon', 
            'ward', 
            'decision_agency', 
            'site_name',
            'lpa_app_no', 
            'decision_date', 
            'PostCode', 
            'Unit_type_Studio_Bedsit',
            'Unit_type_Flat_Apartment_Maisonette', 
            'Provider_Local_Authority',
            'Provider_Private_rented_sector', 
            'Provider_Private',
            'Provider_Housing_Association', 
            'Development_type_New_Build',
            'Development_type_Change_of_Use', 
            'Borough', 
            'App_ID',
            'Polygon_coords', 
            'latitude', 
            'longitude', 
            'color',
            'floorspace_detail_actual_completion_date',
            'floorspace_detail_gia_existing', 
            'floorspace_detail_gia_gained',
            'floorspace_detail_gia_lost',
            'floorspace_detail_superseded_by_lpa_app_no',
            'floorspace_detail_superseded_date', 
            'floorspace_detail_use_class',
            'Site_area',

### Parking details
            'parking_net_bluebadge', 
            'parking_net_bus', 
            'parking_net_carclub', 
            'parking_net_cycle', 
            'parking_net_lgv', 
            'parking_net_car', 
            'parking_net_motorcycle', 
            'parking_net_other', 
            'parking_net_resi_offstreet', 
            'parking_no_existing_bluebadge', 
            'parking_no_existing_bus', 
            'parking_no_existing_car', 
            'parking_no_existing_carclub', 
            'parking_no_existing_cycle', 
            'parking_no_existing_lgv', 
            'parking_no_existing_motorcycle', 
            'parking_no_existing_other', 
            'parking_no_existing_resi_offstreet', 
            'parking_no_proposed_bluebadge', 
            'parking_no_proposed_bus', 
            'parking_no_proposed_car', 
            'parking_no_proposed_carclub', 
            'parking_no_proposed_cycle', 
            'parking_no_proposed_lgv', 
            'parking_no_proposed_motorcycle', 
            'parking_no_proposed_other', 
            'parking_no_proposed_resi_offstreet'
            ]

for name in columns:
    if name == 'Status':
        created_projects.add_to_class(name, models.TextField(default = "MY_PROJECT", null = True))
    else:
        created_projects.add_to_class(name, models.TextField(default = "0", null = True))
    