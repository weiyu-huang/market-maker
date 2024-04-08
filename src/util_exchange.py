from sortedcontainers import SortedDict

class Exchange:
    def __init__(self, initial_cash=10000, max_open_orders=5):
        self.sell_orders = SortedDict()  # sellPrice : sellQuantity
        self.buy_orders = SortedDict()  # buyPrice : buyQuantity
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.max_open_orders = max_open_orders
        self.asset = 0
        self.index = 0
        self.mid_price = None

    def place_order(self, direction, price, quantity):
        price = int(round(price, 2) * 100)
        quantity = (round(quantity, 2) * 100)
        if direction == 'BUY':
            if price in self.buy_orders:
                self.buy_orders[price] += quantity
            else:
                self.buy_orders.setdefault(price, quantity)
                if len(self.buy_orders) > self.max_open_orders:
                    self.buy_orders.popitem(0)  # remove the cheapest
        elif direction == 'SELL':
            if price in self.sell_orders:
                self.sell_orders[price] += quantity
            else:
                self.sell_orders.setdefault(price, quantity)
                if len(self.sell_orders) > self.max_open_orders:
                    self.sell_orders.popitem(-1)  # remove the most expensive

    def simulate_latest_data(self, time, bid0, ask0):
        # TODO: need to check if we have enough bid or ask volumes
        bid0, ask0 = int(round(bid0, 2) * 100), int(round(ask0, 2) * 100)
        self.mid_price = (bid0 + ask0) // 2
        self.index += 1
        self.simulate_buy(ask0)
        self.simulate_sell(bid0)
        return self.asset / 100, self.cash

    def simulate_buy(self, ask0):
        if not self.buy_orders:  # no buy orders
            return
        our_highest_buy_price = self.buy_orders.keys()[-1]
        if ask0 > our_highest_buy_price:  # lowest sell price is above our highest buy price
            return
        quantity = self.buy_orders[our_highest_buy_price]
        transaction_amount = quantity * ask0 / 10000
        if self.cash < transaction_amount:  # not enough cash
            return

        self.asset += quantity
        self.cash -= transaction_amount
        print(f'{self.index}: Bought {quantity / 100} at {ask0 / 100:.2f}; Profit {self.compute_profit():.2f}')
        self.buy_orders.pop(our_highest_buy_price)

    def simulate_sell(self, bid0):
        if not self.sell_orders:  # no sell orders
            return
        our_lowest_sell_price = self.sell_orders.keys()[0]
        if bid0 < our_lowest_sell_price:  # highest buy price is below our lowest sell price
            return
        quantity = self.sell_orders[our_lowest_sell_price]
        if self.asset < quantity:  # not enough asset
            return

        self.asset -= quantity
        self.cash += quantity * bid0 / 10000
        print(f'{self.index}: Sold {quantity} at {bid0 / 100:.2f}; Profit {self.compute_profit():.2f}')
        self.sell_orders.pop(our_lowest_sell_price)

    def compute_profit(self):
        return self.asset / 100 * self.mid_price / 100 + self.cash - self.initial_cash

    def get_asset_amount(self):
        return self.asset / 100
