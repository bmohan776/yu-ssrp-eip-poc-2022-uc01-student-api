import logging
import json
from re import I
from urllib import response
import azure.functions as func
import datetime as dt
import requests
from requests.exceptions import HTTPError
import configparser

current_time = dt.datetime.now()
config = configparser.ConfigParser()
config.readfp(open(r'config.ini'))

studentRegistration_url = config.get('studentRecordsAPI', 'studentRegistration')
studentCourses_url = config.get('studentRecordsAPI', 'studentCourses')
StudAPIKEY = config.get('APIKEY', 'studentAPIKEY')


def api_call(sisid,academicyear,url):
    try:
       reg_url = url+""+sisid+""+"/academicyear/"+""+academicyear
       print(f" Student URL : {reg_url} ")
       headers = {'Accept': 'application/json', 'X-API-Key': StudAPIKEY}
 
       # GET request
       logging.info("Invoke Student API")
       response = requests.request("GET", reg_url, headers=headers)
       response.raise_for_status()
       json_data = json.loads(response.text)
       return json_data
   
    except Exception as err:
     print('studentRegistration exception occured while exectuing', err)
    
    
def studentRegistration(sisid, academicyear):
    try:
       logging.info("Invoke Student Registration API")
       json_data = api_call(sisid, academicyear,studentRegistration_url)
       i_registrationstatus = [db_item["registrationstatus"] for db_item in json_data]
       i_yuarprogtype = [db_item["yuarprogtype"] for db_item in json_data]

       #print(i_registrationstatus[0])
       #print(i_yuarprogtype[0]) 
       
       if i_registrationstatus[0] == "RA" and i_yuarprogtype[0] == "GR" :
          json_data = json.dumps({"sisid": f"{sisid}",  "eligibility": "Eligible - Graduate Housing", "datetime": f"{current_time}"})
       else:
          json_data = ""
       return json_data
   
    except Exception as err:
     print('studentRegistration exception occured while exectuing', err)


def studentcourses(sisid, academicyear):
    try:
       logging.info("Invoke Student Courses API")
        
       json_data = api_call(sisid, academicyear,studentCourses_url)
       
       print([db_item["creditweight"] for db_item in json_data])
       i_creditweight = ([db_item["creditweight"] for db_item in json_data])
       print("credit", sum(i_creditweight))
       
       if sum(i_creditweight) == 18 or sum(i_creditweight) > 18:
           json_data = json.dumps({"sisid": f"{sisid}",  "eligibility": "Eligible - Undergraduate Housing", "datetime": f"{current_time}"})
       else:
           json_data = ""
                  
       return json_data
    except Exception as err:
        print('studentcourses exception occured while exectuing', err)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    sisid=req.params.get('sisid')
    academicyear=req.params.get('academicyear')

    logging.info('studentRegistration')

    #check Student registration APL
    sisidresponse=studentRegistration(sisid, academicyear)
    logging.info(sisidresponse)

    #check Student Courses APL
    if not sisidresponse:
       sisidresponse = studentcourses(sisid,academicyear)

    if sisidresponse:
        return func.HttpResponse(f"{sisidresponse}")
    else:
        return func.HttpResponse(f" Student ID : {sisid} student is not eligible for housing.",
             status_code = 200
        )

if __name__ == "__main__":
    main()