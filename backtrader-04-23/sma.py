from datetime import datetime
import backtrader as bt
import backtrader.feeds as btfeeds

# sma cross strategy
class SmaCross(bt.Strategy):
    # 交易紀錄
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    # 設定交易參數
    params = dict(
        ma_period_short=5,
        ma_period_long=10
    )

    def __init__(self):
        # 均線交叉策略
        sma1 = bt.ind.SMA(period=self.p.ma_period_short)
        sma2 = bt.ind.SMA(period=self.p.ma_period_long)

        self.crossover = bt.ind.CrossOver(sma1, sma2)

        # 使用自訂的sizer函數，將帳上的錢all-in
        self.setsizer(sizer())

        # 用開盤價做交易
        self.dataopen = self.datas[0].open

    def next(self):
        # 帳戶沒有部位
        if not self.position:
            # 5ma往上穿越20ma
            if self.crossover > 0:
                # 印出買賣日期與價位
                self.log('BUY ' + ', Price: ' + str(self.dataopen[0]))
                # 使用開盤價買入標的
                self.buy(price=self.dataopen[0])
        # 5ma往下穿越20ma
        elif self.crossover < 0:
            # 印出買賣日期與價位
            self.log('SELL ' + ', Price: ' + str(self.dataopen[0]))
            # 使用開盤價賣出標的
            self.close(price=self.dataopen[0])


# 計算交易部位
class sizer(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            return bt.math.floor(cash / data[1])
        else:
            return self.broker.getposition(data)


cerebro = bt.Cerebro()
cerebro.broker.setcommission(commission=0.002) # 设置手续费
cerebro.broker.setcash(10000) # 设置初始资金

cerebro.addstrategy(SmaCross) # 放入交易策略

data0 = bt.feeds.YahooFinanceData(dataname='0700.hk', fromdate=datetime(2019, 1, 1),
                                  todate=datetime(2020, 12, 31))
cerebro.adddata(data0) # 放入历史数据
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.run()
print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.plot()
