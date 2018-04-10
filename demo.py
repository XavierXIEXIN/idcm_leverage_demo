# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 17:19:27 2018

@author: XX
"""

class leverage(object):
    
    max_lever = 3   # Maximum lever
    margin = 0  # Initial margin
    borrow = 0  # Initial borrowed assets, maximum = margin * (max_lever - 1)
    capital = margin + borrow # Initial capital
    risk_tatio = capital / margin if margin > 0 else 10
    available_cap = capital - borrow    # Available capital
    
    
    def __init__(self, currency1, currency2, price):
        self.currency1 = currency1
        self.currency2 = currency2
        self.price = price
        
    def deposit(currency1=0, currency2=0, price = 1):
        '''
        Initial deposit, both currency as collateral.
        '''
        collateral1 = currency1 + currency2 * price
        collateral2 = currency2 + currency1 / price
        
        