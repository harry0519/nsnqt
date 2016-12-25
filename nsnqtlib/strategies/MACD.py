# -*- coding:utf-8 -*-
from nsnqtlib.strategies.strategy import  basestrategy,reportforms
import pandas as pd
import tushare as ts
import traceback

class macd(basestrategy):
    '''
           ��д��������������������
    '''
    
    def __init__(self,startdate=(2016, 1, 1),enddate=[],emafast=12,emaslow=26,demday=9):
        self.emafast = emafast
        self.emaslow = emaslow
        self.demday = demday
        self.tempstatus = []
        self.procedurevol = ["stock","date","data","s_ema","f_ema","diff","dem","macd","status"]
        self.status = False
        self.count = 0
        self.gain_grads = 0.1
        self.loss_grads = -0.10
        
        super(macd,self).__init__(startdate,enddate)
    
    def setprocedure(self,lst,count):
        status = self.status
        dem = self.demlist[count]
        macd = self.macdlist[count]
        diff = self.difflist[count]
        s_ema = self.s_ema[count]
        f_ema = self.f_ema[count]
        data = lst[count]
        data[0] = self.timestamp2date(data[0])
        self.tempstatus = [self.collection,data[0],data,s_ema,f_ema,diff,dem,macd,status]
        
    def buy(self,lst,count):
        ''' input:
                lst: [] ,row data in every stock data,default is in self.formatlist = ["date","volume","close","high","low","open","pre_close"]
                count: float, the number to the row since first row
            ouput:
                bool, can buy or not buy
                [], buy record,if can't buy,is empty list
        '''
        self.setprocedure(lst,count)
        rst = False
        if self.buy_condition1(count) and \
            self.buy_condition2(count) and self.status :
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
    
    def buy_condition3(self,count):
        if self.difflist[count]>self.precross:
            return True
        return False
    
    def setstatus(self,lst,count):
        if self.macdlist[count]<0 and \
            self.macdlist[count-1]>0:
            self.status = True
            self.count = count
            self.precross = self.difflist[count]
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
        try:
            trading_rate10 = lst[count][1]/self.mean(lst[count-10:count])
        except:
            trading_rate10 = (trading_rate2 + trading_rate1)/2
        return [minmacd,days,*stocktype,trading_rate1,trading_rate2,trading_rate10]
    
    def sell(self,lst,count,buyrecord):
        sell_date = self.timestamp2date(lst[count][0])
        close = lst[count][2]
        currentday_high = lst[count][3]
        currentday_low = lst[count][4]
        gain_grads = self.gain_grads
        loss_grads = self.loss_grads
        buy_price = buyrecord[0][2]
        hold_days = count - buyrecord[1]
        buy_date = self.timestamp2date(buyrecord[0][0])
        collection = buyrecord[2]
        feature = buyrecord[3]
#         if self.sell_condition(lst,count):
#             return True,[collection,buy_date,sell_date,hold_days,(close-buy_price)/buy_price,feature]
        
        if self.stopgain_condition(buy_price,currentday_high,gain_grads):
            return True,[collection,buy_date,sell_date,hold_days,gain_grads,feature]
        elif self.stoploss_condition(buy_price,currentday_low,loss_grads):
            return True,[collection,buy_date,sell_date,hold_days,(close-buy_price)/buy_price,feature]
        return False,None
    
    def sell_condition(self,lst,count):
        meanday = 20
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
        self.precross = -1000
        return
    
    def setmacdlist(self,lst):
        s_ema = f_ema = lst[0][2]
        dem = 0
        self.difflist = []
        self.demlist = []
        self.macdlist = []
        self.s_ema = []
        self.f_ema = []
        
        for line in lst:
            s_ema = (s_ema*(self.emaslow-1)+ 2*line[2])/(self.emaslow+1)
            f_ema = (f_ema*(self.emafast-1)+ 2*line[2])/(self.emafast+1)
            dif = f_ema-s_ema
            self.difflist.append(dif)
            self.s_ema.append(s_ema)
            self.f_ema.append(f_ema)
           
            dem = (dem*(self.demday-1)+ 2*dif)/(self.demday+1)
            self.demlist.append(dem)
            self.macdlist.append(2*(dif-dem))

    def saveprocedure(self,filename="procedure_records.csv"):
        df = pd.DataFrame(self.lateststatus,columns=self.procedurevol)
        df.to_csv(filename)
        return 
    
    def saveprocedure2db(self,db="macd",collection="processstatus"):
        self.lateststatus
        db = eval("self.m.client.{}".format(db))
        bulk = db[collection].initialize_ordered_bulk_op()
        for line in self.lateststatus:
            bulk.find({'stock': line[0]}).upsert().update(\
                                                          {'$set': {'date': line[1],\
                                                                    'data': line[2],\
                                                                    's_ema': line[3],\
                                                                    'f_ema': line[4],\
                                                                    'diff': line[5],\
                                                                    'dem': line[6],\
                                                                    'macd': line[7],\
                                                                    'status': line[8],\
                                                                    }})
        bulk.execute()
        return
    
    def getprocedure(self,filename="procedure_records.csv",isdb=False,collection="processstatus",db="macd"):
        '''"stock","date","data","s_ema","f_ema","diff","dem","macd","status"
        '''
        buy = []
        out=["stock","date","data","s_ema","f_ema","diff","dem","macd","status"]
        if isdb:
            df = self._getdata(collection, db,out=out,isfilt = False)[out]
        else:
            df = pd.read_csv(filename)[out]
        currentdata = { i[0]:i for i in self.getcurrentdata().values}
        for i in df[df.status == True].values:
            try:
                stock = i[0].split(".")[0]
                s_ema = i[3]
                f_ema = i[4]
                macd = i[7]
                dem = i[6]
                close = i[2][2]
                c_close = currentdata[stock][1]
                
                n_s_ema = (s_ema*(self.emaslow-1)+ 2*c_close)/(self.emaslow+1)
                n_f_ema = (f_ema*(self.emafast-1)+ 2*c_close)/(self.emafast+1)
                n_diff = n_f_ema-n_s_ema
                n_dem = (dem*(self.demday-1)+ 2*n_diff)/(self.demday+1)
                n_macd = 2*(n_diff-n_dem)
                if n_macd >0 and macd <0 and n_diff<0:
                    buy.append(stock) 
            except:
                traceback.print_exc()
                print (i)
        return buy
            
            
            
    def getcurrentdata(self):
        '''code：代码, name:名称 ,changepercent:涨跌幅 , trade:现价 ,open:开盘价 ,high:最高价, low:最低价, settlement:昨日收盘价 ,
           volume:成交量 ,turnoverratio:换手率 ,amount:成交量 ,per:市盈率 ,pb:市净率, mktcap:总市值 ,nmc:流通市值
        '''
        out = ["code","trade","open","high","low","settlement"]
        rst = ts.get_today_all()
        return rst[out]
    
    
    
class realtimecheck():
    def __init__(self,df):
        """df: "stock","date","data","s_ema","f_ema","diff","dem","macd","status"
        """
        self.df = df
        self.buy = []
    
    def createstatus(self):
        for i in self.df.values:
            stock = i[1]
            date = i[2]
            data = i[3]
            diff = i[4]
            macd = i[5]
            status = i[6]
            print(i)
    
    def isbuy(self,diff,dem,status,currentdata):
#         diff = processdata
        
        pass
    
    def savestatus(self):
        pass
        

        
if __name__ == '__main__':
    s = macd()
    s.setlooplist()
    s.looplist_historyreturn()
    s.savetrading2csv("macd.csv")
    s.saveholding2csv("macdhold.csv")
    s.saveprocedure("procedure_records.csv")
    s.saveprocedure2db()
    df = pd.read_csv('macd.csv')
    report = reportforms(df)
    report.cumulative_graph()
    report.positiongain(5)
    buy = s.getprocedure('procedure_records.csv')
    print (buy)
     









