# coding: utf-8
'''
Created on 2016年10月13日

@author: 04yyl
'''
from db.mdb import mdb
import pandas as pd
class Query(mdb):
    '''
    Query data from mongodb on server
    '''

    def get_ml_security_table(self,db,collection,filt={}): 
        '''
        colections:  collection in mongodb ,which your want to get data from
        filt: filter condition
        '''
        db = eval("self.client.{}".format(db))
        return db[collection].find(filt)
    
    def formatdata(self,query,out=[]):
        '''
        query:your source data ,should be a list with dict
        out:the fields you want to convert into dataframe 
        '''
        if not out:
            query = [i for i in query]
        else:
            query = [{k:i[k] for k in out} for i in query]
        return pd.DataFrame(query)

# query = Query()
# print(query.formatdata(query.get_ml_security_table("ml_security_table","600789.SH"),["date"]))




    
    
    
        
        
        
                    
        
