from django.http import HttpResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from webapp.models import ProductInscope
from django.db.models import Q
import json
from django_pandas.io import read_frame
import re

product_column = ["NAM PROD","BDT","CAS NUMBER","SPEC-ID","MATERIAL NUMBER"]
df_product = read_frame(ProductInscope.objects.all())
df_product.columns=product_column
last=''

@csrf_exempt
def all_products(requests):
    try:
        global last
        if requests.method=="POST":
            try: 
                data=''
                data_json=''
                search=''
                data = requests.body.decode('utf-8')
                data_json=json.loads(data)
                search = data_json.get("SearchData",None).strip()
                print("all_products",data_json)
                if last != search:
                    all_product_list=[]
                    rex=re.compile(r"(^{})".format(search),re.I)
                    for column in product_column:
                        edit_df=df_product[df_product[column].str.contains(rex)]
                        column_value=edit_df[column].unique()
                        for item in column_value:
                            out_dict={"name":item,"type":column}
                            all_product_list.append(out_dict)                       
                last=search
                print("len of all_product_list",len(all_product_list))
                print(all_product_list[0:5])
                res=sorted(all_product_list, key=lambda k: k['type']) 
                return JsonResponse(res,content_type="application/json",safe=False)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)


@csrf_exempt
def selected_products(requests):
    try:
        if requests.method=="POST":
            try:
                searched_product_list=[]
                data=''
                data_json=''
                column_add=[]
                all_product_column=["NAM PROD","BDT","CAS NUMBER","SPEC-ID","MATERIAL NUMBER"]
                data = requests.body.decode('utf-8')
                data_json=json.loads(data)
                print("selectedproducts",data_json)
                filter_df=df_product.copy()            
                for item in data_json:
                    search_value = item.get("name")
                    search_column = item.get("type")
                    column_add.append(search_column)
                    filter_df=filter_df[filter_df[search_column]==search_value]
                for remove in column_add:
                    if remove in all_product_column:
                        all_product_column.remove(remove) 
                for column in all_product_column:
                    value_list=filter_df[column].unique()
                    for item in value_list:
                        out_dict={"name":item,"type":column}
                        searched_product_list.append(out_dict)
                print("len of selectedproducts",len(searched_product_list))
                print(searched_product_list)
                return JsonResponse(searched_product_list,content_type="application/json",safe=False)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

@csrf_exempt
def selected_categories(requests):
    try:
        if requests.method=="POST":
            try: 
                category_product_list=[]
                search_category=''
                data=''
                data_json=''
                data = requests.body.decode('utf-8')
                data_json=json.loads(data)
                print("selected_categories",data_json)
                search_category = data_json.get("SelectedKey",None).strip()
                if search_category in product_column:
                    column_value=df_product[search_category].unique()
                    for item in column_value:
                        out_dict={"name":item,"type":search_category}
                        category_product_list.append(out_dict)  
                print("len of categorydproducts",len(category_product_list))
                print("categorydproducts",category_product_list[0:5])          
                return JsonResponse(category_product_list,content_type="application/json",safe=False)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

