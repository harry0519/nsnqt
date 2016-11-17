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
        self.df = df
    
    def formatdate(self,s):
        t = time.strptime(s, "%Y/%m/%d")
        y,m,d = t[0:3]
        return datetime.datetime(y,m,d).strftime('%Y-%m-%d')
    
    def positiongain(self):
        totalmony = 100
        leftmony = 100
        holds = []
        date = [i.strftime('%Y-%m-%d') for i in pd.date_range('2013-03-01', '2016-10-31')]
        result = {d:[] for d in date}
        gains = {d:0 for d in date}
        df = pd.read_csv('test.csv')
        for i in df.values:
            i[2] = self.formatdate(i[2])
            i[3] = self.formatdate(i[3])
            result[i[2]].append(i)
        for day in date:
            currentholdnum = len(holds)
            currentdaynum = len(result[day])
            if currentdaynum >=1 and currentholdnum < 10:
                buymony = leftmony/(10-currentholdnum)
                if currentdaynum + currentholdnum <= 10:
                    leftmony = leftmony - buymony*currentdaynum
                    holds.extend([(i,buymony) for i in result[day]])
                else:
                    leftmony = 0
                    holds.extend([(i,buymony) for i in random.sample(result[day],10-currentholdnum)])
            for d in holds[:]:
                if d[0][3]>= day : 
                    holds.remove(d)
                    leftmony += d[1]*(d[0][5]+1)  
                    totalmony += d[1]*d[0][5]
            gains[day] = totalmony
        newdf = pd.DataFrame(data=[gains[i] for i in date], index=date,columns=["a",])
        newdf["date"] = newdf.index
        newdf.plot(x="date", y="a", kind='line')
        plt.show()
        print (totalmony)
    
    
    def cumulative_graph(self,datafile=""):
        date = [i.strftime('%Y-%m-%d') for i in pd.date_range('2013-03-01', '2016-10-31')]
        result = {d:[0,0] for d in date}
        df = pd.read_csv('test.csv')
        for i in df.values:
            i[2] = self.formatdate(i[2])
            i[3] = self.formatdate(i[3])
            result[i[3]][0] += i[5]
            result[i[3]][1] += 1
#         print (result)    
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
    df = pd.read_csv('test.csv')
    r = report(df)
    r.positiongain()