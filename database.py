import yfinance as yf
import pandas_market_calendars as mcal
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from table2ascii import table2ascii, Alignment,TableStyle
from matplotlib.ticker import FuncFormatter
import numpy as np

from firebase import firebase
from firebase_admin import db, credentials
import firebase_admin
import json
import discord

default_money = 10000

def plot_history(df):
    #figure = plt.figure()
    fig = plt.figure()
    #values = df.values
    plt.plot(df.index,df.values)
    plt.ylabel('Price')
    ax = fig.gca()
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.2%}'.format(y)))
    equidate_ax(fig,ax,df.index,fmt='%Y-%m-%d',label="Date")
    print(df)
    fig.show()

    filename = 'test.png'
    fig.savefig(filename, dpi = fig.dpi)
    image = discord.File(filename)
    plt.close()

def equidate_ax(fig,ax,dates,fmt='%Y-%m-%d',label="Date"):
    N = len(dates)
    def format_date(index,pos):
        index = np.clip(int(index+0.5),0,N-1)
        return dates[index].strftime(fmt)
    ax.xaxis.set_major_formatter(FuncFormatter(format_date))
    ax.set_xlabel(label)
    fig.autofmt_xdate()

def valid_market_time(market_exchange='NYSE'): # helper function for get_valid_times
  time = datetime.now()
  #time = time - datetime.timedelta(seconds=time.second,microseconds=time.microsecond)

  exchange = mcal.get_calendar(market_exchange)
  #dt = dt.astimezone()(pytz.timezone('America/New_York'))

  return time.weekday() not in [5,6] and 9*60+30 <= time.hour*60+time.minute <= 16*60 # 9:30AM to 4:00PM in NY time, will use pytz to automatically adjust

def initialize_db():
    url = 'https://some-yellows-paper-trader-default-rtdb.firebaseio.com/'
    cred = credentials.Certificate(r'C:\Users\Alexa\Downloads\some-yellows-paper-trader-firebase-adminsdk-qdh9a-8dcd662a62.json')
    # https://firebase.google.com/docs/admin/setup#python
    #firebase = firebase.FirebaseApplication(url,None)
    default_app = firebase_admin.initialize_app(cred,{'databaseURL':url})

initialize_db()
#Post adds data. Put returns data that was just sent
# https://firebase.google.com/docs/database/admin/save-data#python_1

class Trader():
    def __init__(self,id: int):
        self.id = id

# Plan to store stocks as a hashmap. Key is ticker. Values are price bought,number of shares
# Can create a ledger to store all transactions as well (history)

ref = db.reference('/users')

def get_users():
    result = firebase.get('/users',None)
    print(result,result['money'])

def create_user(id,money,bypass=False):
    # need to check if user exists
    if not bypass:
        pass
    user = Trader(id)
    user_data = json.dumps(user.__dict__)
    new_user_ref = ref.child(str(id))
    new_user_ref.child('money').set(money)
    new_user_ref = ref.child(f'{id}')
    #new_user_ref.child('stocks').set()
    #new_user_ref.child('transactions').set()

    return f"User {id} added. Starting funds: {money}"


# https://firebase.google.com/docs/database/admin/retrieve-data

def buy_stock(id: str,tkr: str,shares: int): #buy after confirmation. Separate quote function will be called when considering
    if not int(shares) >= 0:
        return "Need positive number of shares"
    try:
        ticker = yf.Ticker(tkr)
        if not ticker:
            return "Invalid ticker."
    except Exception as e:
        return f"Purchase failed. Error: {e}"
    
    # get refs
    id_ref = ref.child(str(id))
    stocks_ref = id_ref.child('stocks')
    transaction_ref = id_ref.child('transactions')

    res = id_ref.get()

    # Get price and calculate remaining funds
    money = res.get('money')
    if money is None:
        return "Error: User funds not available"
    
    money = float(money)
    price = get_price(tkr)
    shares = int(shares)
    remaining_funds = money - (int(shares)*price)

    if remaining_funds < 0:
        return "Error. You do not have enough money."

    if stocks_ref.get() is None:
        cur_shares = 0
    else:
        cur_shares = stocks_ref.get().get(tkr,0)
        print(f'Stocks ref: {stocks_ref.get().get(tkr,0)},{type(stocks_ref.get().get(tkr,0))}')
    
    # Update in Firebase
    id_ref.update({'money':remaining_funds})
    stocks_ref.update({tkr:shares+cur_shares})
    transaction_ref.update({datetime.now().strftime('%Y-%m-%d %H:%M %S'):(tkr,shares,remaining_funds)})
    return f"You have purchased {shares} share(s) of {tkr.upper()} for {(int(shares)*price):.2f}. Remaining funds: {remaining_funds:.2f}."

def sell_stock(id: str,tkr: str,shares: int):
    if not int(shares) >= 0:
        return "Need positive number of shares"
    try:
        ticker = yf.Ticker(tkr)
    except Exception as e:
        return f"Sale failed. Error: {e}"
    
    
    # get refs
    id_ref = ref.child(str(id))
    stocks_ref = id_ref.child('stocks')
    transaction_ref = id_ref.child('transactions')

    res = id_ref.get()

    # Get price and calculate remaining funds
    money = res.get('money')
    if money is None:
        return "Error: User funds not available."
    
    money = float(money)
    price = get_price(tkr)
    shares = int(shares)
    remaining_funds = money + (int(shares)*price)
    if remaining_funds < 0:
        return "Error: You are too poor."

    if stocks_ref.get() is None:
        cur_shares = 0
    else:
        cur_shares = stocks_ref.get().get(tkr,0)
        print(f'Stocks ref: {stocks_ref.get().get(tkr,0)},{type(stocks_ref.get().get(tkr,0))}')
    
    if shares > cur_shares:
        return "Error. You do not have enough shares."
    # Update in Firebase
    id_ref.update({'money':remaining_funds})
    if shares == cur_shares:
        stocks_ref.update({tkr:None})
    else:
        stocks_ref.update({tkr:cur_shares-shares})
    transaction_ref.update({datetime.now().strftime('%Y-%m-%d %H:%M %S'):(tkr,-shares,remaining_funds)})
    return f"You have sold {shares} share(s) of {tkr.upper()} for {(int(shares)*price):.2f}. Remaining funds: {remaining_funds:.2f}."

def get_price(ticker: str):
    data = yf.download(tickers=ticker,period='1m',interval='1m')['Close']
    return data.iloc[-1]

def get_user_stocks(id):
    id_ref = ref.child(str(id))
    stocks_ref = id_ref.child('stocks')
    print(stocks_ref.get(),type(stocks_ref.get()))
    return stocks_ref.get() #type dict

def reset(id,money):
    id_ref = ref.child(str(id))
    #print(id_ref.get())
    id_ref.delete(str(id))
    create_user(id,money,bypass=True)
    return f"Reset {id} with ${money}."

def get_money(id):
    id_ref = ref.child(str(id))
    res = id_ref.get()
    money = res.get('money')

    return f"You have ${money}"


'''
Links:
https://stackoverflow.com/questions/63565825/how-to-make-data-to-be-shown-in-tabular-form-in-discord-py
https://firebase.google.com/docs/storage/web/upload-files
https://stackoverflow.com/questions/7906365/matplotlib-savefig-plots-different-from-show
implement hybrid commands
'''

def stocks_to_table(id):
    stocks = get_user_stocks(id)
    header = ["Ticker","Shares"]
    body = []

    if not stocks:
        return "You do not have any stocks"
    for ticker,shares in stocks.items():
        body.append([ticker,shares])
    
    print(body)
    style = TableStyle.from_string("═" * 30).set(left_and_right_edge="", col_sep="",header=False)
    output = table2ascii(header=header,body=body,column_widths=[20,20], alignments=[Alignment.LEFT,Alignment.RIGHT],style = style,first_col_heading=False,last_col_heading=False)

    return output

def merge_series(data_list,df,shares): # issue is that we keep on counting money multiple times. We can fix this by making a separate dataframe and merging based on right
    #weighted_data = pd.Series([data * shares for data in data_list],name="_")
    data_list *= shares
    #data_list -= (default_money-money)
    print(data_list)
    #print(merged_data)
    #df.merge([df,weighted_data],how='cross',copy=False)
    df = pd.concat([df,data_list],axis=1,join='outer')
    return df

def get_portfolio_history(id,api=False): # Utilize generator functions
    id_ref = ref.child(str(id)) # Me
    transactions_ref = id_ref.child('transactions') #access transactions

    history = transactions_ref.get()
    #df = pd.DataFrame()

    if not history.items():
        return "ERROR"
    
    #.days,.seconds
    #timedelta object does not have hour or second attributes
    
    print(type((datetime.now() - datetime.strptime(list(history.items())[0][0],"%Y-%m-%d %H:%M %S")).seconds//3600))
    period_list = [f'{max(1,(datetime.now() - datetime.strptime(item[0],"%Y-%m-%d %H:%M %S")).seconds//3600)}h' for item in list(history.items())]
    print(period_list)

    df = pd.DataFrame()
    cash = pd.Series()

    for i,item in enumerate(list(history.items())): # item[0] is datetime, item[1][0] is ticker, item[1][1] is shares, item[1]2[] is liquid cash after transaction
        data = yf.download(tickers=item[1][0],period=period_list[i],interval='15m')['Close'] # '1h' means loading data before bought. period needs to be specified in hours
        start_date = data.head(1).index.item()

        # Get Cash        
        money = item[1][2]
        shares = item[1][1]

        print(f"Ticker: {item[1][0]} Shares: {shares} Money: {money}")

        new = pd.Series(data=[money]*len(data),index = data.index)
        new = new.rename(f'{item[1][0]}')
        cash = cash[cash.index < start_date] # acts as filter
        cash = pd.concat([cash,new],axis=0,join='outer')

        df = merge_series(data,df,shares)

    print(f'Preconversion\n{df}')
    cash = cash.rename("Liquid Cash")
    print(f'Cash: {cash}')
    df = pd.concat([df,cash],axis=1,join='outer')
    df = df.sum(axis=1,numeric_only=True)
    
    if api:
        return df
    
    print(df)
    print("Converting to percentage")
    df = df.apply(lambda x: (x-default_money)/default_money)
    print(df)

    plot_history(df)

    # https://pandas.pydata.org/docs/reference/api/pandas.DatetimeIndex.tz_localize.html
    
    return df.values