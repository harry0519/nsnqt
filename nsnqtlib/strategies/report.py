# -*- coding:utf-8 -*-
import pandas as pd
import time,datetime
import matplotlib.pyplot as plt
import random

pd.set_option('display.height',1000)
pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',50)
pd.set_option('display.width',1000)


class report(object):
    def __init__(self,df):
        '''
        df should be follow this format:"index(title is none)" "stock","buy_date","sell_date","holddays","profit"
        '''
        self.df = df
    
    def formatdate(self,s):
        try:
            t = time.strptime(s, "%Y/%m/%d")
            y,m,d = t[0:3]
            rst = datetime.datetime(y,m,d).strftime('%Y-%m-%d')
        except:
            print (s)
            rst = s
        return rst
    
    def positiongain(self,start="2011-01-01",end="2016-11-18"):
        totalmoney = 100
        leftmoney = 100
        holds = []
        datelist = [i.strftime('%Y-%m-%d') for i in pd.date_range(start, end)]
        result = {d:[] for d in datelist}
        gains = {d:0 for d in datelist}
        df = self.df
        for i in df.values:
            i[2] = self.formatdate(i[2])
            i[3] = self.formatdate(i[3])
            result[i[2]].append(i)
        for date in datelist:
            currentholdnum = len(holds)
            current_day_could_buy_num = len(result[date])
            if current_day_could_buy_num >=1 and currentholdnum < 10:
                buymoney = leftmoney/(10-currentholdnum)
                if current_day_could_buy_num + currentholdnum <= 10:
                    leftmoney = leftmoney - buymoney*current_day_could_buy_num
                    holds.extend([(i,buymoney) for i in result[date]])
                else:
                    leftmoney = 0
                    holds.extend([(i,buymoney) for i in random.sample(result[date],10-currentholdnum)])
            for d in holds[:]:
                if d[0][3]>= date : 
                    holds.remove(d)
                    leftmoney += d[1]*(d[0][5]+1)  
                    totalmoney += d[1]*d[0][5]
            gains[date] = totalmoney
        newdf = pd.DataFrame(data=[gains[i] for i in datelist], index=datelist,columns=["a",])
        newdf["date"] = newdf.index
        newdf.plot(x="date", y="a", kind='area')
        plt.savefig("positiongain_from_{}_to_{}.png".format(start,end))
        plt.show()
    
    
    def cumulative_graph(self,datafile="",start="2013-03-01",end="2016-11-18"):
        date = [i.strftime('%Y-%m-%d') for i in pd.date_range(start, end)]
        result = {d:[0,0] for d in date}
        df = self.df
        for i in df.values:
            i[2] = self.formatdate(i[2])
            i[3] = self.formatdate(i[3])
            result[i[3]][0] += i[5]
            result[i[3]][1] += 1
        newdf = pd.DataFrame(data=[[result[i][0],result[i][1]] for i in date], index=date,columns=["a","b"])
        newdf["data"] = newdf["a"].cumsum()
        newdf["buys"] = newdf["b"].cumsum()
        newdf["c"] = (newdf["a"]/newdf["b"]).fillna(0)
        newdf["d"] = newdf["c"].cumsum().fillna(0)
        newdf["date"] = newdf.index
        print (newdf)
        
        newdf.plot(x="date", y="d", kind='line')
        plt.savefig("test_buys_mean.png")
        plt.show()  

if __name__ == '__main__':
    df = pd.read_csv('test1_tushare.csv')
    r = report(df)
    r.positiongain(start="2011-01-01",end="2016-11-18")
    
    