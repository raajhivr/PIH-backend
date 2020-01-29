from django.http import HttpResponse
from . import configuration
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from webapp.models import ProductInscope
from django.db.models import Q
import json
# product = ProductInscope.objects.all()
product_list=[]
product_column = ["nam_prod","bdt","cas_no","spec_id","material_no"]
last=''
@csrf_exempt
def index(requests):
    global last
    if requests.method=="POST": 
        items=[]
        data = requests.body.decode('utf-8')
        data1=json.loads(data)
        search = data1.get("SearchData",None)
        if last != search:
            product_list=[]
            product = ProductInscope.objects.filter(Q(nam_prod__startswith=search.lower())|
                                                Q(bdt__startswith=search.lower()))
            for row in product:
                namprod={"name":row.nam_prod,"type":"Namprod"}
                product_list.append(namprod)
                bdt={"name":row.bdt,"type":"BDT"}
                product_list.append(bdt)
        # for row in cursor:
        #     val=row[0]
        #     if data.get('search_key').lower() in str(val).lower():
        #         rdata={"name":str(val),
        #                 "type":"Namprod"}
        #         items.append(rdata)
        # parameter = config.DATABASES
        last=search
        res=sorted(product_list, key=lambda k: k['type']) 
        return JsonResponse(res,content_type="application/json",safe=False)
        # return JsonResponse(product_list)
    elif requests.method=="GET":
        print("mmmm",requests.body)
        return HttpResponse("hello world")
