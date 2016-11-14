# -*- coding:utf-8 -*-
from  nsnqtlib.db.mongodb import MongoDB
import threading
import time
import datetime
import math
DATES = []
HOLDS=[]
RESULTS=[]

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
    
    def max_price(self):
        pass
    
    def min_price(self):
        pass
    
    def histofyreturn(self,db="ml_security_table",table=""):
        buy = []
        vol_a = 1.2
        vol_day = 10
        price_day = 60
        df = self._getdata(collection=table)
        count=60
        origindata=[]
        lst = [l for l in df[["date","volume","close","high","low","open","pre_close"]].fillna(0).values if l[1] !=0]
        for line in lst[count:]:
            if line[1] == 0:continue
            vol_data = [i[1] for i in lst[count-vol_day:count]]
            maxprice = max([i[3]] for i in lst[count-price_day:count])[0]
            minprice = min([i[4]] for i in lst[count-price_day:count])[0]
            for b in buy:
                d=b[0]
                c=b[1]
                if (line[3]-d[2])/d[2]>=0.1:
                    buy.remove(b)
                    print (0.1)
#                     print (0.1)
                    RESULTS.append(0.1)
                elif count-c >=10:
                    buy.remove(b)
                    print ((line[2]-d[2])/d[2])
                elif (line[4]-d[2])/d[2]<=-0.05:
                    buy.remove(b)
                    print (-0.05)
            
            if line[1] >= vol_a * self.mean_volume(vol_data)and line[2]>=lst[count-1][3] \
            and (maxprice-line[2])/maxprice >=0.2 and (line[2]-minprice)/minprice<=0.05:
                buy.append((line,count))
            count +=1
            
#         print (table)
#         print (holding)
            
    def getnewindex(self,datas,newdata,l,base=0):
        '''datas:should be sorted from min to max,
           newdats: the data need to check the position in the sorted datas
           l:len of data
           base:first position of the datas in origin datas
        '''
        index = int(l/2)
        if datas[index] > newdata:
            if l==1:return base
            d = datas[:index]
            nl = index
            return self.getnewindex(d,newdata,nl,base)
        elif datas[index] < newdata:
            if l<=2:return base+l
            d = datas[index+1:] 
            nl = int((l-1)/2)
            return self.getnewindex(d,newdata,nl,base+index+1)
        elif datas[index] == newdata:
            return base+index    
    
            
s=strategy1()
stocklist = s.m.getallcollections("ml_security_table")
# s.histofyreturn(table="600455.SH")
for i in stocklist:
#     print (i)  
    try:
        s.histofyreturn(table=i)
    except:
        pass
    
# 
# print (len(set(DATES)))
# print (sum(HOLDS)/len(HOLDS))





