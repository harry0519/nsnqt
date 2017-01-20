

import numpy as np
import pandas as pd
import datetime as dt
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import calendar


#Moving average
def MA(data=[], timeperiod=10):
    ma = []
    ma_a = pd.DataFrame(data,columns=['MA']).rolling(window=timeperiod).mean()
    for i in ma_a['MA']:
        ma.append(i)
    return ma
    
#MACD related indicators
#Moving average: there will be unstable period in the beginning
#input: list of close price
def EMA(close=[], timeperiod=10):
    ema = []
    current = close[0]
    for i in close:
        current = (current*(timeperiod-1)+ 2*i)/(timeperiod+1)
        ema.append(current)
    return ema
            
def DIF(close=[], fastperiod=12, slowperiod=26):
    dif = []
    s_ema = EMA(close, slowperiod)
    f_ema = EMA(close, fastperiod)
    for i in range(len(close)):
        dif.append(f_ema[i]-s_ema[i])
    return dif
    
def DEA(close=[], fastperiod=12, slowperiod=26, signalperiod=9):
    dif = DIF(close,fastperiod,slowperiod)
    return EMA(dif, signalperiod)
    
def MACD(close=[], fastperiod=12, slowperiod=26, signalperiod=9):
    macd = []
    dif = DIF(close,fastperiod,slowperiod)
    dea = EMA(dif, signalperiod)
    for i in range(len(close)):
        macd.append(2*(dif[i]-dea[i]))
    return macd

    
# 夏普比率： 平均收益率/收益率标准差
#Sharpe Ratio: Sharpe ratio = Excess return / Standard deviation
#input: 
#    erp: Portfolio expected return rate 
#         within fixed timeperiod (e.g.yearly/monthly) 
#    rf: risk-free/expect rate of interest  
def sharpe(erp=[], rf=0):
    a = np.array(erp)
    return (np.mean(a)-rf)/np.std(a,ddof=1)

#最大回撤率
#Max draw down ratio
#input:
#    accumulated: accumulated money history
#    period: To be added....
#         >0 means short-term MADD within input period -> worth list
def MDD(accumulated=[],period=0):
    current_mdd = mdd = 0
    for i in range(len(accumulated)):
        if period>0 and i>period: 
            j = i-period
        else: 
            j = 0
    
        if i > 0:
            top = max(accumulated[int(j):int(i)])
            current_mdd = (top - accumulated[i])/top
                              
        if mdd < current_mdd:
            mdd = current_mdd
    return mdd


    
#To be added:
#DMI related indicators
#KDJ
#RSI
#BIAS

#日净值历史
def daily_accumulated(principal,trade_history):
    '''
    Daily accumulated money
    input: 
        principal: initial invest money
        trade_history: stock buy-in and sell-out history. format should be
            "index(title is none)","stock","buy_date","sell_date","holddays","profit","buy_money"
            date format: %Y-%m-%d
    output:
        dict:{date:total_money}   !!no order for dict
              Daily accumulated history during whole trade
    '''
    df = trade_history[["stock","buy_date","sell_date","holddays","profit","buy_money"]]
    
    start_date = min(dt.datetime.strptime(i, "%Y-%m-%d") for i in df["buy_date"].values)
    end_date = max(dt.datetime.strptime(i, "%Y-%m-%d") for i in df["sell_date"].values)

    datelist = [i.strftime('%Y-%m-%d') for i in pd.date_range(start_date, end_date)]
    sell_history = {d:[] for d in datelist}
    current_money = {d:0 for d in datelist}

    for i in df.values:
        selldate = i[2]
        sell_history[dt.datetime.strptime(selldate,"%Y-%m-%d").strftime("%Y-%m-%d")].append(i)

    current = principal
    for date in datelist:
        if len(sell_history[date]) > 0:
            for sell_stock in sell_history[date]:
                current = current + sell_stock[4]*sell_stock[5]
        current_money[date] = current

    '''    
    newdf = pd.DataFrame(data=[current_money[i] for i in datelist], \
                               index=datelist,columns=["totalmoney"])
    newdf["date"] = newdf.index
    newdf.plot(x="date", y="totalmoney", kind='area')
    plt.savefig("positiongain_from_{}_to_{}.png".format(start_date.strftime("%Y_%m_%d"),end_date.strftime("%Y_%m_%d")))
    plt.show()
    '''
    return current_money

#月净值历史, 月度年化收益率
#结算日：月末最后一天
def monthly_accumulated(principal,trade_history):
    '''
    Daily accumulated money
    input: 
        principal: initial invest money
        trade_history: stock buy-in and sell-out history. format should be
            "index(title is none)","stock","buy_date","sell_date","holddays","profit","buy_money"
            date format: %Y-%m-%d
    output:
        dict:{date:[total_money,growth_ratio,annual_yield]}   !!no order for dict
              Monthly accumulated history during whole trade
    '''
    daily = daily_accumulated(principal,trade_history)
    date_list = sorted(daily.keys())
    start_date = date_list[0]
    end_date = date_list[-1]

    enddatelist = [i.strftime('%Y-%m-%d') \
                for i in pd.date_range(start_date, end_date, freq='M')]
    monthlist = [i.strftime('%Y-%m') \
                for i in pd.date_range(start_date, end_date, freq='M')]
    monthly_money = {d:[0,0,0] for d in monthlist}

    last_money = principal
    for date in enddatelist:
        date_time = dt.datetime.strptime(date,"%Y-%m-%d")
        month = date_time.strftime("%Y-%m")
        total_money = daily[date]
        growth = total_money/last_money-1
        annual_yield = growth * 365 / \
            calendar.monthrange(date_time.year, date_time.month)[1]
        monthly_money[month] = [total_money,growth,annual_yield]
        last_money = daily[date]

    '''
    newdf = pd.DataFrame(data=[monthly_money[i] for i in monthlist], \
                               index=monthlist,columns=["totalmoney","growth","annualyield"])
    newdf["month"] = newdf.index
    newdf.plot(x="month", y="totalmoney", kind='area')
    plt.show()
    print(newdf)
    '''
    return monthly_money
    
#评估结果（基于月度收益评估）：夏普比率，最大回撤率
def evaluation_m(principal,trade_history):
    '''
    Daily accumulated money
    input: 
        principal: initial invest money
        trade_history: stock buy-in and sell-out history. format should be
            "index(title is none)","stock","buy_date","sell_date","holddays","profit","buy_money"
            date format: %Y-%m-%d
    output:
        Sharpe: sharpe ratio
        MDD:max draw down
    '''
    accumulated = []
    erp = []
    monthly = monthly_accumulated(principal,trade_history)
    month_list = sorted(monthly.keys())
    
    for month in month_list:
        accumulated.append(monthly[month][0])
        erp.append(monthly[month][2])
    
    return sharpe(erp),MDD(accumulated)

''' for debug
if __name__ == '__main__':
    #test = [11.9,10.8,20.0,9.1,7.9,4.1,31.2,16,29.9,15.1,11,12]
    #print(MA(test,3))
    df = pd.read_csv('positiongain.csv')
    print(evaluation_m(100,df))
'''   
