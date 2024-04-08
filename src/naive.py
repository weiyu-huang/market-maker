import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from util_exchange import Exchange


def main():
    df = pd.read_csv('../datasets/BTC_1min.csv')
    df2 = df[[
        'system_time',
        'midpoint',
        'bids_distance_0',
        'bids_notional_0',
        'asks_distance_0',
        'asks_notional_0'
    ]]
    df2['bid0'] = round(df2.midpoint * (1 + df2.bids_distance_0), 2)
    df2['ask0'] = round(df2.midpoint * (1 + df2.asks_distance_0), 2)

    initial_cash = 100000
    delta = 40
    quantity = 0.05
    target = 0.1
    exchange = Exchange(initial_cash=initial_cash)

    assets, cashes = [], []
    exchange.place_order('BUY', 56000, 0.15)
    exchange.place_order('SELL', 60000, 0.05)
    exchange.place_order('SELL', 61000, 0.05)
    exchange.place_order('SELL', 62000, 0.05)
    for row in df2.itertuples(index=False):
        time = getattr(row, 'system_time')
        bid0, ask0, mid_price = getattr(row, 'bid0'), getattr(row, 'ask0'), getattr(row, 'midpoint')

        # if exchange.asset < target:
        #     exchange.place_order('BUY', mid_price - delta, quantity)
        # else:
        #     exchange.place_order('SELL', mid_price + delta, quantity)

        asset, cash = exchange.simulate_latest_data(time, bid0, ask0)
        assets.append(asset)
        cashes.append(cash)

    df_r = pd.DataFrame({'asset': assets, 'cash': cashes})
    df_r['system_time'] = df2['system_time']
    df_r['price'] = df2['midpoint']
    plt.figure(figsize=(10, 10))
    plt.subplot(3, 1, 1)
    plt.plot( df_r['price'])
    plt.subplot(3, 1, 2)
    plt.plot(df_r['asset'])
    plt.subplot(3, 1, 3)
    plt.plot(df_r['asset'] * df_r['price'] + df_r['cash'] - initial_cash)
    plt.savefig('temp.png', format='png')


if __name__ == "__main__":
    main()
