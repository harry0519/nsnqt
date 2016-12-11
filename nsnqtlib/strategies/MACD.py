# -*- coding:utf-8 -*-
from nsnqtlib.strategies.strategy import  basestrategy,reportforms
import pandas as pd

class macd(basestrategy):
    '''
           ��д��������������������
    '''
    
    def __init__(self,startdate=(2011, 1, 1),enddate=[],emafast=12,emaslow=26,demday=9):
        self.emafast = emafast
        self.emaslow = emaslow
        self.demday = demday
        self.status = False
        self.count = 0
        self.gain_grads = 0.1
        self.loss_grads = -0.05
        
        super(macd,self).__init__(startdate,enddate)
    
    def buy(self,lst,count):
        ''' input:
                lst: [] ,row data in every stock data,default is in self.formatlist = ["date","volume","close","high","low","open","pre_close"]
                count: float, the number to the row since first row
            ouput:
                bool, can buy or not buy
                [], buy record,if can't buy,is empty list
        '''
        
        rst = False
        if self.buy_condition1(count) and \
            self.buy_condition2(count) and self.status:
            rst = True
        self.setstatus(lst,count)
        return rst
    
    def buy_condition1(self,count):
        if self.macdlist[count]>0 and \
            self.macdlist[count-1]<0:
            return True 
        return False
    
    def buy_condition2(self,count):
        if self.difflist[count] <0 :
            return True
        return False
    
    def setstatus(self,lst,count):
        if self.macdlist[count]<0 and \
            self.macdlist[count-1]>0:
            self.status = True
            self.count = count
        elif self.macdlist[count]>0 and \
            self.macdlist[count-1]<0:
            self.status = False
        elif self.difflist[count] > 0 or self.demlist[count] >0 :
            self.status = False
            
    def getstocktype(self):
        if self.collection.startswith("300"):
            return [1,0,0,0]
        elif self.collection.startswith("002"):
            return [0,1,0,0]
        elif self.collection.startswith("000"):
            return [0,0,1,0]
        else:
            return [0,0,0,1]
    
    def mean(self,lst):
        total=0
        for i in lst:
            total += i[1]
        return total/len(lst)
            
    
    def getfeatures(self,lst,count):
        """
        MACD最小值   上一轮MACD小于0的天数   股票类型  换手率比值(前一交易日) 换手率比值（前二交易日） 换手率比值（前十天均值）
        """
        minmacd = min(self.macdlist[self.count:count])
        days = count - self.count
        stocktype = self.getstocktype()
        trading_rate1 = lst[count][1]/lst[count-1][1]
        trading_rate2 = lst[count][1]/lst[count-2][1]
        trading_rate10 = lst[count][1]/self.mean(lst[count-10:count])
        return [minmacd,days,*stocktype,trading_rate1,trading_rate2,trading_rate10]
    
    def sell(self,lst,count,buyrecord):
        sell_date = self.timestamp2date(lst[count][0])
        close = lst[count][2]
        currentday_high = lst[count][3]
        currentday_low = lst[count][4]
        gain_grads = 0.1
        loss_grads = -0.05
        buy_price = buyrecord[0][2]
        hold_days = count - buyrecord[1]
        buy_date = self.timestamp2date(buyrecord[0][0])
        collection = buyrecord[2]
        feature = buyrecord[3]
        if self.sell_condition(lst,count):
            return True,[collection,buy_date,sell_date,hold_days,(close-buy_price)/buy_price,feature]
        
#         if self.stopgain_condition(buy_price,currentday_high,gain_grads):
#             return True,[collection,buy_date,sell_date,hold_days,gain_grads,feature]
#         elif self.stoploss_condition(buy_price,currentday_low,loss_grads):
#             return True,[collection,buy_date,sell_date,hold_days,(close-buy_price)/buy_price,feature]
        return False,None
    
    def timestamp2date(self,timestamp):
        try:
            return str(timestamp).split(" ")[0]
        except:
            return timestamp
    
    def sell_condition(self,lst,count):
        meanday = 5
        close = lst[count][2] 
        meanlist = [i[2] for i in lst[count-meanday+1:count+1]]
        if close <= sum(meanlist)/meanday:
            return True
        return False
    
    def stopgain_condition(self,buy_price,current_price,grads=0.1):
        if (current_price-buy_price)/buy_price >= grads:
            return True
        return False
    
    def stoploss_condition(self,buy_price,current_price,grads=-0.05):
        if (current_price-buy_price)/buy_price <= grads:
            return True
        return False
    
    def setenv(self,collection):
        self.collection = collection
        data = self._getdata(collection)
        self.datalst = [l for l in data[self.formatlist].fillna(0).values if l[1] !=0]
        self.datalst = self.rehabilitation(self.datalst)
        self.setmacdlist(self.datalst)
        return
    
    def setmacdlist(self,lst):
        s_ema = f_ema = lst[0][2]
        dem = 0
        self.difflist = []
        self.demlist = []
        self.macdlist = []
        for line in lst:
            s_ema = (s_ema*(self.emaslow-1)+ 2*line[2])/(self.emaslow+1)
            f_ema = (f_ema*(self.emafast-1)+ 2*line[2])/(self.emafast+1)
            dif = f_ema-s_ema
            self.difflist.append(dif)
           
            dem = (dem*(self.demday-1)+ 2*dif)/(self.demday+1)
            self.demlist.append(dem)
            self.macdlist.append(2*(dif-dem))
        
if __name__ == '__main__':
    s = macd()
    s.setlooplist()
    s.looplist_historyreturn()
    s.savetrading2csv("macd.csv")
    s.saveholding2csv("macdhold.csv")
    df = pd.read_csv('macd.csv')
    report = reportforms(df)
    report.cumulative_graph()
    report.positiongain(100)
    









