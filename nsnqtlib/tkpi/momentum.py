

#Moving average: there will be unstable period in the beginning
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

