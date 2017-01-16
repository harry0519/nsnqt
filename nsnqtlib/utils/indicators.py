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
    def __init__(self,startdate=(1990, 1, 1),end=(),init=False,mdb=None,yearperid=300,perid=20):
        self.isinit = init
        self.yearperid = yearperid
        self.perid = perid
        self.m = mdb
        self.formatlist = ["date","volume","close","high","low","open","pre_close"]
#         self.startdate = datetime.datetime( *startdate,0,0,0,0)
        self.startdate = datetime.datetime.now() + datetime.timedelta(days = -perid)
        self.emaslow  = 26
        self.emafast = 12
        self.demday = 9
    
    def generateindics(self):
        rst = []
        isstart = self.precheck()
        for count in range(len(self.datalst)):
            currentdata = self.datalst[count]
            date = str(currentdata[0]).split(" ")[0]
            if not isstart:
                isstart = self.checkstartdate(date)
                if not isstart: continue
            
            tradedata = self.getperdaytradedata(currentdata)
            filt = {"date":date}
            data = {'$set': tradedata}
            indics = self.mapindicwithfunc(self.datalst,count)
            for k,v in indics:
                data['$set'][k] = v
            rst.append([data,filt])
        return rst
    
    def checkstartdate(self,date,):
        if date > self.duplicatedate[1]:
            return True
        return False
    
    def precheck(self):
        if self.isinit:return True
        if len(self.duplicatedate) == 0:return True
        return False
    
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
        date = str(d[0]).split(" ")[0]
        if not self.macds:
            n_s_ema = c_close
            n_f_ema = c_close
            n_diff = 0
            n_dem = 0
            n_macd = 0
            n_cross_dist = 0
        else:
            pre_date = str(lst[count-1][0]).split(" ")[0]
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
        p_filt = [{"$sort":{"date":-1}},{"$limit":20}]
        self.p_data = self._getdata(collection,db="stockdatas",filt=p_filt,is_aggregate=True)
        if self.p_data.empty:
            self.duplicatedate = []
            limt=3000
            self.isinit = True
        else:
            self.duplicatedate = [l[0] for l in self.p_data[["date"]].values]
            limt=self.yearperid+self.perid
            self.isinit = False
        
        filt = [{"$sort":{"date":-1}},{"$limit":limt}]
        data = self._getdata(collection,out=self.formatlist,filt=filt,is_aggregate=True)
        self.datalst = [l for l in data[self.formatlist].fillna(0).values if l[1] !=0]
        
        if not self.isinit and self.checkexright(self.p_data,self.datalst):
            filt = [{"$sort":{"date":-1}},{"$limit":3000}]
            data = self._getdata(collection,out=self.formatlist,filt=filt,is_aggregate=True)
            self.datalst = [l for l in data[self.formatlist].fillna(0).values if l[1] !=0]
            self.isinit = True
            
        self.datalst.reverse()
        self.datalst = self.rehabilitation(self.datalst)
        self.macds = self.getmacdsfromdb()
    
    def checkexright(self,data,datas):
        date=data.iloc[[0]].date.values[0]
        tmp = datas[0]
        for i in datas[1:]:
            if str(i[0]).split(" ")[0] >= date:
                if i[2] != tmp[6]:
                    print ("{} is ex-right now!".format(self.collection))
                    return True
                tmp = i
            else:
                return False       
        
    def getmacdsfromdb(self,):
        '''output:{date:[macd,ema12,ema26,diff12_26,dem9,cross_dist]}
        '''
        macdskey = ["date","macd","ema12","ema26","diff12_26","dem9","cross_dist"]
        rst = {}
        if self.isinit:
            return rst
        else:
            for i in self.p_data[macdskey].values:
                rst[i[0]] = {"macd":i[1],"ema12":i[2],"ema26":i[3],"diff12_26":i[4],"dem9":i[5],"cross_dist":i[6]}
            return rst
    
    def setlooplist(self,lst=[]):
        if not lst:
            self.looplist = self.m.getallcollections("ml_security_table")
            try:self.looplist.remove("stock")
            except:pass#remove not stock collection
        else:
            self.looplist = lst
        return self.looplist
    
    
    def _getdata(self,collection="600455.SH",db="ml_security_table",out=[],isfilt=True,filt={},is_aggregate=False):
        query = self.m.read_data(db,collection,filt=filt,is_aggregate=is_aggregate)
        return self.formatquery(query,out)
    
    def formatquery(self,query,out):
        '''
        query:your source data ,should be a list with dict
        out:the fields you want to convert into dataframe 
        '''
        if not out:
            query = [i for i in query]
        else:
            query = [{k:i[k] for k in out} for i in query]
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
        result.extend(lst[sc:])
        return result
    
    def recount(self,lst,sc,ec,weight):
        rst = []
        for line in lst[sc:ec]:
            rst.append([line[0],line[1],*[i*weight for i in line [2:]]])
        return rst     
    
if __name__ == '__main__':
    db = MongoDB(DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME)
    s= StockIndicator(mdb=db)
    s.setlooplist()
    s.updateallstocks2db()
    
    
    
    