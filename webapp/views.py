from django.http import HttpResponse
from . import configuration
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from webapp.models import ProductInscope
from django.db.models import Q
# product = ProductInscope.objects.all()
product_list=[]
product_column = ["nam_prod","bdt","cas_no","spec_id","material_no"]
last=''
@csrf_exempt
def index(requests):
    global last
    if requests.method=="POST":           
        items=[]
        data = requests.POST
        if last != data.get('search_key',None):
            product = ProductInscope.objects.filter(Q(nam_prod__contains=data.get('search_key',None).lower())|
                                                Q(bdt__contains=data.get('search_key',None).lower())|
                                                Q(cas_no__contains=data.get('search_key',None).lower())|
                                                Q(spec_id__contains=data.get('search_key',None).lower())|
                                                Q(material_no__contains=data.get('search_key',None).lower()))
            for row in product:
                namprod={"name":row.nam_prod,"type":"Namprod"}
                product_list.append(namprod)
                bdt={"name":row.bdt,"type":"BDT"}
                product_list.append(bdt)
                casno = {"name":row.cas_no,"type":"CAS"}
                product_list.append(casno)
                specid = {"name":row.spec_id,"type":"specid"}
                product_list.append(specid)
                material = {"name":row.material_no,"type":"material"}
                product_list.append(material)
        # for row in cursor:
        #     val=row[0]
        #     if data.get('search_key').lower() in str(val).lower():
        #         rdata={"name":str(val),
        #                 "type":"Namprod"}
        #         items.append(rdata)
        # parameter = config.DATABASES
        last=data.get('search_key',None)
        res=sorted(product_list, key=lambda k: k['type']) 
        return JsonResponse(res,safe=False)
        # return JsonResponse(product_list)
    elif requests.method=="GET":
        print("mmmm",requests.body)
        return HttpResponse("hello world")
