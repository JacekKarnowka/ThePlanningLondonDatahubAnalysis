from django.urls import re_path, include
from MainApp.views import home, application_details, search_for_application
from . import views

from MyProjects.views import manage_projects

#from MainApp.views import Table

urlpatterns = [
    re_path(r'^$', home.as_view(), name= 'home'),
    re_path(r'^application/(?P<word>.*)/$', application_details.as_view(), name= 'aplication_details'),
    re_path(r'^search_for_application/$', search_for_application.as_view(), name ="search_for_application"),
    re_path(r'^manage_projects/$', manage_projects.as_view(), name = "manage_projects"),
    re_path(r'^django_plotly_dash/', include('django_plotly_dash.urls'))
]
