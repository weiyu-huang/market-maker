import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from util_exchange import Exchange
import warnings

warnings.filterwarnings('ignore')


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
    df2.loc[:, 'bid0'] = round(df2.midpoint * (1 + df2.bids_distance_0), 2)
    df2.loc[:, 'ask0'] = round(df2.midpoint * (1 + df2.asks_distance_0), 2)
    df2['bid0_std'] = df2.bid0.rolling(window=20).std()
    df2['ask0_std'] = df2.ask0.rolling(window=20).std()
    df2.loc[:, 'std'] = (df2.bid0_std + df2.ask0_std) / 2
    df2.loc[:, 'volume'] = (df2.bids_notional_0 + df2.asks_notional_0) / 2

    initial_cash = 100000
    target_asset = 0.1
    gamma = 0.01
    t = 0
    T = df2.shape[0]
    exchange = Exchange(initial_cash=initial_cash, max_open_orders=3)

    assets, cashes, rs, optimal_buys, optimal_sells = [], [], [], [], []
    for row in df2.itertuples(index=False):
        t += 1
        bid0, ask0, s = row.bid0, row.ask0, row.midpoint
        vol, std = row.volume, row.std

        if pd.isna(std):  # wait until we have enough volatility data
            assets.append(np.nan)
            cashes.append(np.nan)
            rs.append(np.nan)
            optimal_buys.append(np.nan)
            optimal_sells.append(np.nan)
            continue

        # if t > 10000:
        #     break

        q = target_asset - exchange.get_asset_amount()
        # T_minus_t = (T - t) / T  # normalized to 1
        T_minus_t = 1
        r = s - q * gamma * std * std * T_minus_t  # reserve price
        kappa = vol / 500_000
        delta_a_plus_delta_b = gamma * std * std * T_minus_t + 2 / gamma * np.log(1 + gamma / kappa)
        delta = delta_a_plus_delta_b / 2

        alpha = 0.5
        min_quantity = 0.1
        if exchange.asset < 0.5:
            exchange.place_order('BUY', r - delta, max(q * alpha, min_quantity))
        exchange.place_order('SELL', r + delta, max(-q * alpha, min_quantity))

        if exchange.buy_orders and exchange.sell_orders:
            print(f"Index {t}: bid0: {bid0}, ask0: {ask0}, highestBuy: {max(exchange.buy_orders)[0]}, lowestSell: {min(exchange.sell_orders)[0]}")
        asset, cash = exchange.simulate_latest_data(bid0, ask0)
        assets.append(asset)
        cashes.append(cash)
        rs.append(r)
        optimal_buys.append(r - delta)
        optimal_sells.append(r + delta)

    df_r = pd.DataFrame({
        'asset': assets,
        'cash': cashes,
        'reserve_price': rs,
        'optimal_buys': optimal_buys,
        'optimal_sells': optimal_sells
    })
    df_r['system_time'] = df2['system_time']
    df_r['price'] = df2['midpoint']
    df_r['bid0'] = df2['bid0']
    df_r['ask0'] = df2['ask0']
    df_r = df_r.iloc[:, :]
    plt.figure(figsize=(15, 15))
    plt.subplot(3, 1, 1)
    plt.plot(df_r['bid0'])
    plt.plot(df_r['ask0'])
    plt.plot(df_r['reserve_price'])
    plt.legend(['bid', 'ask', 'r'], loc='best')

    plt.subplot(3, 1, 2)
    plt.plot(df_r['asset'])
    plt.subplot(3, 1, 3)
    plt.plot(df_r['asset'] * df_r['price'] + df_r['cash'] - initial_cash)
    plt.savefig('temp.png', format='png')


if __name__ == "__main__":
    main()
