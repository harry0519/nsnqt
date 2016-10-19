# -*- coding:utf-8 -*-
# Author:harry
# Editdate:2016-10-05
# coding: utf-8
from pymongo import MongoClient
import pandas as pd
import nsnqtlib.db.fields
from nsnqtlib.db.base  import BaseDB
from nsnqtlib.config import DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME
 
class MongoDB(BaseDB):
    def __init__(self,ip=DB_SERVER, 
                     port=DB_PORT, 
                     user_name=USER, 
                     pwd=PWD,
                     authdb=AUTHDBNAME):
        self.__server_ip = ip
        self.__server_port = port
        self.__user_name = user_name
        self.__pwd = pwd
        self.__authdb = authdb
        super(MongoDB,self).__init__(ip=ip,port=port,user_name=user_name,pwd=pwd,authdb=authdb)
        self.client = self.connect()
    
    def getallcollections(self,db="ml_security_table"):
        cls = [i for i in eval("self.client.{}".format(db)).collection_names()]
        return cls
    
    def read_data(self,db,collection,filt={}): 
        '''
        colections:  collection in mongodb ,which your want to get data from
        filt: filter condition
        '''
        db = eval("self.client.{}".format(db))
        return db[collection].find(filt)
    
    def format2dataframe(self,query,out=[]):
        '''
        query:your source data ,should be a list with dict
        out:the fields you want to convert into dataframe 
        '''
        if not out:
            query = [i for i in query]
        else:
            query = [{k:i[k] for k in out} for i in query]
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


    def save_data(self, db_name, table_name, dataset, fields):
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
