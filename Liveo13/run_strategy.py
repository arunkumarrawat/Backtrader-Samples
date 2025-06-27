import os, sys, argparse, datetime
import pandas as pd
import backtrader as bt
from backtrader import Cerebro
from strategies.GoldenCross import GoldenCross
from strategies.BuyHold import BuyHold
from strategies.strategy import TestStrategy
from strategies.rsimean import RSIMean
from strategies.bbands import BBands
from strategies.stoploss import ManualStopOrStopTrail
from strategies.sma_cross import SmaCross
from strategies.emacrossover import EMACrossOver

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # prices = pd.read_csv('data/spy_2000-2020.csv', index_col='Date', parse_dates=True)
    final_year_roi = 0
    final_year_sharpe = 0
    final_year_returns = 0
    final_year_ddown = 0
    final_6month_roi = 0
    stock_count = 0

    yearly = 9
    devfactor = 2.2

    six_month = 20 #9
    sel_stocks = (
                  ("DECK", yearly, devfactor),
                  ("TTSH", yearly, devfactor),
                  ("TSLA", yearly, devfactor),
                  ("MYRG",yearly, devfactor),
                  ("FTNT",yearly, devfactor),
                  ("GRMN", yearly, devfactor),
                  # ("ACLS", yearly, devfactor),
                  ("ADBE",yearly, devfactor),
                  # ("HLNE", yearly, devfactor),
                  ("MSFT",yearly, devfactor),
                  ("HZO", yearly, devfactor), # BBS*
                  ("SAM",yearly, devfactor),# BB*
                  ("SNBR", yearly, devfactor), # BBB
                  ("NSIT", yearly, devfactor), # BSB*
                  ("BMI", yearly, devfactor), # BBB*
                  ("ALGN", yearly, devfactor), # BBB**
                  ("TPX",yearly, devfactor), # BSB
                  ("SITE",yearly, devfactor), # BBB
                  ("AAPL", yearly, devfactor), # BBB
                  ("CCS",yearly, devfactor), # BSB
                  ("GNRC",yearly, devfactor), # BBB*
                  ("V", yearly, devfactor),
                  ("VIPS", yearly, devfactor), # BBB*
                  ("ENVA", yearly, devfactor),
                  ("TWTR", yearly, devfactor),
                  # ("GBTC", yearly, six_month),# BBB*
                  # ("ETHE", yearly, six_month),# BBB*
                  # ("LTCN", yearly, six_month),# BBB*
                  # ("GLD", yearly, six_month),# BBB*
                  # ("FNV", yearly, six_month),# BBB*
                  # ("GOLD", yearly, six_month),# BBB*
                  )
    now = datetime.datetime.now()
    print(f"#################### STARTING {now.strftime('%H:%M:%S')} ##############\n\n")
    # sel_stocks = (("DECK")) # ("TTSH"), ("TSLA"))
    for devfactor in [2.0]: #[1.9, 2.0, 2.1, 2.5, 3.0]:
        print(f'%%%%%%%%%%%%% Devfactor {devfactor} %%%%%%%%%%%%%%%%')
        for yearly in [9]: #[6,7,8,9,10,11,12,15,18,20,22,25,30,32,35,40,45,50]:
            for sel_stock in sel_stocks:
                avg_roi = 0
                buy_or_sell = ""

                for strat in ['bbands1']:
                    # initialize the Cerebro engine
                    cerebro = Cerebro()
                    START_VALUE = 1000
                    cerebro.broker.setcash(START_VALUE)

                    # add OHLC data feed
                    # feed = bt.feeds.PandasData(dataname=prices)


                    strategies = {
                        "golden_cross": GoldenCross,
                        "buy_hold": BuyHold,
                        "strategy": TestStrategy,
                        "rsi_mean": RSIMean,
                        "bbands": BBands,
                        "stop_loss": ManualStopOrStopTrail,
                        "sma_cross": SmaCross,
                        "emacrossover": EMACrossOver
                    }

                    # parse command line arguments
                    parser = argparse.ArgumentParser()
                    parser.add_argument("strategy", help="Which strategy to run", type=str)
                    args = parser.parse_args()

                    if not args.strategy in strategies:
                        print("Invalid strategy, must select one of {}".format(strategies.keys()))
                        sys.exit()

                    # if args.strategy == 'bbands':
                    if strat == 'bbands1':
                        # cerebro.addstrategy(strategy=strategies[args.strategy],
                        cerebro.addstrategy(strategy=BBands,
                                            BBandsperiod=yearly,
                                            DevFactor=devfactor)
                    else:
                        cerebro.addstrategy(strategy=strategies[args.strategy])
                        # cerebro.addstrategy(strategy=GoldenCross)

                    ## Analyzers
                    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
                    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
                    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

                    # Add a FixedSize sizer according to the stake

                    cerebro.broker.setcommission(commission=0.000)  # 0.5% of the operation value
                    cerebro.addsizer(bt.sizers.AllInSizer)

                    ## Set up for looping through the stocks

                    # Loop through selected stocks
                    # Download the relevant feed
                    # if strat == 'bbands2':
                    start_date = datetime.datetime(2020, 3, 26)
                        # start_date = datetime.datetime(2016, 4, 1)
                    end_date = datetime.datetime(2021, 1, 27)

                    feed = bt.feeds.YahooFinanceData(
                        dataname=sel_stock[0],
                        # Do not pass values before this date
                        fromdate=start_date,
                        # Do not pass values after this date
                        todate=end_date,
                        reverse=False)

                    cerebro.adddata(feed)

                    print(f'Stock = {sel_stock[0]}, strategy = {strat}, start={start_date}')
                    results = cerebro.run()
                    if strat in ['bbands1', 'bbands2']:
                        for i, strat_result in enumerate(results):
                            if strat_result.params.BuyLast:
                                buy_or_sell += "BUY "
                            else:
                                buy_or_sell += "SELL "

                        print(buy_or_sell)

                        #     print(strat_result.params.LastTransaction)
                        # print("strat_parameters - {}: {}".format(i, strat_result.params))
                # cerebro.strategy.set_sma(opt_slow, opt_fast)

                    # print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
                    # print('Final Cash Value: %.2f' % cerebro.broker.get_cash())

                    # Calculate ROI
                    roi = (cerebro.broker.get_value() / START_VALUE) - 1.0
                    print('ROI:        {:.2f}%'.format(100.0 * roi))

                    ## Calculate Sharpe
                    sharpe = results[0].analyzers.sharpe_ratio.get_analysis()['sharperatio']
                    print(f'Sharpe = {sharpe}')

                    ## Calculate Annual Return
                    # year_count = 0
                    # for ars in results[0].analyzers.returns.get_analysis()['rnorm100']:
                    #     AnnRet += ars[1]
                    #     year_count += 1
                    # AnnRet = AnnRet/year_count
                    Returns = results[0].analyzers.returns.get_analysis()['rnorm100']
                    print(f'Returns = {Returns}')

                    ## Calculate drawdown
                    DDown = results[0].analyzers.drawdown.get_analysis()['max']['drawdown']
                    print(f'DDown = {DDown}')

                    avg_roi += roi
                    # if strat == 'bbands1':
                    final_year_roi += roi
                    final_year_sharpe += sharpe
                    final_year_returns += Returns
                    final_year_ddown += DDown
                    # elif strat == 'bban?ds2':
                    #     final_6month_roi += roi
                    stock_count += 1

                    # if strat == 'golden_cross':
                    #     print(f"######### AVG = {round((avg_roi/3), 2)}%")

    # cerebro.plot()
            print(f"***** Period = {yearly}  Devfactor = {devfactor} *****")
            print(f'Final year ROI mean  = {final_year_roi/stock_count:.2f}')
            print(f'Final year Sharpe mean  = {final_year_sharpe/stock_count:.2f}')
            print(f'Final year Returns mean  = {final_year_returns/stock_count:.2f}')
            print(f'Final year DrawDown mean  = {final_year_ddown/stock_count:.2f}')
            # print(f'Final 6 month ROI mean = {final_6month_roi/stock_count}')
