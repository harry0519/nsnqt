# -*- coding:utf-8 -*-
from nsnqtlib.strategies.strategy import  basestrategy

class examplestock(basestrategy):
    '''
           重写买入条件和卖出条件，
    '''
    
    def buy(self,lst,count):
        ''' input:
                line: [] ,row data in every stock data,default is in self.formatlist = ["date","volume","close","high","low","open","pre_close"]
                count: float, the number to the row since first row
            ouput:
                bool, can buy or not buy
                [], buy record,if can't buy,is empty list
        '''
        vol_day = 10
        price_day = 60
        vol_weight = 1.2
        vol = lst[count][1]
        close = lst[count][2]
#         high = lst[count][3]
#         low = lst[count][4]
#         open = lst[count][5]
#         pre_close = lst[count][6]
        vol_data = [i[1] for i in lst[count-vol_day:count]]
        maxprice = max([i[3]] for i in lst[count-price_day:count])[0]
        minprice = min([i[4]] for i in lst[count-price_day:count])[0]
        maxindex = [ i for i in range(count-price_day,count) if lst[i][3] == maxprice][0]
        
        if  self.buy_condition1(vol,vol_data,vol_weight) and \
            self.buy_condition2(close,lst[count-1][3]) and \
            self.buy_condition3(close,maxprice) and \
            self.buy_condition4(close,minprice) and \
            self.buy_condition5(count,maxindex): 
            return True
        return False
    
    def sell(self,lst,count,buyrecord):
        currentday_high = lst[count][3]
        gain_grads = 0.1
        loss_grads = -0.05
        dayout = 10
        currentday_low = lst[count][4]
        sell_date = lst[count][0]
        close = lst[count][2]
        
        buy_price = buyrecord[0][2]
        hold_days = count - buyrecord[1]
        buy_date = buyrecord[0][0]
        collection = buyrecord[2]
        
        if self.stopgain_condition(buy_price,currentday_high,gain_grads):
            return True,[collection,buy_date,sell_date,hold_days,gain_grads]
        
        elif self.stoploss_condition(buy_price,currentday_low,loss_grads):
            return True,[collection,buy_date,sell_date,hold_days,(close-buy_price)/buy_price]
        
        elif self.holdingtime_condition(hold_days,dayout):
            return True,[collection,buy_date,sell_date,hold_days,(close-buy_price)/buy_price]
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
    
    def mean_volume(self,data):
        m_vol = sum(data)/len(data)
        return m_vol
    
    def buy_condition1(self,vol,vol_data,vol_weight=1.2):
        if vol >= vol_weight * self.mean_volume(vol_data):
            return True
        return False
    
    def buy_condition2(self,close,last_high):
        if close >= last_high:
            return True
        return False
    
    def buy_condition3(self,close,high,grads=0.2):
        if (high-close)/high >= grads:
            return True
        return False
    
    def buy_condition4(self,close,low,grads=0.05):
        if (close-low)/low <= grads:
            return True
        return False
    
    def buy_condition5(self,currentday,highday,grads=60):
        if currentday - highday  >= grads:
            return True
        return False
    
if __name__ == '__main__':
    pass