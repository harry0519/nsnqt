# -*- coding:utf-8 -*-
from nsnqtlib.strategies.strategy import basestrategy
import pandas as pd
import tushare as ts

class FundClassificationBGridStrategy(basestrategy):
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

        super(FundClassificationBGridStrategy, self).__init__(startdate, enddate)

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

    def _getdata(self,collection="600455.SH",db="ml_security_table"):
        if db == "ml_security_table":
            query = self.m.read_data(db,collection,filt={"date":{"$gt": self.startdate}})
            query.to_csv('db_'+collection + '.csv')
            out = self.formatlist
            return self.formatquery(query, out)
        elif db == "tushare":
            #query = ts.get_hist_data(collection, start='2005-01-01', end='2016-12-23', )
            query = ts.get_hist_data(collection)
            print(collection)
            query['pre_close'] = query['close'].shift(1)
            query.to_csv(collection + '.csv')
            print(collection)
           # print(query)
            #out = self.formatlist
            return query
        elif db == 'local':
            query = pd.read_csv(str(collection) + '.csv')
            #out = self.formatlist
            return query

    '''
    def _getdata(self,collection="600455.SH",db="ml_security_table"):
        #query = pd.read_csv(str(collection) + '.csv', parse_dates=['date'])
        #print(query)
        query = self.m.read_data(db,collection,filt={"date":{"$gt": self.startdate}})
        out = self.formatlist
        return self.formatquery(query,out)
    '''

    def historyreturn_new(self, collection, par):
        trading_record = []
        holding_record = []
        #print(collection)
        data = self._getdata(collection,'tushare')
        self.selltimes = 0
        self.buytimes = 0
        #print(data)
        lst = [l for l in data[self.formatlist].fillna(0).values if l[1] != 0]
        df = pd.DataFrame(lst)
        df.to_csv(collection+'.csv')
        return

    def historyreturn(self, collection, par):
        trading_record = []
        holding_record = []
        #print(collection)
        data = self._getdata(collection,'tushare')
        self.selltimes = 0
        self.buytimes = 0
        #print(data)
        lst = [l for l in data[self.formatlist].fillna(0).values if l[1] != 0]
        df = pd.DataFrame(lst)
        df.to_csv(collection+'.csv')
        count = 0
        for line in lst[:]:
            isbuy = self.buy(lst, count, par)

            for b in holding_record[:]:
                issell, traderecord = self.sell(lst, count, b)
                if issell and self.buytimes > 0:
                    holding_record.remove(b)
                    trading_record.append(traderecord)
                    print (traderecord)
                    self.buytimes = self.buytimes -1
                    if self.buytimes == 0:
                        self.selltimes = 0
                    break

            if isbuy:
                #holding_record.append((line, count, collection))
                holding_record.append(([i for i in line], count, collection))

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
            print(par)
            stock_name = str(df.iat[count, 0])
            #try:
            tr,hr = self.historyreturn(stock_name, par)
            self.trading_records.extend(tr)
            self.holding_records.extend(hr)
            #except:
                #error_list.append(stock_name)
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
        #if count <= 60: return False
        vol_data = [i[1] for i in lst[count - vol_day:count]]
        #maxprice = max([i[3]] for i in lst[count - price_day:count])[0]
        #minprice = min([i[4]] for i in lst[count - price_day:count])[0]
        #maxindex = [i for i in range(count - price_day, count) if lst[i][3] == maxprice][0]
        self.startingprice = par[0]

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

        if self.ETFGridbuycondition1(close, self.startingprice) :
            #print(dat)
            #self.buyprice = pre_close
            self.buytimes = self.buytimes + 1
            #print(close)
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
        if self.ETFGridsellcondition1(high, self.startingprice):
            #sell_date = sell_date.strftime('%Y-%m-%d')
            #buy_date = buy_date.strftime('%Y-%m-%d')
            self.selltimes = self.selltimes + 1
            #self.buytimes = self.buytimes - 1
            if self.selltimes > 5:
                self.selltimes = 0
            return True, [collection, buy_date, sell_date, hold_days, (close - buy_price) / buy_price, '']
        return False, None
        '''
                elif self.holdingtime_condition(hold_days, dayout):
                    sell_date = sell_date.strftime('%Y-%m-%d')
                    buy_date = buy_date.strftime('%Y-%m-%d')
                    return True, [collection, buy_date, sell_date, hold_days, (close - buy_price) / buy_price, '']
       '''

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

    def ETFGridbuycondition1(self, close, startingprice):
        if close < startingprice *(1- self.buytimes * 0.05) and self.buytimes < 6:
            print(self.buytimes)
            print(str(startingprice *(1- self.buytimes * 0.05)))
            return True
        return False

    def ETFGridsellcondition1(self, close, startingprice):
        if close > startingprice * (1.1 + self.selltimes*0.05):
            print('sell times: '+str(self.selltimes))
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
    s = FundClassificationBGridStrategy()
    df_stocklist = s.import_stocklist("ABFund")
    print(df_stocklist)
    #s.setlooplist()
    s.looplist_historyreturn(df_stocklist)
    s.savetrading2csv()
    s.saveholding2csv()
    #report = reportforms(df)
    #report.cumulative_graph()
    #report.positiongain(100)
