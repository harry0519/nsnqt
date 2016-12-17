# -*- coding:utf-8 -*-
from nsnqtlib.strategies.strategy import basestrategy
import pandas as pd
import tushare as ts

class cashoptionstrategy(basestrategy):
    '''
           重写买入条件和卖出条件，
    '''

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

    '''
    def _getdata(self,collection="600455.SH",db="ml_security_table"):
        if db == "ml_security_table":
            query = self.m.read_data(db,collection,filt={"date":{"$gt": self.startdate}})
            out = self.formatlist
        elif db == "tushare":
            print(db)
            query = ts.get_hist_data(collection, start='2005-01-01', end='2016-11-18', )
            print(query)
            out = self.formatlist
        return self.formatquery(query,out)
    '''

    def historyreturn(self, collection, par):
        trading_record = []
        holding_record = []
        print(collection)
        data = self._getdata(collection)
        print(data)
        lst = [l for l in data[self.formatlist].fillna(0).values if l[1] != 0]
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
            try:
                tr,hr = self.historyreturn(stock_name, par)
                self.trading_records.extend(tr)
                self.holding_records.extend(hr)
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
        vol = lst[count][1]
        close = lst[count][2]
        #         high = lst[count][3]
        #         low = lst[count][4]
        #         open = lst[count][5]
        #         pre_close = lst[count][6]
        if count <= 60: return False
        vol_data = [i[1] for i in lst[count - vol_day:count]]
        maxprice = max([i[3]] for i in lst[count - price_day:count])[0]
        minprice = min([i[4]] for i in lst[count - price_day:count])[0]
        maxindex = [i for i in range(count - price_day, count) if lst[i][3] == maxprice][0]
        '''
        if self.buy_condition1(vol, vol_data, vol_weight) and \
                self.buy_condition2(close, lst[count - 1][3]) and \
                self.buy_condition3(close, maxprice) and \
                self.buy_condition4(close, minprice) and \
                self.buy_condition5(count, maxindex):
            return True
        '''
        if self.condition8(close):
            return True

        return False

    def sell(self, lst, count, buyrecord):
        currentday_high = lst[count][3]
        gain_grads = 0.2
        loss_grads = -0.05
        dayout = 10
        currentday_low = lst[count][4]
        sell_date = lst[count][0]
        close = lst[count][2]

        buy_price = buyrecord[0][2]
        hold_days = count - buyrecord[1]
        buy_date = buyrecord[0][0]
        collection = buyrecord[2]

        if self.condition9(close):
            gain_grads = (currentday_high - buy_price) / buy_price
            sell_date = sell_date.strftime('%Y-%m-%d')
            buy_date = buy_date.strftime('%Y-%m-%d')
            #sell_date = changedateformat(sell_date)
            return True, [collection, buy_date, sell_date, hold_days, gain_grads]
        '''
        elif self.stoploss_condition(buy_price, currentday_low, loss_grads):
            return True, [collection, buy_date, sell_date, hold_days, (close - buy_price) / buy_price]

        elif self.holdingtime_condition(hold_days, dayout):
            return True, [collection, buy_date, sell_date, hold_days, (close - buy_price) / buy_price]
        '''
        return False, None

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
            return True
        return False

    def condition7(self, close, cashprice):
        if close < cashprice:
            return True
        return False

    def condition8(self, close):
        if close < 115:
            return True
        return False

    def condition9(self, close):
        if close > 120:
            return True
        return False

if __name__ == '__main__':
    s = cashoptionstrategy()
    #df_stocklist = s.import_stocklist("convertiblebond")
    #print(df_stocklist)
    s.setlooplist()
    #s.looplist_historyreturn(df_stocklist)
    #s.savetrading2csv()
