
# coding: utf-8

# In[29]:

import numpy as np
import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
#import seaborn as sns
get_ipython().magic('matplotlib inline')
#sns.set_style('white')

window_short = 20
window_long = 120
SD = 0.05

# 定义导入数据函数，分析数据函数
def import_data( stock, start, end ):
    df = ts.get_h_data(stock, start=start, end=end).sort_index(ascending=True)
    #df.head(10);
    print(df.head(10));
    return df;

def analyze_data( df ):
    df['short_window'] = pd.rolling_mean(df.close,window_short)
    #df['short_window'] = pd.Series.rolling(window=20,center=False,'self').mean()
    df['long_window'] = pd.rolling_mean(df.close,window_long)
    #df['long_window'] = pd.Series.rolling(window=120,center=False).mean()
    df['s-l'] = df['short_window'] - df['long_window']
    
    df['Regime'] = np.where(df['s-l'] > df['long_window'] * SD, 1, 0)
    df['Regime'].value_counts()
    
    #print(df[['close','ave20','ave120','s-l']]);
    print(df['Regime'].value_counts());
    #df[['close','ave20','ave120','s-l']].plot(figsize=(20, 12))
    df['Regime'].plot(grid=False, lw=1.5, figsize=(12,8))
    plt.ylim((-0.1,1.1))
    #sns.despine()
    return;

def trade_result( df ):
    df['Market'] = np.log(df['close'] / df['close'].shift(1))
    df['Strategy'] = df['Regime'].shift(1) * df['Market']
    print(df[['Market', 'Strategy', 'Regime']].tail())
    df[['Market', 'Strategy']].cumsum().apply(np.exp).plot(grid=False, figsize=(12,8))
    return;

# 调用函数
stock_data = import_data('002202','2008-01-01','2015-04-23')
analyze_data(stock_data)
trade_result(stock_data)
#list_trade_Oppt()
#send mail()


# In[ ]:




# In[ ]:



