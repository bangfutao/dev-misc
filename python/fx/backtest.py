from datetime import datetime, timedelta
from zipfile import ZipFile
import pandas as pd
import pandas_ta as ta
import numpy as np
from matplotlib.widgets import Cursor
import matplotlib.pyplot as plt
import mplcursors
from dateutil import parser
import enum


import time, requests
import os, sys, io
import glob


def main():
   dataStatsManager = DataStatsManager()    
   dataStatsManager.ticker_stats_calc('EURUSD')


###############################################################################
class OrderType(enum.Enum):
    NONE = 0
    LONG = 1
    SHORT = 2
    EXIT = 3
    CANCEL = 4
        
class PositionType(enum.Enum):
    NONE = 0
    LONG = 1
    SHORT = 2

class ForexSize(enum.Enum):
    STANDARD_LOT = 100000
    MINI_LOT = 10000
    MICRO_LOT = 1000

class Broker():
    def __init__(self, df, size = ForexSize.STANDARD_LOT):
        self.df = df
        self.size = size
        self.order = OrderType.NONE         # requesting only
        self.postion = PositionType.NONE    # filled / positioned
        self.orders = []
        self.orders_df = pd.DataFrame()

    def excute_order(self, price, df_index):
        if self.order == OrderType.EXIT:
            if len(self.orders) > 0:
                order = self.orders[-1]
                order['exit_price'] = price
                delt = (order['exit_price'] - order['entry_price'])
                if (order['order_type'] == OrderType.SHORT):
                    delt = - delt
                order['profit_loss'] = delt * self.size  # convert pips to money
                order['exit_index'] = df_index
                self.orders[-1] = order
            self.order = OrderType.NONE
            return

        if self.order == OrderType.LONG:
            dict = {'order_type': OrderType.LONG, 'entry_price': price, 'exit_price': 0, 'profit_losss': 0, 'entry_index': df_index, 'exit_index': 0}
            self.orders.append(dict)
            self.order = OrderType.NONE
            self.postion = PositionType.LONG
            return

        if self.order == OrderType.SHORT:
            dict = {'order_type': OrderType.SHORT, 'entry_price': price, 'exit_price': 0, 'profit_losss': 0, 'entry_index': df_index, 'exit_index': 0}
            self.orders.append(dict)
            self.order = OrderType.NONE
            self.postion = PositionType.SHORT
            return
        

    def send_order(self, type):
        if (self.order != OrderType.NONE):
            return False
        if (self.postion != PositionType.NONE):
            return False
        self.order = type
        return True

    def get_orders_df(self):
        self.orders_df = pd.DataFrame(self.orders)
        return self.orders_df


class SecurityInfo():
    def __init__(self, ticker_name = ""):
        self.ticker_name = ticker_name
        self.csv_file_name = "data/datasets/"+ticker_name+'.csv'
        self.df = {}
        self.broker = Broker(self.df)

    def load_dataframe(self, df_header):
        self.df = pd.read_csv(self.csv_file_name)
        self.df.columns = df_header.split(',')

class DataStatsManager():
    def __init__(self):
        self.count = 0
        self.csv_header = "<TICKER>,<DTYYYYMMDD>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>"
        self.df_header = "Ticker,Date,Time,Open,High,Low,Close"
        self.tickers_map = {
        'EURUSD': SecurityInfo(ticker_name = 'EURUSD'),
        'GBPUSD': SecurityInfo(ticker_name = 'GBPUSD'),
        'USDCHF': SecurityInfo(ticker_name = 'USDCHF'),
        'USDJPY': SecurityInfo(ticker_name = 'USDJPY'),
        'EURGBP': SecurityInfo(ticker_name = 'EURGBP'),
        'EURCHF': SecurityInfo(ticker_name = 'EURCHF'),
        'EURJPY': SecurityInfo(ticker_name = 'EURJPY'),
        'GBPCHF': SecurityInfo(ticker_name = 'GBPCHF'),
        'GBPJPY': SecurityInfo(ticker_name = 'GBPJPY'),
        'CHFJPY': SecurityInfo(ticker_name = 'CHFJPY'),
        'USDCAD': SecurityInfo(ticker_name = 'USDCAD'),
        'EURCAD': SecurityInfo(ticker_name = 'EURCAD'),
        'AUDUSD': SecurityInfo(ticker_name = 'AUDUSD'),
        'AUDJPY': SecurityInfo(ticker_name = 'AUDJPY'),
        'NZDUSD': SecurityInfo(ticker_name = 'NZDUSD'),
        'NZDJPY': SecurityInfo(ticker_name = 'NZDJPY'),
        'XAUUSD': SecurityInfo(ticker_name = 'XAUUSD'),
        'XAGUSD': SecurityInfo(ticker_name = 'XAGUSD'),
        'USDCZK': SecurityInfo(ticker_name = 'USDCZK'),
        'USDDKK': SecurityInfo(ticker_name = 'USDDKK'),
        'USDHUF': SecurityInfo(ticker_name = 'USDHUF'),
        'USDNOK': SecurityInfo(ticker_name = 'USDNOK'),
        'USDPLN': SecurityInfo(ticker_name = 'USDPLN'),
        'USDSEK': SecurityInfo(ticker_name = 'USDSEK'),
        'USDSGD': SecurityInfo(ticker_name = 'USDSGD'),
        'USDZAR': SecurityInfo(ticker_name = 'USDZAR'),
        'USDHKD': SecurityInfo(ticker_name = 'USDHKD'),
        'USDMXN': SecurityInfo(ticker_name = 'USDMXN'),
        'USDTRY': SecurityInfo(ticker_name = 'USDTRY'),
        'EURHKD': SecurityInfo(ticker_name = 'EURHKD'),
        'EURMXN': SecurityInfo(ticker_name = 'EURMXN'),
        'EURTRY': SecurityInfo(ticker_name = 'EURTRY'),
        'EURAUD': SecurityInfo(ticker_name = 'EURAUD'),
        'EURNZD': SecurityInfo(ticker_name = 'EURNZD'),
        'EURSGD': SecurityInfo(ticker_name = 'EURSGD'),
        'EURZAR': SecurityInfo(ticker_name = 'EURZAR'),
        'XAUEUR': SecurityInfo(ticker_name = 'XAUEUR'),
        'XAGEUR': SecurityInfo(ticker_name = 'XAGEUR'),
        'GBPCAD': SecurityInfo(ticker_name = 'GBPCAD'),
        'GBPAUD': SecurityInfo(ticker_name = 'GBPAUD'),
        'GBPNZD': SecurityInfo(ticker_name = 'GBPNZD'),
        'AUDCHF': SecurityInfo(ticker_name = 'AUDCHF'),
        'AUDCAD': SecurityInfo(ticker_name = 'AUDCAD'),
        'AUDNZD': SecurityInfo(ticker_name = 'AUDNZD'),
        'NZDCHF': SecurityInfo(ticker_name = 'NZDCHF'),
        'NZDCAD': SecurityInfo(ticker_name = 'NZDCAD'),
        'CADCHF': SecurityInfo(ticker_name = 'CADCHF'),
        'CADJPY': SecurityInfo(ticker_name = 'CADJPY'),
        'USDCNH': SecurityInfo(ticker_name = 'USDCNH'),
        'BTCUSD': SecurityInfo(ticker_name = 'BTCUSD'),
        'ETHUSD': SecurityInfo(ticker_name = 'ETHUSD'),
        'LTCUSD': SecurityInfo(ticker_name = 'LTCUSD'),
        'USDILS': SecurityInfo(ticker_name = 'USDILS'),
        'EURILS': SecurityInfo(ticker_name = 'EURILS'),
        'EURNOK': SecurityInfo(ticker_name = 'EURNOK'),
        'EURSEK': SecurityInfo(ticker_name = 'EURSEK'),
        'EURDKK': SecurityInfo(ticker_name = 'EURDKK'),
        'EURCZK': SecurityInfo(ticker_name = 'EURCZK'),
        'EURHUF': SecurityInfo(ticker_name = 'EURHUF'),
        'EURPLN': SecurityInfo(ticker_name = 'EURPLN'),
        'EURCNH': SecurityInfo(ticker_name = 'EURCNH'),
        'WTIUSD': SecurityInfo(ticker_name = 'WTIUSD'),
        'DJIUSD': SecurityInfo(ticker_name = 'DJIUSD'),
        'SPXUSD': SecurityInfo(ticker_name = 'SPXUSD'),
        'NDQUSD': SecurityInfo(ticker_name = 'NDQUSD'),
        'GASUSD': SecurityInfo(ticker_name = 'GASUSD'),
        'BTCEUR': SecurityInfo(ticker_name = 'BTCEUR'),
        'ETHEUR': SecurityInfo(ticker_name = 'ETHEUR'),
        'LTCEUR': SecurityInfo(ticker_name = 'LTCEUR')
        }

    
    def ticker_stats_calc(self, ticker_symbol):
        security = self.tickers_map[ticker_symbol]
        security.load_dataframe(self.df_header)
        #print(security.stats)
        #security.stats = "TO DO"
        #print(security.stats)
        #security.df['ema200'] = ta.ema(security.df['Close'], length=200)
        #security.df['ema400'] = ta.ema(security.df['Close'], length=200*2)
        #security.df['ema600'] = ta.ema(security.df['Close'], length=200*3)
        #security.df['ema800'] = ta.ema(security.df['Close'], length=200*4)
        #security.df['ema1000'] = ta.ema(security.df['Close'], length=200*5)
        #security.df['ema1200'] = ta.ema(security.df['Close'], length=200*6)
        #security.df['ema3000'] = ta.ema(security.df['Close'], length=50*60)
        security.df['sma_long'] = ta.sma(security.df['Close'], length=50*60)
        security.df['sma_mid'] = ta.sma(security.df['Close'], length=50*15)
        macd_df = ta.macd(security.df['Close'], 12*5, 26*5)
        #print(macd_df)
        """
                MACD_12_26_9  MACDh_12_26_9  MACDs_12_26_9
        0                NaN            NaN            NaN
        1                NaN            NaN            NaN
        2                NaN            NaN            NaN
        3                NaN            NaN            NaN
        4                NaN            NaN            NaN
        ...              ...            ...            ...
        932300     -0.000013      -0.000007      -0.000006
        932301     -0.000014      -0.000006      -0.000008
        932302     -0.000014      -0.000005      -0.000009        

        """
        security.df['macd_line'] = macd_df.iloc[:, 2]  # diff
        security.df['macd_signal'] = ta.ema(security.df['macd_line'], length=9*5) # extra filter
        security.df['macd_histogram'] = security.df['macd_line'] - security.df['macd_signal']

        #print(security.df.head(10))
        print(security.df)


        #print(security.df.loc[3, ['Date', 'Time']])
        #row = security.df.loc[3, ['Date', 'Time']]

        #print("row:")
        #print(row)

        #d = security.df.at[3, 'Date']
        #t = security.df.at[3, 'Time']
        #print(f"{d}-{t}")

        #print(security.df.loc[3, ['Date']] )
        #print(security.df.loc[3, ['Time']] )
        #security.df['Close'].plot(style='.-', title=f"{ticker_symbol}")
        #plt.grid()
        #plt.show()

        #stats = {'daily_range': [], '2h_range': [], '1h_range': [], '30m_range': []}
        #self.df_daily = self.resample('daily')
        #self.df_2h = self.resample('2h')
        #self.df_1h = self.resample('1h')
        #self.df_30m = self.resample('30m')
        #self.df_15m = self.resample('15m')
        #self.df_5m = self.resample('5m')

        fig, (ax1, ax2) = plt.subplots(2, 1)
        #ax = fig.add_axes(security.df['Close'])
        #ax.plot(list(security.df.index.values), security.df['Close'], linestyle='-.')
        #cursor = Cursor(ax, color='pink', linewidth=0.5)
        df_size = security.df.shape[0]
        data_start = df_size - 100*24*60;
        data_end = df_size
        print(f"df_size={df_size}")
        ax1.plot(security.df.index[data_start:data_end], security.df['Close'][data_start:data_end], linestyle='-', marker='.', label='price')
        #ax.plot(security.df.index[0:24*60*num_days+1], security.df['ema200'][0:24*60*num_days+1], linestyle='-', marker='.', label='ema200')
        #ax.plot(security.df.index[0:24*60*num_days+1], security.df['ema400'][0:24*60*num_days+1], linestyle='-', marker='.', label='ema400')
        #ax.plot(security.df.index[0:24*60*num_days+1], security.df['ema600'][0:24*60*num_days+1], linestyle='-', marker='.', label='ema600')
        #ax.plot(security.df.index[0:24*60*num_days+1], security.df['ema800'][0:24*60*num_days+1], linestyle='-', marker='.', label='ema800')
        #ax.plot(security.df.index[0:24*60*num_days+1], security.df['ema1000'][0:24*60*num_days+1], linestyle='-', marker='.', label='ema1000')
        #ax.plot(security.df.index[0:24*60*num_days+1], security.df['ema1200'][0:24*60*num_days+1], linestyle='-', marker='.', label='ema1200')
        #ax.plot(security.df.index[0:24*60*num_days+1], security.df['ema3000'][0:24*60*num_days+1], linestyle='-', marker='.', label='ema3000')
        ax1.plot(security.df.index[data_start:data_end], security.df['sma_long'][data_start:data_end], linestyle='-', marker='.',  linewidth=0.5, label='sma_long')
        ax1.plot(security.df.index[data_start:data_end], security.df['sma_mid'][data_start:data_end], linestyle='-', marker='.',  linewidth=0.5, label='sma_mid')

        ax2.plot(security.df.index[data_start:data_end], security.df['macd_line'][data_start:data_end], linestyle='-', marker='.',  linewidth=0.5, label='macd_line')
        ax2.plot(security.df.index[data_start:data_end], security.df['macd_signal'][data_start:data_end], linestyle='-', marker='.',  linewidth=0.5, label='macd_signal')
        #ax2.bar(security.df.index[data_start:data_end], security.df['macd_histogram'][data_start:data_end], label='macd_histogram')
        #ax.plot(security.df.index[0:], security.df['Close'][0:], linestyle='-', marker='.')
        #cursor = Cursor(ax, color='m', linewidth=0.25)

        crs1 = mplcursors.cursor(ax1, hover=True)
        crs1.connect("add", lambda sel: sel.annotation.set_text(f"{parser.parse(str(security.df.at[int(sel.target[0]), 'Date'])).strftime('%a')}, {str(security.df.at[int(sel.target[0]), 'Date'])[2:]}-{str(security.df.at[int(sel.target[0]), 'Time']).zfill(6)} {str(int(sel.target[1]*10000)/10000)}"))
        ax1.set_title(f"{ticker_symbol}")
        ax1.grid(True)
        ax1.legend()

        crs2 = mplcursors.cursor(ax2, hover=True)
        crs2.connect("add", lambda sel: sel.annotation.set_text(f"{parser.parse(str(security.df.at[int(sel.target[0]), 'Date'])).strftime('%a')}, {str(security.df.at[int(sel.target[0]), 'Date'])[2:]}-{str(security.df.at[int(sel.target[0]), 'Time']).zfill(6)} {str(int(sel.target[1]*10000)/10000)}"))
        #print(f"{parser.parse(str(security.df.at[1, 'Date'])).strftime('%a')}");
        
        #parser.parse(str(security.df.at[int(sel.target[0]), 'Date'])).strftime("%a")

        


       
        ax2.grid(True)
        ax2.legend()
        plt.show()





if __name__ == "__main__":
    main()

