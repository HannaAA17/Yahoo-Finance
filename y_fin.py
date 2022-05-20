import time
import argparse
import datetime

import pandas as pd
from tqdm import tqdm

# the file description
parser = argparse.ArgumentParser(description='Yahoo Finance Scraper')

# required arguments
parser.add_argument('-nd', '--days', type=int, metavar='', required=True, help='Number of Days')

# optional arguments
parser.add_argument('-of', '--output_file', type=str, metavar='', help='Output File Name, default="output.csv"', default='output.csv')

# you have to choose only one from the group
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-sf', '--symbols_file', type=str, metavar='', help='Symbols File Name (Ticker / Line)')
group.add_argument('-sl', '--symbols_list', type=str, metavar='', help='Symbols List (Comma-Separated)')

# parse arguments
args = parser.parse_args()

def make_req(ticker, n_of_days=60):

    today_date = datetime.date.today()
    from_date = today_date - datetime.timedelta(days = n_of_days)

    period1 = int(time.mktime(from_date.timetuple()))
    period2 = int(time.mktime(today_date.timetuple()))

    interval = '1d' # 1d, 1m

    query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'

    df = pd.read_csv(query_string)
    df['ticker'] = ticker
    df['Date'] = pd.to_datetime(df['Date'])

    df = df[['Date', 'ticker', 'Adj Close']]
    return df

def make_reqs(tickers, n_of_days, out_fname):
    e_tickers = []

    df = pd.DataFrame()
    
    for ticker in tqdm(tickers.split(',')):
        ticker = ticker.strip()
        try:
            df = df.append(make_req(ticker, n_of_days), ignore_index = True)
        except:
            e_tickers.append(ticker)

    final_df = pd.pivot_table(df, values='Adj Close', index='Date', columns='ticker')
    final_df.sort_index()

    final_df[[ticker.strip() for ticker in tickers.split(',') if ticker.strip() not in e_tickers]].to_csv(out_fname)
    return e_tickers

# read Tickers (Symbols)
if args.symbols_file:
    with open(args.symbols_file, 'r') as f:
        tickers = ','.join(line.strip() for line in f.readlines() if line.strip())
else:
    tickers = ','.join(ticker.strip() for ticker in args.symbols_list.split(',') if ticker.strip())

print(f'tickers: {tickers}\n')

e_tickers = make_reqs(tickers, args.days, args.output_file)

if e_tickers:
    print(f'\nErrors: {e_tickers}')