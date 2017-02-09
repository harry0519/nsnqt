# -*- coding:utf-8 -*-
from nsnqtlib.strategies.strategy import basestrategy, reportforms
import pandas as pd
import tushare as ts
from datetime import datetime


class updatestocklist(basestrategy):

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

    def updatelist(self,df, db="strategyconfig", collection="FundBstrategy"):
        db = eval("self.m.client.{}".format(db))
        bulk = db[collection].initialize_ordered_bulk_op()
        for line in df.values:
            print(line[0])
            print(line[1])
            bulk.find({'stock': line[0]}).upsert().update( \
                {'$set': {'stock': line[0], \
                          'startprice': line[1], \
                          'status': ''
                          }})
        bulk.execute()
        return

if __name__ == '__main__':
    s = updatestocklist()
    df_stocklist = s.import_stocklist("fundb")
    print(df_stocklist)
    s.updatelist(df_stocklist)

    #df = self._getdata(collection, db, out=out, isfilt=False)




