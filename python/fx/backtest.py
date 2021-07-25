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
   backTest = BackTest()    
   backTest.control('EURUSD')


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
        self.order = OrderType.NONE         # requesting only
        self.postion = PositionType.NONE    # filled / positioned
        self.orders = []
        self.orders_df = pd.DataFrame()
        self.size = 0.0
        if size == ForexSize.MINI_LOT:
            self.size = 10000.0
        elif size == ForexSize.MICRO_LOT:
            self.size = 1000.0
        else:
            self.size = 100000.0
        


    def excute_order(self, price, df_index):
        #print(f"excute_order:  self.order={self.order}")
        if self.order == OrderType.EXIT:
            if len(self.orders) > 0:
                print(f"excute_order: OrderType.EXIT: len(self.orders)={len(self.orders)}")
                order = self.orders[-1]
                order['exit_price'] = price
                delt = (order['exit_price'] - order['entry_price'])
                if (order['order_type'] == OrderType.SHORT):
                    delt = - delt
                order['profit_loss'] = delt * self.size  # convert pips to money
                order['exit_index'] = df_index
                self.orders[-1] = order
            self.order = OrderType.NONE
            self.postion = PositionType.NONE
            return

        if self.order == OrderType.LONG:
            print(f"excute_order: OrderType.LONG: len(self.orders)={len(self.orders)}")
            dict = {'order_type': OrderType.LONG, 'entry_price': price, 'exit_price': 0.0, 'profit_loss': 0.0, 'entry_index': df_index, 'exit_index': 0}
            self.orders.append(dict)
            self.order = OrderType.NONE
            self.postion = PositionType.LONG
            return

        if self.order == OrderType.SHORT:
            print(f"excute_order: OrderType.SHORT: len(self.orders)={len(self.orders)}")
            dict = {'order_type': OrderType.SHORT, 'entry_price': price, 'exit_price': 0.0, 'profit_loss': 0.0, 'entry_index': df_index, 'exit_index': 0}
            self.orders.append(dict)
            self.order = OrderType.NONE
            self.postion = PositionType.SHORT
            return
        

    def send_order(self, type):
        if type == OrderType.EXIT:
            self.order = type
            print(f"send_order: type={type}")
            return True

        if (self.order != OrderType.NONE):
            return False

        if (self.postion != PositionType.NONE):
            return False

        self.order = type
        print(f"send_order: type={type}")
        return True

    def get_orders_df(self):
        self.orders_df = pd.DataFrame(self.orders)
        orders = self.orders_df
        acc_profit = 0
        profits = []
        for m in range(orders.shape[0]):
            acc_profit  += orders.at[m, 'profit_loss']
            profits.append(acc_profit)
        self.orders_df['ACC_PL'] = profits
        return self.orders_df


class SecurityInfo():
    def __init__(self, ticker_name = ""):
        self.ticker_name = ticker_name
        self.csv_file_name = "data/datasets/"+ticker_name+'.csv'
        self.df = {}
        self.count = 0

    def load_dataframe(self, df_header):
        self.df = pd.read_csv(self.csv_file_name)
        self.df.columns = df_header.split(',')  # replace orignal headers
        self.broker = Broker(self.df)

    def on_data(self, index, forceExit = False):
        self.count += 1
        #print(f"index1 = {index}")

        #print(f"index2 = {index}")
        price = self.df.at[index, 'Close']
        self.broker.excute_order(price, index);

        if forceExit:
            #print(f"forceExit: index = {index}")
            self.broker.send_order(OrderType.EXIT)
            return


        # analysis
        #print(f"index3 = {index}")

        #if self.broker.order == OrderType.NONE and self.broker.postion == PositionType.NONE:


        if self.count == 60:
            #print(f"on_data: Enter: index = {index}")
            self.broker.send_order(OrderType.LONG)

        if self.count == 120:
            #print(f"-> on_data: Exit: index = {index}")
            self.broker.send_order(OrderType.EXIT)

        if self.count == 180:
            self.count = 0
            
        

class BackTest():
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

    
    def control(self, ticker_symbol):
        security = self.tickers_map[ticker_symbol]
        security.load_dataframe(self.df_header)
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
        print(security.df)

        _, (ax1, ax2) = plt.subplots(2, 1)
        df_size = security.df.shape[0]
        data_start = 0 # df_size - 3*24*60;
        data_end = df_size
        print(f"df_size={df_size}")

        # -------------------------------------------------------------------------------------------------------------------------------------------
        for n in range(data_start, data_end):
            if (data_end - n) < 5:
                security.on_data(n, forceExit=True)
            else:
                security.on_data(n, forceExit=False)
            
        orders = security.broker.get_orders_df()
        print(orders)

        # -------------------------------------------------------------------------------------------------------------------------------------------
        """
        ax1.plot(security.df.index[data_start:data_end], security.df['Close'][data_start:data_end], linestyle='-', marker='.', label='price')
        ax1.plot(security.df.index[data_start:data_end], security.df['sma_long'][data_start:data_end], linestyle='-', marker='.',  linewidth=0.5, label='sma_long')
        ax1.plot(security.df.index[data_start:data_end], security.df['sma_mid'][data_start:data_end], linestyle='-', marker='.',  linewidth=0.5, label='sma_mid')
        ax2.plot(security.df.index[data_start:data_end], security.df['macd_line'][data_start:data_end], linestyle='-', marker='.',  linewidth=0.5, label='macd_line')
        ax2.plot(security.df.index[data_start:data_end], security.df['macd_signal'][data_start:data_end], linestyle='-', marker='.',  linewidth=0.5, label='macd_signal')

        crs1 = mplcursors.cursor(ax1, hover=True)
        crs1.connect("add", lambda sel: sel.annotation.set_text(f"{parser.parse(str(security.df.at[int(sel.target[0]), 'Date'])).strftime('%a')}, {str(security.df.at[int(sel.target[0]), 'Date'])[2:]}-{str(security.df.at[int(sel.target[0]), 'Time']).zfill(6)} {str(int(sel.target[1]*10000)/10000)}"))
        ax1.set_title(f"{ticker_symbol}")
        ax1.grid(True)
        ax1.legend()
        crs2 = mplcursors.cursor(ax2, hover=True)
        crs2.connect("add", lambda sel: sel.annotation.set_text(f"{parser.parse(str(security.df.at[int(sel.target[0]), 'Date'])).strftime('%a')}, {str(security.df.at[int(sel.target[0]), 'Date'])[2:]}-{str(security.df.at[int(sel.target[0]), 'Time']).zfill(6)} {str(int(sel.target[1]*10000)/10000)}"))
        ax2.grid(True)
        ax2.legend()
        plt.show()
        """






if __name__ == "__main__":
    main()

