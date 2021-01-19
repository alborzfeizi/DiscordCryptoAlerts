import config

from discord.ext import commands
import datetime
import asyncio
import requests
import numpy as np
from scipy.stats import linregress

time = datetime.datetime.now
bot = commands.Bot(command_prefix='!')


ticker_symbols = "BTC/USD,ETH/USD,XRP/USD"
alertThresh = float(3) #percentage change that triggers a discord message/alert
interval_time= "1min" #supports 1min, 5min, 15min, 30min, 45min
num_time_points = 30 #not yet incorporated into api calls, default value is 30
monitorFrequency = float(5) #how often the api is called in minutes

api_key = config.api_key #obtain apikey from twelvedata.com
bot_token = config.bot_token #obtain bot token from discord.com/developers

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
    print("delta: ", deltaVal, "%")
    return deltaVal

@bot.command()
async def serverInfo(ctx, arg=None):
    await ctx.send("ticker symbols monitored: {}".format(ticker_symbols))
    await ctx.send("alert threshold: {}%".format(alertThresh))
    await ctx.send("interval time: {}".format(interval_time))
    await ctx.send("monitor frequency: every {} minutes".format(monitorFrequency))
    
@bot.command()
async def setTickerSymbols(ctx, arg="BTC/USD,ETH/USD,XRP/USD"):
    global ticker_symbols
    ticker_symbols = arg
    await ctx.send("I am now monitoring {}".format(ticker_symbols))
    
@bot.command()
async def setAlertThresh(ctx, arg=float(3)):
    global alertThresh
    alertThresh = arg
    await ctx.send("I have set alert threshold to {}%".format(alertThresh))
    
@bot.command()
async def setIntervalTime(ctx, arg="1min"):
    global interval_time
    interval_time = arg
    await ctx.send("I have set interval time to {}".format(interval_time))
    
@bot.command()
async def setMonitorFreq(ctx, arg=float(5)):
    global monitorFrequency
    monitorFrequency = arg
    await ctx.send("I have set monitor frequency to every {} minutes".format(monitorFrequency))

@bot.command()
async def setToDefault(ctx, arg=None):
    global ticker_symbols
    ticker_symbols = "BTC/USD,ETH/USD,XRP/USD"
    global alertThresh
    alertThresh = float(3)
    global interval_time
    interval_time= "1min"
    global monitorFrequency
    monitorFrequency = float(5)
    await ctx.send("I have reset the server with default values")
    await serverInfo(ctx)
    
async def timer():
    await bot.wait_until_ready()
    channel = bot.get_channel(config.channel_id) # replace with channel ID that you want to send to
    await channel.send('Hello, my name is CryptoBot')
    await channel.send("I am monitoring {}".format(ticker_symbols))
    print(">>>>>>>>>>>>>>crypto script running<<<<<<<<<<<<<<<<<")
    
    
    cmdprint = False

    while True:
        if time().minute%monitorFrequency == 0:
            
            if not cmdprint:
                
                time_series_json = get_stock_time_series(ticker_symbols, interval_time, api_key)
                cmdprint = True
                print("****************************************************")    
                
                for ticker in ticker_symbols.split(','):
                    delta = calculate_delta(time_series_json, ticker)
                    if delta > alertThresh or delta < -1*alertThresh:
                        stuff_in_string = "{} had a {:.2f}% change within the past {} minutes.".format(ticker, delta, int(interval_time[0:-3])*30)
                        await channel.send(stuff_in_string)
        
        else:
            cmdprint = False
            
        await asyncio.sleep(1)

bot.loop.create_task(timer())
bot.run(bot_token)