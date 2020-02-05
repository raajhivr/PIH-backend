from django.http import HttpResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from webapp.models import ProductInscope
from django.db.models import Q
import json
from django_pandas.io import read_frame
import re

@csrf_exempt
def basic_properties(requests):
    pass

def product_attributes(requests):
    pass

