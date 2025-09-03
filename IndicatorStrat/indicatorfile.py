import numpy as np
import pandas as pd

class Indicators:
    def __init__(self, data):
        self.data = data  # DataFrame with OHLC (Open, High, Low, Close) prices
        self.close = data['Close']
    
    
class RSI(Indicators):
    def __init__(self, data, period=14):
        super().__init__(data)
        self.period = period

    def RSI(self):
        
        '''
    
        close: (m,) closing prices
        length: (int) duration to be considered for RSI calculation

        Returns:
        RSI: (m)  list with RSI values
    
    '''
        close=self.close
        length=self.period
        differ = close.diff()
        gain, loss = differ.copy(), differ.copy()
        gain[gain < 0] = 0
        loss[loss > 0] = 0

        avggain = gain.rolling(window=length).mean()
        avgloss = -loss.rolling(window=length).mean()
        rsi= 100.0 - (100.0*avgloss / (avggain+avgloss))

        self.data['RSI']=rsi
        self.data['RSISignal']=self.data['RSI'].apply(lambda x: 1 if x > 70 else (-1 if x < 30 else 0))
    
    @staticmethod
    def pivotid(df,i,n1=5,n2=5):
        if i-n1<0 or i+n2>=len(df):
            return 0
        
        pvidlow=1
        pvidhigh=1
        for k in range(i-n1,i+n2+1):
            if df['Low'][i]>df['Low'][k]:
                pvidlow=0
            if df['High'][i]<df['High'][k]:
                pvidhigh=0
        if pvidlow and pvidhigh:
            return 3
        elif pvidlow:
            return 1
        elif pvidhigh:
            return 2
        else:
            return 0
    
    @staticmethod
    def rsipivotid(df,i,n1=5,n2=5):
        if i-n1<0 or i+n2>=len(df):
            return 0
        
        pvidlow=1
        pvidhigh=1
        for k in range(i-n1,i+n2+1):
            if df['RSI'][i]>df['RSI'][k]:
                pvidlow=0
            if df['RSI'][i]<df['RSI'][k]:
                pvidhigh=0
        if pvidlow and pvidhigh:
            return 3
        elif pvidlow:
            return 1
        elif pvidhigh:
            return 2
        else:
            return 0
    
    @staticmethod
    def divsignal(df,x, backcandles):
        candleid=int(x.name)
        maxx=np.array([])
        mini=np.array([])
        xxmin=np.array([])
        xxmax=np.array([])
        
        maxRSI=np.array([])
        minRSI=np.array([])
        xxminRSI=np.array([])
        xxmaxRSI=np.array([])
        
        for i in range(candleid-backcandles,candleid+1):
            if df.iloc[i].pivot==1:
                mini=np.append(mini,df.iloc[i].Low)
                xxmin=np.append(xxmin,i)
            if df.iloc[i].pivot==2:
                maxx=np.append(maxx,df.iloc[i].high)
                xxmax=np.append(xxmax,i)
            if df.iloc[i].RSIpivot==1:
                minRSI=np.append(minRSI,df.iloc[i].RSI)
                xxminRSI=np.append(xxminRSI,df.iloc[i].name)
            if df.iloc[i].RSIpivot==2:
                maxRSI=np.append(maxRSI,df.iloc[i].RSI)
                xxminRSI=np.append(xxmaxRSI,df.iloc[i].name)
        
        if maxx.size<2 or mini.size<2 or maxRSI.size<2 or minRSI<2:
            return 0
        
        slmin,intercmin=np.polyfit(xxmin,mini,1)
        slmax,intercmax=np.polyfit(xxmax,maxx,1)
        slminRSI,intercminRSI=np.polyfit(xxminRSI,minRSI,1)
        slmaxRSI,intercmaxRSI=np.polyfit(xxmaxRSI,maxRSI,1)        
         
        if slmin > 1e-4 and slmax > 1e-4 and slmaxRSI<-0.1:
            return -1
        elif slmin < -1e-4 and slmax < -1e-4 and slminRSI>0.1:
            return 1
        else:
            return 0 
         
    def RSIDivergence(self):
        self.data['pivot']=self.data.apply(lambda x: self.pivotid(self.data,x.name,5,5),axis=1)
        self.data['RSIpivot']= self.data.apply(lambda x:self.rsipivotid(self.data,x.name,5,5),axis=1)
        self.data['divSignal']=self.data.apply(lambda row: self.divsignal(row,30),axis=1)
        

    
               
class SMA_EMA(Indicators):
    def __init__(self, data, period=50):
        super().__init__(data)
        self.period = period

    def SMA(self):
        '''
        Args:
        close: (m,) pandas series of closing prices
        length: (int) duration to be considered for SMA calculation

        Returns:
        SMA: pandas series with SMA values, including expanding SMA for the first (length-1) rows
        '''
        close=self.close
        length=self.period 
        expanding_sma = close.expanding().mean()

        rolling_sma = close.rolling(window=length).mean()

        SMA = expanding_sma.copy()  
        SMA[length-1:] = rolling_sma[length-1:]  

        self.data['SMA']=SMA
        return self
    
    def EMA(self):
        '''
        Args:
        close: (m,) pandas Series of closing prices
        length: (int) duration to be considered 

        Returns:
        EMA: pandas Series with EMA values

        '''
        close=self.close
        length=self.period 
        EMA = close.ewm(span=length,adjust=False).mean()
        self.data['EMA']=EMA
        
        return self
        

class MACD(Indicators):
    def __init__(self, data):
        super().__init__(data)
    def MACD(self):
        EMA12=self.close.ewm(span=12, adjust=False).mean()
        EMA26=self.close.ewm(span=26, adjust=False).mean()
        self.data['MACD']=EMA12-EMA26
        self.data['Signal_Line']=self.data['MACD'].ewm(span=9, adjust=False).mean()
        self.data['MACDSignal']=self.data['MACD'].apply(lambda x: 1 if  x['MACD']>x['Signal_Line'] else (-1 if  x['MACD']<x['Signal_Line'] else 0),axis=1)
    
        return self
    
class BB(SMA_EMA):
    
    def __init__(self, data):
        super().__init__(data)
     
    @staticmethod   
    def std(close,length):
        '''
        Args:
        close: (m,) pandas series of closing prices
        length: (int) duration to be considered for std calculation

        Returns:
        std: pandas series with standard deviation
        '''
        if isinstance(close, pd.DataFrame):
            close = close.squeeze()  # Convert single-column DataFrame to Series
        
        expanding_std = close.expanding().std()
        rolling_std = close.rolling(window=length).std()

        std = expanding_std.copy()  
        std[length-1:] = rolling_std[length-1:]  

        return std
    
           
    def bollingerbands(self):
        self.data['20 Day MA']=self.SMA(self)
        self.data['Upper']=self.data['20 Day MA']+2*self.std(self.data['Close'],20)
        self.data['Lower']=self.data['20 Day MA']-2*self.std(self.data['Close'],20)
        self.data['BBSignal']=self.data.apply(lambda x: 1 if x['Close']<x['Lower'] else(-1 if x['Close']>x['Upper'] else 0 ),axis=1)
            
        return self
