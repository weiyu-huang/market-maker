from heapq import heappush, heappop

class Exchange:
    def __init__(self, initial_cash=10000):
        self.sell_prices = []  # minHeap
        self.buy_prices = []  # maxHeap
        self.sell_quantities = {}  # sellPrice : sellQuantity
        self.buy_quantities = {}  # buyPrice : buyQuantity
        self.cash = initial_cash
        self.asset = 0

    def place_order(self, direction, price, quantity):
        if direction == 'BUY':
            heappush(self.buy_prices, -price)
            if price in self.buy_quantities:
                self.buy_quantities[price] += quantity
            else:
                self.buy_quantities[price] = quantity
        elif direction == 'SELL':
            heappush(self.sell_prices, price)
            if price in self.sell_quantities:
                self.sell_quantities[price] += quantity
            else:
                self.sell_quantities[price] = quantity

    def simulate_latest_data(self, bid0, ask0):
        # TODO: need to check if we have enough bid or ask volumes
        self.simulate_buy(ask0)
        self.simulate_sell(bid0)
        return self.asset, self.cash

    def simulate_buy(self, ask0):
        if not self.buy_quantities:  # no buy orders
            return
        our_highest_buy_price = -self.buy_prices[0]
        if ask0 > our_highest_buy_price:  # lowest sell price is above our highest buy price
            return
        transaction_amount = self.buy_quantities[our_highest_buy_price] * ask0
        if self.cash < transaction_amount:  # not enough cash
            return

        self.asset += self.buy_quantities[our_highest_buy_price]
        self.cash -= transaction_amount
        print(f'Bought {self.buy_quantities[our_highest_buy_price]} at {ask0}')
        del self.buy_quantities[our_highest_buy_price]
        heappop(self.buy_prices)

    def simulate_sell(self, bid0):
        if not self.sell_quantities:  # no sell orders
            return
        our_lowest_sell_price = self.sell_prices[0]
        if bid0 < our_lowest_sell_price:  # highest buy price is below our lowest sell price
            return
        if self.asset < self.sell_quantities[our_lowest_sell_price]:  # not enough asset
            return

        self.asset -= self.sell_quantities[our_lowest_sell_price]
        self.cash += self.sell_quantities[our_lowest_sell_price] * bid0
        print(f'Sold {self.sell_quantities[our_lowest_sell_price]} at {bid0}')
        del self.sell_quantities[our_lowest_sell_price]
        heappop(self.sell_prices)
