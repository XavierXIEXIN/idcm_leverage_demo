# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 17:19:27 2018

@author: XX
"""

import numpy as np
import pandas as pd
import requests
from time import *

class Leverage(object):
    
    def __init__(self, currency_1, currency_2):
        
        self.currency_1 = currency_1 # First currency name
        self.currency_2 = currency_2 # Second cunrrency name

        # Parameter controlled by backend
        self.max_lever = 3   # Maximum lever
        self.withdraw_risk_rate = 2 # When risk rate > 200% when the leverage is 2, surplus currency can be withdrawed
        self.margin_call_risk_rate = 1.5 # Margin call risk rate as 150% when the leverage reach max 3
        self.stop_out_risk_rate = 1.1 # When risk rate reach 110%, mandatory liquidate
        
        self.interest_rate_1 = 0.001 # Interest rate as 0.1%
        self.interest_rate_2 = 0.001
        self.trading_fee = 0.001
        
        # Initial
        self.deposit_count = 0
        self.all_deposit = pd.DataFrame(columns=['time', 'deposit_1', 'deposit_2'])
        self.loan_count = 0
        self.all_loan = pd.DataFrame(columns=['time', 'loan_1', 'loan_2', 'interest_1', 'interest_2'])
        self.trade_count = 0
        self.all_trade = pd.DataFrame(columns=['time', 'trade_1', 'trade_2', 'fee_1', 'fee_2'])
        self.interest_1 = 0
        self.interest_2 = 0

        self.price = 1 # Price as how much currency_2 worth one currency_1
        self.risk_rate = 5 # Risk Rate = (margin + borrowed - interests) / borrowed
        self.risk_rate_info = "No Risk"
        
        # Capital variables
        self.total_asset_1 = 0
        self.total_asset_2 = 0
        
        self.borrow_available_1 = 0 # Maximum available for borrow = margin_1 * (max_lever - 1)
        self.borrow_available_2 = 0
        
        self.borrowed_1 = 0 # Initial borrowed currency 1
        self.borrowed_2 = 0 # Initial borrowed currency 2
        
        self.withdraw_available_1 = 0 # When risk rate > withdraw_risk_rate, surplus currency can be withdrawed
        self.withdraw_available_2 = 0
        
        self.stop_out_price = None # Approximate stop out price
        self.risk = pd.Series(index=['Risk Rate', 'STOP OUT PRICE'], name = currency_1.upper() + '/' + currency_2.upper() )
        self.monitor = pd.DataFrame(index=[currency_1, currency_2], columns=['Total', 'Borrowed', 'Borrow Available', 'Withdraw Available'])        
        
    def get_price(self, price = 0, ticker_url = "https://api.binance.com/api/v1/ticker/24hr?symbol="):
        '''Get current price.
        '''
        pair_symbol = str(self.currency_1).upper() + str(self.currency_2).upper()
        ticker_url += pair_symbol
        if price > 0:
            self.price = price
            print("Current", self.currency_1, self.currency_2, "price is", self.price)
        elif len(ticker_url) > 0:
            try:
                ticker_data = requests.get(ticker_url).json()
                self.price = (float(ticker_data['askPrice']) + float(ticker_data['bidPrice']) ) / 2.0
                print("Current", pair_symbol, "price is", self.price)
            except:
                print("Unable to get price by current url")
        else:
            print("None price parameter, unable to get current price")
            
    def calculte_cap(self):
        '''Calculate all the capital variables.
        '''
        self.get_price()
        
        capital_1 = self.total_asset_1 + self.total_asset_2 / self.price   # Total capital in currency 1
        capital_2 = self.total_asset_1 * self.price + self.total_asset_2
        borrowed_capital_1 = self.borrowed_1 + self.borrowed_2 / self.price   # Total borrowed capital in currency 1
        borrowed_capital_2 = self.borrowed_1 * self.price + self.borrowed_2
        interest_capital_1 = self.interest_1 + self.interest_2 / self.price   # Total interest capital in currency 1
        interest_capital_2 = self.interest_1 * self.price + self.interest_2
        if borrowed_capital_1 >0:
            self.risk_rate = capital_1 / borrowed_capital_1
#           self.risk_rate = capital_2 / borrowed_capital_2
        if self.risk_rate > self.margin_call_risk_rate:
            self.risk_rate_info = 'No Risk'
        elif self.risk_rate > self.stop_out_risk_rate and self.risk_rate <= self.margin_call_risk_rate:
            self.risk_rate_info = 'Margin Call'
        elif self.risk_rate <= self.stop_out_risk_rate:
            self.risk_rate_info = 'STOP OUT'
        
        self.borrow_available_1 = (capital_1 - borrowed_capital_1 - interest_capital_1) * (self.max_lever - 1) - borrowed_capital_1
        self.borrow_available_2 = (capital_2 - borrowed_capital_2 - interest_capital_2) * (self.max_lever - 1) - borrowed_capital_2
        self.withdraw_available_1 = min(capital_1 - borrowed_capital_1 * self.withdraw_risk_rate, self.total_asset_1)
        self.withdraw_available_2 = min(capital_2 - borrowed_capital_2 * self.withdraw_risk_rate, self.total_asset_2)
        
        self.stop_out_price = (self.borrowed_2 * self.stop_out_risk_rate + self.interest_2 - self.total_asset_2) / (self.total_asset_1 - self.interest_1 - self.borrowed_1 * self.stop_out_risk_rate)

    def deposit(self, amount_1=0, amount_2=0):
        '''Deposit assets.
        For a trading pair, both currency can be collateral and exchange with current price.
        '''
        self.deposit_count += 1
        self.all_deposit.loc[self.deposit_count] = [time(), amount_1, amount_2]

        self.total_asset_1 += amount_1
        self.total_asset_2 += amount_2
        
        self.calculte_cap()
        
    def loan(self, amount_1=0, amount_2=0):
        '''Loan assets to customer.
        '''
        if amount_1 > self.borrow_available_1 or amount_2 > self.borrow_available_2:
            print("Borrow amount exceed maximum!")
        elif amount_1 < 0 or amount_2 < 0:
            print("Loan amount must be positive!")
        else:
            self.loan_count += 1
            self.all_loan.loc[self.loan_count] = [time(), amount_1, amount_2, amount_1 * self.interest_rate_1, amount_2 * self.interest_rate_2]
            
            self.borrowed_1 += amount_1
            self.borrowed_2 += amount_2
            
            self.interest_1 = self.all_loan['interest_1'].sum()
            self.interest_2 = self.all_loan['interest_2'].sum()
            
            self.total_asset_1 += amount_1
            self.total_asset_2 += amount_2
            
            self.calculte_cap()

    def interest_grow(self):
        '''
        Caculate the interests as time past
        '''
        calc_period = 24 * 60 * 60.0 # Interest grow every 24 hrs
#        calc_period = 1.0
        for i in range(self.loan_count):
            n = i + 1
            period = time() - self.all_loan.loc[n]['time']
            interest_period = period // calc_period + 1
            # If compound then
#            current_interest_1 = all_loan.loc[i]['loan_1'] * pow( (1+self.interest_1), interest_period) - all_loan.loc[i]['loan_1']
            current_interest_1 = self.all_loan.loc[n]['loan_1'] * self.interest_rate_1 * interest_period
            current_interest_2 = self.all_loan.loc[n]['loan_2'] * self.interest_rate_2 * interest_period
            self.all_loan.loc[n]['interest_1', 'interest_2'] = [current_interest_1, current_interest_2]
    
        self.interest_1 = self.all_loan['interest_1'].sum()
        self.interest_2 = self.all_loan['interest_2'].sum()
        
        self.calculte_cap()
        
    def trade(self, amount_1=0, amount_2=0):
        '''
        Trade
        '''
        self.get_price()
        
        if amount_1 > self.total_asset_1 or amount_2 > self.total_asset_2:
            print("There is not enough assets for trading!")
        elif amount_1 < 0 or amount_2 < 0:
            print("Trade volume must be positive!")
        else:
            self.trade_count += 1
            self.all_trade.loc[self.trade_count] = [time(), amount_1, amount_2, amount_1 * self.trading_fee, amount_2 * self.trading_fee]
            
            self.total_asset_1 = self.total_asset_1 - amount_1 + amount_2 * (1 - self.trading_fee) / self.price
            self.total_asset_2 = self.total_asset_2 - amount_2 + amount_1 * (1 - self.trading_fee) * self.price
            
            self.calculte_cap()
            
    
    def risk_monitor(self):
        '''Monitoring risk by risk rate
        '''
        self.get_price()
        self.interest_grow()
        self.calculte_cap()
        self.risk = [self.risk_rate, self.stop_out_price]
        self.monitor.loc[self.currency_1] = [self.total_asset_1, self.borrowed_1, self.borrow_available_1, self.withdraw_available_1]
        self.monitor.loc[self.currency_2] = [self.total_asset_2, self.borrowed_2, self.borrow_available_2, self.withdraw_available_2]
        
        print(self.risk)
        print(self.monitor)
    
if __name__ == "__main__":
    
    btc_usdt = Leverage('btc', 'usdt')
    btc_usdt.get_price()
    print(btc_usdt.price)
    
    btc_usdt.deposit(0.5, 1000)
    print(btc_usdt.total_asset_1, btc_usdt.borrow_available_1, btc_usdt.withdraw_available_1)
    print(btc_usdt.total_asset_2, btc_usdt.borrow_available_2, btc_usdt.withdraw_available_2)
    print(btc_usdt.all_deposit)
    
    btc_usdt.loan(0.4, 0)
    print(btc_usdt.total_asset_1, btc_usdt.borrow_available_1, btc_usdt.withdraw_available_1)
    print(btc_usdt.total_asset_2, btc_usdt.borrow_available_2, btc_usdt.withdraw_available_2)
    print(btc_usdt.all_loan)
    
    btc_usdt.trade(0.8, 0)
    print(btc_usdt.total_asset_1, btc_usdt.borrow_available_1, btc_usdt.withdraw_available_1)
    print(btc_usdt.total_asset_2, btc_usdt.borrow_available_2, btc_usdt.withdraw_available_2)
    print(btc_usdt.all_trade)
    
    btc_usdt.risk_monitor()
    