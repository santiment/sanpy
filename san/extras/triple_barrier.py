import pandas as pd
import mlfinlab as ml
import matplotlib.pyplot as plt


def get_labels_df(prices, signals, days, pt_sl, min_ret, lookback):
    daily_vol = ml.util.get_daily_vol(close=prices, lookback=lookback)

    vertical_barriers = ml.labeling.add_vertical_barrier(t_events=signals, close=prices, num_days=days)
    triple_barrier_events = ml.labeling.get_events(close=prices,
                                                   t_events=signals,
                                                   pt_sl=pt_sl,
                                                   target=daily_vol,
                                                   min_ret=min_ret,
                                                   num_threads=1,
                                                   vertical_barrier_times=vertical_barriers)

    labels = ml.labeling.get_bins(triple_barrier_events, prices)
    return labels


def evaluate(prices, signals, pt_sl = [1, 2],min_ret = 0.005, num_days = 5, lookback=50, interval='1d'):

    labels = pd.DataFrame()
    slugs = signals.slug.unique()
    for slug in slugs:
        try:
            project_signals=signals[signals['slug']==slug].index.tz_localize('UTC')
            project_prices = prices[slug]
            label_project= get_labels_df(project_prices, project_signals, pt_sl=pt_sl, min_ret=min_ret, days=num_days, lookback=lookback)
            label_project['slug']=slug
            labels=pd.concat([labels, label_project])
        except Exception as e:
            print(e)
    return labels


def plot_rectangle(ax1, project_prices, labels, color, side, num_days, pt_sl, alpha=0.4, ls='--'):
    for point in labels[labels['bin']==side].index:

        xdata=[point, (point + pd.DateOffset(num_days))]
        ypoint_price_upper=project_prices[point]+(project_prices[point]*labels['trgt'][point]*pt_sl[0])
        ypoint_price_lower=project_prices[point]-(project_prices[point]*labels['trgt'][point]*pt_sl[1])
        ydata=[ypoint_price_upper, ypoint_price_upper]
        ax1.plot(xdata, ydata,color=color, alpha=alpha, ls=ls)
        ax1.plot(xdata, [ypoint_price_lower,ypoint_price_lower], color=color,alpha=alpha,ls=ls)


        xdata=[point, point]
        ydata=[ypoint_price_upper,ypoint_price_lower]
        ax1.plot(xdata, ydata,color=color, alpha=alpha, ls=ls)

        xdata=[point+ pd.DateOffset(num_days), point+ pd.DateOffset(num_days)]
        ydata=[ypoint_price_upper,ypoint_price_lower]
        ax1.plot(xdata, ydata,color=color, alpha=alpha, ls=ls)
    


def plot(prices, labels,pt_sl = [1, 2], num_days=5, lookback=50):
    
    slug=labels['slug'][0]
    project_prices = prices[slug]
    plt.rcParams["figure.figsize"] = (20,3)
    fig = plt.figure()
    ax = plt.subplot()
    ax.plot(prices[slug].index, project_prices, color='g', label='price')
    ax1 = plt.subplot()     
    plot_rectangle(ax1, project_prices, labels, color='red', side=1, pt_sl = [1, 2], num_days=num_days)
    plot_rectangle(ax1, project_prices, labels, color='blue', side=-1, pt_sl = [1, 2], num_days=num_days)
    plot_rectangle(ax1, project_prices, labels, color='black', side=0, pt_sl = [1, 2], num_days=num_days)
    ax.legend()
    plt.show()
