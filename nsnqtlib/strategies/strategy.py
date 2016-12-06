# -*- coding:utf-8 -*-
from  nsnqtlib.db.mongodb import MongoDB
import time
import datetime
import pandas as pd
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import random
from nsnqtlib.config import DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME

class basestrategy(object):
    '''
    trading volume is the lowest in 60 days
    '''
    def __init__(self,startdate=(2011, 1, 1),enddate=[]):
        self.startdate = datetime.datetime( *startdate,0,0,0,0)
        self.enddate = enddate
        self.m = MongoDB(DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME)
        self.formatlist = ["date","volume","close","high","low","open","pre_close"]
        self.savevols = ["stock","buy_date","sell_date","holddays","profit"]
        self.looplist = []
        self.trading_records = []
        self.holding_records = []
        self.datalst = []
    
    def setlooplist(self,lst=[]):
        if not lst:
            self.looplist = self.m.getallcollections("ml_security_table")
        else:
            self.looplist = lst
        return 
    
    def _getdata(self,collection="600455.SH",db="ml_security_table"):   
        query = self.m.read_data(db,collection,filt={"date":{"$gt": self.startdate}})
        out = self.formatlist
        return self.formatquery(query,out)
    
    def formatquery(self,query,out):
        '''
        query:your source data ,should be a list with dict
        out:the fields you want to convert into dataframe 
        '''
        if not out:
            query = [i for i in query.sort("date", 1)]
        else:
            query = [{k:i[k] for k in out} for i in query.sort("date", 1)]
        return pd.DataFrame(query)
    
    def buy(self,line,count):
        return False
    
    def sell(self,line,count,holding_record):
        traderecord = []
        return False,traderecord
    
    def setenv(self,collection):
        data = self._getdata(collection)
        self.datalst = [l for l in data[self.formatlist].fillna(0).values if l[1] !=0]
        self.datalst = self.rehabilitation(self.datalst)
        return 
    
    def rehabilitation(self,lst):
        close = lst[0][2]
        c = 1
        reh = []
        for line in lst[1:]:
            c_preclose = line[6]
            if c_preclose != close:
                reh = [[i[0],i[1]*c_preclose/close] for i in reh]
                reh.append([c,c_preclose/close])
            close = line[2]
            c += 1
        result = []
        sc = 0
        for idx in range(len(reh)):
            weight = reh[idx][1]
            ec = reh[idx][0]
            piece = self.recount(lst,sc,ec,weight)
            result.extend(piece)
            sc = ec
        return result
    
    def recount(self,lst,sc,ec,weight):
        rst = []
        for line in lst[sc:ec]:
            rst.append([line[0],line[1],*[i*weight for i in line [2:]]])
        return rst    
    
    def historyreturn(self,collection):
        self.setenv(collection)
        trading_record = []
        holding_record = []
        count = 0
        lst = self.datalst
        for line in lst[:]:
            isbuy = self.buy(lst,count)
            
            for b in holding_record[:]:
                issell,traderecord = self.sell(lst,count,b)
                if issell:
                    holding_record.remove(b)
                    trading_record.append(traderecord)
                    print (traderecord)
            if isbuy:
                holding_record.append(([i for i in line],count,collection))
            count += 1
        return trading_record,holding_record
    
    def looplist_historyreturn(self):
        for collection in self.looplist:
            try:
                tr,hr = self.historyreturn(collection)
                self.trading_records.extend(tr)
                self.holding_records.extend(hr)
            except:
                print ("error: {}".format(collection))
        return self.trading_records,self.holding_records
    
    def savetrading2csv(self,filename="trading_records.csv"):
        df = pd.DataFrame(self.trading_records,columns=self.savevols)
        df.to_csv(filename)
        return
        
    def saveholding2csv(self,filename="holding_records.csv"):
        df = pd.DataFrame(self.holding_records,columns=["date","buy_data","stock"])
        df.to_csv(filename)
        return

class reportforms(object):
    def __init__(self,df):
        '''
        df should be follow this format:"index(title is none)" "stock","buy_date","sell_date","holddays","profit"
        '''
        self.df = df[["stock","buy_date","sell_date","holddays","profit"]]
        self.start = sorted(self.df["buy_date"].values)[0]
        self.end = sorted(self.df["sell_date"].values)[-1]

    def positiongain(self,piece=10):
        '''
        '''
        totalmoney = 100
        leftmoney = 100
        holds = []
        datelist = [i.strftime('%Y-%m-%d') for i in pd.date_range(self.start, self.end)]
        result = {d:[] for d in datelist}
        gains = {d:0 for d in datelist}
        for i in self.df.values:
            buydate = i[1]
            result[buydate].append(i)
        
        for date in datelist:
            currentholdnum = len(holds)
            current_day_could_buy_num = len(result[date])
            if current_day_could_buy_num >=1 and currentholdnum < piece:
                buymoney = leftmoney/(piece-currentholdnum)
                if current_day_could_buy_num + currentholdnum <= piece:
                    leftmoney = leftmoney - buymoney*current_day_could_buy_num
                    holds.extend([(i,buymoney) for i in result[date]])
                else:
                    leftmoney = 0
                    holds.extend([(i,buymoney) for i in random.sample(result[date],piece-currentholdnum)])
            for d in holds[:]:
                sell_date = d[0][2]
                if sell_date >= date : 
                    holds.remove(d)
                    leftmoney += d[1]*(d[0][4]+1)  
                    totalmoney += d[1]*d[0][4]
            gains[date] = totalmoney
            
        newdf = pd.DataFrame(data=[gains[i] for i in datelist], index=datelist,columns=["totalmoney",])
        newdf["date"] = newdf.index
        newdf.plot(x="date", y="totalmoney", kind='area')
        plt.savefig("positiongain_from_{}_to_{}.png".format(self.start,self.end))
#         plt.show()
    
    def cumulative_graph(self,):
        date = [i.strftime('%Y-%m-%d') for i in pd.date_range(self.start, self.end)]
        result = {d:[0,0] for d in date}
        df = self.df
        for i in df.values:
            selldate = i[2]
            gains = i[4]
            result[selldate][0] += gains
            result[selldate][1] += 1
        newdf = pd.DataFrame(data=[[result[i][0],result[i][1]] for i in date], index=date,columns=["profit","buynums"])
        newdf["totalprofit"] = newdf["profit"].cumsum()
        newdf["totalbuys"] = newdf["buynums"].cumsum()
        newdf["averageprofit"] = (newdf["profit"]/newdf["buynums"]).fillna(0)
        newdf["addup_averageprofit"] = newdf["averageprofit"].cumsum().fillna(0)
        newdf["date"] = newdf.index
        newdf.plot(x="date", y="addup_averageprofit", kind='line')
        
        plt.savefig("addup_averageprofit.png")
        
#         plt.show()  

    

if __name__ == '__main__':
    s=basestrategy()
    s.setlooplist()
    for i in s.looplist:
        print (s._getdata(i))




