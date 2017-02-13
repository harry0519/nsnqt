# -*- coding:utf-8 -*-
import pandas as pd
import tushare as ts
import traceback
from nsnqtlib.config import DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME
from nsnqtlib.db.mongodb import MongoDB


class macd(object):
    '''
           ��д��������������������
    '''
    def __init__(self):
        self.db = MongoDB(DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME)
        self.looplist = []
    
    def setlooplist(self,lst=[]):
        excludelst = ["399001.SZ","399006.SZ","000001.SH","000300.SH","399005.SZ"]
        if not lst:
            self.looplist = [i for i in self.db.getallcollections("stockdatas") if i not in excludelst]
        else:
            self.looplist = lst
        return self.looplist
    
    def buycondition(self,data):
        '''out = ["macd","cross_dist"]'''
        if data["macd"] > 0 and data["cross_dist"] == 0 \
            and data["diff12_26"] < 0:
            return True
        return False
    
    def enhancebuycondition(self,data):
        if data["macd"] < 0 and data["diff12_26"] < 0:
            return True
        return False
    
    def sellcondition(self,data):
        pass
    
    def getlastbuylst(self,):
        dbname = "stockdatas"
        num = 1
        filt = [{"$sort":{"date":-1}},{"$limit":num}]
        buylst = []
        enhancebuylst = []
        for i in self.looplist:
            collection = i
            query = self.db.read_data(dbname,collection,filt,is_aggregate=True)
            data = [i for i in query]
            if self.buycondition(data[0]): 
                buylst.append(i)
#                 print ("normal condition buy stock:{}".format(i))
                query = self.db.read_data(dbname,collection,[{"$sort":{"date":-1}},{"$match":{"cross_dist":0,"macd":{"$ne":0}}},{"$limit":2}],is_aggregate=True)
                newdata = [i for i in query]
                if self.enhancebuycondition(newdata[1]):
                    enhancebuylst.append(i)
                    print ("enhance condition buy stock:{}".format(i))
        return buylst,enhancebuylst
    
    def gethistorybuylst(self,starttime="2011-01-01"):
        dbname = "stockdatas"
        filt = [{"$sort":{"date":1}},{"$match":{"date":{"$gt":starttime}}}]
        buylst = []
        enhancebuylst = []
        for i in self.looplist:
            collection = i
            query = self.db.read_data(dbname,collection,filt,is_aggregate=True)
            data = [i for i in query]
            for record in data:
                if self.buycondition(record):
                    buylst.append([i,record["date"],record["close"]])
#                     print ([i,record["date"],record["close"]])
                    idx = data.index(record)
                    precross = idx - data[idx-1]["cross_dist"] - 1
                    if precross >= 0 and self.enhancebuycondition(data[precross]):
                        enhancebuylst.append(i)
                        print ([i,record["date"],record["close"]])
            
        return buylst,enhancebuylst
    
    def gettraderecord(self,starttime="2011-01-01"):
        
        pass
    
    def save2db(self):
        pass
    
    def save2csv(self):
        pass
    

        
if __name__ == '__main__':
    s = macd()
    s.setlooplist()
    s.getlastbuylst()
#     s.gethistorybuylst()
     









