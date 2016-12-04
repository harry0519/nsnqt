# -*- coding:utf-8 -*-
from nsnqtlib.db.mongodb import MongoDB
import threading
import time
import datetime
import sys
import pandas as pd
import tushare as ts
from nsnqtlib.config import DB_SERVER, DB_PORT, USER, PWD, AUTHDBNAME


class strategy1(object):
    '''
    trading volume is the lowest in 60 days
    '''

    def __init__(self, stock="600455.SH"):
        self.m = MongoDB(DB_SERVER, DB_PORT, USER, PWD, AUTHDBNAME)

    def _getdata(self, db="ml_security_table", collection="600455.SH"):
        query = self.m.read_data(db, collection, filt={"date": {"$gt": datetime.datetime(2013, 1, 1, 0, 0, 0, 0)}})
        return self.m.format2dataframe(query)

    # 获取股票列表
    def import_stocklist(self, stocklistname):
        # df = pd.read_csv(str(stocklistname) + '.csv', parse_dates=['date'])
        df = pd.read_csv(str(stocklistname) + '.csv', parse_dates=['startdate'])
        return df

    def mean_volume(self, data):
        m_vol = sum(data) / len(data)
        return m_vol

    def buy_condition1(self, dat, vol, vol_data, close, last_high, maxprice, minprice, count, vol_weight=1.2):
        if self.condition1(vol, vol_data, vol_weight) and \
                self.condition2(close, last_high) and \
                self.condition3(close, maxprice) and \
                self.condition4(close, minprice):
            return True
        return False

    def buy_condition(self, dat, vol, vol_data, close, last_high, maxprice, minprice, count, parameter, vol_weight=1.2):
        if self.condition6(dat, parameter[1]) and \
                self.condition7(close, parameter[0]):
            return True
        return False

    def buy_condition2(self, dat, vol, vol_data, close, last_high, maxprice, minprice, count, parameter,
                       vol_weight=1.2):
        if self.condition8(close):
            return True
        return False

    def sell_conditon(self, buy_price, currentday_high, currentday_low, hold_days, gain_grads=0.1, loss_grads=-0.05,
                      dayout=10):
        if self.stopgain_condition(buy_price, currentday_high, gain_grads):
            return True, "stopgain"
        elif self.stoploss_condition(buy_price, currentday_low, loss_grads):
            return True, "stoploss"
        elif self.holdingtime_condition(hold_days, dayout):
            return True, "holdtime"
        return False, None

    def sell_conditon1(self, buy_price, currentday_high, currentday_low, hold_days, gain_grads=0.1, loss_grads=-0.05,
                       dayout=10):
        if self.condition9(close):
            return True, "Sold"
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

    def condition1(self, vol, vol_data, vol_weight=1.2):
        if vol >= vol_weight * self.mean_volume(vol_data):
            return True
        return False

    def condition2(self, close, last_high):
        if close >= last_high:
            return True
        return False

    def condition3(self, close, high, grads=0.2):
        if (high - close) / high >= grads:
            return True
        return False

    def condition4(self, close, low, grads=0.05):
        if (close - low) / low <= grads:
            return True
        return False

    def condition5(self, close, low, grads=0.05):
        if close <= 100:
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
        if close < 110:
            return True
        return False

    def condition9(self, close):
        if close > 120:
            return True
        return False

    def formatdata(self, stock, source="mongodb"):
        if source == "mongodb":
            df = self._getdata(collection=stock)
        elif source == "tushare":
            df = ts.get_hist_data(stock, start='2005-01-01', end='2016-11-18', )
            df.sort_index(inplace=True)
            df["date"] = df.index
            df["pre_close"] = df["close"] - df["price_change"]
            df.to_csv(stock + '.csv')
        return df

    def histofyreturn(self, parameter, db="ml_security_table", table="", source="mongodb"):
        buy = []
        stopgain = 0.1
        stoploss = -0.1
        vol_day = 10
        price_day = 60
        count = 60
        transaction_record = []
        df = self.formatdata(table, source)
        # df.to_csv(table+'.csv')
        lst = [l for l in df[["date", "volume", "close", "high", "low", "open", "pre_close"]].fillna(0).values if
               l[1] != 0]
        for line in lst[count:]:
            dat = line[0]
            vol = line[1]
            if vol == 0: continue
            close = line[2]
            last_high = lst[count - 1][3]
            vol_data = [i[1] for i in lst[count - vol_day:count]]
            maxprice = max([i[3]] for i in lst[count - price_day:count])[0]
            minprice = min([i[4]] for i in lst[count - price_day:count])[0]

            for b in buy[:]:
                d = b[0]
                c = b[1]
                buy_date = d[0]
                sell_date = line[0]
                hold_days = count - c
                buy_price = d[2]
                currentday_high = line[3]
                currentday_low = line[4]

                is_sell, selltype = self.sell_conditon(buy_price, currentday_high, currentday_low, \
                                                       hold_days, gain_grads=0.1, \
                                                       loss_grads=-0.05, dayout=10)
                if is_sell:
                    #print(buy)
                    #print(b)
                    buy.remove(b)
                    if selltype == "stopgain":
                        profit = stopgain
                    elif selltype == "stopgain":
                        profit = stoploss
                    else:
                        profit = (close - buy_price) / buy_price
                    transaction_record.append([table, buy_date, sell_date, hold_days, profit])
                    # print (profit)
                    # print(transaction_record)
            if self.buy_condition(dat, vol, vol_data, close, last_high, maxprice, minprice, count, parameter,
                                  vol_weight=1.2):
                buy.append(([i for i in line], count, table))
            count += 1
        # df_buy = pd.DataFrame(transaction_record)
        # df_buy.to_csv("test_tushare_buy_new.csv")
        return transaction_record, buy

    def filter_with_all_stocks(self, stocklist, source="mongodb"):
        error_list = []
        result = []
        buyresult = []
        for i in stocklist:
            print (i[0])
            startdate = i[1]
            cashprice = i[2]
            # try:
            r, buyed = self.histofyreturn(startdate, cashprice, table=i[0], source=source)
            # if r: result.extend(r)
            result.extend(r)
            print(result)
            if buyed: buyresult.extend(buyed)
            # except:
            #   error_list.append(i)
        return result, buyresult, error_list

    def filter_with_all_stocks_new(self, df, source="mongodb"):
        error_list = []
        result = []
        buyresult = []
        par = []
        count = 0
        df_len = len(df.index)
        column_num = len(df.count())
        while (count < df_len):
            columncount = 1
            # print(df.iat[0,1])
            par = []
            while (columncount < column_num):
                par.append(df.iat[count, columncount])
                columncount = columncount + 1
            print(par)
            # try:
            print(count)
            print(df.iat[count, 0])
            stock_name = str(df.iat[count, 0])
            print(stock_name)

            if len(stock_name) == 1:
                stock_name = '00000' + stock_name
            elif len(stock_name) == 2:
                stock_name = '0000' + stock_name
            elif len(stock_name) == 3:
                stock_name = '000' + stock_name
            elif len(stock_name) == 4:
                stock_name = '00' + stock_name
            elif len(stock_name) == 5:
                stock_name = '0' + stock_name
            print(stock_name)
            r, buyed = self.histofyreturn(par, table=stock_name, source=source)
            # if r: result.extend(r)
            result.extend(r)
            # if buyed: buyresult.extend(buyed)
            buyresult.extend(buyed)
            # except:
            error_list.append(stock_name)
            count = count + 1
        return result, buyresult, error_list


if __name__ == '__main__':
    s = strategy1()
    #     stocklist = s.m.getallcollections("ml_security_table")
    #     result,buyed,errorlist = s.filter_with_all_stocks(stocklist)

    # stocklist =  ts.get_stock_basics().index
    df_stocklist = s.import_stocklist("cashoption")
    print(df_stocklist)
    column_num = len(df_stocklist.count())
    # print(column_num)
    # print(df_stocklist)
    result, buyed, errorlist = s.filter_with_all_stocks_new(df_stocklist, "tushare")
    print('error code:')
    print(errorlist)

    # print(result)
    df = pd.DataFrame(result, columns=["stock", "buy_date", "sell_date", "holddays", "profit"])
    # print(df)
    df_buy = pd.DataFrame(buyed, columns=["date", "buy_data", "stock"])
    df_buy.to_csv("test_tushare_buy.csv")
    df.to_csv("test1_tushare.csv")

