# -*- coding: utf-8 -*-
import easytrader
import random
from nsnqtlib.strategies.ETFGRIDStrategy import ETFstrategy
from nsnqtlib.strategies.moneyfundstrategy import moneyfundstrategy
from nsnqtlib.strategies.cashoption_strategy import cashoptionstrategy
from nsnqtlib.strategies.convertiblebondstrategy import convertiblebondstrategy
from nsnqtlib.strategies.FundBGRIDStrategy import FundBstrategy
from click.decorators import password_option
from nsnqtlib.config import DB_SERVER, DB_PORT, USER, PWD, AUTHDBNAME
from  nsnqtlib.db.mongodb import MongoDB
from datetime import datetime
import tushare as ts
import argparse
from nsnqtlib.mail import mail
import pandas as pd

class trade():
    def __init__(self, user="wangxian.111@163.com", password="nokiax56wang", zuhe="ZH1008383"):
        self.user = easytrader.use('xq')
        self.user.prepare(user=user, password=password, portfolio_code=zuhe)
        self.buylist = []
        self.selllist = []
        self.limitnum = 20
        self.m = MongoDB()

    def getcurrentdata(self):
        '''code：代码, name:名称 ,changepercent:涨跌幅 , trade:现价 ,open:开盘价 ,high:最高价, low:最低价, settlement:昨日收盘价 ,
           volume:成交量 ,turnoverratio:换手率 ,amount:成交量 ,per:市盈率 ,pb:市净率, mktcap:总市值 ,nmc:流通市值
        '''
        out = ["code", "trade", "open", "high", "low", "settlement"]
        rst = ts.get_today_all()
        return rst[out]

    def getbuylist(self, filename="procedure_records.csv"):
        s = macd()
        self.buylist = s.getprocedure(isdb=True)
        return self.buylist

    def justsellit(self, db="macd", collection="operatequeue", stoploss=False):
        currentdata = {i[0]: i for i in self.getcurrentdata().values}
        rst = self.m.read_data(db, collection, filt={"status": "HOLD"})
        position = self.getposition()
        for i in rst:
            stock = i["stock"]
            for xq in position:
                if stock == xq["stock_code"][2:]:
                    rate = xq["market_value"] / i["buymoney"]
                    print ("check stock:{}       rate:{}".format(stock, rate))
                    print (i)
                    print (xq)
                    print ("********************")
                    bias = 1
                    if stoploss:
                        bias = currentdata[stock][4] / currentdata[stock][1]
                    self.trysell(stock, rate, stoploss, bias=bias)
                    break

    def trysell(self, stock, rate, stoploss=False, bias=1):
        if stoploss and rate / bias <= 0.9:
            self.sell(stock=stock, number=100, price=0.55)
            self.updateholdlst(stock)
        elif rate >= 1.1:
            self.sell(stock=stock, number=100, price=0.55)
            self.updateholdlst(stock)

    def updateholdlst(self, stock, db="macd", collection="operatequeue"):
        data = {'$set': {'status': 'SELL'}}
        self.m.update_data(data, db, collection, filt={"stock": stock})

    def getholdlst(self, holddate, db="etfgrid", collection="operatequeue"):
        out = ["stock", "buymoney", "date", "startprice", "status"]
        #df = self.m._getdata(collection, db, out=out, filt={"date": holddate})
        #df = self.m.read_data(db, collection, filt={"date": holddate})
        #df = self.m.read_data(db, collection)
        df = self.m.read_data(db, collection, filt={"status": "HOLD"})
        #if isfilt and not filt: filt = {"date": {"$gt": self.startdate}}
        #query = self.m.read_data(db, collection, filt=filt)
        print('hold list:')
        print(df)
        #holdlist = [l for l in df[['date', 'startprice', "buytimes", 'close']].values]
        return
        #data = {'$set': {'status': 'SELL'}}
        #self.m.update_data(data, db, collection, filt={"stock": stock})

    def buyitnow(self):
        localbackup = []
        holdlist = []
        tradedate = datetime.today().strftime('%Y-%m-%d')
        holdlist = self.getholdlst(tradedate)
        print(holdlist)
        balance = self.getbalance()
        lst = self.getposition()
        holdnum = len(lst)
        leftmony = balance[0]["current_balance"]
        couldbynum = self.limitnum - holdnum
        holdlst = [i["stock_code"][2:] for i in lst]
        couldbuylst = [i for i in self.buylist if i not in holdlst]
        triggerbuynum = len(couldbuylst)
        print ("could buy list:{}".format(self.buylist))
        if couldbynum > 0:
            permoney = leftmony / couldbynum
            if triggerbuynum > couldbynum:
                buylst = random.sample(couldbuylst, couldbynum)
            else:
                buylst = couldbuylst
        else:
            buylst = []

        for stock in buylst:
            try:
                t.buy(stock=stock, number=permoney, price=1)
                localbackup.append({"stock": stock, "buymoney": permoney, "date": datetime.today().strftime('%Y-%m-%d'),
                                    "status": "HOLD"})
            except:
                print ("buy {} failed!!!!".format(stock))
        return localbackup

    def connetdb(self):
        self.m = MongoDB(DB_SERVER, DB_PORT, USER, PWD, AUTHDBNAME)
        return self.m

    def savebackup2db(self, data, db="etfgrid", collection="operatequeue"):
        if not data: return
        db = eval('self.m.client.{}'.format(db))
        db[collection].insert_many(data)
        return

    def getbalance(self):
        '''output:[{ 'asset_balance': '资产总值','current_balance': '当前余额','enable_balance': '可用金额','market_value': '证券市值',
                    'money_type': '币种','pre_interest': '预计利息' }]
        '''
        return self.user.balance

    def getposition(self):
        '''output:[{'cost_price': '摊薄成本价','current_amount': '当前数量','enable_amount': '可卖数量','income_balance': '摊薄浮动盈亏','keep_cost_price': '保本价',
                    'last_price': '最新价','market_value': '证券市值','position_str': '定位串','stock_code': '证券代码','stock_name': '证券名称'}]
        '''
        return self.user.position

    def getentrust(self):
        '''获取今日委托单
          output：[{'business_amount': '成交数量', 'business_price': '成交价格','entrust_amount': '委托数量','entrust_bs': '买卖方向','entrust_no': '委托编号','entrust_price': '委托价格',
           'entrust_status': '委托状态', 废单 / 已报   'report_time': '申报时间', 'stock_code': '证券代码', 'stock_name': '证券名称'}]
        '''
        return self.user.entrust

    def buy(self, stock="600461", number=10000, price=0):
        self.user.buy(stock, price=price, amount=number)

    def cancel(self, entrust):
        '''entrust:委托单号
        '''
        self.user.cancel_entrust(entrust)

    def cancelall(self):
        entrust = [i for i in self.getentrust() if i["entrust_status"] == "已报" and i["entrust_bs"] == "买入"]
        for i in entrust:
            flash_entrust = [i for i in self.getentrust() if i["entrust_status"] == "已报" and i["entrust_bs"] == "买入"]
            entrust_no = flash_entrust[0]["entrust_no"]
            self.cancel(entrust_no)
        return

    def sell(self, stock="600461", number=100, price=0.55):
        self.user.sell(stock, price=price, amount=number)

    def adjust_weight(self, stock='000001', weight=10):
        self.user.adjust_weight(stock, weight)

    def updatebuyoppor(self,buyopporlist,lst,tradetype):
        #buyopporlist = []
        if not lst: return buyopporlist
        for line in lst:
            buyopporlist.append({"stock": line, "tradetype": tradetype})
        return buyopporlist

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str)
    parser.add_argument("-s", "--stoploss", action="store", type=str,
                        dest="stoploss",
                        help="stoploss now")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    trading_records = []
    holding_records = []
    bylst = []
    dailybuyoppor = []
    t = trade()
    #t.connetdb()

    '''
    #ETF网格交易策略
    s = ETFstrategy()
    df_stocklist = s.import_stocklist("ETFGrid_new")
    #s.looplist_historyreturn(df_stocklist, actiontype="trade")
    trading_records, holding_records, t.buylist, t.selllist = s.looplist_historyreturn(df_stocklist,actiontype="trade")
    print('ETF Grid Strategy buy list:')
    print(t.buylist)
    #bylst = t.buyitnow()
    print ("buy list:{}".format(bylst))
    dailybuyoppor = t.updatebuyoppor(dailybuyoppor,t.buylist,'ETFGrid')
    print(dailybuyoppor)
    '''


    #现金管理交易策略
    moneyfund = moneyfundstrategy()
    #df_stocklist = s.import_stocklist("moneyfundstrategy")
    formatlist = ['stock', 'status']
    df_stocklist = moneyfund._getdata('moneyfundstrategy', 'strategyconfig', formatlist, isfilt=False)
    #df_stocklist = moneyfund._getdata('moneyfundstrategy', 'strategyconfig',formatlist,isfilt=False)
    print(df_stocklist)

    #s.setlooplist()
    #getprocedure(self, filename="procedure_records.csv", isdb=False, collection="processstatus", db="etfgrid")

    trading_records, holding_records, t.buylist, t.selllist = moneyfund.looplist_historyreturn(df_stocklist, actiontype="trade")
    print('Money fund Strategy buy list:')
    print(t.buylist)
    bylst = t.buyitnow()
    print ("buy list:{}".format(bylst))
    dailybuyoppor = t.updatebuyoppor(dailybuyoppor, t.buylist, 'moneyfund')

    '''
    #现金选择权交易策略
    cashoption = cashoptionstrategy()
    df_stocklist = s.import_stocklist("cashoption")
    print(df_stocklist)
    #s.setlooplist()
    #getprocedure(self, filename="procedure_records.csv", isdb=False, collection="processstatus", db="etfgrid")
    trading_records, holding_records, t.buylist, t.selllist = cashoption.looplist_historyreturn(df_stocklist, actiontype="trade")
    print('Money fund Strategy buy list:')
    print(t.buylist)
    dailybuyoppor = t.updatebuyoppor(dailybuyoppor, t.buylist, 'cashoption')

    #可转债交易策略
    convertiblebond = convertiblebondstrategy()
    df_stocklist = s.import_stocklist("convertiblebond")
    print(df_stocklist)
    #s.setlooplist()
    #getprocedure(self, filename="procedure_records.csv", isdb=False, collection="processstatus", db="etfgrid")
    trading_records, holding_records, t.buylist, t.selllist = convertiblebond.looplist_historyreturn(df_stocklist, actiontype="trade")
    print('onvertible bond Strategy buy list:')
    print(t.buylist)
    dailybuyoppor = t.updatebuyoppor(dailybuyoppor, t.buylist, 'convertiblebond')
    '''


    #B级基金网格交易策略
    s = FundBstrategy()
    #s = eval('FundBstrategy()')
    #print('successfully')
    #df_stocklist = s.import_stocklist("fundb")
    #df_stocklist = s._getdata('FundBstrategy', 'strategyconfig')
    formatlist = ['stock', 'startprice', 'status']
    df_stocklist = s._getdata('FundBstrategy', 'strategyconfig',formatlist,isfilt=False)
    print(df_stocklist)

    #s.looplist_historyreturn(df_stocklist, actiontype="trade")
    trading_records, holding_records, t.buylist, t.selllist = s.looplist_historyreturn(df_stocklist,actiontype="trade")
    print('Fund B Grid Strategy buy list:')
    print(t.buylist)
    bylst = t.buyitnow()
    print ("buy list:{}".format(bylst))
    dailybuyoppor = t.updatebuyoppor(dailybuyoppor,t.buylist,'FundB')
    print(dailybuyoppor)

    df = pd.DataFrame(dailybuyoppor)
    print(df)


    '''
    m = mail.mail()
    m.setmessage("buylist:{}".format(bylst))
    m.sendmail()
    m.disconnect()
    '''
    t.savebackup2db(bylst)
    #for stock in t.selllist:
     #   t.sell(stock)



    #bylst = t.buyitnow()
    #print ("buy list:{}".format(bylst))
    #t.savebackup2db(bylst)
    '''
    if parseargs().action == "sell":
        t.connetdb()
        if parseargs().stoploss:
            t.justsellit(stoploss=True)
        else:
            t.justsellit()

    elif parseargs().action == "buy":
        #         print (t.user.session.get("https://xueqiu.com/p/update?action=holdings&symbol=ZH995042").text)
        #         t.cancelall()
        t.getbuylist()
        bylst = t.buyitnow()
        print ("buy list:{}".format(bylst))
        t.savebackup2db(bylst)
    '''
