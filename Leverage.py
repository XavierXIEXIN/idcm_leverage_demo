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
        self.price = 1 # Price as how much currency_2 worth one currency_1
        self.risk_rate = 5 # Risk Rate = (margin + borrowed - interests) / borrowed
        self.risk_rate_info = "No risk"
        
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
        # Parameter controlled by backend
        self.max_lever = 3   # Maximum lever
        self.withdraw_risk_rate = 2 # When risk rate > 200% when the leverage is 2, surplus currency can be withdrawed
        self.margin_call_risk_rate = 1.5 # Margin call risk rate as 150% when the leverage reach max 3
        self.stop_out_risk_rate = 1.1 # When risk rate reach 110%, mandatory liquidate

        # Capital variables
        self.capital_1 = 0  # Capital including margin and borrowed assets in currency 1
        self.capital_2 = 0
        
        self.collateral_1 = 0 # Initial currency 1 amount as collateral
        self.collateral_2 = 0 # Initial currency 2 amount as collateral
        
        self.margin_1 = 0   # Initial margin in currency 1
        self.margin_2 = 0   # Initial margin in currency 2
        
        self.borrow_available_1 = 0 # Maximum available for borrow = margin_1 * (max_lever - 1)
        self.borrow_available_2 = 0
        
        self.borrowed_1 = 0 # Initial borrowed currency 1
        self.borrowed_2 = 0 # Initial borrowed currency 2
        
        self.trade_available_1 = 0 # Available for trading = collatera + borrowed
        self.trade_available_2 = 0
        
        self.withdraw_available_1 = 0 # When risk rate > withdraw_risk_rate, surplus currency can be withdrawed
        self.withdraw_available_2 = 0
    
    def capital_cal(self):
        '''
        Calculate all the capital variables.
        '''
        self.capital_1 = self.trade_available_1 + self.trade_available_2 / self.price
        self.capital_2 = self.trade_available_2 * self.price + self.trade_available_2
        
        
    
    def get_price(self, price = 0, ticker_url = "https://api.binance.com/api/v1/ticker/24hr?symbol="):
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
            
    def deposit(self, amount_1=0, amount_2=0):
        '''
        Deposit assets as collateral margin.
        For a trading pair, both currency can be collateral and exchange with current price.
        '''
        self.deposit_count += 1
        self.all_deposit.loc[self.deposit_count] = [time(), amount_1, amount_2]

        self.collateral_1 += amount_1
        self.collateral_2 += amount_2
        
        self.margin_1 = self.collateral_1 + self.collateral_2 / self.price
        self.margin_2 = self.collateral_1 * self.price + self.collateral_2
        
        
        
        self.borrow_available_1 = self.margin_1 * (self.max_lever - 1) - (self.borrowed_1 + self.borrowed_2 / self.price)
        self.borrow_available_2 = self.margin_2 * (self.max_lever - 1) - (self.borrowed_1 * self.price + self.borrowed_2)
        
        self.trade_available_1 = min(self.margin_1 * self.max_lever, self.collateral_1 + self.borrowed_1)
        self.trade_available_2 = min(self.margin_2 * self.max_lever, self.collateral_2 + self.borrowed_2)
        
        self.withdraw_available_1 = min(self.margin_1 - (self.borrowed_1 + self.borrowed_2 / self.price) * self.withdraw_risk_rate, self.trade_available_1)
        self.withdraw_available_2 = min(self.margin_2 - (self.borrowed_1 * self.price + self.borrowed_2) * self.withdraw_risk_rate, self.trade_available_2)
        
        
    def loan(self, amount_1=0, amount_2=0):
        '''
        Loan assets to customer
        '''
        if amount_1 > self.borrow_available_1 or amount_2 > self.borrow_available_2:
            print("Borrow amount exceed maximum!")
        else:
            self.loan_count += 1
            self.all_loan.loc[self.loan_count] = [time(), amount_1, amount_2, amount_1 * self.interest_rate_1, amount_2 * self.interest_rate_2]
            
            self.borrowed_1 += amount_1
            self.borrowed_2 += amount_2
            
            self.borrow_available_1 = self.margin_1 * (self.max_lever - 1) - (self.borrowed_1 + self.borrowed_2 / self.price)
            self.borrow_available_2 = self.margin_2 * (self.max_lever - 1) - (self.borrowed_1 * self.price + self.borrowed_2)
            self.trade_available_1 = min(self.margin_1 * self.max_lever, self.collateral_1 + self.borrowed_1)
            self.trade_available_2 = min(self.margin_2 * self.max_lever, self.collateral_2 + self.borrowed_2)
            self.withdraw_available_1 = min(self.margin_1 - (self.borrowed_1 + self.borrowed_2 / self.price) * self.withdraw_risk_rate, self.trade_available_1)
            self.withdraw_available_2 = min(self.margin_2 - (self.borrowed_1 * self.price + self.borrowed_2) * self.withdraw_risk_rate, self.trade_available_2)



    def trade(self, amount_1=0, amount_2=0):
        '''
        Trade
        '''
        if amount_1 > self.trade_available_1 or amount_2 > self.trade_available_2:
            print("There is not enough assets for trading!")
        else:
            self.trade_count += 1
            self.all_trade.loc[self.trade_count] = [time(), amount_1, amount_2, amount_1 * self.trading_fee, amount_2 * self.trading_fee]
            
            self.collateral_1 = self.collateral_1 - amount_1 + amount_2 / self.price
            self.collateral_2 = self.collateral_2 - amount_1 * self.price + amount_2
            
            self.borrow_available_1 = self.margin_1 * (self.max_lever - 1) - (self.borrowed_1 + self.borrowed_2 / self.price)
            self.borrow_available_2 = self.margin_2 * (self.max_lever - 1) - (self.borrowed_1 * self.price + self.borrowed_2)
            self.trade_available_1 = min(self.margin_1 * self.max_lever, self.collateral_1 + self.borrowed_1)
            self.trade_available_2 = min(self.margin_2 * self.max_lever, self.collateral_2 + self.borrowed_2)
            self.withdraw_available_1 = min(self.margin_1 - (self.borrowed_1 + self.borrowed_2 / self.price) * self.withdraw_risk_rate, self.trade_available_1)
            self.withdraw_available_2 = min(self.margin_2 - (self.borrowed_1 * self.price + self.borrowed_2) * self.withdraw_risk_rate, self.trade_available_2)



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

    def margin_call():
        pass
        
    def stop_out():
        pass
    
    def risk_monitor():
        pass
    
    
if __name__ == "__main__":
    
    btc_usdt = Leverage('btc', 'usdt')
    btc_usdt.get_price()
    print(btc_usdt.price)
    
    btc_usdt.deposit(0.5, 1000)
    print(btc_usdt.margin_1, btc_usdt.borrow_available_1, btc_usdt.trade_available_1, btc_usdt.withdraw_available_1)
    print(btc_usdt.all_deposit)
    
    btc_usdt.loan(0.4, 0)
    print(btc_usdt.margin_1, btc_usdt.borrow_available_1, btc_usdt.trade_available_1, btc_usdt.withdraw_available_1)
    print(btc_usdt.all_loan)
    
    btc_usdt.trade(0.8, 0)
    print(btc_usdt.margin_1, btc_usdt.borrow_available_1, btc_usdt.trade_available_1, btc_usdt.withdraw_available_1)
    print(btc_usdt.all_trade)
    
    