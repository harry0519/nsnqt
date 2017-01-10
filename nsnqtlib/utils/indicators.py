# -*- coding:utf-8 -*-
import random
from nsnqtlib.config import DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME
from  nsnqtlib.db.mongodb import MongoDB
import pandas as pd
import datetime
import logging 

'''
指标说明：：
macd：   指数平滑异同平均线
ema12： 12日价格指数平均数，EMAtoday=α * Pricetoday + ( 1 - α ) * EMAyesterday，α为平滑指数，一般取作2/(N+1)
ema26：26日价格指数平均数
diff12_26： 12日价格指数平均数和26日价格指数平均数的差离值，DIF = EMA（12） - EMA（26）
dem9：9日离差平均值，此值又名DEA或DEM
cross_dist： macd交叉点距离现在的交易日数

vol_m1：当天成交量
vol_m5：过去五个交易日平均成交量
vol_m10：过去10个交易日平均成交量
vol_m20：过去20个交易日平均成交量
vol_m30：过去30个交易提平均成交量

y_pri_high：过去300个交易日价格最高值
y_pri_low：过去300个交易日价格最低值
y_pri_h_dist：过去300个交易日价格最高日和现在的时间跨度
y_pri_l_dist过去300个交易日价格最低日和现在的时间跨度

c_rate_h：当日最高价对于最高价和最低价均值的涨幅
c_rate_l：当日最低价对于最高价和最低价均值的涨幅
c_rate_o：当日开盘价对于最高价和最低价均值的涨幅
c_rate_c：当日收盘价对于最高价和最低价均值的涨幅
c_rate_m：当日最高价和最低价均值的涨跌幅

f_pri_c1：买入第一天的收盘价
f_pri_c2：买入第二天的收盘价
f_pri_c3：买入第三天的收盘价
f_pri_c5：买入第五天的收盘价
f_pri_c7：买入第七天的收盘价
f_pri_c9：买入第九天的收盘价
f_pri_c11：买入第十一天的收盘价
f_pri_c13：买入第十三天的收盘价
f_pri_c15：买入第十五天的收盘价
f_pri_h1：买入第一天的最高价
f_pri_h2：买入第二天的最高价
f_pri_h3：买入第三天的最高价
f_pri_h5：买入第五天的最高价
f_pri_h7：买入第七天的最高价
f_pri_h9：买入第九天的最高价
f_pri_h11：买入第十一天的最高价
f_pri_h13：买入第十三天的最高价
f_pri_h15：买入第十五天的最高价
'''

class StockIndicator(object):
    '''
    various kinds of stock indicator method
    '''
    def __init__(self,startdate=(1990, 1, 1),end=(),init=False,mdb=None):
        self.isinit = init
        self.m = mdb
        self.formatlist = ["date","volume","close","high","low","open","pre_close"]
        self.startdate = datetime.datetime( *startdate,0,0,0,0)
        self.emaslow  = 26
        self.emafast = 12
        self.demday = 9
    
    def generateindics(self):
        rst = []
        for count in range(len(self.datalst)):
            currentdata = self.datalst[count]
            date = currentdata[0]
            tradedata = self.getperdaytradedata(currentdata)
            
            filt = {"date":str(date).split(" ")[0]}
            data = {'$set': tradedata}
            indics = self.mapindicwithfunc(self.datalst,count)
            for k,v in indics:
                data['$set'][k] = v
            rst.append([data,filt])
        return rst
    
    def getperdaytradedata(self,data):
        date = str(data[0]).split(" ")[0]
        volume = data[1]
        close = data[2]
        high = data[3]
        low = data[4]
        open = data[5]
        pre_close = data[6]
        rst = {"date":date,"volume":volume,"close":close,"high":high,"low":low,"open":open,"pre_close":pre_close}
        return rst
        
    
    def updateindics2db(self,datas,db,collection):
        if not datas:return
        bulk = db[collection].initialize_ordered_bulk_op()
        for data,filt in datas:
            bulk.find(filt).upsert().update(data)
        bulk.execute()
        return 
    
    def updateallstocks2db(self):
        db = self.m.client.stockdatas
        for collection in self.looplist:
            print ("udate stock:{}".format(collection))
            logging.info("udate stock:{}".format(collection))
            self.setenv(collection)
            indics = self.generateindics()
            self.updateindics2db(indics,db,collection)
        return 
    
    def mapindicwithfunc(self,lst,count,oldnum=300):
        # "date","volume","close","high","low","open","pre_close"
        indicators=[]
        futuredays=[1,2,3,5,7,9,11,13,15]
        voldays = [1,5,10,20,30]
        vol_m = "vol_m{}"
        f_pri_h ="f_pri_h{}"
        h_index = 3
        f_pri_c ="f_pri_c{}"
        c_index = 2
        if self.isinit or count >=oldnum:
            indicators.extend(self.getyearindic(lst,count,oldnum))
            indicators.extend([(f_pri_h.format(i),self.getfuture(lst,count,h_index,i)) for i in futuredays])
            indicators.extend([(f_pri_c.format(i),self.getfuture(lst,count,c_index,i)) for i in futuredays])
            indicators.extend([(vol_m.format(i),self.getvols(lst,count,i)) for i in voldays])
            indicators.extend(self.getcurrentday_k(lst,count))
            indicators.extend(self.getmacdrelates(lst,count))
        return indicators
    
    def getvols(self,lst,count,days):
        end = count+1
        if end>=days:start = end-days
        else: start=0
        vol = 0
        for i in lst[start:end]:
            vol += i[1]
        return vol/(end-start)

    def getfuture(self,lst,count,index,f_day):
        '''获取未来的价格涨跌幅特征
        '''
        try: rst = lst[count+f_day][index]
        except: rst = 0
        return rst
    
    def getyearindic(self,lst,count,oldnum=300):
        '''获取近300个交易日的最高价，最低价特征
        '''
        end = count+1
        if end >=oldnum:start = end-oldnum
        else: start=0
        h_queue = [i[3] for i in lst[start:end]]
        l_queue = [i[4] for i in lst[start:end]]
        high = max(h_queue)
        low = min(l_queue)
        h_dist = count-start-h_queue.index(high)
        l_dist = count-start-l_queue.index(low)
        
        rst = [("y_pri_high",high),("y_pri_low",low),("y_pri_h_dist",h_dist),("y_pri_l_dist",l_dist)]
        return rst
        
    def getcurrentday_k(self,lst,count):
        '''获取当天的k柱特征值
        '''
        preclose = lst[count][6]
        close = lst[count][2]
        high = lst[count][3]
        low = lst[count][4]
        openpri = lst[count][5]
        if not preclose:preclose = openpri
        
        middle = (high+low)/2
        c_rate_h = (high-middle)/preclose
        c_rate_l = (low-middle)/preclose
        c_rate_o = (openpri-middle)/preclose
        c_rate_c = (close-middle)/preclose
        c_rate_m = (middle-preclose)/preclose
        rst = [("c_rate_h",c_rate_h),("c_rate_l",c_rate_l),
               ("c_rate_o",c_rate_o),("c_rate_c",c_rate_c),
               ("c_rate_m",c_rate_m)]
        
        return rst
    
    def getmacdrelates(self,lst,count):
        d = lst[count]
        c_close = d[2]
        date = d[0]
        if not self.macds:
            n_s_ema = c_close
            n_f_ema = c_close
            n_diff = 0
            n_dem = 0
            n_macd = 0
            n_cross_dist = 0
        else:
            pre_date = lst[count-1][0]
            s_ema = self.macds[pre_date]["ema26"]
            f_ema = self.macds[pre_date]["ema12"]
            dem = self.macds[pre_date]["dem9"]
            macd = self.macds[pre_date]["macd"]
            cross_dist = self.macds[pre_date]["cross_dist"]
            
            n_s_ema = (s_ema*(self.emaslow-1)+ 2*c_close)/(self.emaslow+1)
            n_f_ema = (f_ema*(self.emafast-1)+ 2*c_close)/(self.emafast+1)
            n_diff = n_f_ema-n_s_ema
            n_dem = (dem*(self.demday-1)+ 2*n_diff)/(self.demday+1)
            n_macd = 2*(n_diff-n_dem)
            if n_macd*macd >0:n_cross_dist = cross_dist + 1
            else: n_cross_dist = 0
        self.macds[date] = {"macd":n_macd,"ema12":n_f_ema,"ema26":n_s_ema,"diff12_26":n_diff,"dem9":n_dem,"cross_dist":n_cross_dist}
        rst = [("macd",n_macd),("ema12",n_f_ema),("ema26",n_s_ema),("diff12_26",n_diff),("dem9",n_dem),("cross_dist",n_cross_dist)]
        return rst
 
    def setenv(self,collection):
        self.count = 0
        self.collection = collection
        data = self._getdata(collection)
        self.datalst = [l for l in data[self.formatlist].fillna(0).values if l[1] !=0]
        self.datalst = self.rehabilitation(self.datalst)
        self.macds = self.getmacdsfromdb(collection)
        
    def getmacdsfromdb(self,collection):
        '''output:{date:[macd,ema12,ema26,diff12_26,dem9,cross_dist]}
        '''
        if self.isinit:return {}
        else:
            pass
    
    def setlooplist(self,lst=[]):
        if not lst:
            self.looplist = self.m.getallcollections("ml_security_table")
        else:
            self.looplist = lst
        return self.looplist
    
    def _getdata(self,collection="600455.SH",db="ml_security_table",out=[],isfilt=True,filt={}):
        if not out:out = self.formatlist
        if isfilt and not filt: filt = {"date":{"$gt": self.startdate}}
        query = self.m.read_data(db,collection,filt=filt)
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
        ec = 0
        for idx in range(len(reh)):
            weight = reh[idx][1]
            ec = reh[idx][0]
            piece = self.recount(lst,sc,ec,weight)
            result.extend(piece)
            sc = ec
        result.extend(self.recount(lst,ec,-1,1))
        return result
    
    def recount(self,lst,sc,ec,weight):
        rst = []
        for line in lst[sc:ec]:
            rst.append([line[0],line[1],*[i*weight for i in line [2:]]])
        return rst     
    
    
    
    
    
    
    
#############################################################################
    
    
    
    
    
    
    
    def getallindictorperday(self,indictors=[]):
        '''input: 
             indictors :should be a list of list,example:[(name,func),(name,func)]
        '''
        indicts={}
        for i in indictors:
            indicts[i[0]] = i[1]()
        return indicts
    
    
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
        
        return self.macdlist
    
    #MACD related indicators
    #Moving average: there will be unstable period in the beginning
    
    #List of all indicators with completed "close" list
    def EMA_list(self, lst, timeperiod=9):
        ema = []
        current = lst[0][2]
        for i in lst:
            current = (current*(timeperiod-1)+ 2*i[2])/(timeperiod+1)
            ema.append(current)
        return ema
                
    def DIF_list(self, lst, fastperiod=12, slowperiod=26):
        dif = []
        dif_t = []
        s_ema = self.EMA_list(lst, slowperiod)
        f_ema = self.EMA_list(lst, fastperiod)
        for i in range(len(lst)):
            current = f_ema[i]-s_ema[i]
            dif.append(current)
            dif_t.append([0,0,current,0])
        return dif, dif_t
        
    def DEA_list(self, lst, fastperiod=12, slowperiod=26, signalperiod=9):
        _,dif = self.DIF_list(lst,fastperiod,slowperiod)
        return self.EMA_list(dif, signalperiod)
        
    def MACD_list(self, lst, fastperiod=12, slowperiod=26, signalperiod=9):
        macd = []
        dif,dif_t = self.DIF_list(lst,fastperiod,slowperiod)
        dea = self.EMA_list(dif_t, signalperiod)
        for i in range(len(lst)):
            macd.append(2*(dif[i]-dea[i]))
        return macd

    #updating value with previous and current value
    '''
    input: 
        history: Sorted list by date: 
                 [["date","EMA12","EMA26","DIF","DEA","MACD"],[...],...]
                 ! Last one should be yesterday's data
        current: float: Todays' close price
    output:
        current indicator value.
    '''
    def EMA(self, last, current, timeperiod = 10):
        return (current*(timeperiod-1)+ 2*last)/(timeperiod+1)
    
    def EMA12(self, history, current):
        return self.EMA(history[-1][1], current, 12)
        
    def EMA26(self, history, current):
        return self.EMA(history[-1][2], current, 26)
    
    def DIF(self, history, current):
        return (self.EMA12(history, current)-self.EMA26(history, current))
    
    def DEA(self, history, current):
        return self.EMA(history[-1][3], self.DIF(history, current), 9)
    
    def MACD(self, history, current):
        return 2*(self.DIF(history, current)-self.DEA(history, current))
    
    '''
    input: 
        history: Sorted list by date: 
                 [["date","EMA12","EMA26","DIF","DEA","MACD"],[...],...]
                 ! Last one should be last available data
        current: [["date","close"],...]
                 Earliest day which is not updated with indicators to todays' close price
    output:
        Indicator value list in date order:
            [["date","EMA12","EMA26","DIF","DEA","MACD"],[...],...]
    '''
    def MACD_update(self, history, current):
        '''
        Update MACD related all values: inc. EMA12, EMA26, DIF, DEA, MACD
        '''
        #To be added: update them into database
        updates = []
        indicators = history[-1]
        for i in range(len(current)):
            indicators = [current[i][0],self.EMA12([indicators], current[i][1]), \
                self.EMA26([indicators], current[i][1]), \
                self.DIF([indicators], current[i][1]), \
                self.DEA([indicators], current[i][1]), \
                self.MACD([indicators], current[i][1])]
            updates.append(indicators)
        return updates
    
    
    def islowestvolume(self,data,section=60):
        if (len(data) >= section) and (data[0] == min(data[0:section])):
            return True
        return False
    
    def getaverageprice(self,data,):
        pass
    
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
    
if __name__ == '__main__':
    db = MongoDB(DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME)
    s= StockIndicator(init=True,mdb=db)
    s.setlooplist()
    s.updateallstocks2db()
    
    
    
    