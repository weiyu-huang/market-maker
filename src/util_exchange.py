from heapq import heappush, heappop


class Exchange:
    def __init__(self, initial_cash=10000):
        self.sell_prices = []  # minHeap
        self.buy_prices = []  # maxHeap
        self.sell_quantities = {}  # sellPrice : sellQuantity
        self.buy_quantities = {}  # buyPrice : buyQuantity
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.asset = 0
        self.index = 0
        self.mid_price = None

    def place_order(self, direction, price, quantity):
        price = int(round(price, 2) * 100)
        if direction == 'BUY':
            if price in self.buy_quantities:
                self.buy_quantities[price] += quantity
            else:
                self.buy_quantities[price] = quantity
                heappush(self.buy_prices, -price)
        elif direction == 'SELL':
            if price in self.sell_quantities:
                self.sell_quantities[price] += quantity
            else:
                self.sell_quantities[price] = quantity
                heappush(self.sell_prices, price)

    def simulate_latest_data(self, time, bid0, ask0):
        # TODO: need to check if we have enough bid or ask volumes
        bid0, ask0 = int(round(bid0, 2) * 100), int(round(ask0, 2) * 100)
        self.mid_price = (bid0 + ask0) // 2
        self.index += 1
        self.simulate_buy(ask0)
        self.simulate_sell(bid0)
        return self.asset, self.cash

    def simulate_buy(self, ask0):
        if not self.buy_quantities:  # no buy orders
            return
        our_highest_buy_price = -self.buy_prices[0]
        if ask0 > our_highest_buy_price:  # lowest sell price is above our highest buy price
            return
        quantity = self.buy_quantities[our_highest_buy_price]
        transaction_amount = quantity * ask0 / 100
        if self.cash < transaction_amount:  # not enough cash
            return

        self.asset += quantity
        self.cash -= transaction_amount
        print(f'{self.index}: Bought {quantity} at {ask0 / 100:.2f}; Profit {self.compute_profit():.2f}')
        del self.buy_quantities[our_highest_buy_price]
        heappop(self.buy_prices)

    def simulate_sell(self, bid0):
        if not self.sell_quantities:  # no sell orders
            return
        our_lowest_sell_price = self.sell_prices[0]
        if bid0 < our_lowest_sell_price:  # highest buy price is below our lowest sell price
            return
        quantity = self.sell_quantities[our_lowest_sell_price]
        if self.asset < quantity:  # not enough asset
            return

        self.asset -= quantity
        self.cash += quantity * bid0 / 100
        print(f'{self.index}: Sold {quantity} at {bid0 / 100:.2f}; Profit {self.compute_profit():.2f}')
        del self.sell_quantities[our_lowest_sell_price]
        heappop(self.sell_prices)

    def compute_profit(self):
        return self.asset * self.mid_price / 100 + self.cash - self.initial_cash

    def get_asset_amount(self):
        return self.asset
