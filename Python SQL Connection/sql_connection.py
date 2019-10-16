import pyodbc
import csv

connection = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=PETEST;"
                      "Database=PETEST;"
                      "uid=;pwd=;")

cursor = connection.cursor()

cursor.execute("SELECT FullDate,ClientCode,REPLACE(ClientName,',','')  ClientName,REPLACE([Service Category],',','')  ServiceCategory,REPLACE([Service Title],',','')  ServiceTitle	,REPLACE(RelationshipPartner,',','') RelationshipPartner ,REPLACE(JobStatus,',','')  JobStatus,REPLACE(JobName,',','')  JobName	,REPLACE(JobManager,',','')  JobManager,REPLACE(StaffName,',','')  StaffName,BusinessUnit,SUM(Hours) Hours,SUM(Cost) Cost,SUM(Billed) Billed	FROM	(SELECT FullDate,c.[Service Category],c.[Service Title],[Client Code] ClientCode, [Client Name] ClientName,[Client Group] ClientGroup, a.ClientKey ClientKey,[Job Code] JobCode	,[Job Name] JobName,[Job Status] JobStatus,Partner RelationshipPartner,[Job Partner] JobPartner,[Manager Name] JobManager,[Staff Name] StaffName,case when d.[Partner Office] = 'Flemington' THEN 'FLEM' ELSE 'WISS' END as BusinessUnit,Hours,case when TransTypeIndex IN (1,2) THEN Amount else 0 end Cost,case when TransTypeIndex IN (3,6,8) THEN Amount * -1 else 0 end Billed FROM FactWorkInProgress a INNER JOIN DimDate b ON a.DateKey = b.DateKey INNER JOIN DimService c ON a.ServiceKey = c.ServiceKey INNER JOIN DimClient d	ON a.ClientKey = d.ClientKey	INNER JOIN DimPeriod e	ON a.PeriodKey = e.PeriodKey	INNER JOIN DimTransType f	ON a.TransTypeKey = f.TransTypeKey	INNER JOIN DimJob j	ON a.JobKey = j.JobKey	INNER JOIN DimManager m	ON a.ManagerKey = m.ManagerKey	INNER JOIN DimStaff s	ON a.StaffKey = s.StaffKey Where FullDate > '2017-01-01') X GROUP BY FullDate,ClientCode,ClientName,[Service Category],[Service Title] ,RelationshipPartner,JobStatus,JobName,JobManager,StaffName,BusinessUnit")

data=cursor.fetchall()

with open("PEExport.csv", "wb") as fp:
    a= csv.writer(fp, delimiter=',')
    for line in data:
        a.writerow(line)

cursor.close()
connection.close()