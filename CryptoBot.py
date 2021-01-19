from discord.ext import commands
import datetime
import asyncio
import requests
import numpy as np
from scipy.stats import linregress

time = datetime.datetime.now
bot = commands.Bot(command_prefix='!')


ticker_symbol = "BTC/USD,ETH/USD,XRP/USD"
interval_time= "1min"
api_key = "be5e259ae1bb4240a11412ccf6f7c7c6"

def get_stock_time_series(ticker, interval, api):
    url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval={interval}&apikey={api}"
    response = requests.get(url).json()
    return response

def calculate_delta(responses, ticker):
    x = np.linspace(1,30, 30)
    time_series = responses[ticker]['values']
    
    arr = np.zeros(len(time_series))
    i = 0
    for timePoint in time_series:
        arr[i] = timePoint['close']
        i = i+1
    print(ticker, "<<<<<<<<<<<<<<<<<<<<<<<")
    arr = np.flip(arr)
    avg = np.average(arr)
    print("average: ", avg)
    slope, intercept, r_value, p_value, stderrline = linregress(x, arr)
    print("slope: ", slope, "intercept", intercept)
    openVal = (slope*x[0])+intercept
    closeVal = (slope*x[-1])+intercept
    print("open: ",  openVal, "close: ", closeVal)
    deltaVal = ((closeVal - openVal)/openVal)*100
    print("delta over 30min", deltaVal, "%")
    return deltaVal

@bot.command()
async def test(ctx, arg='hi'):
    await ctx.send(arg)
    await ctx.send('server is running fine')
    await ctx.send(ticker_symbol)
    await ctx.send(interval_time)

async def timer():
    await bot.wait_until_ready()
    channel = bot.get_channel(799707483173158947) # replace with channel ID that you want to send to
    await channel.send('crypto script running')
    await channel.send(ticker_symbol)
    alertThresh = 3
    cmdprint = False

    while True:
        if time().minute%5 == 0:
            
            if not cmdprint:
                
                time_series_json = get_stock_time_series(ticker_symbol, interval_time, api_key)
                cmdprint = True
                print("****************************************************")
                                
                ticker = 'BTC/USD'
                delta = calculate_delta(time_series_json, ticker)
                
                if delta > alertThresh or delta < -1*alertThresh:
                    stuff_in_string = "{} had a {:.2f}% change within the past 30 minutes.".format(ticker, delta)
                    await channel.send(stuff_in_string)
                
                ticker = 'ETH/USD'
                delta = calculate_delta(time_series_json, ticker)
                
                if delta > alertThresh or delta < -1*alertThresh:
                    stuff_in_string = "{} had a {:.2f}% change within the past 30 minutes.".format(ticker, delta)
                    await channel.send(stuff_in_string)
                
                ticker = 'XRP/USD'
                delta = calculate_delta(time_series_json, ticker)
                
                if delta > alertThresh or delta < -1*alertThresh:
                    stuff_in_string = "{} had a {:.2f}% change within the past 30 minutes.".format(ticker, delta)
                    await channel.send(stuff_in_string)
        
        else:
            cmdprint = False
            
        await asyncio.sleep(1)

bot.loop.create_task(timer())
bot.run('Nzk5NzA3NzgxMTE1NTQzNjAy.YAHf6A.dW814yPQJ1P6uF5TtZWivipZlYc')