from django.http import HttpResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from webapp.models import ProductInformation
from django.db.models import Q
import json
from django_pandas.io import read_frame
import re
import pandas as pd

product_column = ["TYPE","TEXT1","TEXT2","TEXT3","TEXT4","SUBCT"]
# df_product = pd.read_excel(r"C:\Coding\momentive-backend\product_info_V2.xlsx",sheet_name="Sheet1")
df_product = read_frame(ProductInformation.objects.all())
print(len(df_product))
product_type = [["BDTEXT","BDT","BDT*"],["MATNBR","MATERIAL NUMBER","MAT*"],["NAMPROD","NAM PROD","NAM*"],["NAMSYN","NAMPROD SYNONYMS","SYN*"],["NUMCAS","CAS NUMBER","CAS*"],["NAMCAS","CHEMICAL NAME","CHEMICAL*"],["REALSUB","REAL-SPEC","RSPEC*"],["PURESUB","PURE-SPEC","PSPEC*"]]
df_product.drop_duplicates(inplace=True)
df_product.columns=product_column
df_product=df_product.fillna(" - ")
for col in product_column:
    df_product[col]=df_product[col].astype('str').str.strip()


df_product_combine = df_product.copy()
df_product_combine=df_product_combine.fillna("-")
# last=''
# df_product_combine["MATERIAL NUMBER"] = df_product_combine["MATERIAL NUMBER"].astype('str')+" "+df_product_combine["DESCRIPTION"]
# df_product_combine.drop(columns=["DESCRIPTION"],inplace=True)
# product_column_combine = ["NAM PROD","BDT","CAS NUMBER","SPEC-ID","MATERIAL NUMBER"]
selected_data_json = {}

def inscope_product_details():
    return df_product,df_product_combine,product_column

def selected_data_details():
    global selected_data_json
    return selected_data_json

@csrf_exempt
def all_products(requests):
    try:
        if requests.method=="POST":
            try: 
                selected_categories=["BDT*","MAT*","NAM*","CAS*","CHEMICAL*","RSPEC*","PSPEC*","SYN*"]
                search_category = ["TEXT1","TEXT2","TEXT3"]
                category_type = ["MATNBR","NUMCAS","NAMPROD"]

                search_field=''
                data=''
                data_json=''
                search=''
                search_split=''
                search_key=''
                search_value=''
                edit_df=pd.DataFrame()
                data = requests.body.decode('utf-8')
                data_json=json.loads(data)
                search = data_json.get("SearchData",None).strip()
                res=''
                if "*" in search:
                    search_split=search.split('*')
                    search_key=search_split[0]+"*"
                    search_value = search_split[1].strip()

                if len(search)>=3 and (search_key.upper() in selected_categories or search.upper() in selected_categories):
                    print("typecat",search_key)
                    print("typeval",search_value)
                    all_product_list=[]                  
                    rex=re.compile(r"(^{})".format(search_value),re.I)
                    if search_key.upper()=="NAM*":
                        if len(search_value)>0:                     
                            edit_df=df_product_combine[df_product_combine["TEXT1"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy()                    
                        temp_df=edit_df[(edit_df["TYPE"]=="NAMPROD") & (edit_df["SUBCT"]=="REAL_SUB")]
                        temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                        for namprod, rspec, namsyn in temp_df:
                            value = str(namprod).strip() + " | "+str(rspec).strip()+" | "+str(namsyn).strip()
                            category = "NAM PROD | REAL-SPEC | SYNONYMS"
                            out_dict={"name":value,"type":category,"key":"NAM*","group":"PRODUCT-LEVEL"}
                            all_product_list.append(out_dict)
                    elif search_key.upper() == "RSPEC*":
                        if len(search_value)>0:                     
                            edit_df=df_product_combine[df_product_combine["TEXT2"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        temp_df = edit_df[(edit_df["SUBCT"]=="REAL_SUB") & (edit_df["TYPE"]=="NAMPROD")]  
                        temp_df = temp_df[["TEXT2","TEXT1","TEXT3"]].values.tolist()
                        for rspec, namprod, namsyn in temp_df:
                            value = str(rspec).strip() + " | " + str(namprod).strip() + " | " + str(namsyn).strip()
                            category = "REAL-SPEC | NAMPROD | SYNONYMS"
                            out_dict={"name":value,"type":category,"key":"RSPEC*","group":"PRODUCT-LEVEL"}
                            all_product_list.append(out_dict)
                    elif search_key.upper() == "SYN*":
                        if len(search_value)>0:                     
                            edit_df=df_product_combine[df_product_combine["TEXT3"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        temp_df=edit_df[(edit_df["TYPE"]=="NAMPROD") & (edit_df["SUBCT"]=="REAL_SUB")]
                        temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                        for namprod, rspec, namsyn in temp_df:
                            value = str(namsyn).strip() + " | "+str(rspec).strip() +" | "+str(namprod).strip()
                            category = "SYNONYMS | REAL-SPEC | NAM PROD"
                            out_dict={"name":value,"type":category,"key":"SYN*","group":"PRODUCT-LEVEL"}
                            all_product_list.append(out_dict)

                    elif search_key.upper()=="BDT*":
                        if len(search_value)>0:
                            edit_df=df_product_combine[df_product_combine["TEXT3"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        temp_df=edit_df[edit_df["TYPE"]=="MATNBR"]
                        print(edit_df)
                        temp_df=temp_df[["TEXT1","TEXT3","TEXT4"]].values.tolist()
                        for matnr, bdt, desc in temp_df:
                            value =  str(bdt).strip()+" | "+str(matnr).strip()+" | "+str(desc).strip()
                            category = "BDT | MATERIAL NUMBER | DESCRIPTION"
                            out_dict={"name":value,"type":category,"key":"BDT*","group":"MATERIAL-LEVEL"}
                            all_product_list.append(out_dict)
                    elif search_key.upper()=="MAT*": 
                        if len(search_value)>0:
                            edit_df=df_product_combine[df_product_combine["TEXT1"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        temp_df=edit_df[edit_df["TYPE"]=="MATNBR"]
                        temp_df=temp_df[["TEXT1","TEXT3","TEXT4"]].values.tolist()
                        for matnr, bdt, desc in temp_df:
                            value = str(matnr).strip() + " | "+str(desc).strip()+" | "+str(bdt).strip()
                            category = "MATERIAL NUMBER | DESCRIPTION | BDT"
                            out_dict={"name":value,"type":category,"key":"MAT*","group":"MATERIAL-LEVEL"}
                            all_product_list.append(out_dict)
                    elif search_key.upper()=="CAS*":
                        if len(search_value)>0:
                            edit_df=df_product_combine[df_product_combine["TEXT1"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        temp_df=edit_df[(edit_df["TYPE"]=="NUMCAS") & (edit_df["SUBCT"]=="PURE_SUB")]
                        temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                        for numcas, pspec, namcas in temp_df:
                            value = str(numcas).strip() + " | "+str(pspec).strip()+" | "+str(namcas).strip()
                            category = "CAS NUMBER | PURE-SPEC | CHEMICAL NAME"
                            out_dict={"name":value,"type":category,"key":"CAS*","group":"CAS-LEVEL"}
                            all_product_list.append(out_dict)
                    elif search_key.upper()=="CHEMICAL*":
                        if len(search_value)>0:
                            edit_df=df_product_combine[df_product_combine["TEXT3"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        temp_df=edit_df[(edit_df["TYPE"]=="NUMCAS") & (edit_df["SUBCT"]=="PURE_SUB")]
                        temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                        for numcas, pspec, namcas in temp_df:
                            value = str(namcas).strip() + " | "+str(pspec).strip() + " | "+str(numcas).strip()
                            category = "CHEMICAL NAME | PURE-SPEC | CAS NUMBER"
                            out_dict={"name":value,"type":category,"key":"SYN*","group":"PRODUCT-LEVEL"}
                            all_product_list.append(out_dict)
                    else:
                        if len(search_value)>0:
                            edit_df=df_product_combine[df_product_combine["TEXT2"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        temp_df = edit_df[(edit_df["SUBCT"]=="PURE_SUB") & (edit_df["TYPE"]=="NUMCAS")]  
                        temp_df = temp_df[["TEXT2","TEXT1","TEXT3"]].values.tolist()
                        for pspec, numcas, namcas in temp_df:
                            value = str(pspec).strip() + " | " + str(numcas).strip() + " | " + str(namcas).strip()
                            category = "PURE-SPEC | CAS NUMBER | CHEMICAL NAME"
                            out_dict={"name":value,"type":category,"key":"PSPEC*","group":"CAS-LEVEL"}
                            all_product_list.append(out_dict)

                    print("len of all_product_list",len(all_product_list))
                    print(all_product_list[0:5])
                    return JsonResponse(all_product_list,content_type="application/json",safe=False)
                    
                else:
                    print("all_products",data_json)
                    all_product_list=[]
                    rex=re.compile(r"(^{})".format(search),re.I)
                    for item in search_category:
                        edit_df=df_product_combine[df_product_combine[item].astype(str).str.contains(rex,na=False)]
                        if len(edit_df)>0:
                            print("item",item)
                            if item=="TEXT2": 
                                #for pure specid 
                                temp_df = edit_df[(edit_df["SUBCT"]=="REAL_SUB") & (edit_df["TYPE"]=="NAMPROD")]  
                                temp_df = temp_df[["TEXT2","TEXT1","TEXT3"]].values.tolist()
                                for rspec, namprod, namsyn in temp_df:
                                    value = str(rspec).strip() + " | " + str(namprod).strip() + " | " + str(namsyn).strip()
                                    category = "REAL-SPEC | NAMPROD | SYNONYMS"
                                    out_dict={"name":value,"type":category,"key":"RSPEC*","group":"PRODUCT-LEVEL"}
                                    all_product_list.append(out_dict)
                                temp_df = edit_df[(edit_df["SUBCT"]=="PURE_SUB") & (edit_df["TYPE"]=="NUMCAS")]  
                                temp_df = temp_df[["TEXT2","TEXT1","TEXT3"]].values.tolist()
                                for pspec, numcas, namcas in temp_df:
                                    value = str(pspec).strip() + " | " + str(numcas).strip() + " | " + str(namcas).strip()
                                    category = "PURE-SPEC | CAS NUMBER | CHEMICAL NAME"
                                    out_dict={"name":value,"type":category,"key":"PSPEC*","group":"CAS-LEVEL"}
                                    all_product_list.append(out_dict)
                                temp_df = pd.DataFrame()
                            elif item=="TEXT1":
                                print("text2")
                                for ctype in category_type:
                                    if ctype=="MATNBR":
                                        temp_df=edit_df[edit_df["TYPE"]==ctype]
                                        temp_df=temp_df[["TEXT1","TEXT3","TEXT4"]].values.tolist()
                                        for matnr, bdt, desc in temp_df:
                                            value = str(matnr).strip() + " | "+str(desc).strip()+" | "+str(bdt).strip()
                                            category = "MATERIAL NUMBER | DESCRIPTION | BDT"
                                            out_dict={"name":value,"type":category,"key":"MAT*","group":"MATERIAL-LEVEL"}
                                            all_product_list.append(out_dict)
                                    elif ctype=="NUMCAS":
                                        temp_df=edit_df[(edit_df["TYPE"]==ctype) & (edit_df["SUBCT"]=="PURE_SUB")]
                                        temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                                        for numcas, pspec, namcas in temp_df:
                                            value = str(numcas).strip() + " | "+str(pspec).strip()+" | "+str(namcas).strip()
                                            category = "CAS NUMBER | PURE-SPEC | CHEMICAL NAME"
                                            out_dict={"name":value,"type":category,"key":"CAS*","group":"CAS-LEVEL"}
                                            all_product_list.append(out_dict)
                                    else:
                                        print("esle namprod",ctype)
                                        print(edit_df)
                                        temp_df=edit_df[(edit_df["TYPE"]==ctype) & (edit_df["SUBCT"]=="REAL_SUB")]
                                        print(edit_df)
                                        temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                                        for namprod, rspec, namsyn in temp_df:
                                            value = str(namprod).strip() + " | "+str(rspec).strip()+" | "+str(namsyn).strip()
                                            category = "NAM PROD | REAL-SPEC | SYNONYMS"
                                            out_dict={"name":value,"type":category,"key":"NAM*","group":"PRODUCT-LEVEL"}
                                            all_product_list.append(out_dict)
                                temp_df = pd.DataFrame()
                            else:
                                print("else bdt")
                                category_text3=["MATNBR","NAMPROD","NUMCAS"]
                                for ctype in category_text3:
                                    if ctype == "MATNBR":
                                       temp_df=edit_df[edit_df["TYPE"]==ctype]
                                       print(edit_df)
                                       temp_df=temp_df[["TEXT1","TEXT3","TEXT4"]].values.tolist()
                                       for matnr, bdt, desc in temp_df:
                                            value =  str(bdt).strip()+" | "+str(matnr).strip()+" | "+str(desc).strip()
                                            category = "BDT | MATERIAL NUMBER | DESCRIPTION"
                                            out_dict={"name":value,"type":category,"key":"BDT*","group":"MATERIAL-LEVEL"}
                                            all_product_list.append(out_dict) 
                                    elif ctype == "NAMPROD":
                                        temp_df=edit_df[(edit_df["TYPE"]==ctype) & (edit_df["SUBCT"]=="REAL_SUB")]
                                        temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                                        for namprod, rspec, namsyn in temp_df:
                                            value = str(namsyn).strip() + " | "+str(rspec).strip()+ " | "+str(namprod).strip() 
                                            category = "SYNONYMS | REAL-SPEC | NAM PROD"
                                            out_dict={"name":value,"type":category,"key":"SYN*","group":"PRODUCT-LEVEL"}
                                            all_product_list.append(out_dict)
                                    else:
                                        temp_df=edit_df[(edit_df["TYPE"]==ctype) & (edit_df["SUBCT"]=="PURE_SUB")]
                                        temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                                        for numcas, pspec, namcas in temp_df:
                                            value = str(namcas).strip() + " | "+str(pspec).strip() + " | "+str(numcas).strip()
                                            category = "CHEMICAL NAME | PURE-SPEC | CAS NUMBER"
                                            out_dict={"name":value,"type":category,"key":"SYN*","group":"PRODUCT-LEVEL"}
                                            all_product_list.append(out_dict)
                                temp_df = pd.DataFrame()

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
                edit_df=pd.DataFrame()
                selected_categories=["BDT*","MAT*","NAM*","CAS*","CHEMICAL*","RSPEC*","PSPEC*","SYN*"]
                searched_product_list=[]
                data=''
                count=0
                product_count=0
                material_count=0
                cas_count=0
                data_json=''
                column_add=[]
                product_level_flag=''
                material_level_flag=''
                cas_level_flag=''
                data = requests.body.decode('utf-8')
                data_json=json.loads(data)
                print("selectedproducts",data_json)
                edit_df=df_product_combine.copy()            
                for item in data_json:
                    search_value = item.get("name")
                    search_value_split = search_value.split(" | ")
                    search_column = item.get("type")
                    search_key = item.get("key")
                    search_column_split = search_column.split(" | ")
                    search_group = item.get("group")
                    column_add.append(search_column)
                    count+=1
                    if search_group == "PRODUCT-LEVEL":
                        product_level_flag = 's'
                        product_count = count
                        product_rspec = search_value_split[search_column_split.index("REAL-SPEC")]
                    if search_group == "MATERIAL-LEVEL":
                        material_level_flag = 's'
                        material_count = count
                        material_number = search_value_split[search_column_split.index("MATERIAL NUMBER")]
                    if search_group == "CAS-LEVEL":
                        cas_level_flag = 's'
                        cas_count = count
                        cas_pspec = search_value_split[search_column_split.index("PURE-SPEC")]

                if product_level_flag=='s' and product_count==1:
                    if material_level_flag=='' and cas_level_flag=='':
                        print(product_rspec)
                        #to find material level details
                        temp_df=edit_df[(edit_df["TYPE"]=="MATNBR") & (edit_df["TEXT2"]==product_rspec)]
                        temp_df=temp_df[["TEXT1","TEXT3","TEXT4"]].values.tolist()
                        for matnr, bdt, desc in temp_df:
                            value = str(matnr).strip() + " | "+str(desc).strip()+" | "+str(bdt).strip()
                            category = "MATERIAL NUMBER | DESCRIPTION | BDT"
                            out_dict={"name":value,"type":category,"key":"MAT*","group":"MATERIAL-LEVEL"}
                            searched_product_list.append(out_dict)
                        #to find cas level details
                        temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT2"]==product_rspec)]
                        column_value = temp_df["TEXT1"].unique()
                        for item in column_value:  
                            temp_df=edit_df[(edit_df["TYPE"]=="NUMCAS") & (edit_df["SUBCT"]=="PURE_SUB") & (edit_df["TEXT2"]==item)]
                            temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                            for numcas, pspec, namcas in temp_df:
                                value = str(pspec).strip()+" | "+str(numcas).strip() + " | "+str(namcas).strip()
                                category = "PURE-SPEC | CAS NUMBER | CHEMICAL NAME"
                                out_dict={"name":value,"type":category,"key":"CAS*","group":"CAS-LEVEL"}
                                searched_product_list.append(out_dict)
                    elif material_level_flag=='s' and material_count==2 and cas_level_flag=='':
                        #to find cas level details
                        temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT2"]==product_rspec)]
                        column_value = temp_df["TEXT1"].unique()
                        for item in column_value:  
                            temp_df=edit_df[(edit_df["TYPE"]=="NUMCAS") & (edit_df["SUBCT"]=="PURE_SUB") & (edit_df["TEXT2"]==item)]
                            temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                            for numcas, pspec, namcas in temp_df:
                                value = str(pspec).strip()+" | "+str(numcas).strip() + " | "+str(namcas).strip()
                                category = "PURE-SPEC | CAS NUMBER | CHEMICAL NAME"
                                out_dict={"name":value,"type":category,"key":"CAS*","group":"CAS-LEVEL"}
                                searched_product_list.append(out_dict)
                    elif cas_level_flag=='s' and cas_count==2 and material_level_flag=='':
                        temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT1"]==cas_pspec)]
                        column_value = temp_df["TEXT2"].unique()
                        for item in column_value:
                            temp_df=edit_df[(edit_df["TYPE"]=="MATNBR") & (edit_df["TEXT2"]==item)]
                            temp_df=temp_df[["TEXT1","TEXT3","TEXT4"]].values.tolist()
                            for matnr, bdt, desc in temp_df:
                                value = str(matnr).strip() + " | "+str(desc).strip()+" | "+str(bdt).strip()
                                category = "MATERIAL NUMBER | DESCRIPTION | BDT"
                                out_dict={"name":value,"type":category,"key":"MAT*","group":"MATERIAL-LEVEL"}
                                searched_product_list.append(out_dict)

                elif material_level_flag =='s':
                    if product_level_flag =='' and cas_level_flag=='':
                        print("mat",material_number)        
                        temp_df=edit_df[(edit_df["TYPE"]=="MATNBR") & (edit_df["TEXT1"]==material_number)]
                        column_value = temp_df["TEXT2"].unique()
                        for item in column_value:
                            # product level details
                            print(item)
                            temp_df=edit_df[(edit_df["TYPE"]=="NAMPROD") & (edit_df["SUBCT"]=="REAL_SUB") & (edit_df["TEXT2"]==item)]
                            temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                            for namprod, rspec, namsyn in temp_df:
                                value = str(rspec).strip()+" | "+str(namprod).strip() + " | "+str(namsyn).strip()
                                category = "REAL-SPEC | NAM PROD | SYNONYMS"
                                out_dict={"name":value,"type":category,"key":"NAM*","group":"PRODUCT-LEVEL"}
                                searched_product_list.append(out_dict)
                            
                            #cas level details
                            temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT2"]==item)]
                            sub_column_value = temp_df["TEXT1"].unique()
                            for element in sub_column_value:  
                                temp_df=edit_df[(edit_df["TYPE"]=="NUMCAS") & (edit_df["SUBCT"]=="PURE_SUB") & (edit_df["TEXT2"]==element)]
                                temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                                for numcas, pspec, namcas in temp_df:
                                    value = str(pspec).strip()+" | "+str(numcas).strip() + " | "+str(namcas).strip()
                                    category = "PURE-SPEC | CAS NUMBER | CHEMICAL NAME"
                                    out_dict={"name":value,"type":category,"key":"CAS*","group":"CAS-LEVEL"}
                                    searched_product_list.append(out_dict)
                    elif product_level_flag =='s' and product_count ==2 and cas_level_flag=='':
                        temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT2"]==product_rspec)]
                        sub_column_value = temp_df["TEXT1"].unique()
                        for element in sub_column_value:  
                            temp_df=edit_df[(edit_df["TYPE"]=="NUMCAS") & (edit_df["SUBCT"]=="PURE_SUB") & (edit_df["TEXT2"]==element)]
                            temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                            for numcas, pspec, namcas in temp_df:
                                value = str(pspec).strip()+" | "+str(numcas).strip() + " | "+str(namcas).strip()
                                category = "PURE-SPEC | CAS NUMBER | CHEMICAL NAME"
                                out_dict={"name":value,"type":category,"key":"CAS*","group":"CAS-LEVEL"}
                                searched_product_list.append(out_dict)
                    elif cas_level_flag=='s' and cas_count==2 and product_level_flag=='':
                        temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT1"]==cas_pspec)]
                        column_value = temp_df["TEXT2"].unique()
                        for item in column_value:
                            temp_df=edit_df[(edit_df["TYPE"]=="NAMPROD") & (edit_df["SUBCT"]=="REAL_SUB") & (edit_df["TEXT2"]==item)]
                            temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                            for namprod, rspec, namsyn in temp_df:
                                value = str(rspec).strip()+" | "+str(namprod).strip() + " | "+str(namsyn).strip()
                                category = "REAL-SPEC | NAM PROD | SYNONYMS"
                                out_dict={"name":value,"type":category,"key":"NAM*","group":"PRODUCT-LEVEL"}
                                searched_product_list.append(out_dict)
                        # elif cas_level_flag=='s' and product_level_flag =='':
                elif cas_level_flag=='s':
                    if product_level_flag =='' and material_level_flag=='':
                        temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT1"]==cas_pspec)]
                        column_value = temp_df["TEXT2"].unique()
                        for item in column_value:
                            temp_df=edit_df[(edit_df["TYPE"]=="NAMPROD") & (edit_df["SUBCT"]=="REAL_SUB") & (edit_df["TEXT2"]==item)]
                            temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                            for namprod, rspec, namsyn in temp_df:
                                value = str(rspec).strip()+" | "+str(namprod).strip() + " | "+str(namsyn).strip()
                                category = "REAL-SPEC | NAM PROD | SYNONYMS"
                                out_dict={"name":value,"type":category,"key":"NAM*","group":"PRODUCT-LEVEL"}
                                searched_product_list.append(out_dict)

                            temp_df=edit_df[(edit_df["TYPE"]=="MATNBR") & (edit_df["TEXT2"]==item)]
                            temp_df=temp_df[["TEXT1","TEXT3","TEXT4"]].values.tolist()
                            for matnr, bdt, desc in temp_df:
                                value = str(matnr).strip() + " | "+str(desc).strip()+" | "+str(bdt).strip()
                                category = "MATERIAL NUMBER | DESCRIPTION | BDT"
                                out_dict={"name":value,"type":category,"key":"MAT*","group":"MATERIAL-LEVEL"}
                                searched_product_list.append(out_dict)
                    elif product_level_flag =='s' and product_count ==2 and material_level_flag=='':
                        temp_df=edit_df[(edit_df["TYPE"]=="MATNBR") & (edit_df["TEXT2"]==product_rspec)]
                        temp_df=temp_df[["TEXT1","TEXT3","TEXT4"]].values.tolist()
                        for matnr, bdt, desc in temp_df:
                            value = str(matnr).strip() + " | "+str(desc).strip()+" | "+str(bdt).strip()
                            category = "MATERIAL NUMBER | DESCRIPTION | BDT"
                            out_dict={"name":value,"type":category,"key":"MAT*","group":"MATERIAL-LEVEL"}
                            searched_product_list.append(out_dict)
                    elif material_level_flag=='s' and material_count==2 and product_level_flag=='':
                        temp_df=edit_df[(edit_df["TYPE"]=="MATNBR") & (edit_df["TEXT1"]==material_number)]
                        column_value = temp_df["TEXT2"].unique()
                        for item in column_value:
                            # product level details
                            print(item)
                            temp_df=edit_df[(edit_df["TYPE"]=="NAMPROD") & (edit_df["SUBCT"]=="REAL_SUB") & (edit_df["TEXT2"]==item)]
                            temp_df=temp_df[["TEXT1","TEXT2","TEXT3"]].values.tolist()
                            for namprod, rspec, namsyn in temp_df:
                                value = str(rspec).strip()+" | "+str(namprod).strip() + " | "+str(namsyn).strip()
                                category = "REAL-SPEC | NAM PROD | SYNONYMS"
                                out_dict={"name":value,"type":category,"key":"NAM*","group":"PRODUCT-LEVEL"}
                                searched_product_list.append(out_dict)
                    
                # print("len of selectedproducts",len(searched_product_list))
                # print(searched_product_list)
                return JsonResponse(searched_product_list,content_type="application/json",safe=False)
            except Exception as e:
                print(e)
                return JsonResponse([],content_type="application/json",safe=False)
                
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

