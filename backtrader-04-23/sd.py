from datetime import datetime
import backtrader as bt
import backtrader.feeds as btfeeds


# sma cross strategy
class SDStrategy(bt.Strategy):
    # 交易紀錄
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))


    def __init__(self):
        self.mean = bt.indicators.Average(period=50, plotname='mean', subplot=False)
        self.std = bt.indicators.StandardDeviation(period=50,  plotname='std')

        self.signalBuy = self.mean - 2 * self.std
        self.signalSell = self.mean + 2 * self.std
        self.closePrice = self.datas[0].close
        self.dataopen = self.datas[0].open

        self.buy_size = 0
        self.sell_size = 0
        self.buy_count = 0
        self.order = None
        self.total = 0
        self.cash = self.broker.getvalue()
        self.file = open('text.csv', 'w')
        self.file.write('Type, Price, Size, Value, Commission\n')
        self.file.close()

    def next(self):
        if self.order:
            return

        if self.closePrice[0] < self.signalBuy[0] and self.broker.getvalue() > self.cash / 50:
            # 印出買賣日期與價位

            self.buy_size = self.cash / 50 / self.dataopen[0]
            self.buy_size = int(self.buy_size)

            self.total += self.buy_size
            # 使用開盤價買入標的
            self.sizer.p.stake = self.buy_size
            self.order = self.buy()
            # 5ma往下穿越20ma

        elif self.closePrice[0] > self.signalSell[0] and self.total > 0:

            self.sizer.p.stake = int(self.total / 2)
            self.sell_size = int(self.total / 2)
            self.total -= int(self.total / 2)
            self.order = self.sell()

    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.file = open('text.csv', 'a')
                self.file.write(f"BUY, "
                                f"{format(order.executed.price, '.2f')}, "
                                f"{self.buy_size}, "
                                f"{format(order.executed.value, '.2f')}, "
                                f"{format(order.executed.comm, '.2f')}\n")
                self.file.close()
                self.log(f"BUY, "
                                f"{format(order.executed.price, '.2f')}, "
                                f"{self.buy_size}, "
                                f"{format(order.executed.value, '.2f')}, "
                                f"{format(order.executed.comm, '.2f')}")

            else:
                self.file = open('text.csv', 'a')
                self.file.write(f"SELL, "
                                f"{format(order.executed.price, '.2f')}, "
                                f"{self.sell_size}, "
                                f"{format(order.executed.value, '.2f')}, "
                                f"{format(order.executed.comm, '.2f')}\n")
                self.file.close()
                self.log(f"SELL, "
                                f"{format(order.executed.price, '.2f')}, "
                                f"{self.sell_size}, "
                                f"{format(order.executed.value, '.2f')}, "
                                f"{format(order.executed.comm, '.2f')}")

            self.bar_executed = len(self)

            # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Transaction Fail')
        self.order = None



cerebro = bt.Cerebro()
cerebro.broker.setcommission(commission=0.002) # 设置手续费
cerebro.broker.setcash(100000) # 设置初始资金

cerebro.addstrategy(SDStrategy) # 放入交易策略

data0 = bt.feeds.YahooFinanceData(dataname='0005.hk', fromdate=datetime(2020, 1, 1),
                                  todate=datetime(2021, 4, 1))
cerebro.adddata(data0) # 放入历史数据
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.run()
print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())
file = open('text.csv', 'a')
file.write('Ending Value, %.2f\n' % cerebro.broker.getvalue())
file.close()

cerebro.plot()
