# -*- coding:utf-8 -*-
from  nsnqtlib.db.mongodb import MongoDB
import threading
import time
import datetime
import sys
import pandas as pd

class strategy1(object):
    '''
    trading volume is the lowest in 60 days
    '''
    def __init__(self,stock="600455.SH"):
        self.m = MongoDB()
    
    def _getdata(self,db="ml_security_table",collection="600455.SH"):   
        query = self.m.read_data(db,collection,filt={"date":{"$gt": datetime.datetime(2013, 1, 1, 0, 0, 0,0)}})
        return self.m.format2dataframe(query)
    
    def mean_volume(self,data):
        m_vol = sum(data)/len(data)
        return m_vol
    
    def buy_condition(self,vol,vol_data,close,last_high,maxprice,minprice,count,vol_weight=1.2):
        if  self.condition1(vol,vol_data,vol_weight) and \
            self.condition2(close,last_high) and \
            self.condition3(close,maxprice) and \
            self.condition4(close,minprice): 
            return True
        return False
    
    def sell_conditon(self,buy_price,currentday_high,currentday_low,hold_days,gain_grads=0.1,loss_grads=-0.05,dayout=10):
        if self.stopgain_condition(buy_price,currentday_high,gain_grads):
            return True,"stopgain"
        elif self.stoploss_condition(buy_price,currentday_low,loss_grads):
            return True,"stoploss"
        elif self.holdingtime_condition(hold_days,dayout):
            return True,"holdtime"
        return False,None
    
    def stopgain_condition(self,buy_price,current_price,grads=0.1):
        if (current_price-buy_price)/buy_price >= grads:
            return True
        return False
    
    def stoploss_condition(self,buy_price,current_price,grads=-0.05):
        if (current_price-buy_price)/buy_price <= grads:
            return True
        return False
    
    def holdingtime_condition(self,hold_days,dayout=10):
        if hold_days >= dayout:
            return True
        return False
    
    def condition1(self,vol,vol_data,vol_weight=1.2):
        if vol >= vol_weight * self.mean_volume(vol_data):
            return True
        return False
    
    def condition2(self,close,last_high):
        if close >= last_high:
            return True
        return False
    
    def condition3(self,close,high,grads=0.2):
        if (high-close)/high >= grads:
            return True
        return False
    
    def condition4(self,close,low,grads=0.05):
        if (close-low)/low <= grads:
            return True
        return False
    
    def histofyreturn(self,db="ml_security_table",table=""):
        buy = []
        stopwin = 0.1
        stoploss = -0.1
        vol_day = 10
        price_day = 60
        df = self._getdata(collection=table)
        count=60
        origindata=[]
        lst = [l for l in df[["date","volume","close","high","low","open","pre_close"]].fillna(0).values if l[1] !=0]
        for line in lst[count:]:
            vol = line[1]
            if vol == 0:continue
            close = line[2]
            last_high = lst[count-1][3]
            vol_data = [i[1] for i in lst[count-vol_day:count]]
            maxprice = max([i[3]] for i in lst[count-price_day:count])[0]
            minprice = min([i[4]] for i in lst[count-price_day:count])[0]
            
            for b in buy[:]:
                d=b[0]
                c=b[1]
                buy_date = d[0]
                sell_date = line[0]
                hold_days = count-c
                buy_price = d[2]
                currentday_high = line[3]
                currentday_low = line[4]
                
                is_sell,selltype = self.sell_conditon(buy_price,currentday_high,currentday_low,\
                                      hold_days,gain_grads=0.1,\
                                      loss_grads=-0.05,dayout=10)
                if is_sell:
                    buy.remove(b)
                    
                    if selltype == "stopgain": 
                        profit = stopwin
                    elif selltype == "stopgain":
                        profit = stoploss
                    else: 
                        profit = (close-buy_price)/buy_price
                    origindata.append([table,buy_date,sell_date,hold_days,profit])
                    print (profit)
            
            if self.buy_condition(vol,vol_data,close,last_high,maxprice,minprice,count,vol_weight=1.2):
                buy.append((line,count))
            count +=1
        return origindata   
            
    def filter_with_all_stocks(self,stocklist):
        error_list = []
        result = [] 
        for i in stocklist:
            try:
                r = self.histofyreturn(table=i) 
                if r:result.extend(r)
            except:
                error_list.append(i)
        return result,error_list


if __name__ == '__main__':
    s=strategy1()
    stocklist = s.m.getallcollections("ml_security_table")
    result,errorlist = s.filter_with_all_stocks(stocklist)
# s.his1tofyreturn(table="600455.SH")
# for i in stocklist:
# #     print (i)  
#     try:
#         r = s.histofyreturn(table=i)
#         if r:result.extend(r)
#     except:
#         pass
#     if stop >=100:
#         print (result)
    df = pd.DataFrame(result,columns=["stock","buy_date","sell_date","holddays","profit"])
    df.to_csv("test1.csv")





