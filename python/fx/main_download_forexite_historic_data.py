from datetime import datetime, timedelta
from zipfile import ZipFile
import pandas as pd
import numpy as num
import time, requests
import os, sys, io
import glob


def main():
    """
    data_source = "forexite"
    start = datetime(2019,1,1)
    end = datetime(2021,7,1)
    if not os.path.exists('./data'):
        os.makedirs('./data') 
    if not os.path.exists('./data/forexite'):
        os.makedirs('./data/forexite')    
    if not os.path.exists('./data/datasets'):
        os.makedirs('./data/datasets')    
    if not os.path.exists('./data/tmp'):
        os.makedirs('./data/tmp') 
    historicDataManager = HistoricDataManager(data_source)
    historicDataManager.download(start, end)  # Override existing zip files under data/forexite/*
    historicDataManager.make_datasets(start, end) # Override existing csv files under data/datasets/*
    """
    #print("main(): please uncomment out the code above !")


###############################################################################
class ExtractInfo():
    def __init__(self, start_index = -1, end_index = -1, ticker_name = ""):
        self.start_index = start_index
        self.end_index = end_index
        self.ticker_name = ticker_name

class HistoricDataManager():
    def __init__(self, data_source):
        self.data_source = data_source
        self.count = 0
        self.forexite_dir = "data/forexite"
        self.tmp_dir = "data/tmp"
        self.dataset_dir = "data/datasets"
        self.csv_header = "<TICKER>,<DTYYYYMMDD>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>"
        self.tickers_map = {
        'EURUSD': ExtractInfo(ticker_name = 'EURUSD'),
        'GBPUSD': ExtractInfo(ticker_name = 'GBPUSD'),
        'USDCHF': ExtractInfo(ticker_name = 'USDCHF'),
        'USDJPY': ExtractInfo(ticker_name = 'USDJPY'),
        'EURGBP': ExtractInfo(ticker_name = 'EURGBP'),
        'EURCHF': ExtractInfo(ticker_name = 'EURCHF'),
        'EURJPY': ExtractInfo(ticker_name = 'EURJPY'),
        'GBPCHF': ExtractInfo(ticker_name = 'GBPCHF'),
        'GBPJPY': ExtractInfo(ticker_name = 'GBPJPY'),
        'CHFJPY': ExtractInfo(ticker_name = 'CHFJPY'),
        'USDCAD': ExtractInfo(ticker_name = 'USDCAD'),
        'EURCAD': ExtractInfo(ticker_name = 'EURCAD'),
        'AUDUSD': ExtractInfo(ticker_name = 'AUDUSD'),
        'AUDJPY': ExtractInfo(ticker_name = 'AUDJPY'),
        'NZDUSD': ExtractInfo(ticker_name = 'NZDUSD'),
        'NZDJPY': ExtractInfo(ticker_name = 'NZDJPY'),
        'XAUUSD': ExtractInfo(ticker_name = 'XAUUSD'),
        'XAGUSD': ExtractInfo(ticker_name = 'XAGUSD'),
        'USDCZK': ExtractInfo(ticker_name = 'USDCZK'),
        'USDDKK': ExtractInfo(ticker_name = 'USDDKK'),
        'USDHUF': ExtractInfo(ticker_name = 'USDHUF'),
        'USDNOK': ExtractInfo(ticker_name = 'USDNOK'),
        'USDPLN': ExtractInfo(ticker_name = 'USDPLN'),
        'USDSEK': ExtractInfo(ticker_name = 'USDSEK'),
        'USDSGD': ExtractInfo(ticker_name = 'USDSGD'),
        'USDZAR': ExtractInfo(ticker_name = 'USDZAR'),
        'USDHKD': ExtractInfo(ticker_name = 'USDHKD'),
        'USDMXN': ExtractInfo(ticker_name = 'USDMXN'),
        'USDTRY': ExtractInfo(ticker_name = 'USDTRY'),
        'EURHKD': ExtractInfo(ticker_name = 'EURHKD'),
        'EURMXN': ExtractInfo(ticker_name = 'EURMXN'),
        'EURTRY': ExtractInfo(ticker_name = 'EURTRY'),
        'EURAUD': ExtractInfo(ticker_name = 'EURAUD'),
        'EURNZD': ExtractInfo(ticker_name = 'EURNZD'),
        'EURSGD': ExtractInfo(ticker_name = 'EURSGD'),
        'EURZAR': ExtractInfo(ticker_name = 'EURZAR'),
        'XAUEUR': ExtractInfo(ticker_name = 'XAUEUR'),
        'XAGEUR': ExtractInfo(ticker_name = 'XAGEUR'),
        'GBPCAD': ExtractInfo(ticker_name = 'GBPCAD'),
        'GBPAUD': ExtractInfo(ticker_name = 'GBPAUD'),
        'GBPNZD': ExtractInfo(ticker_name = 'GBPNZD'),
        'AUDCHF': ExtractInfo(ticker_name = 'AUDCHF'),
        'AUDCAD': ExtractInfo(ticker_name = 'AUDCAD'),
        'AUDNZD': ExtractInfo(ticker_name = 'AUDNZD'),
        'NZDCHF': ExtractInfo(ticker_name = 'NZDCHF'),
        'NZDCAD': ExtractInfo(ticker_name = 'NZDCAD'),
        'CADCHF': ExtractInfo(ticker_name = 'CADCHF'),
        'CADJPY': ExtractInfo(ticker_name = 'CADJPY'),
        'USDCNH': ExtractInfo(ticker_name = 'USDCNH'),
        'BTCUSD': ExtractInfo(ticker_name = 'BTCUSD'),
        'ETHUSD': ExtractInfo(ticker_name = 'ETHUSD'),
        'LTCUSD': ExtractInfo(ticker_name = 'LTCUSD'),
        'USDILS': ExtractInfo(ticker_name = 'USDILS'),
        'EURILS': ExtractInfo(ticker_name = 'EURILS'),
        'EURNOK': ExtractInfo(ticker_name = 'EURNOK'),
        'EURSEK': ExtractInfo(ticker_name = 'EURSEK'),
        'EURDKK': ExtractInfo(ticker_name = 'EURDKK'),
        'EURCZK': ExtractInfo(ticker_name = 'EURCZK'),
        'EURHUF': ExtractInfo(ticker_name = 'EURHUF'),
        'EURPLN': ExtractInfo(ticker_name = 'EURPLN'),
        'EURCNH': ExtractInfo(ticker_name = 'EURCNH'),
        'WTIUSD': ExtractInfo(ticker_name = 'WTIUSD'),
        'DJIUSD': ExtractInfo(ticker_name = 'DJIUSD'),
        'SPXUSD': ExtractInfo(ticker_name = 'SPXUSD'),
        'NDQUSD': ExtractInfo(ticker_name = 'NDQUSD'),
        'GASUSD': ExtractInfo(ticker_name = 'GASUSD'),
        'BTCEUR': ExtractInfo(ticker_name = 'BTCEUR'),
        'ETHEUR': ExtractInfo(ticker_name = 'ETHEUR'),
        'LTCEUR': ExtractInfo(ticker_name = 'LTCEUR')
        }
        
    def download(self, start, end):
        if self.data_source == "forexite":
            print(f"download: self.data_source: {self.data_source}")
            self.count = 0
            self.__download_forexite(start, end)
        else:
            print(f"self.data_source: ${self.data_source} is not supported.")

    def make_datasets(self, start, end):
        if self.data_source == "forexite":
            print(f"make_datasets: self.data_source: {self.data_source}")
            self.count = 0
            self.__create_csv_files()  # create empty csv header
            self.__datasets_forexite(start, end);      
        else:
            print(f"self.data_source: ${self.data_source} is not supported.")

    def __download_forexite(self, start, end):
        while start <= end: 
            print(start)
            yy = str(start.year)
            mm = str(start.month)
            dd = str(start.day)
            if len(mm) == 1: mm = '0'+ mm
            if len(dd) == 1: dd = '0'+ dd
            start += timedelta(hours = 24)
            file_name = f"{self.forexite_dir}/{yy+mm+dd}.zip"  # Renamed zip file name
            try:
                # https://www.forexite.com/free_forex_quotes/2011/11/011111.zip
                res = requests.get(f'https://www.forexite.com/free_forex_quotes/{yy}/{mm}/{dd+mm+yy[2:]}.zip')
                time.sleep(0.5)
                if res.status_code == 200:
                    self.count += 1
                    print(f"{file_name}, count={self.count}")
                    with open(file_name, "wb") as code:
                        code.write(res.content)
                time.sleep(0.5)
            except:
                print(f"Download error: file: {file_name} ")


    def __create_csv_files(self):
        print(f"__create_csv_files: number of csv files: {len(self.tickers_map.keys())}")
        files = glob.glob(f"{self.dataset_dir}/*")
        for f in files: os.remove(f)

        for ticker in self.tickers_map.keys():
            ticker_name = self.tickers_map[ticker].ticker_name
            file_path = f"./data/datasets/{ticker_name}.csv"
            if not os.path.exists(file_path):
                with open(file_path, "a") as file_object:
                    file_object.write(f"{self.csv_header}\n")


    def __update_tickers_map(self, curr_ticker, line_pos):
        #print(f"__update_tickers_map: curr_ticker: {curr_ticker}, line_pos: {line_pos}")
        if curr_ticker not in self.tickers_map:
            return
        object = self.tickers_map[curr_ticker]
        if object.start_index < 0:
            object.start_index = line_pos
        if object.start_index >= 0:
            object.end_index = line_pos


    def __csv_file_append(self, lines):
        print(f"__csv_file_append: lines: {len(lines)}")
        for object in self.tickers_map.values():
            if object.start_index >= 0 and object.end_index >= object.start_index:
                with open(f"{self.dataset_dir}/{object.ticker_name}.csv", 'a') as file:
                    text = "".join(lines[object.start_index: object.end_index+1])
                    file.write(text)


    def __datasets_forexite(self, start, end):

        print(f"__datasets_forexite: start: {start}, end: {end}")

        files = glob.glob(f"{self.tmp_dir}/*")
        for f in files: os.remove(f)

        while start <= end:            
            print(start)
            yy = str(start.year)
            mm = str(start.month)
            dd = str(start.day)
            if len(mm) == 1: mm = '0'+ mm
            if len(dd) == 1: dd = '0'+ dd
            start += timedelta(hours = 24)
            self.count += 1;

            files = glob.glob(f"{self.tmp_dir}/*")  # make sure tmp foler is empty
            for f in files: os.remove(f)

            zip_file_name = f"{self.forexite_dir}/{yy+mm+dd}.zip"
            print(f"{zip_file_name}, count={self.count}")

            try:
                with ZipFile(zip_file_name, "r") as zip_ref:
                    zip_ref.extractall(self.tmp_dir)  # unzipped file in tmp folder

                files = glob.glob(f"{self.tmp_dir}/*")
                if len(files) == 0:
                    continue
                time.sleep(0.25)
                
                for value in self.tickers_map.values():  # clear map
                    value.start_index = -1
                    value.end_index = -1

                line_pos = 0;
                with open(files[0], "r") as file:  # open raw .txt file with mixed tickers
                    for line in file.readlines()[1:]:  # skip first line
                        words = line.split(',')
                        line_pos += 1;
                        if len(words) < 2:
                            continue
                        curr_ticker = words[0].strip()
                        self.__update_tickers_map(curr_ticker, line_pos)

                time.sleep(0.25)
                with open(files[0], "r") as file:  # open again raw .txt file with mixed tickers
                    lines = file.readlines()
                    self.__csv_file_append(lines)

            except:
                print(f"Unzip error: file: {zip_file_name} ")


if __name__ == "__main__":
    main()

