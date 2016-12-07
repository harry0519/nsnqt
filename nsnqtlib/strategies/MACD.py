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
        super(macd,self).__init__(startdate,enddate)
    
    def buy(self,lst,count):
        ''' input:
                lst: [] ,row data in every stock data,default is in self.formatlist = ["date","volume","close","high","low","open","pre_close"]
                count: float, the number to the row since first row
            ouput:
                bool, can buy or not buy
                [], buy record,if can't buy,is empty list
        '''
        if self.buy_condition1(count) and \
            self.buy_condition2(count) and self.status:
            self.status = False
            return True
        return False
    
    def buy_condition1(self,count):
        if self.macdlist[count]>0 and \
            self.macdlist[count-1]<0:
            return True 
        if self.macdlist[count]<0 and \
            self.macdlist[count-1]>0:
            self.status = True
        return False
    
    def buy_condition2(self,count):
        if self.difflist[count] <0 :
            return True
        return False
    
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
        
        if self.stopgain_condition(buy_price,currentday_high,gain_grads):
            return True,[collection,buy_date,sell_date,hold_days,gain_grads]
        elif self.stoploss_condition(buy_price,currentday_low,loss_grads):
            return True,[collection,buy_date,sell_date,hold_days,(close-buy_price)/buy_price]
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
    report.positiongain(200)
    









