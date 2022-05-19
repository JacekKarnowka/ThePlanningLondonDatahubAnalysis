"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import django
import pandas as pd
from pandas.util.testing import assert_frame_equal
from django.test import TestCase

from .views import get_status_color
from .views import GIA_plot_data

# TODO: Configure your database in settings.py and sync before running tests.


class SimpleTest(TestCase):
    """Tests for the application views."""

    # Django requires an explicit setup() when running tests in PTVS
    @classmethod
    def setUpClass(cls):
        super(SimpleTest, cls).setUpClass()
        django.setup()

    def test_views_get_status_color(self):
        df_input = pd.DataFrame(
            {
                "Status": [
                    "Allowed",
                    "Approved",
                    "Commenced",
                    "Completed",
                    "Lapsed",
                    "Submited",
                ]
            }
        )
        df_ouput = pd.DataFrame(
            {
                "Status": [
                    "Allowed",
                    "Approved",
                    "Commenced",
                    "Completed",
                    "Lapsed",
                    "Submited",
                ],
                "color": [
                    "rgb(124,98,78)",
                    "rgb(226,207,190)",
                    "rgb(109,148,198)",
                    "rgb(3,100,110)",
                    "rgb(241,234,226)",
                    "rgb(217,50,34)",
                ],
            }
        )
        assert_frame_equal(get_status_color(df_input), df_ouput)

    # Test GIA_Plot_data
    def test_GIA_plot_data_numbers(self):
        df_input = pd.DataFrame(
            {
                "floorspace_detail_gia_gained": [1],
                "floorspace_detail_gia_lost": [1],
                "floorspace_detail_gia_existing": [1],
                "App_ID": ["test_1"],
            }
        )

        df_output = [1, 2], [1.0, 1.0]

        self.assertEqual(GIA_plot_data(df_input, "test_1"), df_output)

    def test_GIA_plot_data_for_strings(self):
        df_input = pd.DataFrame(
            {
                "floorspace_detail_gia_gained": ["test"],
                "floorspace_detail_gia_lost": [1],
                "floorspace_detail_gia_existing": [1],
                "App_ID": ["test_1"],
            }
        )

        with self.assertRaises(ValueError):
            GIA_plot_data(df_input, "test_1")

    def test_GIA_plot_data_for_wrong_id(self):
        df_input = pd.DataFrame(
            {
                "floorspace_detail_gia_gained": [1],
                "floorspace_detail_gia_lost": [1],
                "floorspace_detail_gia_existing": [1],
                "App_ID": ["test_1"],
            }
        )

        with self.assertRaises(TypeError):
            GIA_plot_data(df_input, "asd")



    
