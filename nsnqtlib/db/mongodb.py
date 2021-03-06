# -*- coding:utf-8 -*-
# Author:harry
# Editdate:2016-10-05
# coding: utf-8
from pymongo import MongoClient
import pandas as pd
import nsnqtlib.db.fields
from nsnqtlib.db.base  import BaseDB
from nsnqtlib.servers.serverlist import *
from nsnqtlib.config import DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME
import sys
import time
from time import clock
import logging

class MongoDB(BaseDB):
    def init_log(self):
        self.dblogger = logging.getLogger()
        self.dblogger.setLevel(logging.DEBUG)

        fh = logging.FileHandler('log/dbupdate.log')   
        ch = logging.StreamHandler() 

        formatter = logging.Formatter('[%(asctime)s][%(filename)s] %(message)s')  
        fh.setFormatter(formatter)  
        ch.setFormatter(formatter) 
        dblogger.addHandler(fh)  
        dblogger.addHandler(ch)
    def __init__(self,ip=LOCAL_SERVER_IP, 
                     port=LOCAL_MONGODB_PORT, 
                     user_name=None, 
                     pwd=None,
                     authdb=None):
        self.__server_ip = ip
        self.__server_port = port
        self.__user_name = user_name
        self.__pwd = pwd
        self.__authdb = authdb
        super(MongoDB,self).__init__(ip=ip,port=port,user_name=user_name,pwd=pwd,authdb=authdb)
        self.client = self.connect()

    def print_config(self):
        print("ip=%s:%s,user_name=%s,pwd=%s,authdb=%s" %(self.__server_ip,self.__server_port,\
            self.__user_name,self.__pwd,self.__authdb))

    def getallcollections(self,db="ml_security_table"):        
        cls = [i for i in eval("self.client.{}".format(db)).collection_names()]
        return cls

    def dropcollection(self,collection,db="ml_security_table"):
        print(collection)
        db = eval("self.client.{}".format(db))
        return db[collection].drop()

    def read_data(self,db,collection,filt={},is_aggregate=False): 
        '''
        colections:  collection in mongodb ,which your want to get data from
        filt: filter condition,when is_aggregate is True ,filt could be a list or dict
        '''
        db = eval("self.client.{}".format(db))
        if is_aggregate:
            return db[collection].aggregate(filt)
        else:
            return db[collection].find(filt)
    
    def update_data(self,data,db,collection,filt={},isupsert=False): 
        '''
        colections:  collection in mongodb ,which your want to get data from
        filt: filter condition
        '''
        db = eval("self.client.{}".format(db))
        bulk = db[collection].initialize_ordered_bulk_op()
        if isupsert:
            bulk.find(filt).upsert().update(data)
        else:
            bulk.find(filt).update(data)
        bulk.execute()
        return 
    
    def format2dataframe(self,query,out=[]):
        '''
        query:your source data ,should be a list with dict
        out:the fields you want to convert into dataframe 
        '''
        if not out:
            query = [i for i in query.sort("date", 1)]
        else:
            query = [{k:i[k] for k in out} for i in query.sort("date", 1)]
        return pd.DataFrame(query)
    
    def connect(self):
        _db_session = MongoClient(self.__server_ip, self.__server_port)
        if  self.__user_name:        
            eval("_db_session.{}".format(self.__authdb)).authenticate(self.__user_name,self.__pwd)      
        
        print("connected to {}".format(self.__server_ip))
        return _db_session

    def disconnect(self):
        self._db_session.close()
        return True

    def save_nav(self, db_name, collection,fields,data_set,show_progress=False):
        db = eval("self.client.{}".format(db_name))
        record_num = len(data_set.Data[0])
        if record_num > 500:
            show_progress = True
             
        if show_progress:
            start = clock()  
            sys.stdout.write("Writing %s: %d/%d \r" %(collection,0,record_num))

        for j in range(record_num):
            table_set = db[collection]
            if show_progress and j % 10 == 0:
                sys.stdout.write("Writing %s: %d/%d \r" %(collection,j,record_num))
            table_set.update_one({"date":data_set.Times[j]},
                {"$set":{ 
                    "nav":data_set.Data[0][j]}}, upsert=True)   
         
        if show_progress:
            finish = clock()
            print("\nUpload complete in %.2fs" %(finish-start))
        return True

    def save_ab(self, db_name, collection,fields,data_set,show_progress=False):        
        #print("===Saving %s to %s @%s===" %(collection,db_name,self.__server_ip))
        db = eval("self.client.{}".format(db_name))
        record_num = len(data_set.Data[0])
        if record_num > 500:
            show_progress = True
             
        if show_progress:
            start = clock()  
            sys.stdout.write("Writing %s: %d/%d \r" %(collection,0,record_num))

        for j in range(record_num):
            table_set = db[collection]
            if show_progress and j % 10 == 0:
                sys.stdout.write("Writing %s: %d/%d \r" %(collection,j,record_num))
            table_set.update_one({"date":data_set.Times[j]},
                {"$set":{ 
                    "pre_close":data_set.Data[0][j],
                    "open":data_set.Data[1][j],
                    "high":data_set.Data[2][j],
                    "low":data_set.Data[3][j],
                    "close":data_set.Data[4][j],
                    "volume":data_set.Data[5][j],
                    "amt":data_set.Data[6][j],
                    "dealnum":data_set.Data[7][j],
                    "nav":data_set.Data[8][j]}}, upsert=True)   
         
        if show_progress:
            finish = clock()
            print("\nUpload complete in %.2fs" %(finish-start))
        return True
    def save_stock(self, db_name, collection,fields,data_set,show_progress=False):        
        #print("===Saving %s to %s @%s===" %(collection,db_name,self.__server_ip))
        
        db = eval("self.client.{}".format(db_name))
        record_num = len(data_set.Data[0])
        if record_num > 500:
            show_progress = True
             
        if show_progress:
            start = clock()  
            sys.stdout.write("Writing %s: %d/%d \r" %(collection,0,record_num))

        for j in range(record_num):
            table_set = db[collection]
            if show_progress and j % 10 == 0:
                sys.stdout.write("Writing %s: %d/%d \r" %(collection,j,record_num))
            table_set.update_one({"date":data_set.Times[j]},
                {"$set":{ 
                    "pre_close":data_set.Data[0][j],
                    "open":data_set.Data[1][j],
                    "high":data_set.Data[2][j],
                    "low":data_set.Data[3][j],
                    "close":data_set.Data[4][j],
                    "volume":data_set.Data[5][j],
                    "amt":data_set.Data[6][j],
                    "dealnum":data_set.Data[7][j]}}, upsert=True)   
         
        if show_progress:
            finish = clock()
            print("\nUpload complete in %.2fs" %(finish-start))
        return True
    def save_data(self, db_name, collection,fields,data_set,show_progress=False):        
        #print("===Saving %s to %s @%s===" %(collection,db_name,self.__server_ip))
        
        if db_name == "ab_etf":
            db_name = "ab"
            self.save_nav(db_name, collection,fields,data_set,show_progress)
        elif db_name == "ab":
            self.save_ab(db_name, collection,fields,data_set,show_progress)
        else:
            self.save_stock(db_name, collection,fields,data_set,show_progress)
    
        return True

#     def save_future_data_to_mdb(self,data_set,table_map,table_name):
#         print("===Start to save data to mongodb===")
#         db = db_client.future
#          
#         for j in range(len(data_set.Data[0])):
#             table_map.get(table_name).update_one({"date":data_set.Times[j]},
#                 {"$set":{ 
#                     "pre_close":data_set.Data[0][j],
#                     "open":data_set.Data[1][j],
#                     "high":data_set.Data[2][j],
#                     "low":data_set.Data[3][j],
#                     "close":data_set.Data[4][j],
#                     "volume":data_set.Data[5][j],
#                     "amt":data_set.Data[6][j],
#                     "oi":data_set.Data[7][j]}}, upsert=True)   
#          
#         print("data have been saved to mongodb")
#  
#     def save_stock_data_to_mdb(self,data_set,table_name):
#         print("===Start to save data to mongodb===")
#         db_engine = db_client = MongoClient(server_ip, server_port)
#         db = db_engine.ml_security_table
#          
#         for j in range(len(data_set.Data[0])):
#             table_set = db[table_name]
#             table_set.update_one({"date":data_set.Times[j]},
#                 {"$set":{ 
#                     "pre_close":data_set.Data[0][j],
#                     "open":data_set.Data[1][j],
#                     "high":data_set.Data[2][j],
#                     "low":data_set.Data[3][j],
#                     "close":data_set.Data[4][j],
#                     "volume":data_set.Data[5][j],
#                     "amt":data_set.Data[6][j],
#                     "dealnum":data_set.Data[7][j]}}, upsert=True)   
#          
#         print("data have been saved to mongodb")
#         disconnect_to_mdb(db_engine)
#          
#     def save_fund_data_to_mdb(self,data_set,table_name):
#         print("===Start to save data to mongodb===")
#         db_engine = connect_to_remote()
#         db = db_engine.ml_fund_table
#          
#         for j in range(len(data_set.Data[0])):
#             table_set = db[table_name]
#             table_set.update_one({"date":data_set.Times[j]},
#                 {"$set":{ 
#                     "pre_close":data_set.Data[0][j],
#                     "open":data_set.Data[1][j],
#                     "high":data_set.Data[2][j],
#                     "low":data_set.Data[3][j],
#                     "close":data_set.Data[4][j],
#                     "volume":data_set.Data[5][j],
#                     "amt":data_set.Data[6][j]}}, upsert=True)   
#          
#         print("data have been saved to mongodb")
#         disconnect_to_mdb(db_engine)



####################test code    ########################## 
# m=MongoDB()
# query = m.read_data("ml_security_table","stock")[2]
# print(query)
# print(m.format2dataframe(query))
