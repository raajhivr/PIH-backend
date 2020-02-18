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
product_nam_category = [["TEXT1","NAM PROD"],["TEXT2","REAL-SPECID"],["TEXT3","SYNONYMS"]]
product_rspec_category = [["TEXT2","REAL-SPECID"],["TEXT1","NAM PROD"],["TEXT3","SYNONYMS"]]
product_namsyn_category = [["TEXT3","SYNONYMS"],["TEXT2","REAL-SPECID"],["TEXT1","NAM PROD"]]
material_number_category = [["TEXT1","MATERIAL NUMBER"],["TEXT3","BDT"],["TEXT4","DESCRIPTION"]]
material_bdt_category = [["TEXT3","BDT"],["TEXT1","MATERIAL NUMBER"],["TEXT4","DESCRIPTION"]]
cas_number_category = [["TEXT1","CAS NUMBER"],["TEXT2","PURE-SPECID"],["TEXT3","CHEMICAL-NAME"]]
cas_pspec_category = [["TEXT2","PURE-SPECID"],["TEXT1","CAS NUMBER"],["TEXT3","CHEMICAL-NAME"]]
cas_chemical_category = [["TEXT3","CHEMICAL-NAME"],["TEXT2","PURE-SPECID"],["TEXT1","CAS NUMBER"]]
df_product = pd.read_excel(r"C:\Coding\momentive-backend\product_info_V2.xlsx",sheet_name="Sheet1")
# df_product = read_frame(ProductInformation.objects.all())
# print(len(df_product))
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

def product_level_creation(product_df,product_category_map,type,subct,key,level_name,filter_flag="no"):
    json_list=[]
    if filter_flag=="no":
        if type !='' and subct !='':
            temp_df=product_df[(product_df["TYPE"]==type) & (product_df["SUBCT"]==subct)]
        else:
            temp_df=product_df[(product_df["TYPE"]==type)]
    else:
        temp_df=product_df
        
    total_count=0
    display_category=''
    json_category=''
    extract_column=[]
    for column,category in product_category_map:
        extract_column.append(column) 
        category_count = len(temp_df[column].unique())
        total_count+=category_count
        display_category+=category+"("+str(category_count)+")|"
        json_category+= category+" | "  
                
    display_category=display_category[:-1] 
    json_category=json_category[:-3]       
    print(product_category_map)
    # print(display_category)
    # print(json_category)           
    temp_df=temp_df[extract_column].values.tolist()
    for value1,value2,value3 in temp_df:
        value = str(value1).strip() + " | "+str(value2).strip()+" | "+str(value3).strip()
        out_dict={"name":value,"type":json_category,"key":key,"group":level_name+"("+display_category+")"+" - "+str(total_count) }
        json_list.append(out_dict)
    # print(json_list)
    return json_list
@csrf_exempt
def all_products(requests):
    try:
        if requests.method=="POST":
            try: 
                category_type = ["MATNBR","NUMCAS","NAMPROD"]
                search_category = ["TEXT1","TEXT2","TEXT3"]
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
                selected_categories=["BDT*","MAT*","NAM*","CAS*","CHEMICAL*","RSPEC*","PSPEC*","SYN*","SPEC*"]                   
                if "*" in search:
                    search_split=search.split('*')
                    search_key=search_split[0]+"*"
                    search_value = search_split[1].strip()
                    print(search_key)
                if len(search)>=3 and (search_key.upper() in selected_categories or search.upper() in selected_categories):
                    all_product_list=[]                  
                    rex=re.compile(r"(^{})".format(search_value),re.I)

                    if search_key.upper()=="NAM*":
                        if len(search_value)>0:                     
                            edit_df=df_product_combine[df_product_combine["TEXT1"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        all_product_list=product_level_creation(edit_df,product_nam_category,"NAMPROD","REAL_SUB","NAM*","PRODUCT-LEVEL")                  
                        
                    elif search_key.upper() == "RSPEC*":
                        if len(search_value)>0:                     
                            edit_df=df_product_combine[df_product_combine["TEXT2"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        all_product_list=product_level_creation(edit_df,product_rspec_category,"NAMPROD","REAL_SUB","RSPEC*","PRODUCT-LEVEL")   
                        
                    elif search_key.upper() == "SYN*":
                        if len(search_value)>0:                     
                            edit_df=df_product_combine[df_product_combine["TEXT3"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        all_product_list=product_level_creation(edit_df,product_namsyn_category,"NAMPROD","REAL_SUB","SYN*","PRODUCT-LEVEL") 
                        

                    elif search_key.upper()=="BDT*":
                        if len(search_value)>0:
                            edit_df=df_product_combine[df_product_combine["TEXT3"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        all_product_list=product_level_creation(edit_df,material_bdt_category,"MATNBR",'',"BDT*","MATERIAL-LEVEL")

                    elif search_key.upper()=="MAT*": 
                        if len(search_value)>0:
                            edit_df=df_product_combine[df_product_combine["TEXT3"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        all_product_list=product_level_creation(edit_df,material_number_category,"MATNBR",'',"MAT*","MATERIAL-LEVEL")

                    elif search_key.upper()=="CAS*":
                        if len(search_value)>0:
                            edit_df=df_product_combine[df_product_combine["TEXT1"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        all_product_list=product_level_creation(edit_df,cas_number_category,"NUMCAS","PURE_SUB","CAS*","CAS-LEVEL")
                       
                    elif search_key.upper()=="CHEMICAL*":
                        if len(search_value)>0:
                            edit_df=df_product_combine[df_product_combine["TEXT3"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        all_product_list=product_level_creation(edit_df,cas_chemical_category,"NUMCAS","PURE_SUB","CHEMICAL*","CAS-LEVEL")
                    
                    elif  search_key.upper()=="SPEC*": 
                        if len(search_value)>0:
                            edit_df=df_product_combine[df_product_combine["TEXT2"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy()
                        #for real specid 
                        real_product_list=product_level_creation(edit_df,product_rspec_category,"NAMPROD","REAL_SUB","RSPEC*","PRODUCT-LEVEL")
                        #for pure details    
                        pure_product_list=product_level_creation(edit_df,cas_pspec_category,"NUMCAS","PURE_SUB","PSEPC*","CAS-LEVEL")                              
                        all_product_list=real_product_list+pure_product_list

                    else:
                        if len(search_value)>0:
                            edit_df=df_product_combine[df_product_combine["TEXT2"].astype(str).str.contains(rex,na=False)]
                        else:
                            edit_df=df_product_combine.copy() 
                        all_product_list=product_level_creation(edit_df,cas_pspec_category,"NUMCAS","PURE_SUB","PSEPC*","CAS-LEVEL")

                        
                    print(all_product_list[0:5])
                    return JsonResponse(all_product_list,content_type="application/json",safe=False)
                    
                else:
                    print("all_products",data_json)
                    all_product_list=[]
                    rex=re.compile(r"(^{})".format(search),re.I)
                    for item in search_category:
                        edit_df=df_product_combine[df_product_combine[item].astype(str).str.contains(rex,na=False)]
                        if len(edit_df)>0:
                            if item=="TEXT2": 
                                #for real specid 
                                all_product_list=all_product_list+product_level_creation(edit_df,product_rspec_category,"NAMPROD","REAL_SUB","RSPEC*","PRODUCT-LEVEL")
                                #cas level details    
                                all_product_list=all_product_list+product_level_creation(edit_df,cas_pspec_category,"NUMCAS","PURE_SUB","PSEPC*","CAS-LEVEL")                              
                                
                            elif item=="TEXT1":
                                for ctype in category_type:
                                    if ctype=="MATNBR":
                                        all_product_list=all_product_list+product_level_creation(edit_df,material_number_category,"MATNBR",'',"MAT*","MATERIAL-LEVEL")
                                    elif ctype=="NUMCAS":
                                        all_product_list=all_product_list+product_level_creation(edit_df,cas_number_category,"NUMCAS","PURE_SUB","CAS*","CAS-LEVEL")
                                    else:
                                        all_product_list=all_product_list+product_level_creation(edit_df,product_nam_category,"NAMPROD","REAL_SUB","NAM*","PRODUCT-LEVEL")
                            else:
                                category_text3=["MATNBR","NAMPROD","NUMCAS"]
                                for ctype in category_text3:
                                    if ctype == "MATNBR":
                                        all_product_list=all_product_list+product_level_creation(edit_df,material_bdt_category,"MATNBR",'',"BDT*","MATERIAL-LEVEL")
                                    elif ctype == "NAMPROD":
                                        all_product_list=all_product_list+product_level_creation(edit_df,product_namsyn_category,"NAMPROD","REAL_SUB","SYN*","PRODUCT-LEVEL")
                                    else:
                                        all_product_list=all_product_list+product_level_creation(edit_df,cas_chemical_category,"NUMCAS","PURE_SUB","CHEMICAL*","CAS-LEVEL")
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
                    search_group = item.get("group").split("(")
                    search_group = search_group[0].strip()
                    column_add.append(search_column)
                    count+=1
                    if search_group == "PRODUCT-LEVEL":
                        product_level_flag = 's'
                        product_count = count
                        product_rspec = search_value_split[search_column_split.index("REAL-SPECID")]
                    if search_group == "MATERIAL-LEVEL":
                        material_level_flag = 's'
                        material_count = count
                        material_number = search_value_split[search_column_split.index("MATERIAL NUMBER")]
                    if search_group == "CAS-LEVEL":
                        cas_level_flag = 's'
                        cas_count = count
                        cas_pspec = search_value_split[search_column_split.index("PURE-SPECID")]

                if product_level_flag=='s' and product_count==1:
                    if material_level_flag=='' and cas_level_flag=='':
                        print(product_rspec)
                        #to find material level details
                        temp_df=edit_df[(edit_df["TYPE"]=="MATNBR") & (edit_df["TEXT2"]==product_rspec)]
                        searched_product_list=searched_product_list+product_level_creation(temp_df,material_number_category,"","","MAT*","MATERIAL-LEVEL","yes")
                        #to find cas level details
                        temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT2"]==product_rspec)]
                        column_value = temp_df["TEXT1"].unique()
                        for item in column_value:  
                            temp_df=edit_df[(edit_df["TYPE"]=="NUMCAS") & (edit_df["SUBCT"]=="PURE_SUB") & (edit_df["TEXT2"]==item)]
                            searched_product_list=searched_product_list+product_level_creation(temp_df,cas_number_category,"","","CAS*","CAS-LEVEL","yes")
                        
                    elif material_level_flag=='s' and material_count==2 and cas_level_flag=='':
                        #to find cas level details
                        temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT2"]==product_rspec)]
                        column_value = temp_df["TEXT1"].unique()
                        for item in column_value:  
                            temp_df=edit_df[(edit_df["TYPE"]=="NUMCAS") & (edit_df["SUBCT"]=="PURE_SUB") & (edit_df["TEXT2"]==item)]
                            searched_product_list=searched_product_list+product_level_creation(temp_df,cas_number_category,"NUMCAS","PURE_SUB","CAS*","CAS-LEVEL","yes")
                    elif cas_level_flag=='s' and cas_count==2 and material_level_flag=='':
                        temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT1"]==cas_pspec)]
                        column_value = temp_df["TEXT2"].unique()
                        for item in column_value:
                            temp_df=edit_df[(edit_df["TYPE"]=="MATNBR") & (edit_df["TEXT2"]==item)]
                            searched_product_list=searched_product_list+product_level_creation(temp_df,material_number_category,"","","MAT*","MATERIAL-LEVEL","yes")

                elif material_level_flag =='s':
                    if product_level_flag =='' and cas_level_flag=='':
                        print("mat",material_number)        
                        temp_df=edit_df[(edit_df["TYPE"]=="MATNBR") & (edit_df["TEXT1"]==material_number)]
                        column_value = temp_df["TEXT2"].unique()
                        for item in column_value:
                            # product level details
                            temp_df=edit_df[(edit_df["TYPE"]=="NAMPROD") & (edit_df["SUBCT"]=="REAL_SUB") & (edit_df["TEXT2"]==item)]
                            searched_product_list=searched_product_list+product_level_creation(temp_df,product_rspec_category,"","","RSPEC*","PRODUCT-LEVEL","yes")                          
                            #cas level details
                            temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT2"]==item)]
                            sub_column_value = temp_df["TEXT1"].unique()
                            for element in sub_column_value:  
                                temp_df=edit_df[(edit_df["TYPE"]=="NUMCAS") & (edit_df["SUBCT"]=="PURE_SUB") & (edit_df["TEXT2"]==element)]
                                searched_product_list=searched_product_list+product_level_creation(temp_df,cas_number_category,"","","CAS*","CAS-LEVEL","yes")                         
                            
                    elif product_level_flag =='s' and product_count ==2 and cas_level_flag=='':
                        temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT2"]==product_rspec)]
                        sub_column_value = temp_df["TEXT1"].unique()
                        for element in sub_column_value:  
                            temp_df=edit_df[(edit_df["TYPE"]=="NUMCAS") & (edit_df["SUBCT"]=="PURE_SUB") & (edit_df["TEXT2"]==element)]
                            searched_product_list=searched_product_list+product_level_creation(temp_df,cas_number_category,"","","CAS*","CAS-LEVEL","yes")                         
                            
                    elif cas_level_flag=='s' and cas_count==2 and product_level_flag=='':
                        temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT1"]==cas_pspec)]
                        column_value = temp_df["TEXT2"].unique()
                        for item in column_value:
                            temp_df=edit_df[(edit_df["TYPE"]=="NAMPROD") & (edit_df["SUBCT"]=="REAL_SUB") & (edit_df["TEXT2"]==item)]
                            searched_product_list=searched_product_list+product_level_creation(temp_df,product_rspec_category,"","","RSPEC*","PRODUCT-LEVEL","yes")                          
                            
                        # elif cas_level_flag=='s' and product_level_flag =='':
                elif cas_level_flag=='s':
                    if product_level_flag =='' and material_level_flag=='':
                        temp_df=edit_df[(edit_df["TYPE"]=="SUBIDREL") & (edit_df["TEXT1"]==cas_pspec)]
                        column_value = temp_df["TEXT2"].unique()
                        for item in column_value:
                            temp_df=edit_df[(edit_df["TYPE"]=="NAMPROD") & (edit_df["SUBCT"]=="REAL_SUB") & (edit_df["TEXT2"]==item)]
                            searched_product_list=searched_product_list+product_level_creation(temp_df,product_rspec_category,"","","RSPEC*","PRODUCT-LEVEL","yes")                          
                            temp_df=edit_df[(edit_df["TYPE"]=="MATNBR") & (edit_df["TEXT2"]==item)]
                            searched_product_list=searched_product_list+product_level_creation(temp_df,material_number_category,"","","MAT*","MATERIAL-LEVEL","yes")

                    elif product_level_flag =='s' and product_count ==2 and material_level_flag=='':
                        temp_df=edit_df[(edit_df["TYPE"]=="MATNBR") & (edit_df["TEXT2"]==product_rspec)]
                        searched_product_list=searched_product_list+product_level_creation(temp_df,material_number_category,"","","MAT*","MATERIAL-LEVEL","yes")

                    elif material_level_flag=='s' and material_count==2 and product_level_flag=='':
                        temp_df=edit_df[(edit_df["TYPE"]=="MATNBR") & (edit_df["TEXT1"]==material_number)]
                        column_value = temp_df["TEXT2"].unique()
                        for item in column_value:
                            # product level details
                            temp_df=edit_df[(edit_df["TYPE"]=="NAMPROD") & (edit_df["SUBCT"]=="REAL_SUB") & (edit_df["TEXT2"]==item)]
                            searched_product_list=searched_product_list+product_level_creation(temp_df,product_rspec_category,"","","RSPEC*","PRODUCT-LEVEL","yes")                          
                    
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

