# PURPOSE: This class will pull data from Drilling Info in a full or incremental manner. You can pass different data
# services to pull different tables back from the API.
# AUTHOR: Justin Lowe (CapTech)
# VERSION: 1.01
import json
import warnings
import argparse
import datetime
import requests
import base64
import logging
import sys
import pandas as pd
from datetime import date, timedelta
import numpy as np
import psutil
import os
import time

class DrillingInfoIntegrationEngine(object):

    def __init__(self, args):
        self.client_id = args.client_id
        self.client_secret = args.client_secret
        self.api_key = args.api_key
        self.links = None
        self.data_service = args.data_service
        self.load_type = args.load_type
        self.app_server = args.app_server
        self.app_user = args.app_user
        self.app_password = args.app_password
        self.app_database =args.app_database
        self.pylib_path = args.pylib
        self.schema_name = args.schema_name
        self.entity_name = args.entity_name
        self.f_string = args.f_string
        self.add_filter = args.add_filter
        self.root_url = "https://di-api.drillinginfo.com/v2"

        
         
        sys.path.insert(0, self.pylib_path)

        from gif.gif_extract import GifTsqlExtract
        from gif.gif_connection import GifTsqlConnection
        from gif.gif_entity import GifTsqlEntity
        from gif.gif_log import GifTsqlLog
        from gif.gif_batch import GifTsqlBatch

        # initialize headers
        self.headers = {
            'x-api-key': self.api_key,
            'cache-control': "no-cache",
            'content-type': "application/x-www-form-urlencoded"
        }

        logging.basicConfig(level=logging.INFO,
                            filename='DrillingInfo_logging_daily.log',
                            filemode='w', format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S')
        

        # a function that returns a connection to SQL database
        def gif_connection():

                self.gif_conn = GifTsqlConnection(
                            self.app_server, self.app_database, self.app_user, self.app_password)

                self.gif_entity = GifTsqlEntity(
                            version=None, connection=self.gif_conn)



        def log_connection():

                log_conn = GifTsqlConnection(
                            self.app_server, self.app_database, self.app_user, self.app_password)
                app_batch = GifTsqlBatch(log_conn)
                app_batch.start_batch(0, "DrillingInfo: " + self.data_service)

                self.app_log = GifTsqlLog(app_batch)



        # get token and store it in headers to use for requests
        def get_token(client_id, client_secret):

                string_to_encode = client_id + ":" + client_secret
                encoded = "Basic " + base64.b64encode(string_to_encode.encode('ascii')).decode()
                self.headers['authorization'] = encoded

                url = self.root_url + "/direct-access/tokens?grant_type=client_credentials"
                response = requests.request("POST", url, headers=self.headers)
                token = response.json()['access_token']

                self.headers['authorization'] = "Bearer " + token



        def url_load_type(data_service, load_type):

            print(self.add_filter)

            if load_type == 'full':
                if data_service in ['well-origins','wellbores','completions','well-rollups']:
                    data_service = data_service
                else:
                    data_service = data_service + "?deleteddate=null" + self.add_filter
            else:
                update_date = (date.today() - timedelta(days=int(args.lag))).strftime('%Y-%m-%d')
                if data_service in ['well-origins','wellbores','completions','well-rollups']:
                    data_service = data_service + "?updateddate=ge(" + update_date + ")&updateddate=ne(null)"
                else:
                    data_service = data_service + "?updateddate=ge(" + update_date + ")&updateddate=ne(null)&deleteddate=null" + self.add_filter

            url = self.root_url + "/direct-access/" + data_service
            return url


        # get DDL for given API data service to map data types to columns
        def get_ddl(data_service):

            ddl = requests.get('https://di-api.drillinginfo.com/v2/direct-access/' + data_service + '?ddl=mssql', headers=self.headers)
            ddl_list = [(x.split(' ')[0],x.split(' ')[1]) for x in [x.split(',')[0] for x in ddl.text.split('\n')][1:-1]]
            
            return ddl_list



        # data is initialized as objects to keep python from making un-castable float 64's
        # these functions map each column to the correct data type based on the DDL response from Drilling Info

        def int_dt(col, df):
            df[col] = df[col].fillna(0).astype(int)
        def char_dt(col, df):
            df[col] = df[col].map(str)
        def float_dt(col, df):
            df[col] = df[col].astype(float)
        def date_dt(col, df):
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
        def f_str(col, df):
            df[col] = df[col].map(lambda x : x if pd.isnull(x) else '{:f}'.format(float(x)))

        dt_dict = {'INT': int_dt,
                   'TEXT': char_dt,
                   'VARCHAR(5)': char_dt,
                   'NUMERIC': float_dt,
                   'DATETIME': date_dt,
                   'f_string': f_str
        }

        # takes json, converts to dataframe to clean and format, returns json payload for insert
        def clean_json(json_payload, ddl):

            df = pd.DataFrame(json_payload, dtype=object)
            try:
                df = df.rename(columns = {'Api10':'API10','Api14':'API14'})
            except:
                pass
            for col, dt in ddl:
                try:
                    dt_dict[dt](col, df)
                except:
                    # unable to change column datatype
                   pass

            df = df.replace('NaT',np.nan)
            df = df.replace('NaN',np.nan)
            df = df.replace('None',np.nan)
	        #Justin Lowe (Captech) Updating logic for new data services, same goal just different method.
            try:
                for col in df.select_dtypes([np.object]).columns[1:]:            
                    df[col] = df[col].str.replace("'",'')
                for col in df.select_dtypes([np.object]).columns[1:]: 
                    df[col] = df[col].str.replace('"','')
            #Anything that falls out is boolean
            except:
                pass

            
            return df


        def payload_format(json_dump):
                return """ { "payload": """ + json_dump + '}' + ""


                       
        # make DI with initial url, if has been run once will use next href
        def DI_request(url):

            if self.links:
                    #Setting pagesize smaller for well-rollups to decrease memory consumption, by far the largest table
                    if self.data_service == 'well-rollups':
                        request = requests.get(self.root_url + '/direct-access' + self.links['next']['url'],
                                               headers=self.headers,  params={'pagesize': '3000'})
                    else:
                        request = requests.get(self.root_url + '/direct-access' + self.links['next']['url'],
                                               headers=self.headers,  params={'pagesize': '10000'})
            else:
                if self.data_service == 'well-rollups':
                    request = requests.get(url, headers=self.headers, params={'pagesize': '3000'})
                else:
                    request = requests.get(url, headers=self.headers, params={'pagesize': '10000'})
            if 'next' in request.links:
                self.links = request.links
                
            return request




        # a function that will make single inserts from a dataframe in case of full load error
        def DI_single_load(df):

            for index, row in df.iterrows():
                try:
                    json_load = payload_format(json.dumps([row.dropna().to_dict()]))
                    
                    try:
                        self.gif_entity.entity_post(self.schema_name, self.entity_name,json_load)
                    except:
                        self.gif_conn.close()
                        gif_connection()
                    try:
                        log('single insert made: ' + str(df['API14'][index]))
                    except:
                        log('single insert made: #'  + str(df.index[index])+  str(json_load))
                except:
                    try:
                        print('failed to insert API: ' + str(df['API14'][index]) + str(json_load))
                        log('failed to insert API: ' + str(df['API14'][index]))
                    except:
                        log('failed to insert: #' + str(df.index[index])+ str(json_load))
                    print(payload_format(json.dumps([row.dropna().to_dict()])))


        # execute requests and make inserts into database
        def DI_engine(initial_url, ddl):

            while True:

                try:

                    request = DI_request(initial_url)
                    json_resp = request.json()
                    
                    if not len(json_resp):
                        log('All records successfully inserted, ending job.')
                        break
                    
                    clean_df = clean_json(json_resp, ddl)
                    
                    json_payload = payload_format(json.dumps([row.dropna().to_dict() for index,row in clean_df.iterrows()]))

                    if 'next' in request.links:
                        self.links = request.links

                    try:
                        self.gif_entity.entity_post(self.schema_name, self.entity_name,json_payload)
                    except:
                        gif_connection()
                        self.gif_entity.entity_post(self.schema_name, self.entity_name,json_payload)
                    

                    log('inserted: ' + str(self.links['next']['url']))
                    #log(self.r_headers)

                    process = psutil.Process(os.getpid())
                    print(str(process.memory_info().rss/1000000))
                    
                    log('memory: ' + str(process.memory_info().rss/1000000))
                    
                    

                except:
                    self.gif_conn.close()
                    gif_connection()
                    log('payload failed, inserting single loads..')
                    print('payload failed, inserting single loads..')
                    DI_single_load(clean_df)

                    continue
                    

        def log(message):
            try:
                self.app_log.add_log(message)
            except:
                # if logging fails re-establish connection
                log_connection()
                self.app_log.add_log(message)
        
                    
        try:
            # get token and store into headers
            get_token(self.client_id,self.client_secret)

            # initialize enterprise well info connection
            gif_connection()

            # initialize log connection
            log_connection()

        except:

            logging.info('unable to create initial connections to database or API, try running again')

        
        # first call to make
        initial_url = url_load_type(self.data_service,self.load_type)


        # get DDL into list with column name and data type and add to manual entered data types
        ddl_list = get_ddl(self.data_service) + list(zip(*[iter(self.f_string.split(','))]*2))
   
        # run the api calls and inserts 
        DI_engine(initial_url, ddl_list)
            
        #proc_conn.close()
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    requiredNamed = parser.add_argument_group('required named arguments')

    # API Credentials:
    requiredNamed.add_argument("-ci", action="store", dest="client_id",
                               help="The client id for the API call.", required=True)
    requiredNamed.add_argument("-cs", action="store", dest="client_secret", help="The client secret for the API call.",
                               required=True)
    requiredNamed.add_argument("-ak", action="store", dest="api_key", help="The API key for the API call.",
                               required=True)
    requiredNamed.add_argument("-ds", action="store", dest="data_service", help="The API collection target.",
                               required=True)
    requiredNamed.add_argument("-lt", action="store", dest="load_type", help="full or incremental to indicate type of load",
                               required=True)
    # app Credentials
    requiredNamed.add_argument("-es", action="store", dest="app_server", help="The address for the app SQL Server",
                               required=True)
    requiredNamed.add_argument("-ed", action="store", dest="app_database", help="The database on the app SQL Server",
                               required=True)
    requiredNamed.add_argument("-eu", action="store", dest="app_user", help="The user on the app SQL Server",
                               required=True)
    requiredNamed.add_argument("-ep", action="store", dest="app_password", help="The password on the app SQL Server",
                               required=True)
    # Pylib path
    requiredNamed.add_argument("-py", action="store", dest="pylib", help="Path to PyLib",
                               required=True)

    # Database Arguments
    requiredNamed.add_argument("-sn", action="store", dest="schema_name", help="Schema name within the app SQL Server",
                               required=True)
    requiredNamed.add_argument("-en", action="store", dest="entity_name", help="Table name within the app SQL Server",
                               required=True)
    requiredNamed.add_argument("-fs", action="store", dest="f_string", help="Manual over ride columns to datatype specific",
                               required=True)

    requiredNamed.add_argument("-af", action="store", dest="add_filter", help="Manual over ride columns to datatype specific",
                               required=True)

    requiredNamed.add_argument("-lp", action="store", dest="lag", help="Manual over ride columns to datatype specific",
                               required=False)

    args = parser.parse_args()

    try:
        DrillingInfoIntegrationEngine(args)
    except Exception as e:
        print(e)
        print("Error occurred while executing main block.")

        logging.basicConfig(level=logging.INFO,
                            filename='DrillingInfo_logging_daily.log',
                            filemode='w', format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S')
        logging.info('Error message: ' + str(e))
        sys.exit(1)
    print("End Script")
