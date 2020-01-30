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
nam_row=[]
bdt_row=[]
@csrf_exempt
def index(requests):
    global last
    global product_list
    if requests.method=="POST": 
        nam_row=[]
        bdt_row=[]
        items=[]
        data = requests.body.decode('utf-8')
        data1=json.loads(data)
        search = data1.get("SearchData",None).strip()
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
