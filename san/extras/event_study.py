import numpy as np
import pandas as pd
import matplotlib.pyplot as pyplot
from datetime import timedelta
from scipy import stats
from IPython.display import display

"""
Event study to  evaluate events or signals.
The main parameters the event study function accepts are a pandas dataframe containing the price data
of the observed projects and the benchmark (data) and dataframe containing the events(ev_data)
that contains the data of occurance in the index and the name of the project for every date.
"""

FIGURE_WIDTH = 20
FIGURE_HEIGHT = 7
FIGURE_SIZE = [FIGURE_WIDTH, FIGURE_HEIGHT]

COLOR_1 = '#14c393'  # used as a main color, jungle-green
COLOR_2 = '#ffad4d'  # used as a second color for 2-line charts, texas-rose
COLOR_3 = '#5275ff'  # benchmark, dodger-blue
COLOR_4 = '#ff5b5b'  # custom red, persommin

FONT_SIZE_LEGEND = 18
FONT_SIZE_AXES = 14


def get_close_price(data, sid, current_date, day_number, interval):
    # If we're looking at day 0 just return the indexed date
    if day_number == 0:
        return data.loc[current_date][sid]
    # Find the close price day_number away from the current_date
    else:
        # If the close price is too far ahead, just get the last available
        total_date_index_length = len(data.index)
        # Find the closest date to the target date
        date_index = data.index.searchsorted(current_date + interval*day_number)
        # If the closest date is too far ahead, reset to the latest date possible
        date_index = total_date_index_length - 1 if date_index >= total_date_index_length else date_index
        # Use the index to return a close price that matches
        return data.iloc[date_index][sid]


def get_first_price(data, starting_point, sid, date, interval):
    starting_day = date - interval*starting_point
    date_index = data.index.searchsorted(starting_day)

    return data.iloc[date_index][sid]


def remove_outliers(returns, num_std_devs):
    return returns[~((returns-returns.mean()).abs() > num_std_devs*returns.std())]


def get_returns(data, starting_point, sid, date, day_num, interval):
    first_price = get_first_price(data, starting_point, sid, date, interval)
    close_price = get_close_price(data, sid, date, day_num, interval)
    if first_price == 0:
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
    bench_prices = np.reshape(bench_prices, len(bench_prices))
    stock_prices = np.reshape(stock_prices, len(stock_prices))
    if len(stock_prices) == 0:
        return None
    # market_beta, benchmark_beta = np.polyfit(bench_prices, stock_prices, 1)
    slope, intercept, r_value, p_value, stderr = stats.linregress(bench_prices, stock_prices)
    return slope


def timedelta_format(seconds):
    numbers = [3600*24,  3600, 60, 1]
    words = [' day', ' hour', ' minute', ' second']
    values = [0, 0, 0, 0]

    value = int(seconds)
    text = ''
    ind = 0
    while value > 0:
        units = value // numbers[ind]
        rem = value % numbers[ind]
        values[ind] = units
        value = rem
        if units > 0:
            if len(text) > 0:
                text += ', '
            text = text + str(units) + words[ind]
            if units > 1:
                text += 's'
        ind += 1

    return text


def neg(n):
    return -1*n


def build_x_ticks(day_numbers, number_of_ticks):
    max_value = day_numbers[len(day_numbers)-1]
    if max_value < 30:
        return [d for d in day_numbers if d % 2 == 0]
    else:
        n1 = round(max_value / number_of_ticks)
        if n1 % 2 > 0:
            n1 += 1
        base = [i for i in range(n1, max_value + 1, n1)]
        base_neg = base.copy()
        base_neg.reverse()
        base_neg = [i * (-1) for i in base_neg]
        return base_neg + [0] + base


def plot_cumulative_returns(returns, x_ticks, events, interval_text):
    pyplot.figure(figsize=FIGURE_SIZE)

    returns.plot(xticks=x_ticks, label="events=%s" % events, color=COLOR_1)

    pyplot.axvline(x=0, color='black', alpha=.3)

    pyplot.title("Cumulative Return from Events")
    pyplot.xlabel("Time Window (t), 1t="+interval_text)
    pyplot.ylabel("Cumulative Return (r)")
    pyplot.grid(b=None, which=u'major', axis=u'y')
    pyplot.legend()


def plot_average_returns(returns, benchmark_returns, x_ticks, interval_text):
    pyplot.figure(figsize=FIGURE_SIZE)

    returns.plot(xticks=x_ticks, label="Cumulative Return from Events", color=COLOR_1)
    benchmark_returns.plot(xticks=x_ticks, label='Benchmark', color=COLOR_3)

    pyplot.axvline(x=0, color='black', alpha=.3)

    pyplot.title("Benchmark's average returns around that time to Signals_Events")
    pyplot.ylabel("% Cumulative Return")
    pyplot.xlabel("Time Window (t), 1t="+interval_text)
    pyplot.grid(b=None, which=u'major', axis=u'y')
    pyplot.legend()


def plot_cumulative_abnormal_returns(returns, abnormal_returns, x_ticks, interval_text):
    pyplot.figure(figsize=FIGURE_SIZE)

    returns.plot(xticks=x_ticks, label="Average Cumulative Returns", color=COLOR_1)
    abnormal_returns.plot(xticks=x_ticks, label="Abnormal Average Cumulative Returns", color=COLOR_2)

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

    pyplot.axvline(x=0, color='black', alpha=.3)

    pyplot.title("Cumulative Abnormal Returns versus Cumulative Returns")
    pyplot.ylabel("% Cumulative Return")
    pyplot.xlabel("Time Window (t), 1t="+interval_text)
    pyplot.grid(b=None, which=u'major', axis=u'y')
    pyplot.legend()


def plot_cumulative_return_with_errors(returns, std_devs, events):
    """
    Plotting the same graph but with error bars
    """
    pyplot.figure(figsize=FIGURE_SIZE)

    pyplot.axvline(x=0, color='black', alpha=.3)

    pyplot.errorbar(returns.index,
                    returns,
                    xerr=0,
                    yerr=std_devs,
                    label="events=%s" % events,
                    color=COLOR_1)
    pyplot.grid(b=None, which=u'major', axis=u'y')
    pyplot.title("Cumulative Return from Events with error")
    pyplot.xlabel("Window Length (t)")
    pyplot.ylabel("Cumulative Return (r)")
    pyplot.legend()
    pyplot.show()


def plot_abnormal_cumulative_return_with_errors(abnormal_volatility, abnormal_returns, events):
    """
    Capturing volatility of abnormal returns
    """
    pyplot.figure(figsize=FIGURE_SIZE)

    pyplot.errorbar(
        abnormal_returns.index,
        abnormal_returns,
        xerr=0,
        yerr=abnormal_volatility,
        label="events=%s" % events,
        color=COLOR_1
    )

    pyplot.axvline(x=0, color='black', alpha=.3)

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
    return [i for i in range(-starting_point, starting_point+1)]


def get_price_history(data, date, beta_window, sid, benchmark):
    """
    Create a DataFrame containing the data for the necessary sids within that time frame
    """
    if not beta_window:
        history_index = data.index.searchsorted(date)
        history_index_start = data.index.searchsorted(data[data[sid] != 0].index[0])
        histotical_prices = data.iloc[history_index_start:history_index][[sid, benchmark]]
    else:
        history_index = data.index.searchsorted(date)
        history_index_start = max([history_index - beta_window, 0])
        histotical_prices = data.iloc[history_index_start:history_index][[sid, benchmark]]
        histotical_prices = histotical_prices[histotical_prices[sid] != 0]
    return histotical_prices[histotical_prices != 0].dropna()


def compute_return_matrix(ev_data, data, sample_size, starting_point,
                          day_num, benchmark, returns, benchmark_returns, abnormal_returns, beta_window, interval):
    """
    Computes the returns for the project, benchmark and abnormal
    """
    for date, row in ev_data.iterrows():
        sid = row.symbol
        if date not in data.index or sid not in data.columns:
            continue
        if sid == 'ethereum' and benchmark == 'ethereum':
            benchmark = 'bitcoin'
        elif sid == 'bitcoin' and benchmark == 'bitcoin':
            benchmark = 'ethereum'

        project_return = get_returns(data, starting_point, sid, date, day_num, interval)
        benchmark_return = get_returns(data, starting_point, benchmark, date, day_num, interval)

        returns.append(project_return)
        benchmark_returns.append(benchmark_return)
        sample_size += 1

        beta = calc_beta(sid, benchmark, get_price_history(data, date, beta_window, sid, benchmark))
        if beta is None:
            continue
        abnormal_return = project_return - (beta * benchmark_return)
        abnormal_returns.append(abnormal_return)
    return sample_size


def compute_averages(ev_data, data, starting_point, day_numbers,
                     benchmark, all_returns, all_std_devs,
                     total_sample_size, all_benchmark_returns,
                     abnormal_volatility, all_abnormal_returns, beta_window, interval):

    """
    Computes the avegare returns and standards deviation of the events
    """

    for day_num in day_numbers:
        returns = []
        benchmark_returns = []
        abnormal_returns = []
        sample_size = 0

        sample_size = compute_return_matrix(ev_data, data, sample_size, starting_point,
                                            day_num, benchmark, returns, benchmark_returns,
                                            abnormal_returns, beta_window, interval)
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
    events_df = events.copy(deep=True)
    events_df['in_pricesdf'] = 0
    id = 0

    for date, row in events_df.iterrows():
        sid = row.symbol
        if date not in data.index or sid not in data.columns:
            events_df.iloc[id, -1] = 1
            id = id+1
            continue
        event_day = data.index.searchsorted(date)
        hist_index_start = event_day - starting_point
        hist_index_end = event_day + starting_point
        event_window = data.iloc[hist_index_start:hist_index_end][[sid]]
        if event_window.min()[0] == 0 or len(event_window) == 0 or True in pd.isnull(list(event_window[sid])):
            events_df.iloc[id, -1] = 1
        id = id+1
    return events_df[events_df['in_pricesdf'] == 0]


def event_study(data,
                events,
                starting_point=30,
                benchmark='bitcoin',
                origin_zero=True,
                beta_window=None,
                interval=timedelta(days=1),
                x_ticks_amount=12):

    ev_data = clean_data(data, events, starting_point)

    all_returns = {}
    all_std_devs = {}
    all_benchmark_returns = {}
    all_abnormal_returns = {}
    abnormal_volatility = {}
    total_sample_size = {}

    day_numbers = build_day_numbers(starting_point)
    compute_averages(ev_data, data, starting_point, day_numbers,
                     benchmark, all_returns, all_std_devs,
                     total_sample_size, all_benchmark_returns,
                     abnormal_volatility, all_abnormal_returns, beta_window, interval)

    plotting_events(day_numbers, all_returns, all_benchmark_returns, all_abnormal_returns,
                    all_std_devs, abnormal_volatility,
                    total_sample_size, origin_zero, x_ticks_amount, interval)


def signals_format(signals, project):
    """
    Returns signals in the needed format.
    Accepts a column with the signals as boolean values and the projects name as a string
    """
    sign = pd.DataFrame(signals)
    sign.columns = ['symbol']
    sign = sign.replace(True, project)
    events_ = sign[sign["symbol"] == project]

    return events_


def plotting_events(day_numbers, all_returns, all_benchmark_returns, all_abnormal_returns, all_std_devs,
                    abnormal_volatility, total_sample_size, origin_zero, x_ticks_amount, interval):

    all_returns = pd.Series(all_returns)
    all_std_devs = pd.Series(all_std_devs)
    all_benchmark_returns = pd.Series(all_benchmark_returns)
    all_abnormal_returns = pd.Series(all_abnormal_returns)
    abnormal_volatility = pd.Series(abnormal_volatility)
    events = np.average(pd.Series(total_sample_size))

    if origin_zero:
        all_returns = all_returns - all_returns.loc[0]
        all_benchmark_returns = all_benchmark_returns - all_benchmark_returns.loc[0]
        all_abnormal_returns = all_abnormal_returns - all_abnormal_returns.loc[0]
        all_std_devs = all_std_devs - all_std_devs.loc[0]
        abnormal_volatility = abnormal_volatility - abnormal_volatility.loc[0]

    all_std_devs.loc[:-1] = 0
    abnormal_volatility.loc[:-1] = 0

    x_ticks = build_x_ticks(day_numbers, x_ticks_amount)

    plot_cumulative_returns(
        returns=all_returns,
        events=events,
        x_ticks=x_ticks,
        interval_text=timedelta_format(interval.total_seconds())
    )

    plot_average_returns(
        returns=all_returns,
        benchmark_returns=all_benchmark_returns,
        x_ticks=x_ticks,
        interval_text=timedelta_format(interval.total_seconds())
    )

    plot_cumulative_abnormal_returns(
        returns=all_returns,
        abnormal_returns=all_abnormal_returns,
        x_ticks=x_ticks,
        interval_text=timedelta_format(interval.total_seconds())
    )
    plot_cumulative_return_with_errors(
        returns=all_returns,
        std_devs=all_std_devs,
        events=events
    )

    plot_abnormal_cumulative_return_with_errors(
        abnormal_volatility=abnormal_volatility,
        abnormal_returns=all_abnormal_returns,
        events=events
    )


def calc_beta_testing(stock, benchmark, price_history):
    """
    Calculate beta and alpha amounts for each security
    """

    stock_prices = np.log(1+price_history[stock].pct_change().dropna())
    bench_prices = np.log(1+price_history[benchmark].pct_change().dropna())

    aligned_prices = bench_prices.align(stock_prices, join='inner')
    bench_prices = aligned_prices[0]
    stock_prices = aligned_prices[1]
    bench_prices = np.array(bench_prices.values)
    stock_prices = np.array(stock_prices.values)
    bench_prices = np.reshape(bench_prices, len(bench_prices))
    stock_prices = np.reshape(stock_prices, len(stock_prices))

    if len(stock_prices) == 0:
        return None
    # market_beta, benchmark_beta = np.polyfit(bench_prices, stock_prices, 1)
    slope, intercept, r_value, p_value, stderr = stats.linregress(bench_prices, stock_prices)
    return slope, intercept


def compute_beta_alpha(data, ev_data, starting_point, benchmark):
    """
    Includes beta and alpha in the event dataframe
    """
    betas_df = ev_data.copy(deep=True)
    betas_df['beta'] = 0
    betas_df['alpha'] = 0
    id = 0
    for date, row in betas_df.iterrows():
        sid = row.symbol
        if date not in data.index or sid not in data.columns:
            continue
        if sid == 'ethereum' and benchmark == 'ethereum':
            benchmark = 'bitcoin'
        elif sid == 'bitcoin' and benchmark == 'bitcoin':
            benchmark = 'ethereum'
        coeff = calc_beta_testing(sid, benchmark, get_price_history(data, date, starting_point, sid, benchmark))
        if coeff:
            beta, alpha = coeff
            betas_df.iloc[id, -2] = beta
            betas_df.iloc[id, -1] = alpha
            id = id+1
    return betas_df.reset_index()


def calculate_ab_returns(returns_df, betas_df, intercept, benchmark):
    """
    Calculate abnormal returns for every event case
    """
    ab_returns = pd.DataFrame()
    for number, dta in betas_df.iterrows():
        sid = dta.symbol
        ind = number
        alpha = dta.alpha
        beta = dta.beta
        if not intercept:
            ab_returns[ind] = returns_df[sid]-beta*returns_df[benchmark]
        else:
            ab_returns[ind] = returns_df[sid]-(alpha+beta*returns_df[benchmark])
    return ab_returns.dropna()


def ab_returns_matrix(ab_returns, betas_df, starting_point):
    """
    Maps the abnormal returns for every event
    """
    abnormal_returns_df = ab_returns.reset_index()
    new_sample = {}
    for number, dta in betas_df.iterrows():
        eventdate = dta.datetime
        sid = number
        # find specific event row, look where Date is equal to event_date
        col_name = abnormal_returns_df.columns[0]
        row = abnormal_returns_df.loc[abnormal_returns_df[col_name] == eventdate]
        # get index of row
        index = row.index[0]
        # select starting_point plus and starting_point minus around that row
        my_sample = abnormal_returns_df.loc[(index - starting_point):(index + starting_point), sid].reset_index(drop=True)
        # add to new set
        new_sample[number] = my_sample
    return new_sample


def calculate_stats(new_sample, starting_point):
    """
    Calculates t statistics for AARs and CAARs
    """
    ev = pd.DataFrame(new_sample)
    ev.index = ev.index - starting_point

    # Calulate CARs
    ev_cumulative = ev.cumsum()

    # Calculate t statistics for AARs
    mean_AR = ev.mean(axis=1)
    std_AR = ev.std(axis=1)
    results = pd.DataFrame(mean_AR, columns=['AAR'])
    # results['STD AR'] = std_AR
    results['t-AAR'] = mean_AR / std_AR
    results['P-Value t-AAR'] = stats.norm.cdf(results['t-AAR'])

    # Calculate t statistics for CAARs
    mean_CAR = ev_cumulative.mean(axis=1)
    std_CAR = ev_cumulative.std(axis=1)
    results['CAAR'] = mean_CAR
    # results['STD CAR'] = std_CAR
    results['t-CAAR'] = mean_CAR / std_CAR
    results['P-Value t-CAAR'] = stats.norm.cdf(results['t-CAAR'])
    return results


def plot_ARR_CAAR(results):
    fig, ax = pyplot.subplots(figsize=FIGURE_SIZE)
    ax.set_title('ARS vs CARS', fontsize=20)
    ax.plot(results.index, results['AAR'], color=COLOR_4, marker="o")
    ax.set_xlabel("Days", fontsize=14)
    ax.set_ylabel("AAR", color=COLOR_4, fontsize=14)
    ax2 = ax.twinx()
    ax2.plot(results.index, results['CAAR'], color=COLOR_1, marker="o")
    ax2.set_ylabel("CAAR", color=COLOR_1, fontsize=14)
    pyplot.show()


def plot_CI(tstats, pvalues, CI):
    c = stats.norm().isf((1-CI)/2)
    fig, ax = pyplot.subplots(nrows=2, figsize=FIGURE_SIZE)
    ax[0].set_title(tstats.name+' Statistic', fontsize=20)
    ax[1].set_title('P-Values ', fontsize=20)
    tstats.plot(ax=ax[0], label=tstats.name, color=COLOR_1)
    ax[0].axhline(y=c, linestyle='--', color=COLOR_4, alpha=.9, label='Significance Line (' + str(round(c, 2)) + ')')
    ax[0].axhline(y=-c, linestyle='--', color=COLOR_4, alpha=.9)
    ax[0].legend()
    ax[1].bar(pvalues.index, pvalues, label=pvalues.name, color=COLOR_1)
    ax[1].axhline(y=(1-CI)/2, linestyle='--', color=COLOR_4, alpha=.9, label='Significance Line('+str(round((1-CI)/2, 2))+')')
    ax[1].legend()


def get_log_returns(data):
    # Get arithmetic returns
    arithmetic_returns = data.pct_change()
    # Transform to log returns
    arithmetic_returns = 1+arithmetic_returns
    returns_array = np.log(arithmetic_returns, out=np.zeros_like(arithmetic_returns), where=(arithmetic_returns != 0))
    return pd.DataFrame(returns_array, index=data.index, columns=data.columns).fillna(0)


def hypothesis_test(data, ev_data, starting_point, benchmark='ethereum', intercept=True, CI=.95, interval=timedelta(days=1)):
    # Drops events with no pricing data
    cleaned_events = clean_data(data, ev_data, starting_point)
    # Call function to calculate betas for events
    betas_df = compute_beta_alpha(data, cleaned_events, starting_point, benchmark)
    # Get log returns
    returns_df = get_log_returns(data)
    # Calculate abnormal returns
    ab_returns = calculate_ab_returns(returns_df, betas_df, intercept, benchmark)
    # Maps the abnorml returns for every event
    new_sample = ab_returns_matrix(ab_returns, betas_df, starting_point)
    # Calculate Statistics
    results = calculate_stats(new_sample, starting_point)
    display(results)
    # Plotting Functions
    plot_ARR_CAAR(results)
    plot_CI(results['t-AAR'], results['P-Value t-AAR'], CI)
    plot_CI(results['t-CAAR'], results['P-Value t-CAAR'], CI)
