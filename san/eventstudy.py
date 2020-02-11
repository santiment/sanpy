import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as pyplot
from datetime import timedelta

""" Event study to  evaluate events or signals.

The main parameters the event study function accepts are a
pandas dataframe containing the price data of the observed
projects and the benchmark (data) and dataframe containing
the events(ev_data)that contains the data of occurance in
the index and the name of the project for every date.
"""

def get_close_price(data, sid, current_date, day_number):
    #: If we're looking at day 0 just return the indexed date
    if day_number == 0:
        return data.loc[current_date][sid]      ##.ix
    #: Find the close price day_number away from the current_date
    else:
        #: If the close price is too far ahead, just get the last available
        total_date_index_length = len(data.index)
        #: Find the closest date to the target date
        date_index = data.index.searchsorted(current_date + timedelta(day_number))
        #: If the closest date is too far ahead, reset to the latest date possible
        date_index = total_date_index_length - 1 if date_index >= total_date_index_length else date_index
        #: Use the index to return a close price that matches
        return data.iloc[date_index][sid]

def get_first_price(data, starting_point, sid, date):
    starting_day = date - timedelta(starting_point)
    date_index = data.index.searchsorted(starting_day)
    return data.iloc[date_index][sid]

def remove_outliers(returns, num_std_devs):
    return returns[~((returns-returns.mean()).abs()>num_std_devs*returns.std())]

def get_returns(data, starting_point, sid, date, day_num):
    #: Get stock prices
    first_price = get_first_price(data, starting_point, sid, date)
    close_price = get_close_price(data, sid, date, day_num)

    #: Calculate returns
    ret = (close_price - first_price)/(first_price + 0.0)
    return ret

########################## Betas

def calc_beta(stock, benchmark, price_history):
    """
    Calculate our beta amounts for each security
    """
    stock_prices = price_history[stock].pct_change().dropna()
    bench_prices = price_history[benchmark].pct_change().dropna()
    aligned_prices = bench_prices.align(stock_prices,join='inner')
    bench_prices = aligned_prices[0]
    stock_prices = aligned_prices[1]
    bench_prices = np.array( bench_prices.values )
    stock_prices = np.array( stock_prices.values )
    bench_prices = np.reshape(bench_prices,len(bench_prices))
    stock_prices = np.reshape(stock_prices,len(stock_prices))
    if len(stock_prices) == 0:
        return None
    market_beta, benchmark_beta = np.polyfit(bench_prices, stock_prices, 1)
    return market_beta

# Simple event study

def event_study(data, ev_data,starting_point = 30, benchmark='bitcoin',
               origin_zero=True):

    if ev_data.symbol[ev_data.symbol == 'bitcoin'].count()!=0:
         benchmark='ethereum'

    #: Dictionaries to store calculated data in
    all_returns = {}
    all_std_devs = {}
    total_sample_size = {}
    benchmark_returns = {}   # Benchmark
    ab_all_returns = {}
    ab_volatility = {}

    #: Create our range of day_numbers that will be used to calculate returns
    #  starting_point = 30   #30
    #: Looking from -starting_point to +starting_point to create timeframe band
    day_numbers = [i for i in range(-starting_point, starting_point)]

    for day_num in day_numbers:
        #: Reset our returns and sample size each iteration
        returns = []
        b_returns = []
        sample_size = 0
        abreturns = []

        #: Get the return compared to t=0
        for date, row in ev_data.iterrows():
            sid = row.symbol

     #       #: Make sure that data exists for the dates
     #       if date not in data['close_price'].index or sid not in data['close_price'].columns:
     #           continue

            #: Make sure that data exists for the dates
            if date not in data.index or sid not in data.columns:
                continue

            returns.append(get_returns(data, starting_point, sid, date, day_num))
                #: 2 is the sid for the benchmark
            b_returns.append(get_returns(data, starting_point, benchmark, date, day_num)) #Benchmark
            sample_size += 1

            ret = get_returns(data, starting_point, sid, date, day_num)
            ############ define benchmark
            b_ret = get_returns(data, starting_point, benchmark, date, day_num)

            ####################################################################
            """
            Calculate beta by getting the last X days of data
            1. Create a DataFrame containing the data for the necessary sids within that time frame
            2. Pass that DataFrame into our calc_beta function in order to spit out a beta
            """
            history_index = data.index.searchsorted(date)
            history_index_start = max([history_index - starting_point, 0])
            price_history = data.iloc[history_index_start:history_index][[sid, benchmark]]
            beta = calc_beta(sid, benchmark, price_history)
            if beta is None:
                continue

            #: Calculate abnormal returns    #### check thisssss
            abnormal_return = ret - (beta*b_ret)
            abreturns.append(abnormal_return)  #####modify
            ####################################################################

        #: Drop any Nans, remove outliers, find outliers and aggregate returns and std dev
        returns = pd.Series(returns).dropna()
        returns = remove_outliers(returns, 2)

        abreturns = pd.Series(abreturns).dropna()
        abreturns = remove_outliers(abreturns, 2)

        all_returns[day_num] = np.average(returns)
        all_std_devs[day_num] = np.std(returns)
        total_sample_size[day_num] = sample_size
        benchmark_returns[day_num] = np.average(pd.Series(b_returns).dropna())   # Benchmark

        ab_volatility[day_num] = np.std(abreturns)
        ab_all_returns[day_num] = np.average(abreturns)

    #: Take all the returns, stds, and sample sizes that I got and put that into a Series
    all_returns = pd.Series(all_returns)
    all_std_devs = pd.Series(all_std_devs)
    N = np.average(pd.Series(total_sample_size))

    """
    Step Four: Plotting our event study graph
    """

    xticks = [d for d in day_numbers if d%2 == 0]
    pyplot.figure(0)
    pyplot.figure(figsize=(20,7))

    #######################################################
    if origin_zero==True:
        all_returns_shited=all_returns-all_returns.loc[0]
    else:
        all_returns_shited=all_returns.copy()
    all_returns_shited.plot(xticks=xticks, label="N=%s" % N)
    #######################################################

    pyplot.grid(b=None, which=u'major', axis=u'y')
    pyplot.title("Cumulative Return from Events")
    pyplot.xlabel("Window Length (t)")
    pyplot.legend()
    pyplot.ylabel("Cumulative Return (r)")


    #: Plot
    xticks = [d for d in day_numbers if d%2 == 0]
    #all_returns = pd.Series(all_returns)
    pyplot.figure(1)
    pyplot.figure(figsize=(20,7))
    all_returns_shited.plot(xticks=xticks, label="Cumulative Return from Events")
    benchmark_returns = pd.Series(benchmark_returns)

    if origin_zero==True:
        benchmark_returns_shited=benchmark_returns-benchmark_returns.loc[0]
    else:
        benchmark_returns_shited=benchmark_returns.copy()

    benchmark_returns_shited.plot(xticks=xticks, label='Benchmark: '+str(benchmark))

    pyplot.title("Benchmark's average returns around that time to Signals_Events")
    pyplot.ylabel("% Cumulative Return")
    pyplot.xlabel("Time Window")
    pyplot.legend()
    pyplot.grid(b=None, which=u'major', axis=u'y')


    """
    Plotting cumulative abnormal returns
    """
    xticks = [d for d in day_numbers if d%2 == 0]
    pyplot.figure()
    pyplot.figure(figsize=(20,7))
    ab_all_returns = pd.Series(ab_all_returns)

    all_returns_shited.plot(xticks=xticks, label="Average Cumulative Returns")
################################################################################
    if origin_zero==True:
        ab_all_returns_shited=ab_all_returns-ab_all_returns.loc[0]
    else:
        ab_all_returns_shited=ab_all_returns.copy()
################################################################################
    ab_all_returns_shited.plot(xticks=xticks,
                               label="Abnormal Average Cumulative Returns")

    pyplot.axhline(y=ab_all_returns_shited.loc[0], linestyle='--',
                   color='black', alpha=.3, label='Drift')
    pyplot.axhline(y=ab_all_returns_shited.max(), linestyle='--', color='black',
                   alpha=.3)
    pyplot.title("Cumulative Abnormal Returns versus Cumulative Returns")
    pyplot.ylabel("% Cumulative Return")
    pyplot.xlabel("Time Window")
    pyplot.grid(b=None, which=u'major', axis=u'y')
    pyplot.legend()

    """
    Plotting the same graph but with error bars
    """
    pyplot.figure()
    pyplot.figure(figsize=(20,7))
    all_std_devs.loc[:-1] = 0

    ############################################################################
    if origin_zero==True:
        all_std_devs_shited=all_std_devs-all_std_devs.loc[0]
        all_std_devs_shited.loc[:-1] = 0
    else:
        all_std_devs_shited=all_std_devs.copy()
    ############################################################################

    pyplot.errorbar(all_returns_shited.index, all_returns_shited, xerr=0,
                    yerr=all_std_devs, label="N=%s" % N)
    pyplot.grid(b=None, which=u'major', axis=u'y')
    pyplot.title("Cumulative Return from Events with error")
    pyplot.xlabel("Window Length (t)")
    pyplot.ylabel("Cumulative Return (r)")
    pyplot.legend()
    pyplot.show()

    """
    Capturing volatility of abnormal returns
    """
    pyplot.figure()
    pyplot.figure(figsize=(20,7))

    ab_volatility = pd.Series(ab_volatility)
    ab_all_returns = pd.Series(ab_all_returns)
    ab_volatility.loc[:-1] = 0

    ############################################################################
    if origin_zero==True:
        ab_volatility_shited=ab_volatility-ab_volatility.loc[0]
        ab_volatility_shited.loc[:-1] = 0
    else:
        ab_volatility_shited=ab_volatility.copy()
    ############################################################################

    pyplot.errorbar(ab_all_returns_shited.index, ab_all_returns_shited, xerr=0,
                    yerr=ab_volatility, label="N=%s" % N)
    pyplot.grid(b=None, which=u'major', axis=u'y')
    pyplot.title("Abnormal Cumulative Return from Events with error")
    pyplot.xlabel("Window Length (t)")
    pyplot.ylabel("Cumulative Return (r)")
    pyplot.legend()
    pyplot.show()

# Helper function to get signals in the right format for the event eventstudy:

def signals_format(signals,project):
    """ Returns signals in the needed format

    Accepts a column with the signals as boolean values
    and the projects name as a string
    """
    sign = pd.DataFrame(signals).tz_convert(None)
    sign.columns= ['symbol']
    sign=sign.replace(True, project)
    events=sign[sign["symbol"] == project]

    return events
