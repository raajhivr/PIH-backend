from django.http import HttpResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from webapp.models import ProductInformation
from django.db.models import Q
import json
from django_pandas.io import read_frame
import re
from . import views
import pandas as pd
df_product,df_product_combine,product_column = views.inscope_product_details()

@csrf_exempt
def basic_properties(requests):
    if requests.method=="POST":
        try:
            basic_details=[]
            product_level_details=[]
            product_level_dict={}
            material_level_details=[]
            material_level_dict = {}
            cas_level_details=[]
            cas_level_dict={}
            product_level_flag=''
            material_level_flag=''
            cas_level_flag=''
            material_id=''
            spec_id_search=''
            material_number=''
            material_desc=''
            product_validate = ["NAM PROD","BDT"]
            basic_df = df_product_combine.copy()
            all_product_column=["NAM PROD","BDT","CAS NUMBER","SPEC-ID","MATERIAL NUMBER"]
            data = requests.body.decode('utf-8')
            data_json=json.loads(data)
            print("basic properties",data_json)
            for item in data_json:
                search_value = item.get("name")
                search_column = item.get("type")
                if search_column in product_validate:
                    product_level_flag='s'
                if search_column in ["BDT","MATERIAL NUMBER"]:
                    material_level_flag='s'
                if search_column=="CAS NUMBER":
                    cas_level_flag='s'
                if search_column=="SPEC-ID":
                    spec_id_search = search_value.strip()
                basic_df=basic_df[basic_df[search_column]==search_value]
            if product_level_flag=='s':
                spec_df = basic_df.copy()
                spec_df = spec_df.drop(columns=["CAS NUMBER","BDT"])
                spec_df_mat=spec_df.copy()
                spec_df_mat.drop_duplicates(inplace=True)
                spec_df = spec_df.drop(columns=["MATERIAL NUMBER"])
                spec_df.drop_duplicates(inplace=True)
                spec_df=spec_df.reset_index(drop=True)
                for item in range(len(spec_df)):
                    temp_df= spec_df_mat[spec_df_mat["SPEC-ID"]==spec_df.loc[item,"SPEC-ID"]]
                    product_level_dict["productName"]=spec_df.loc[item,"NAM PROD"]
                    product_level_dict["spec_id"]=spec_df.loc[item,"SPEC-ID"]
                    product_level_dict["ProdIdentifiers"]=spec_df.loc[item,"NAM PROD"]
                    product_level_dict["Synonyms"]=''
                    product_level_dict["No_Active_Materials"]=len(temp_df["MATERIAL NUMBER"].unique())
                    product_level_dict["Sales_Volume"]=''
                    product_level_dict["GHS_Information"]=''
                    product_level_dict["tab_modal"]='compositionModal'
                    product_level_details.append(product_level_dict)
                    product_level_dict={}

            if material_level_flag=='s':
                spec_table=[]
                spec_mat_dict={}
                material_df=df_product_combine.copy()
                material_df.drop(columns=["CAS NUMBER"])
                material_df.drop_duplicates(inplace=True)
                material_df=material_df.reset_index(drop=True)
                outer_mat_df = basic_df[["MATERIAL NUMBER","BDT"]]
                outer_mat_df.drop_duplicates(inplace=True)
                outer_mat_df=outer_mat_df.reset_index(drop=True)
                print("material level",outer_mat_df)
                for i in range(len(outer_mat_df)):
                    material_id = outer_mat_df.loc[i,"MATERIAL NUMBER"].strip()
                    print(material_id)
                    bdt = outer_mat_df.loc[i,"BDT"].strip()
                    material_id_split = material_id.split()
                    material_number = material_id_split[0]
                    material_desc = material_id.replace(material_number,'')
                    material_level_dict["Material_id"] = material_id
                    material_level_dict["Material_Number"]=material_number
                    material_level_dict["Description"]=material_desc
                    material_level_dict["BDT"]=bdt
                    material_level_dict["Sales_Vol"]=''
                    spec_mat_df=material_df[material_df["MATERIAL NUMBER"]==material_id]
                    spec_mat_df = spec_mat_df[["SPEC-ID","NAM PROD"]]
                    spec_mat_df.drop_duplicates(inplace=True)
                    spec_mat_df=spec_mat_df.reset_index(drop=True)
                    print("ffff",spec_mat_df)
                    for item in range(len(spec_mat_df)):
                        spec_mat_dict["productName"]=spec_mat_df.loc[item,"NAM PROD"]
                        spec_mat_dict["spec_id"]=spec_mat_df.loc[item,"SPEC-ID"]
                        spec_mat_dict["ProdIdentifiers"]=spec_mat_df.loc[item,"NAM PROD"]
                        spec_mat_dict["Synonyms"]=''
                        spec_mat_dict["No_Active_Materials"]=''
                        spec_mat_dict["Sales_Volume"]=''
                        spec_mat_dict["GHS_Information"]=''
                        spec_mat_dict["tab_modal"]=''
                        spec_table.append(spec_mat_dict)
                        spec_mat_dict={}
                        print(spec_mat_dict)
                    material_level_dict["spec_table"]=spec_table
                    spec_mat_dict={}
                    spec_table=[]
                    material_level_details.append(material_level_dict)
                    material_level_dict={}
                    spec_mat_df=pd.DataFrame()
                
            if cas_level_flag == "s":
                cas_level_details=[]

            basic_details.append({"productLevel":product_level_details})
            basic_details.append({"MaterialLevel":material_level_details})
            basic_details.append({"CasLevel":cas_level_details})       
            return JsonResponse(basic_details,content_type="application/json",safe=False)       
        except Exception as e:
            print(e)
            return JsonResponse([],content_type="application/json",safe=False)
            
def product_attributes(requests):
    pass

