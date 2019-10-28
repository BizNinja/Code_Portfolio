REM Created by Justin Lowe
REM The point of this code is to create a csv from a SQL connection that represents Practice Engine Data.
python PEexport.py
REM Next Pandas is leveraged to add date data to an HR export, which allows us to define what year a month exists in.
python C:\Code\pandasconv.py
REM Copying csv data up to the google cloud bucket.
call gsutil -m cp C:\*.csv gs://wreporting/

REM Delete csv files to guard against security breaches.
del "C:\FTEbyBusinessUnit.csv"
del "C:\GrossPaybyBusinessUnit.csv"
del "C:\FTEbyBusinessUnit.xls"
del "C:\GrossPaybyBusinessUnit.xls"

REM Next we call SQL files that are stored as plain text that define the ETL procedures. The goal being to load new data, then update insert into reporting tables thereafter.
call bq query --use_legacy_sql=false < "C:\Code\DEL_LKP_SERVICE.txt" 
call bq --location=US load --source_format=CSV COMPANY.LKP_SERVICE gs://wreporting/ServiceLookup.csv ADPField:STRING,PEField:STRING 
REM call bq --location=US load --skip_leading_rows=1 --source_format=CSV COMPANY.STG_MONTH gs://wreporting/MonthDim.csv MonthKey:INTEGER,Month:STRING,MonthNum:INTEGER,Year:INTEGER,StartDate:STRING,EndDate:STRING
REM call bq query --use_legacy_sql=false < "C:\Code\MonthDim.txt" 

call bq query --use_legacy_sql=false < "C:\Code\DEL_STG_GP_BU.txt" 

call bq --location=US load  --skip_leading_rows=4 --source_format=CSV COMPANY.STG_GP_BU gs://wreporting/GrossPaybyBusinessUnit.csv index:STRING,BusinessUnitCode:STRING,HomeDepartmentCode:INTEGER,PayrollName:STRING,JobTitleDescription:STRING,Jan:FLOAT,Feb:FLOAT,Mar:FLOAT,Apr:FLOAT,May:FLOAT,Jun:FLOAT,Jul:FLOAT,Aug:FLOAT,Sep:FLOAT,Oct:FLOAT,Nov:FLOAT,Dec:FLOAT,StartDate:STRING,EndDate:STRING  

call bq query --use_legacy_sql=false < "C:\Code\DEL_STG_FTE_BU.txt"   

call bq --location=US load  --skip_leading_rows=4 --source_format=CSV COMPANY.STG_FTE_BU gs://wreporting/FTEbyBusinessUnit.csv index:STRING,BusinessUnitCode:STRING,HomeDepartmentCode:INTEGER,PayrollName:STRING,JobTitleDescription:STRING,Jan:FLOAT,Feb:FLOAT,Mar:FLOAT,Apr:FLOAT,May:FLOAT,Jun:FLOAT,Jul:FLOAT,Aug:FLOAT,Sep:FLOAT,Oct:FLOAT,Nov:FLOAT,Dec:FLOAT,StartDate:STRING,EndDate:STRING  

call bq query --use_legacy_sql=false < "C:\Code\DEL_STG_PE_DATA.txt"   

call bq --location=US load --source_format=CSV COMPANY.STG_PE_DATA gs://wreporting/PEExport.csv Date:STRING,ClientCode:STRING,ClientName:STRING,ServiceCategory:STRING,ServiceTitle:STRING,RelationshipPartner:STRING,JobStatus:STRING,JobName:STRING,JobManager:STRING,StaffName:STRING,BusinessUnit:STRING,Hours:FLOAT,Cost:FLOAT,Billed:FLOAT

call bq query --use_legacy_sql=false < "C:\Code\GP_BU.txt"   
call bq query --use_legacy_sql=false < "C:\Code\FTE_BU.txt"   
call bq query --use_legacy_sql=false < "C:\Code\PE_DATA.txt"  
call bq query --use_legacy_sql=false < "C:\Code\SERVICE_XWALK.txt"


call bq query --use_legacy_sql=false < "C:\Code\RPT_PL_SUM.txt"