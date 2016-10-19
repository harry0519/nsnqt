# -*- coding:utf-8 -*-
from  nsnqtlib.db.mongodb import MongoDB

class strategy1(object):
    '''
    trading volume is the lowest in 60 days
    '''
    def __init__(self,stock="600455.SH"):
        self.m = MongoDB()
    
    def _getdata(self,db="ml_security_table",collection="600455.SH"):   
        query = self.m.read_data(db,collection)
        return self.m.format2dataframe(query)
        
        
s=strategy1()
print(s._getdata())