from django.shortcuts import render
from MainApp import urls

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import View

from django_pandas.io import read_frame

from .models import created_projects
from collections import OrderedDict, defaultdict
from django.forms.models import model_to_dict
 
import pandas as pd

# Import app files
from . import Save_to_Database

def delete_models(names):

    for name in names:
                created_projects.objects.filter(App_ID = name).delete()

class manage_projects(View):
            
    def get(self, request):

        project_list = list(created_projects.objects.values_list('App_ID', flat = True))
        
        return render(request, 'front/manage_projects.html', {'project_list': project_list})

    def post(self, request):

        # Add project form POST response 
        # Get form data and save it to created_projects database
        if 'add_project' in request.POST:

            form_data = dict(request.POST.items())

            Save_to_Database.save_to_database(form_data)

            project_list = list(created_projects.objects.values_list('App_ID', flat = True))

            return render(request, 'front/manage_projects.html', {'project_list': project_list})
        
        # Delete project form POST response
        # Get all choosen project and dalate it from database (by App_ID)
        elif 'delete_project' in request.POST:

            project_list_to_delete = request.POST.getlist('choose_project')

            delete_models(project_list_to_delete)

            project_list = list(created_projects.objects.values_list('App_ID', flat = True))

            return render(request, 'front/manage_projects.html', {'project_list': project_list})
