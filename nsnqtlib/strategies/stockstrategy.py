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
    
    def histofyreturn(self,db="ml_security_table"):
        stocklist = self.m.getallcollections(db)
        df = self._getdata()
        print(df.ndim)
#         data = [i for i in self._getdata().sort("date").values]
#         for i in range(len(data)-60):
#             print(i)
#         print(self._getdata())
    
        
            
    
        
        
s=strategy1()
s.histofyreturn()