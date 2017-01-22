# -*- coding:utf-8 -*-
from nsnqtlib.strategies.strategy import basestrategy,reportforms
import pandas as pd
import tushare as ts
from datetime import datetime

class ETFstrategy(basestrategy):
    '''
           重写买入条件和卖出条件，
    '''

    def __init__(self,startdate=(2011, 1, 1),enddate=[],emafast=12,emaslow=26,demday=9):
        self.pre_MA = False
        self.curr_MA = False
        self.buyprice = 0
        self.startingprice = 0
        self.buytimes = 0
        self.selltimes = 0
        self.bought = False
        self.tempstatus = []
        self.collection = ''
        self.procedurevol = ["stock", "date", "close", "startprice", "buytimes", "selltimes"]

        super(ETFstrategy, self).__init__(startdate, enddate)

    # 获取需要交易股票列表
    def import_stocklist(self, stocklistname):
        df = pd.read_csv(str(stocklistname) + '.csv')
        #df = pd.read_csv(str(stocklistname) + '.csv', parse_dates=['startdate'])
        df['code'] = df['code'].astype('str')
        count = 0
        df_len = len(df.index)
        while (count < df_len):
            stock_name = str(df.iat[count, 0])
            if len(stock_name) == 1:
                stock_name = '00000' + stock_name
                df.iat[count, 0] = stock_name
            elif len(stock_name) == 2:
                stock_name = '0000' + stock_name
                df.iat[count, 0] = stock_name
            elif len(stock_name) == 3:
                stock_name = '000' + stock_name
                df.iat[count, 0] = stock_name
            elif len(stock_name) == 4:
                stock_name = '00' + stock_name
                df.iat[count, 0] = stock_name
            elif len(stock_name) == 5:
                stock_name = '0' + stock_name
                df.iat[count, 0] = stock_name
            count = count + 1
        return df

    def _getdata(self,collection="600455.SH",db="ml_security_table",out=[],isfilt=True,filt={}):
        self.collection = collection
        if db == "tushare":
            #d1 = datetime.datetime.now()
            #d2 = d1 + datetime.timedelta(-240)
            #d1 = d1.strftime('%Y-%m-%d')
            #d2 = d2.strftime('%Y-%m-%d')
            #query = ts.get_hist_data(collection, start=d2, end=d1, )
            query = ts.get_hist_data(collection)
            query['date'] = query.index
            query = query.sort_index(axis=0, ascending=True)
            query['pre_close'] = query['close'].shift(1)
            return query
        elif db == 'local':
            query = pd.read_csv(str(collection) + '.csv')
            #out = self.formatlist
            return query
        else:
            if not out: out = self.formatlist
            if isfilt and not filt: filt = {"date": {"$gt": self.startdate}}
            query = self.m.read_data(db, collection, filt=filt)
            return self.formatquery(query, out)

    def historyreturn(self, collection, par):
        trading_record = []
        holding_record = []
        data = self._getdata(collection,"tushare")
        self.selltimes = 0
        self.buytimes = 0
        self.startingprice = 0
        self.bought = False
        lst = [l for l in data[self.formatlist].fillna(0).values if l[1] != 0]
        count = 0
        for line in lst[:]:
            isbuy = self.buy(lst, count, par)

            for b in holding_record[:]:
                issell, traderecord = self.sell(lst, count, b)
                if issell:
                    holding_record.remove(b)
                    trading_record.append(traderecord)
                    break

            if isbuy:
                print(collection)
                holding_record.append(([i for i in line], count, collection))
                print(count)

            count += 1
        return trading_record, holding_record

    def looplist_historyreturn(self, df):
        error_list = []
        count = 0
        df_len = len(df.index)
        column_num = len(df.count())
        while (count < df_len):
            columncount = 1
            par = []
            while (columncount < column_num):
                par.append(df.iat[count, columncount])
                columncount = columncount + 1
            #print(par)
            stock_name = str(df.iat[count, 0])
            try:
                tr,hr = self.historyreturn(stock_name, par)
                #self.lateststatus.append(self.tempstatus)
                self.trading_records.extend(tr)
                self.holding_records.extend(hr)
                #self.getprocedure(isdb=True, collection=stock_name)
                self.saveprocedure2db(collection=stock)
            except:
                error_list.append(stock_name)
            count = count + 1
        print(error_list)
        return self.trading_records,self.holding_records

    def buy(self, lst, count, par):
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
        dat = lst[count][0]
        close = lst[count][2]
        pre_close = lst[count][6]
        position = self.getposition(lst,dat)
        #position = lst_index[0] / lst_len
        #print(position)
        lst[count][6] = position

        #and self.condition7(close, par[0])  and self.condition9(close, pre_close)
        #if self.condition10(close) and self.condition9(close, pre_close) and self.MA_condition(lst, count):

        rst = False
        if self.ETFGridbuycondition2(position) and self.bought == False:
            self.startingprice = close
            print('startingprice'+str(self.startingprice)+' ')
            print('statingdate'+str(dat))
            #return True
        #return False

        if self.ETFGridbuycondition1(close, self.startingprice, self.buytimes) and self.startingprice > 0:
            #if self.bought == False:
                #print('self.bought:false')
            print('buy:'+str(close))
            self.buytimes = self.buytimes + 1
            self.bought = True
            #print('buy date:'+str(dat)+'  buy price:'+str(close)+' startingprice'+str(self.startingprice))
            #print('buy times:'+str(self.buytimes))
            #print('position:'+str(position))
            rst = True
            #return True
        self.setprocedure(lst, count)
        #print(self.temstatus)
        self.lateststatus.append(self.tempstatus)
        return rst

    def sell(self, lst, count, buyrecord):
        currentday_high = lst[count][3]
        gain_grads = 0.2
        loss_grads = -0.05
        dayout = 60
        currentday_low = lst[count][4]
        sell_date = lst[count][0]
        close = lst[count][2]
        high = lst[count][3]
        low = lst[count][4]

        buy_price = buyrecord[0][2]
        hold_days = count - buyrecord[1]
        buy_date = buyrecord[0][0]
        collection = buyrecord[2]

        if self.holdingtime_condition(hold_days, dayout) or self.ETFGridsellcondition1(high, self.startingprice, self.selltimes):
            #sell_date = sell_date.strftime('%Y-%m-%d')
            #buy_date = buy_date.strftime('%Y-%m-%d')
            self.selltimes = self.selltimes + 1
            self.buytimes = self.buytimes - 1
            print('sell date:'+str(sell_date)+'  sell price:'+str(close))
            print('sell times:'+str(self.selltimes))
            print('buytimes @ sell: '+str(self.buytimes))
            if self.buytimes == 0:
                self.bought = False
                self.startingprice = 0
                self.selltimes = 0
                print('self.bought: False')
            #if self.selltimes > 5:
                #self.selltimes = 0
            return True, [collection, buy_date, sell_date, hold_days, (close - buy_price) / buy_price, '']
        return False, None

    def getposition(self,lst, dat):

        count = len(lst)
        if count <= 200: return False
        new_lst = lst.copy()
        new_lst.sort(key=lambda x: x[3])
        l = [x[0] for x in new_lst]
        lst_index = self.find_index(l, dat)
        lst_len = len(l)
        position = lst_index[0] / lst_len
        #lst[count][6] = position
        return position

    def getprocedure(self, filename="procedure_records.csv", isdb=False, collection="processstatus", db="etfgrid"):
        '''"stock","date","data","s_ema","f_ema","diff","dem","macd","status"
        '''
        buy = []
        sell = []
        newlist = []
        newdatalist = []
        out = ["stock", "date", "close", "startprice", "buytimes", "selltimes"]
        if isdb:
            #df = self._getdata(collection, db, out=out, isfilt=False)[out]
            df = self._getdata(collection, db, out=out, isfilt=False)
            print(df)
        else:
            #df = pd.read_csv(filename)[out]
            df = pd.read_csv(filename)
        print(df)
        stock = str(df['stock'].iloc[0])
        print(stock)
        new_df = ts.get_realtime_quotes(stock)
        print(new_df)
        price = float(new_df['ask'].iloc[0])
        high = float(new_df['high'].iloc[0])
        #price = 0.89
        df_len = len(df.index) - 1
        startprice = df['startprice'].iloc[df_len]
        buynumber = df['buytimes'].iloc[df_len]
        sellnumber = df['selltimes'].iloc[df_len]
        if buynumber == 0:
            dat = datetime.today().strftime('%Y-%m-%d')
            lastdata = [dat,0,0,price]
            newdatalist = [l for l in df[['date', 'startprice', "buytimes", 'close']].values]
            newdatalist.append(lastdata)
            position = self.getposition(newdatalist,dat)
            print(position)
            if position < 0.05:
                buy.append(collection)
        elif self.ETFGridbuycondition1(price, startprice, buynumber) and buynumber > 0:
            #print(1.2*0.75)
            buy.append(collection)
        elif self.ETFGridsellcondition1(high, startprice, sellnumber):
            sell.append(collection)
        #print(buy)
        return buy, sell

    def setprocedure(self, lst, count):
        dat = lst[count][0]
        close = lst[count][2]
        self.tempstatus = [self.collection, dat, close, self.startingprice, self.buytimes,self.selltimes]

    def saveprocedure(self,filename="procedure_records.csv"):
        df = pd.DataFrame(self.lateststatus,columns=self.procedurevol)
        #df = pd.DataFrame(self.lateststatus)
        df.to_csv(filename)
        return

    def saveprocedure2db(self, db="etfgrid", collection="processstatus"):
        self.lateststatus
        db = eval("self.m.client.{}".format(db))
        bulk = db[collection].initialize_ordered_bulk_op()
        for line in self.lateststatus:
            bulk.find({'date': line[1]}).upsert().update( \
                {'$set': {'stock': line[0], \
                          'close': line[2], \
                          'startprice': line[3], \
                          'buytimes': line[4], \
                          'selltimes': line[5], \
                          }})
        bulk.execute()
        return

    def stopgain_condition(self, buy_price, current_price, grads=0.1):
        if (current_price - buy_price) / buy_price >= grads:
            return True
        return False

    def stoploss_condition(self, buy_price, current_price, grads=-0.05):
        if (current_price - buy_price) / buy_price <= grads:
            return True
        return False

    def holdingtime_condition(self, hold_days, dayout=10):
        if hold_days >= dayout:
            return True
        return False

    def mean_volume(self, data):
        m_vol = sum(data) / len(data)
        return m_vol

    def buy_condition1(self, vol, vol_data, vol_weight=1.2):
        if vol >= vol_weight * self.mean_volume(vol_data):
            return True
        return False

    def buy_condition2(self, close, last_high):
        if close >= last_high:
            return True
        return False

    def buy_condition3(self, close, high, grads=0.2):
        if (high - close) / high >= grads:
            return True
        return False

    def buy_condition4(self, close, low, grads=0.05):
        if (close - low) / low <= grads:
            return True
        return False

    def buy_condition5(self, currentday, highday, grads=60):
        if currentday - highday >= grads:
            return True
        return False

    def condition6(self, dat, startdate):
        newdat = pd.to_datetime(dat)
        newdat = newdat.strftime('%Y-%m-%d')
        newstartdate = pd.to_datetime(startdate)
        newstartdate = newstartdate.strftime('%Y-%m-%d')
        # print(newdat)
        # print(newstartdate)
        if newdat > newstartdate:
            #print(newdat)
            return True
        return False

    def ETFGridbuycondition1(self, close, startingprice, buytime):
        if close <= startingprice *(1- buytime * 0.05) and buytime < 6:
            #print(self.buytimes)
            #print(str(startingprice *(1- self.buytimes * 0.05)))
            return True
        return False

    def ETFGridbuycondition2(self, position):
        if position < 0.05:
            return True
        return False

    def ETFGridsellcondition1(self, close, startingprice, selltime):
        if close > startingprice * (1.1 + selltime*0.05) and self.bought == True:
            #print('sell times: '+str(self.selltimes))
            return True
        return False

    def condition8(self, close, low, pre_close):
        if low > pre_close:
             return True
        return False

    def condition9(self, close, pre_close):
        if (close - pre_close) / pre_close < 0.099:
             return True
        return False

    def condition10(self, close):
        if close < 100:
             return True
        return False

    def MA_judge_result(self, lst, count):
        self.curr_MA = self.MA_condition(lst,count)
        if self.pre_MA == False and self.curr_MA == True:
            self.pre_MA = self.curr_MA
            return True
        self.pre_MA = self.curr_MA
        return False

    def MA_condition(self,lst,count):
        if self.MA_result(lst,count,5) > self.MA_result(lst,count, 10) and \
                self.MA_result(lst, count, 10) > self.MA_result(lst, count, 20) and \
                self.MA_result(lst, count, 20) > self.MA_result(lst, count, 30):
             #print(count)
             return True
        return False

    def MA_result(self, lst,count, meanday):
        meanlist = [i[2] for i in lst[count - meanday + 1:count + 1]]
        return sum(meanlist) / meanday

    def moneyfundbuycondiction(self, close, pre_close):
        if close - pre_close < -0.05 and \
                close - pre_close > -1:
             return True
        return False

    def Sellcondition1(self, lst, high, count, maxday):
        meanlist = [i[2] for i in lst[count - maxday + 1:count + 1]]
        if high > max(meanlist):
            return True
        return False

    def Sellcondition2(self, lst, high, low, close):
        if high - low > 0:
            if (close-low)/(high-close) < 0.2:
                return True
        return False

    def Sellcondition3(self, close):
        if close > 130:
            return True
        return False

    def moneyfundsellcondiction(self, close):
        if close > self.buyprice and \
                close - self.buyprice < 1:
            return True
        return False

    def find_index(self, arr, item):
        return [i for i, a in enumerate(arr) if a == item]

if __name__ == '__main__':

    s = ETFstrategy()

    df_stocklist = s.import_stocklist("ETFGrid_new")
    print(df_stocklist)
    stock = df_stocklist.iat[0,0]
    print("test:"+stock)
    #df.iat[count, 0]
    #s.setlooplist()
    s.looplist_historyreturn(df_stocklist)
    s.savetrading2csv()
    #s.saveholding2csv()
    #print(s.tempstatus)
    #print(s.lateststatus)
    #df = pd.DataFrame(s.lateststatus)
    #df.to_csv('lateststatus.csv')
    #s.saveprocedure()
    #s.saveprocedure2db(collection=stock)


    #new_df = ts.get_realtime_quotes('159920')
    #print(new_df)
    #new_df = ts.get_realtime_quotes('159920')
    #print(new_df['ask'].iloc[0])
    #print(df.ix[0, 'ask'])
    #print(new_df[['code','name','price','bid','ask','volume','amount','time']])
    '''
    ls = s.getcurrentdata()
    new_df = pd.DataFrame(ls)
    new_df.to_csv('new_df.csv')
    print(ls)
    '''
    #df = pd.read_csv('trading_records.csv')
    #report = reportforms(df)
    #report.cumulative_graph()
    #report.positiongain(100)
