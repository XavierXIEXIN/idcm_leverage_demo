# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 15:43:45 2018

@author: XX
"""
import sys
import signal

from Leverage import *

signal.signal(signal.SIGINT, quit) 
signal.signal(signal.SIGTERM, quit)

high_lev = Leverage('eth', 'btc')
print('以币安的ETH/BTC为例')

print('放大杠杆倍数')
high_lev.max_lever = 10000
print('最大',high_lev.max_lever,'倍')
print('假设借贷利率与交易手续费均为0，平仓风险率为100%，即本金亏损完全时')
high_lev.interest_1 = 0
high_lev.interest_2 = 0
high_lev.trading_fee = 0
high_lev.stop_out_risk_rate = 1
print('充入0.1个',high_lev.currency_1)
high_lev.deposit(0.1,0)
print('借入最高可借的',high_lev.borrow_available_1,'个',high_lev.currency_1)
high_lev.loan(high_lev.borrow_available_1,0)
print('全部卖出')
high_lev.trade(high_lev.total_asset_1,0)
print('当前价格：', high_lev.price)

while True:
    sleep( 5 )
    high_lev.risk_monitor()
    print('\n当前风险状况：')
    print(high_lev.risk)
    print('当前资产情况：')
    print(high_lev.monitor)
    print('当前价格：')
    print(high_lev.price)
    
    if high_lev.risk_rate < 1.0:
        print('此时风险率小于100%，穿仓！')
        break
    