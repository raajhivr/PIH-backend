from django.http import HttpResponse
from . import configuration
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from webapp.models import ProductInscope
from django.db.models import Q
import json
from django_pandas.io import read_frame
import re

product_column = ["nam_prod","bdt","cas_no","spec_id","material_no"]
df_product = read_frame(ProductInscope.objects.all(),fieldnames=product_column)
product_list=[]
last=''

@csrf_exempt
def index(requests):
    global last
    global product_list
    if requests.method=="POST": 
        data = requests.body.decode('utf-8')
        data_json=json.loads(data)
        search = data_json.get("SearchData",None).strip()
        if last != search:
            product_list=[]
            rex=re.compile(r"(^{})".format(search),re.I)
            for column in product_column:
                edit_df=df_product[df_product[column].str.contains(rex)]
                column_value=edit_df[column].unique()
                for item in column_value:
                    out_dict={"name":item,"type":column}
                    product_list.append(out_dict)
                
        last=search
        res=sorted(product_list, key=lambda k: k['type']) 
        return JsonResponse(res,content_type="application/json",safe=False)
        # return JsonResponse(product_list)
    elif requests.method=="GET":
        print("mmmm",requests.body)
        return HttpResponse("get function called")
