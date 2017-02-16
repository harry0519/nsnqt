# -*- coding:utf-8 -*-
from nsnqtlib.strategies.strategy import basestrategy
import pandas as pd
import tushare as ts

class moneyfundstrategy(basestrategy):
    '''
           重写买入条件和卖出条件，
    '''

    def __init__(self,startdate=(2011, 1, 1),enddate=[],emafast=12,emaslow=26,demday=9):
        self.pre_MA = False
        self.curr_MA = False
        self.buyprice = 0
        #self.formatlistnew = ["date", "volume", "close", "high", "low", "open", "pre_close", 'actualvalue','cumulativevalue']
        self.formatlistnew = ["date", "volume", "close", "high", "low", "open", "pre_close", 'actualvalue']

        super(moneyfundstrategy, self).__init__(startdate, enddate)

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
            query = ts.get_hist_data(collection, start='2012-01-01', end='2017-02-03')
            query['date'] = query.index
            query = query.sort_index(axis=0, ascending=True)
            query['pre_close'] = query['close'].shift(1)
            query.to_csv(collection + 'new.csv')
            return query
        elif db == 'local':
            query = pd.read_csv(str(collection) + '.csv')
            #out = self.formatlist
            return query
        else:
            if not out: out = self.formatlist
            if isfilt and not filt: filt = {"date": {"$gt": self.startdate}}
            query = self.m.read_data(db, collection, filt=filt)
            #query.to_csv(collection)
            #df = pd.DataFrame(query)
            #df.to_csv(collection+'new.csv')
            print(query)
            print('downloaded')
            return self.formatquery(query, out)

    '''
    #def _getdata(self,collection="600455.SH",db="ml_security_table"):
    def _getdata(self, collection="600455.SH", db="ml_security_table", out=[], isfilt=True, filt={}):
        if db == "ml_security_table":
            query = self.m.read_data(db,collection,filt={"date":{"$gt": self.startdate}})
            query.to_csv('db_'+collection + '.csv')
            out = self.formatlist
            return self.formatquery(query, out)
        elif db == "tushare":
            query = ts.get_hist_data(collection)
            #query = ts.get_hist_data(collection)
            #print(collection)
            query['date'] = query.index
            query = query.sort_index(axis=0, ascending=True)
            query['pre_close'] = query['close'].shift(1)
            query['actualvalue'] = query['close'] - query['pre_close']
            out = self.formatlist
            #return self.formatquery(query, out)
            return query
        elif db == 'local':
            query = pd.read_csv(str(collection) + '.csv')
            #out = self.formatlist
            return query
    '''
    '''
    def _getdata(self,collection="600455.SH",db="ml_security_table"):
        #query = pd.read_csv(str(collection) + '.csv', parse_dates=['date'])
        #print(query)
        query = self.m.read_data(db,collection,filt={"date":{"$gt": self.startdate}})
        out = self.formatlist
        return self.formatquery(query,out)
    '''

    def historyreturn(self, collection, par):
        trading_record = []
        holding_record = []
        data = self._getdata(collection, 'tushare')
        #print(collection)
        #newdata = self.updatemoneyfund(data)
        #newdata.to_csv(collection+'moneyfundstrategy_new.csv')
        #print(data)
        lst = [l for l in data[self.formatlistnew].fillna(0).values if l[1] != 0]
       #lst.extend('dddd')
        #df = pd.DataFrame(lst)
        #df.to_csv(collection+'moneyfundstrategy.csv')
        count = 0
        for line in lst[:]:
            isbuy = self.buy(lst, count, par)

            for b in holding_record[:]:
                issell, traderecord = self.sell(lst, count, b)
                if issell:
                    holding_record.remove(b)
                    trading_record.append(traderecord)
                    print (traderecord)

            if isbuy:
                #holding_record.append((line, count, collection))
                holding_record.append(([i for i in line], count, collection))

            count += 1
        return trading_record, holding_record

    def updatemoneyfund(self, df):
        count = 1
        df_len = len(df.index)
        yearvaluelist = []
        year1end = 0
        year2end = 0
        df['cumulativevalue'] = df['actualvalue']
        while (count < df_len):
            if df['actualvalue'].iloc[count] < -1:
                yearvalue = [-1 * df['actualvalue'].iloc[count],count]
                yearvaluelist.append(yearvalue)
                df['cumulativevalue'].iloc[count] = df['close'].iloc[count]
            count = count + 1
        newdf = pd.DataFrame(yearvaluelist)
        #for b in yearvaluelist[:]:
            #print(b[0],b[1])
        count = 0
        df_len = len(df.index)
        newdf_count = 0
        newdf_len = len(newdf.index)
        while (newdf_count < newdf_len):
             #print(newdf[1].iloc[newdf_count])
             if newdf[1].iloc[newdf_count] < 200:
                while (count < newdf[1].iloc[newdf_count]):
                    df['cumulativevalue'].iloc[count] = df['close'].iloc[count]
                    count = count + 1
             elif newdf[1].iloc[newdf_count] - newdf[1].iloc[newdf_count-1] > 200:
                count = newdf[1].iloc[newdf_count-1]
                print(count)
                endcount = newdf[1].iloc[newdf_count]
                print(endcount)
                increasevalue = newdf[0].iloc[newdf_count] / (endcount - count)
                print(increasevalue)
                df['cumulativevalue'].iloc[count] = df['close'].iloc[count]
                count = count +1
                while (count < endcount):
                    df['cumulativevalue'].iloc[count] = df['cumulativevalue'].iloc[count-1] + increasevalue
                    count = count + 1

             if newdf_count == newdf_len-1:
                 count = newdf[1].iloc[newdf_count]
                 #increasevalue = newdf[0].iloc[newdf_count] / (df_len - newdf[1].iloc[newdf_count])
                 df['cumulativevalue'].iloc[count] = df['close'].iloc[count]
                 count = count + 1
                 while (count < df_len):
                     df['cumulativevalue'].iloc[count] = df['cumulativevalue'].iloc[count - 1] + increasevalue
                     count = count + 1
             newdf_count = newdf_count + 1
        #print(newdf)
        return df

    def looplist_historyreturn(self, df, actiontype="regression"):
        error_list = []
        buylist = []
        selllist = []
        count = 0
        df_len = len(df.index)
        column_num = len(df.count())
        while (count < df_len):
            columncount = 1
            par = []
            while (columncount < column_num):
                par.append(df.iat[count, columncount])
                columncount = columncount + 1
            print(par)
            #stock_name = str(df.iat[count, 0])
            stock_name = str(df.ix[count, 'stock'])
            try:
                if actiontype == 'regression':
                    tr,hr = self.historyreturn(stock_name, par)
                    self.trading_records.extend(tr)
                    self.holding_records.extend(hr)
                elif actiontype == 'trade':
                    buy, sell = self.getprocedure(isdb=True, collection=stock_name)
                    buylist.extend(buy)
                    selllist.extend(sell)
            except:
                 error_list.append(stock_name)
            count = count + 1
        print(error_list)
        print(buylist)
        print(selllist)
        return self.trading_records,self.holding_records, buylist, selllist

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
        #if count <= 60: return False
        vol_data = [i[1] for i in lst[count - vol_day:count]]
        #maxprice = max([i[3]] for i in lst[count - price_day:count])[0]
        #minprice = min([i[4]] for i in lst[count - price_day:count])[0]
        #maxindex = [i for i in range(count - price_day, count) if lst[i][3] == maxprice][0]
        '''
        if self.buy_condition1(vol, vol_data, vol_weight) and \
                self.buy_condition2(close, lst[count - 1][3]) and \
                self.buy_condition3(close, maxprice) and \
                self.buy_condition4(close, minprice) and \
                self.buy_condition5(count, maxindex):
            return True
        '''
        #and self.condition7(close, par[0])  and self.condition9(close, pre_close)
        #if self.condition10(close) and self.condition9(close, pre_close) and self.MA_condition(lst, count):
        if self.moneyfundbuycondiction(close, pre_close):
            #print(dat)
            self.buyprice = pre_close
            return True
        return False
            #print(self.waitbuy)

        #and self.condition9(close, pre_close)

    def waitforbuy(self, dat, close, par):
        if self.condition6(dat, par[1]) and \
                self.condition7(close, par[0]):
             return True
        return False

    def sell(self, lst, count, buyrecord):
        currentday_high = lst[count][3]
        gain_grads = 0.2
        loss_grads = -0.05
        dayout = 30
        currentday_low = lst[count][4]
        sell_date = lst[count][0]
        close = lst[count][2]
        high = lst[count][3]
        low = lst[count][4]

        buy_price = buyrecord[0][2]
        hold_days = count - buyrecord[1]
        buy_date = buyrecord[0][0]
        collection = buyrecord[2]

        '''
        if self.stopgain_condition(buy_price, currentday_high, gain_grads):
            self.bought = False
            gain_grads = (currentday_high - buy_price) / buy_price
            #sell_date = sell_date.strftime('%Y-%m-%d')
            #buy_date = buy_date.strftime('%Y-%m-%d')
            #sell_date = changedateformat(sell_date)
            return True, [collection, buy_date, sell_date, hold_days, gain_grads, '']
        elif self.stoploss_condition(buy_price, currentday_low, loss_grads):
            #sell_date = sell_date.strftime('%Y-%m-%d')
            #buy_date = buy_date.strftime('%Y-%m-%d')
            return True, [collection, buy_date, sell_date, hold_days, (close - buy_price) / buy_price, '']
        elif self.holdingtime_condition(hold_days, dayout):
            #sell_date = sell_date.strftime('%Y-%m-%d')
            #buy_date = buy_date.strftime('%Y-%m-%d')
            return True, [collection, buy_date, sell_date, hold_days, (close - buy_price) / buy_price, '']
        el
        if self.Sellcondition3(close):
            #sell_date = sell_date.strftime('%Y-%m-%d')
            #buy_date = buy_date.strftime('%Y-%m-%d')
            return True, [collection, buy_date, sell_date, hold_days, (close - buy_price) / buy_price, '']
        return False, None
       '''
        if self.moneyfundsellcondiction(close):
            #sell_date = sell_date.strftime('%Y-%m-%d')
            #buy_date = buy_date.strftime('%Y-%m-%d')
            return True, [collection, buy_date, sell_date, hold_days, (close - buy_price) / buy_price, '']
        return False, None
        '''
                elif self.holdingtime_condition(hold_days, dayout):
                    sell_date = sell_date.strftime('%Y-%m-%d')
                    buy_date = buy_date.strftime('%Y-%m-%d')
                    return True, [collection, buy_date, sell_date, hold_days, (close - buy_price) / buy_price, '']
       '''

        # 取实时数据，根据历史回测数据比较是否存在交易机会
    def getprocedure(self, filename="procedure_records.csv", isdb=False, collection="processstatus", db="etfgrid"):
        '''"stock","date","data","s_ema","f_ema","diff","dem","macd","status"
        '''
        buy = []
        sell = []
        newlist = []
        newdatalist = []
        #out = ["stock", "date", "close", "startprice", "buytimes", "selltimes"]
        '''
        if isdb:
            # df = self._getdata(collection, db, out=out, isfilt=False)[out]
            #df = self._getdata(collection, db, out=out, isfilt=False)
            df = self._getdata(collection, 'tushare')
            # print(df)
        else:
            # df = pd.read_csv(filename)[out]
            df = pd.read_csv(filename)
       '''
        # df.to_csv(collection)
        #df_len = len(df.index)
        #stock = str(df['stock'].iloc[0])
        #print(stock)
        #pre_close = float(df['close'].iloc[df_len-1])
        #print(pre_close)
        print(collection)
        print('159005')
        new_df = ts.get_realtime_quotes(collection)
        print(new_df)
        pre_close = float(new_df['pre_close'].iloc[0])
        print('pre_close:' + str(pre_close))
        price = float(new_df['ask'].iloc[0])
        print('price:' + str(price))
        high = float(new_df['high'].iloc[0])
        # price = 0.89
        #df_len = len(df.index) - 1
        #if df_len < 200: return buy, sell
        #startprice = df['startprice'].iloc[df_len]
        #buynumber = df['buytimes'].iloc[df_len]
        #sellnumber = df['selltimes'].iloc[df_len]
        if price - pre_close < -0.1:
            buy.append(collection)
        # print(buy)
        return buy, sell

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

    def condition7(self, close, cashprice):
        if close < cashprice:
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

if __name__ == '__main__':
    s = moneyfundstrategy()
    df_stocklist = s.import_stocklist("moneyfundstrategy")
    print(df_stocklist)
    #s.setlooplist()
    #getprocedure(self, filename="procedure_records.csv", isdb=False, collection="processstatus", db="etfgrid")
    s.looplist_historyreturn(df_stocklist, actiontype="trade")
    #s.looplist_historyreturn(df_stocklist)
    s.savetrading2csv()
    #s.saveholding2csv()
    #report = reportforms(df)
    #report.cumulative_graph()
    #report.positiongain(100)
