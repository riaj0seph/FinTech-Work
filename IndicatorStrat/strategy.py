import numpy as np
import pandas as pd
import yfinance as yf
from indicatorfile import Indicators,RSI, MACD, SMA_EMA, BB


class TradingStrategy:
    def __init__(self, data):
        self.data = data
        df=df[df['volume']!=0]
        df.reset_index(drop=True, inplace=True)
        
        
    def apply_strategy(self):
        tradebook=[]
        add={}
        self.data['Position Signal']=0
        '''
        Note:
        
        0 stands for no position
        1 stands for long
        -1 stands for short
        
        '''
        
        self.data = RSI(self.data).RSI().data
        self.data = MACD(self.data).MACD().data
        self.data = SMA_EMA(self.data, period=50).SMA().EMA().data
        self.data = BB(self.data).bollingerbands().data
        
        
        for i in range(len(self.data)):
            if self.data.loc[i,'BBSignal'] and self.data.loc[i,'MACDSignal'] and self.data.loc[i,'divSignal'] and self.data.loc[i,'RSISignal']:
                if self.data.loc[i,'Position Signal']==0:
                    #start a long trade
                    add['entry_date']=df.index[i]
                    add['entry_price']= df.iloc[i]['Close']
                    add['open']=df.iloc[i]['Open']
                    add['high']=df.iloc[i]['High']
                    add['low']=df.iloc[i]['Low']
                    add['trade_type']=1
                    self.data.loc[i:,'Position Signal']=1
                if self.data.loc[i,'Position Signal']==-1:
                    #exit the trade
                    self.data.loc[i:,'Position Signal']=0
                    add['exit_date']=df.index[i]
                    add['exit_price']=df.iloc[i]['Close']
                    tradebook.append(add)
                    add={}
            if not self.data.loc[i,'BBSignal'] or self.data.loc[i,'MACDSignal'] or self.data.loc[i,'divSignal'] or self.data.loc[i,'RSISignal']:
                if self.data.loc[i,'Position Signal']==0:
                    #start a short trade
                    add['entry_date']=df.index[i]
                    add['open']=df.iloc[i]['Open']
                    add['high']=df.iloc[i]['High']
                    add['low']=df.iloc[i]['Low']
                    add['entry_price'] = df.iloc[i]['Close']
                    add['trade_type']=-1
                    self.data.loc[i:,'Position Signal']=-1
                if self.data.loc[i,'Position Signal']==1:
                    #exit the trade; stoploss for a long trade
                    self.data.loc[i:,'Position Signal']=0 
                    add['exit_date']=df.index[i]
                    add['exit_price']=df.iloc[i]['Close']
                    tradebook.append(add)
                    add={}  


# getting the data
end_date=yf.datetime.today()
start_date=end_date-yf.timedelta(days=4*365)
df=pd.DataFrame()
df=yf.download("AAPL",start=start_date,end=end_date)


# applying indicators
df = TradingStrategy(df).apply_strategy().data



       
        