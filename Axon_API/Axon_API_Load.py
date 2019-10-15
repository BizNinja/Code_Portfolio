#Ensure python is installed
#pip install requests
#pip install json
#pip install csv


import requests
from requests.auth import HTTPBasicAuth
import time
import json
import csv

#Params

#Pull Auth Token
axonurl='http://rhel75informatica2.infolink.local:9999'
username='admin@informatica.com'
password='@xonAdm1n'
authurl = axonurl + '/api/login_check'
data = {'username':username,'password':password}
resptoken = requests.post(url=authurl, data=data)

token_data = json.loads(resptoken.text)
token = json.dumps(token_data['token'])

#Take token and upload a file from your desktop
#For different targetRef values see the Informatica Axon API guide, different targetRef's will also require a different CSV file.
bulkurl = axonurl + '/bulkupload/v1/job/file?targetRef=InvolvedParty_bulkUpdate'
headers = {"Authorization": "Bearer " + token}
respfile = requests.post(url=bulkurl, headers=headers,files={"file":open('C:/Users/Justin.Lowe/Documents/Clients/Janus/api_test.csv',"rb")})


#Take File reference and map columns for the People inventory
file_data = json.loads(respfile.text)
fileRef = json.dumps(file_data['fileRef'])
joburl= axonurl + '/bulkupload/v1/job'
headers_job= {"Authorization": "Bearer " + token}

job_mapping = { 'fileRef': fileRef, "options": { "STOP_ON_WARNING":"false", }, "targetRef":"InvolvedParty_bulkUpdate","fieldMappings": [ { "sourceField":"People ID", "targetField":"People ID" }, { "sourceField":"First Name", "targetField":"First Name" }, { "sourceField":"Last Name", "targetField":"Last Name" }, { "sourceField":"Email", "targetField":"Email" },{ "sourceField":"Org Unit Reference", "targetField":"Org Unit Reference" },{ "sourceField":"Profile", "targetField":"Profile" },{ "sourceField":"Employment Type", "targetField":"Employment Type" },{ "sourceField":"Lifecycle", "targetField":"Lifecycle" },]}
respjob = requests.post(url=joburl, headers=headers_job,json=job_mapping)
print(respjob.text)

#Response should show that the job has been submitted. If errors are encountered, explore the HTTPD logs at /opt/Axon/axonhome/third-party-apps/httpd/logs