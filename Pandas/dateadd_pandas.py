# Created by Justin Lowe
# The point of this code is to add a date column from a location in the file to decode the Jan - Dec distinctions that lack a year attribute.
import csv
import pandas as pd

with open('C:\FTEbyBusinessUnit.csv') as csvDataFile:
    data = [row for row in csv.reader(csvDataFile)]
    startdate = (data[0][2])
    enddate = (data[1][2])
    print(startdate)
    print(enddate)

csv_input = pd.read_csv('C:\FTEbyBusinessUnit.csv')
csv_input['StartDate'] = startdate
csv_input['EndDate'] = enddate

csv_input.to_csv('C:\FTEbyBusinessUnit.csv', index=False)

# Add Dates to Gross Pay file

with open('C:\GrossPaybyBusinessUnit.csv') as csvDataFile:
    data = [row for row in csv.reader(csvDataFile)]
    startdate = (data[0][2])
    enddate = (data[1][2])
    print(startdate)
    print(enddate)

csv_input = pd.read_csv('C:\GrossPaybyBusinessUnit.csv')
csv_input['StartDate'] = startdate
csv_input['EndDate'] = enddate

csv_input.to_csv('C:\GrossPaybyBusinessUnit.csv', index=False)