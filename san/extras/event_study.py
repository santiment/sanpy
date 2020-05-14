import numpy as np
import pandas as pd
import matplotlib.pyplot as pyplot
from datetime import timedelta
from scipy import stats


"""
Event study to  evaluate events or signals.
The main parameters the event study function accepts are a pandas dataframe containing the price data
of the observed projects and the benchmark (data) and dataframe containing the events(ev_data)
that contains the data of occurance in the index and the name of the project for every date.
"""

FIGURE_WIDTH = 20
FIGURE_HEIGHT = 7
FIGURE_SIZE = [FIGURE_WIDTH, FIGURE_HEIGHT]

def get_close_price(data, sid, current_date, day_number):
    # If we're looking at day 0 just return the indexed date
    if day_number == 0:
        return data.loc[current_date][sid]
    # Find the close price day_number away from the current_date
    else:
        # If the close price is too far ahead, just get the last available
        total_date_index_length = len(data.index)
        # Find the closest date to the target date
        date_index = data.index.searchsorted(current_date + timedelta(day_number))
        # If the closest date is too far ahead, reset to the latest date possible
        date_index = total_date_index_length - 1 if date_index >= total_date_index_length else date_index
        # Use the index to return a close price that matches
        return data.iloc[date_index][sid]

def get_first_price(data, starting_point, sid, date):
    starting_day = date - timedelta(starting_point)
    date_index = data.index.searchsorted(starting_day)

    return data.iloc[date_index][sid]

def remove_outliers(returns, num_std_devs):
    return returns[~((returns-returns.mean()).abs()>num_std_devs*returns.std())]

def get_returns(data, starting_point, sid, date, day_num):
    first_price = get_first_price(data, starting_point, sid, date)
    close_price = get_close_price(data, sid, date, day_num)
    if first_price==0:
        return 0
    return (close_price - first_price) / (first_price + 0.0)

def calc_beta(stock, benchmark, price_history):
    """
    Calculate beta amounts for each security
    """
    stock_prices = price_history[stock].pct_change().dropna()
    bench_prices = price_history[benchmark].pct_change().dropna()
    aligned_prices = bench_prices.align(stock_prices, join='inner')
    bench_prices = aligned_prices[0]
    stock_prices = aligned_prices[1]
    bench_prices = np.array(bench_prices.values)
    stock_prices = np.array(stock_prices.values)
    bench_prices = np.reshape(bench_prices,len(bench_prices))
    stock_prices = np.reshape(stock_prices,len(stock_prices))
    if len(stock_prices) == 0:
        return None
#    market_beta, benchmark_beta = np.polyfit(bench_prices, stock_prices, 1)
    slope,intercept,r_value,p_value,stderr = stats.linregress(bench_prices,stock_prices)
    return slope


def build_x_ticks(day_numbers):
    return [d for d in day_numbers if d % 2 == 0]

def plot_cumulative_returns(returns, x_ticks,events):
    pyplot.figure(figsize=FIGURE_SIZE)

    returns.plot(xticks=x_ticks, label="events=%s" % events)

    pyplot.title("Cumulative Return from Events")
    pyplot.xlabel("Window Length (t)")
    pyplot.ylabel("Cumulative Return (r)")
    pyplot.grid(b=None, which=u'major', axis=u'y')
    pyplot.legend()

def plot_average_returns(returns, benchmark_returns, x_ticks):
    pyplot.figure(figsize=FIGURE_SIZE)

    returns.plot(xticks=x_ticks, label="Cumulative Return from Events")
    benchmark_returns.plot(xticks=x_ticks, label='Benchmark')

    pyplot.title("Benchmark's average returns around that time to Signals_Events")
    pyplot.ylabel("% Cumulative Return")
    pyplot.xlabel("Time Window")
    pyplot.grid(b=None, which=u'major', axis=u'y')
    pyplot.legend()

def plot_cumulative_abnormal_returns(returns, abnormal_returns, x_ticks):
    pyplot.figure(figsize=FIGURE_SIZE)

    returns.plot(xticks=x_ticks, label="Average Cumulative Returns")
    abnormal_returns.plot(xticks=x_ticks, label="Abnormal Average Cumulative Returns")

    pyplot.axhline(
        y=abnormal_returns.loc[0],
        linestyle='--',
        color='black',
        alpha=.3,
        label='Drift'
    )

    pyplot.axhline(
        y=abnormal_returns.max(),
        linestyle='--',
        color='black',
        alpha=.3
    )

    pyplot.title("Cumulative Abnormal Returns versus Cumulative Returns")
    pyplot.ylabel("% Cumulative Return")
    pyplot.xlabel("Time Window")
    pyplot.grid(b=None, which=u'major', axis=u'y')
    pyplot.legend()


def plot_cumulative_return_with_errors(returns, std_devs,events):
    """
    Plotting the same graph but with error bars
    """
    pyplot.figure(figsize=FIGURE_SIZE)

    pyplot.errorbar(returns.index, returns, xerr=0, yerr=std_devs, label="events=%s" % events)
    pyplot.grid(b=None, which=u'major', axis=u'y')
    pyplot.title("Cumulative Return from Events with error")
    pyplot.xlabel("Window Length (t)")
    pyplot.ylabel("Cumulative Return (r)")
    pyplot.legend()
    pyplot.show()

def plot_abnormal_cumulative_return_with_errors(abnormal_volatility, abnormal_returns,events):
    """
    Capturing volatility of abnormal returns
    """
    pyplot.figure(figsize=FIGURE_SIZE)

    pyplot.errorbar(
        abnormal_returns.index,
        abnormal_returns,
        xerr=0,
        yerr=abnormal_volatility,
        label="events=%s" % events
    )

    pyplot.grid(b=None, which=u'major', axis=u'y')
    pyplot.title("Abnormal Cumulative Return from Events with error")
    pyplot.xlabel("Window Length (t)")
    pyplot.ylabel("Cumulative Return (r)")
    pyplot.legend()
    pyplot.show()

def build_day_numbers(starting_point):
    """
    Create our range of day_numbers that will be used to calculate returns
    Looking from -starting_point to +starting_point to create timeframe band
    """
    return [i for i in range(-starting_point, starting_point)]

def get_price_history(data,date,beta_window,sid,benchmark):
    """
    Create a DataFrame containing the data for the necessary sids within that time frame
    """
    if beta_window==None:
        history_index = data.index.searchsorted(date)
        history_index_start = data.index.searchsorted(data[data[sid]!=0].index[0])
        histotical_prices=data.iloc[history_index_start:history_index][[sid, benchmark]]
    else:
        history_index = data.index.searchsorted(date)
        history_index_start = max([history_index - beta_window, 0])
        histotical_prices=data.iloc[history_index_start:history_index][[sid, benchmark]]
        histotical_prices=histotical_prices[histotical_prices[sid]!=0]
    return histotical_prices[histotical_prices!=0].dropna()


def compute_return_matrix(ev_data,data,sample_size,starting_point,
                          day_num,benchmark,returns,benchmark_returns,abnormal_returns,beta_window):
    """
    Computes the returns for the project, benchmark and abnormal
    """
    for date, row in ev_data.iterrows():
        sid = row.symbol
        if date not in data.index or sid not in data.columns:
                continue
		
        if sid=='ethereum' and benchmark=='ethereum':
            benchmark='bitcoin'
        elif sid=='bitcoin' and benchmark=='bitcoin':
            benchmark='ethereum'
		
        project_return = get_returns(data, starting_point, sid, date, day_num)
        benchmark_return = get_returns(data, starting_point, benchmark, date, day_num)

        returns.append(project_return)
        benchmark_returns.append(benchmark_return)
        sample_size += 1

        beta = calc_beta(sid, benchmark, get_price_history(data,date,beta_window,sid,benchmark))
        if beta is None:
            continue
        abnormal_return = project_return - (beta * benchmark_return)
        abnormal_returns.append(abnormal_return)
    return sample_size     
        

def compute_averages(ev_data,data,starting_point,day_numbers,
                     benchmark,all_returns,all_std_devs,
                     total_sample_size,all_benchmark_returns,
                     abnormal_volatility,all_abnormal_returns,beta_window): 
    
    """
    Computes the avegare returns and standards deviation of the events
    """
        
    for day_num in day_numbers:
        returns = []
        benchmark_returns = []
        abnormal_returns = []
        sample_size = 0

        sample_size=compute_return_matrix(ev_data,data,sample_size,starting_point,
                                          day_num,benchmark,returns,benchmark_returns,abnormal_returns,beta_window)
        returns = pd.Series(returns).dropna()
        returns = remove_outliers(returns, 2)

        abnormal_returns = pd.Series(abnormal_returns).dropna()
        abnormal_returns = remove_outliers(abnormal_returns, 2)

        all_returns[day_num] = np.average(returns)
        all_std_devs[day_num] = np.std(returns)
        total_sample_size[day_num] = sample_size
        all_benchmark_returns[day_num] = np.average(pd.Series(benchmark_returns).dropna())

        abnormal_volatility[day_num] = np.std(abnormal_returns)
        all_abnormal_returns[day_num] = np.average(abnormal_returns)
        
        
def clean_data(data, events, starting_point):
    """
    Cleans signals that does not have enough pricing data
    """
    events_df=events.copy(deep=True)
    events_df['in_pricesdf']=0
    id=0
    
    for date, row in events_df.iterrows():
        sid = row.symbol
        if date not in data.index or sid not in data.columns:
            events_df.iloc[id,-1]=1
            id=id+1
            continue
        event_day= data.index.searchsorted(date)
        hist_index_start = event_day - starting_point
        hist_index_end = event_day + starting_point
        event_window=data.iloc[hist_index_start:hist_index_end][[sid]]
        if event_window.min()[0]==0 or len(event_window)==0:
            events_df.iloc[id,-1]=1
        id=id+1
    return events_df[events_df['in_pricesdf']==0]    
        


def event_study(data, events, starting_point=30, benchmark='bitcoin', origin_zero=True,beta_window=None):
    
    ev_data=clean_data(data, events, starting_point)
    
    all_returns = {}
    all_std_devs = {}
    all_benchmark_returns = {}
    all_abnormal_returns = {}
    abnormal_volatility = {}
    total_sample_size = {}

    day_numbers = build_day_numbers(starting_point)
    compute_averages(ev_data,data,starting_point,day_numbers,
                     benchmark,all_returns,all_std_devs,
                     total_sample_size,all_benchmark_returns,
                     abnormal_volatility,all_abnormal_returns,beta_window)
   
    plotting_events(day_numbers,all_returns,all_benchmark_returns,all_abnormal_returns,
                    all_std_devs,abnormal_volatility,
                    total_sample_size,origin_zero)

def signals_format(signals,project):
    """
    Returns signals in the needed format.
    Accepts a column with the signals as boolean values and the projects name as a string
    """
    sign = pd.DataFrame(signals).tz_convert(None)
    sign.columns = ['symbol']
    sign = sign.replace(True, project)
    events_ = sign[sign["symbol"] == project]

    return events_

def plotting_events(day_numbers,all_returns,all_benchmark_returns,all_abnormal_returns,all_std_devs,
                    abnormal_volatility,total_sample_size,origin_zero):

    all_returns = pd.Series(all_returns)
    all_std_devs = pd.Series(all_std_devs)
    all_benchmark_returns = pd.Series(all_benchmark_returns)
    all_abnormal_returns = pd.Series(all_abnormal_returns)
    abnormal_volatility = pd.Series(abnormal_volatility)
    events = np.average(pd.Series(total_sample_size))
    
    if origin_zero==True:
        all_returns = all_returns - all_returns.loc[0]
        all_benchmark_returns = all_benchmark_returns - all_benchmark_returns.loc[0]
        all_abnormal_returns = all_abnormal_returns - all_abnormal_returns.loc[0]
        all_std_devs = all_std_devs - all_std_devs.loc[0]
        abnormal_volatility = abnormal_volatility - abnormal_volatility.loc[0]

    all_std_devs.loc[:-1] = 0
    abnormal_volatility.loc[:-1] = 0
    
    x_ticks = build_x_ticks(day_numbers)

    plot_cumulative_returns(
        returns=all_returns,
        x_ticks=x_ticks,
        events=events
    )

    plot_average_returns(
        returns=all_returns,
        benchmark_returns=all_benchmark_returns,
        x_ticks=x_ticks
    )

    plot_cumulative_abnormal_returns(
        returns=all_returns,
        abnormal_returns=all_abnormal_returns,
        x_ticks=x_ticks
    )
    plot_cumulative_return_with_errors(
        returns=all_returns,
        std_devs=all_std_devs,
        events=events
    )

    plot_abnormal_cumulative_return_with_errors(
        abnormal_volatility=abnormal_volatility,
        abnormal_returns=all_abnormal_returns,
        events=events)
