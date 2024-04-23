from collections import deque

class Exchange:
    def __init__(self, initial_cash=10000, max_open_orders=5):
        self.sell_orders = deque()  # (sell_price, sell_quantity)
        self.buy_orders = deque()  # (buy_price, buy_quantity)
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.max_open_orders = max_open_orders
        self.asset = 0
        self.index = 0
        self.mid_price = None

    def place_order(self, direction, price, quantity):
        price = round(price, 2)
        if direction == 'BUY':
            self.buy_orders.append((price, quantity))
            if len(self.buy_orders) > self.max_open_orders:
                self.buy_orders.popleft()
        elif direction == 'SELL':
            self.sell_orders.append((price, quantity))
            if len(self.sell_orders) > self.max_open_orders:
                self.sell_orders.popleft()

    def simulate_latest_data(self, bid0, ask0):
        # TODO: need to check if we have enough bid or ask volumes
        self.mid_price = (bid0 + ask0) / 2
        self.index += 1
        self.simulate_buy(ask0)
        self.simulate_sell(bid0)
        return self.asset, self.cash

    def simulate_buy(self, ask0):
        if len(self.buy_orders) == 0:  # no buy orders
            return
        max_tuple = max(self.buy_orders)
        (our_highest_buy_price, quantity) = max_tuple
        if ask0 > our_highest_buy_price:  # make market when lowest sell price <= our highest buy price
            return
        transaction_amount = round(quantity * ask0, 2)
        if self.cash < transaction_amount:  # not enough cash
            return

        self.asset += quantity
        self.cash -= transaction_amount
        print(f'{self.index}: Bought {quantity} at {ask0:.2f}; Profit {self.compute_profit():.2f}')
        self.buy_orders.remove(max_tuple)

    def simulate_sell(self, bid0):
        if len(self.sell_orders) == 0:  # no sell orders
            return
        min_tuple = min(self.sell_orders)
        (our_lowest_sell_price, quantity) = min_tuple
        if bid0 < our_lowest_sell_price:  # make market when highest buy price >= our lowest sell price
            return
        if self.asset < quantity:  # not enough asset
            return

        self.asset -= quantity
        self.cash += round(quantity * bid0, 2)
        print(f'{self.index}: Sold {quantity} at {bid0:.2f}; Profit {self.compute_profit():.2f}')
        self.sell_orders.remove(min_tuple)

    def compute_profit(self):
        return self.asset * self.mid_price + self.cash - self.initial_cash

    def get_asset_amount(self):
        return self.asset
