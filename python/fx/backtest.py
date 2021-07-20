from datetime import datetime, timedelta
from zipfile import ZipFile
import pandas as pd
import numpy as np
from matplotlib.widgets import Cursor
import matplotlib.pyplot as plt
import mplcursors

import time, requests
import os, sys, io
import glob



def main2():
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    num = 100
    x = np.random.rand(num)
    y = np.random.rand(num)

    ax.scatter(x, y, c='blue')
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')

    cursor = Cursor(ax, color='green', linewidth=2)
    plt.show()


def main():
    dataStatsManager = DataStatsManager()
    dataStatsManager.ticker_stats_calc('EURUSD')


###############################################################################
class SecurityInfo():
    def __init__(self, ticker_name = ""):
        self.ticker_name = ticker_name
        self.csv_file_name = "data/datasets/"+ticker_name+'.csv'
        self.stats = {}
        self.df = {}

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
        print(security.df.head(10))
        print(security.df.loc[3, ['Date', 'Time']])
        row = security.df.loc[3, ['Date', 'Time']]

        print("row:")
        print(row)

        d = security.df.at[3, 'Date']
        t = security.df.at[3, 'Time']
        print(f"{d}-{t}")

        print(security.df.loc[3, ['Date']] )
        print(security.df.loc[3, ['Time']] )
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

        fig, ax = plt.subplots()
        #ax = fig.add_axes(security.df['Close'])
        #ax.plot(list(security.df.index.values), security.df['Close'], linestyle='-.')
        #cursor = Cursor(ax, color='pink', linewidth=0.5)
        #ax.plot(security.df.index[0:24*60*100], security.df['Close'][0:24*60*100], linestyle='-', marker='.')
        ax.plot(security.df.index[0:], security.df['Close'][0:], linestyle='-', marker='.')
        #cursor = Cursor(ax, color='m', linewidth=0.25)

        crs = mplcursors.cursor(ax,hover=True)
        #crs.connect("add", lambda sel: sel.annotation.set_text('Point {},{}'.format(sel.target[0], sel.target[1])))
        
        crs.connect("add", lambda sel: sel.annotation.set_text(f"{str(security.df.at[int(sel.target[0]), 'Date'])}-{str(security.df.at[int(sel.target[0]), 'Time']).zfill(6)} {str(int(sel.target[1]*10000)/10000)}"))
        #crs.connect("add", lambda sel: sel.annotation.set_text(f"{sel.target[1]}"))
        #crs.connect("add", lambda sel: sel.annotation.set_text(f"{sel.target[0]}"))


        plt.title(f"{ticker_symbol}")
        plt.grid()
        plt.show()





if __name__ == "__main__":
    main()

