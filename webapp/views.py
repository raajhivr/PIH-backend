from django.http import HttpResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from webapp.models import ProductInscope
from django.db.models import Q
import json
from django_pandas.io import read_frame
import re
import pandas as pd

product_column = ["SPEC-ID","NAM PROD","MATERIAL NUMBER","DESCRIPTION","BDT","CAS NUMBER"]
df_product = pd.read_excel(r"C:/Coding/momentive-backend/inscope-mat-list.xlsx")
# df_product = read_frame(ProductInscope.objects.all())

df_product.drop_duplicates(inplace=True)
df_product.columns=product_column
df_product_combine = df_product.copy()
last=''
df_product_combine["MATERIAL NUMBER"] = df_product_combine["MATERIAL NUMBER"].astype('str')+" "+df_product_combine["DESCRIPTION"]
df_product_combine.drop(columns=["DESCRIPTION"],inplace=True)
product_column_combine = ["NAM PROD","BDT","CAS NUMBER","SPEC-ID","MATERIAL NUMBER"]

def inscope_product_details():
    return df_product,df_product_combine,product_column,product_column_combine

@csrf_exempt
def all_products(requests):
    try:
        if requests.method=="POST":
            try: 
                all_products_product_column=["SPEC-ID","NAM PROD","MATERIAL NUMBER","BDT","CAS NUMBER"]
                selected_categories=["BDT","NAM","CAS","MAT","SPEC"]
                matched_categories = [["BDT","BDT"],["NAM","NAM PROD"],["MAT","MATERIAL NUMBER"],["CAS","CAS NUMBER"],["SPEC","SPEC-ID"]]
                data=''
                data_json=''
                search=''
                data = requests.body.decode('utf-8')
                data_json=json.loads(data)
                search = data_json.get("SearchData",None).strip()
                res=''
                if len(search) >= 3 and search.upper() in selected_categories:
                    print("typecat",search)
                    all_product_list=[]
                    for item,match in matched_categories:
                        if search.upper()==item:
                            column_value=df_product_combine[match].unique()
                            for value in column_value:
                                out_dict={"name":str(value).strip(),"type":match}
                                all_product_list.append(out_dict)
                                res = all_product_list
                            break
                    print("new cat",res)
                else:
                    print("all_products",data_json)
                    all_product_list=[]
                    rex=re.compile(r"(^{})".format(search),re.I)
                    for column in all_products_product_column:
                        edit_df=df_product_combine[df_product_combine[column].astype(str).str.contains(rex,na=False)]
                        column_value=edit_df[column].unique()
                        for item in column_value:
                            out_dict={"name":str(item).strip(),"type":column}
                            all_product_list.append(out_dict)  
                    print("len of all_product_list",len(all_product_list))
                    print(all_product_list[0:5])
                    res=sorted(all_product_list, key=lambda k: k['type'])
                return JsonResponse(res,content_type="application/json",safe=False)
            except Exception as e:
                print(e)
                return JsonResponse([],content_type="application/json",safe=False)               
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
                all_product_column=["SPEC-ID","NAM PROD","MATERIAL NUMBER","BDT","CAS NUMBER"]
                data = requests.body.decode('utf-8')
                data_json=json.loads(data)
                print("selectedproducts",data_json)
                filter_df=df_product_combine.copy()            
                for item in data_json:
                    search_value = item.get("name")
                    search_column = item.get("type")
                    column_add.append(search_column)
                    if search_value.isdigit():
                        search_value=int(search_value)
                    filter_df=filter_df[filter_df[search_column]==search_value]
                for remove in column_add:
                    if remove in all_product_column:
                        all_product_column.remove(remove) 
                for column in all_product_column:
                    value_list=filter_df[column].unique()
                    for item in value_list:
                        out_dict={"name":str(item).strip(),"type":column}
                        searched_product_list.append(out_dict)
                print("len of selectedproducts",len(searched_product_list))
                print(searched_product_list)
                return JsonResponse(searched_product_list,content_type="application/json",safe=False)
            except Exception as e:
                return JsonResponse([],content_type="application/json",safe=False)
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
                    column_value=df_product_combine[search_category].unique()
                    for item in column_value:
                        out_dict={"name":str(item).strip(),"type":search_category}
                        category_product_list.append(out_dict)  
                print("len of categorydproducts",len(category_product_list))
                print("categorydproducts",category_product_list[0:5])          
                return JsonResponse(category_product_list,content_type="application/json",safe=False)
            except Exception as e:
                return JsonResponse([],content_type="application/json",safe=False)
                print(e)
    except Exception as e:
        print(e)

