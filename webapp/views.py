from django.http import HttpResponse
from . import configuration
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def index(requests):
    if requests.method=="POST":           
        print("ff")  
        connect=SQL_connection()
        items=[]
        cursor=connect.cursor()
        # query1="select IDTXT from momentive.sap_substance_identifier where (IDCAT='PROD' or IDCAT='MAT') and IDTYP='NAM'"
        query1="select * from momentive.product_inscope"
        cursor.execute(query1)
        data = requests.POST
        for row in cursor:
            print(row)
            break
        # for row in cursor:
        #     val=row[0]
        #     if data.get('search_key').lower() in str(val).lower():
        #         rdata={"name":str(val),
        #                 "type":"Namprod"}
        #         items.append(rdata)
        # parameter = config.DATABASES
        # return JsonResponse(items,safe=False)
        return JsonResponse({"data":"hello world"})
    elif requests.method=="GET":
        print("mmmm",requests.body)
        return HttpResponse("hello world")
def SQL_connection():
  import pyodbc
  server = configuration.sql_db["server"]
  database = configuration.sql_db["database"]
  username = configuration.sql_db["username"]
  password = configuration.sql_db["password"]
  
  driver= "{ODBC Driver 17 for SQL Server}"
  connection_string = 'DRIVER=' + driver + \
                      ';SERVER=' + server + \
                      ';PORT=1433' + \
                      ';DATABASE=' + database + \
                      ';UID=' + username + \
                      ';PWD=' + password
  try:
      sql_conn = pyodbc.connect(connection_string)
      return sql_conn
      # execute query and save data in pandas df
  except Exception as error:
      print("    \u2717 error message: {}".format(error))
      # I found that traceback prints much more detailed error message
      