

import numpy as np
import pandas as pd


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
#Max draw down
#input:
#    worth: net worth ratio history
#    period: To be added....
#         >0 means short-term MADD within input period -> worth list
def MDD(worth=[],period=0):
    current_mdd = mdd = 0
    for i in range(len(worth)):
        if period>0 and i>period: 
            j = i-period
        else: 
            j = 0
    
        if i > 0:
            current_mdd = max(worth[int(j):int(i)])-worth[i]
                              
        if mdd < current_mdd:
            mdd = current_mdd
    return mdd


    
#To be added:
#DMI related indicators
#KDJ
#RSI
#BIAS

if __name__ == '__main__':
    test = [11.9,10.8,20.0,9.1,7.9,4.1,31.2,16,29.9,15.1,11,12]
    print(MA(test,3))
    
