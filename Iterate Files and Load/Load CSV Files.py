# Created by Justin Lowe
import os
import pandas
import pyodbc
import csv
import sqlalchemy

engine = sqlalchemy.create_engine("mssql+pyodbc://SQLEXPRESS")

dir = "C:/Users/busin/Documents/Python/Code_Portfolio/Code_Portfolio/Iterate Files and Load/Files"

# Loop over defined directory and load all files found there into SQL DB, filename without extension will be used as tablename.
for subdir, dirs, files in os.walk(dir):
    for file in files:
        filepath = subdir + os.sep + file
        if filepath.endswith(".csv"):
            df = pandas.read_csv(filepath)
            table = file[0:file.find('.')]
            df.to_sql(table,engine,if_exists='replace')
            os.replace(filepath,"C:/Users/busin/Documents/Python/Code_Portfolio/Code_Portfolio/Iterate Files and Load/Files/Archive/"+ file)