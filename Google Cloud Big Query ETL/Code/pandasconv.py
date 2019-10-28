#Created by Justin Lowe
import pandas as pd
import csv
from xlrd import *
import win32com.client
import sys

xcl = win32com.client.Dispatch("Excel.Application")
wb1 = xcl.Workbooks.Open("//PETEST/Excel Share/FTE by Business Unit", False, True, None)
wb2 = xcl.Workbooks.Open("//PETEST/Excel Share/Gross Pay by Business Unit", False, True, None)
xcl.DisplayAlerts = False
wb1.SaveAs("C:\FTEbyBusinessUnit.xls", None, '', '')
wb2.SaveAs("C:\GrossPaybyBusinessUnit.xls", None, '', '')
xcl.Quit()

data_xls = pd.read_excel('C:/WissReporting/FTEbyBusinessUnit.xls', 0, index_col=None)
data_xls.to_csv('C:/WissReporting/FTEbyBusinessUnit.csv', encoding='utf-8')

data_xls1 = pd.read_excel('C:/WissReporting/GrossPaybyBusinessUnit.xls', 0, index_col=None)
data_xls1.to_csv('C:/WissReporting/GrossPaybyBusinessUnit.csv', encoding='utf-8')

# Add Dates to FTE file

with open('C:\FTEbyBusinessUnit.csv') as csvDataFile:
    data = [row for row in csv.reader(csvDataFile)]
    startdate = (data[0][2])
    enddate = (data[1][2])


csv_input = pd.read_csv('C:\FTEbyBusinessUnit.csv')
csv_input['StartDate'] = startdate
csv_input['EndDate'] = enddate

csv_input.to_csv('C:\FTEbyBusinessUnit.csv', index=False)

# Add Dates to Gross Pay file

with open('C:\GrossPaybyBusinessUnit.csv') as csvDataFile:
    data = [row for row in csv.reader(csvDataFile)]
    startdate = (data[0][2])
    enddate = (data[1][2])


csv_input = pd.read_csv('C:\GrossPaybyBusinessUnit.csv')
csv_input['StartDate'] = startdate
csv_input['EndDate'] = enddate

csv_input.to_csv('C:\GrossPaybyBusinessUnit.csv', index=False)