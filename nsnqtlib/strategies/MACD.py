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
    
    def getcurrentdata(self):
        '''code：代码, name:名称 ,changepercent:涨跌幅 , trade:现价 ,open:开盘价 ,high:最高价, low:最低价, settlement:昨日收盘价 ,
           volume:成交量 ,turnoverratio:换手率 ,amount:成交量 ,per:市盈率 ,pb:市净率, mktcap:总市值 ,nmc:流通市值
        '''
        out = ["code","trade","open","high","low","settlement"]
        rst = ts.get_today_all()
        return rst[out].set_index('code')
    
    def gettradebuylst(self):
        dbname = "stockdatas"
        num = 1
        emaslow  = 26
        emafast = 12
        demday = 9
        filt = [{"$sort":{"date":-1}},{"$limit":num}]
        buylst = []
        currentdata = self.getcurrentdata()
        for i in self.looplist:
            collection = i
            query = self.db.read_data(dbname,collection,filt,is_aggregate=True)
            data = [i for i in query]
            s_ema = data[0]["ema26"]
            f_ema = data[0]["ema12"]
            dem = data[0]["dem9"]
            macd = data[0]["macd"]
            try:
                c_close = currentdata["trade"].ix[collection.split(".")[0]]
            except:
                print ("error stock:{}".format(collection))
                continue
            n_s_ema = (s_ema*(emaslow-1)+ 2*c_close)/(emaslow+1)
            n_f_ema = (f_ema*(emafast-1)+ 2*c_close)/(emafast+1)
            n_diff = n_f_ema-n_s_ema
            n_dem = (dem*(demday-1)+ 2*n_diff)/(demday+1)
            n_macd = 2*(n_diff-n_dem)
            if macd*n_macd < 0 and n_macd >0:
                buylst.append(collection)
        [print ("buylist:{}".format(collection)) for  collection in buylst]
        return buylst
    
    def save2db(self):
        pass
    
    def save2csv(self):
        pass
    

        
if __name__ == '__main__':
    s = macd()
    s.setlooplist()
#     s.getlastbuylst()
    s.gettradebuylst()
    
#     s.gethistorybuylst()
     









