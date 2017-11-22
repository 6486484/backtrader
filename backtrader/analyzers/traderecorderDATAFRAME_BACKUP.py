#######################################
# Code: Rich O'Regan  (London) Nov 2017
#######################################

import math
import numpy as np
import pandas as pd

from backtrader import Analyzer
from backtrader.utils import AutoOrderedDict, AutoDict


class TradeRecorder(Analyzer):
    '''
    Summary:

        Keep a track of all trades made in a dictionary (hidden to user).
        After strategy has ran, generate two lists of Trade objects;
        1) A list of closed trades and 2) A list of trades still open.

        These can then be accessed by user to e.g. plot trades entry and exit
        on a chart.

        Allow access of trades after strategy ran via;
            self.rets.openTrades
            self.rets.closedTrades

    Params:

         - No parameters are needed.

    Methods:

      - get_analysis

        Returns a dictionary holding the list of open and closed trades.


    [This 'traderecorder.py' was coded by Richard O'Regan (London) Nov 2017]
    '''


    def create_analysis(self):
        # Keep dict of trades based on tradeid
        # Note: must be a unique tradeid defined for each trade else will
        # get overwritten..
        self.rets = AutoOrderedDict()
        self.rets.openTrades = []   # List of all open trades..
        self.rets.closedTrades = [] # List of all closed trades..
        self.rets.equityCurve = [] # List of dictonary

        # Hidden from user, destroyed at end, useful to track trades..
        self._tradeDict = {}    # Temp store Trade objects..


    def notify_trade(self, trade):
        # Add trade to our trade dict which records all trades..
        # Great thing is, don't care if open or closed, if an open trade
        # becomes closed, it is simply rewritten.
        # Note: must be a unique tradeid for each trade else overwritten.
        self._tradeDict[trade.tradeid]=trade


    def stop(self):
        # Create our output list of closed and open trades we have tracked..
        for n in self._tradeDict:

            trade = self._tradeDict[n]   # Get value (ie Trade object)

            # Create DataFrame of essential attributes of Trade object..
            # Note: we dont save Trade objects because they are inefficient and
            # each Trade saves market data (retarded)..

            if trade.isopen:
                # Trade open..
                if hasattr(trade,'R'):
                    # Apend R stop if it exists..
                    _trade=pd.DataFrame([
                    {'entry_price':trade.entry_price,
                    'entry_date':trade.open_datetime(),
                    'pnl':trade.pnl,
                    'pnlcomm':trade.pnlcomm,
                    'tradeid':trade.tradeid,
                    'R':trade.R}])
                else:
                    # No R stop..
                    _trade=pd.DataFrame([
                    {'entry_price':trade.entry_price,
                    'entry_date':trade.open_datetime(),
                    'pnl':trade.pnl,
                    'pnlcomm':trade.pnlcomm,
                    'tradeid':trade.tradeid}])

                self.rets.openTrades.append(_trade)  # Save open trade dict

            else:
                # Trade closed, add attributes above + exit price & date..
                if hasattr(trade,'R'):
                    # Apend R stop if it exists..
                    _trade=pd.DataFrame([
                    {'entry_price':trade.entry_price,
                    'entry_date':trade.open_datetime(),
                    'exit_price':trade.exit_price,
                    'exit_date':trade.close_datetime(),
                    'pnl':trade.pnl,
                    'pnlcomm':trade.pnlcomm,
                    'tradeid':trade.tradeid,
                    'R':trade.R}])
                else:
                    # No R stop..
                    _trade=pd.DataFrame([
                    {'entry_price':trade.entry_price,
                    'entry_date':trade.open_datetime(),
                    'exit_price':trade.exit_price,
                    'exit_date':trade.close_datetime(),
                    'pnl':trade.pnl,
                    'pnlcomm':trade.pnlcomm,
                    'tradeid':trade.tradeid}])

                self.rets.closedTrades.append(_trade)  # Save closed trade dict

                # Save equity curve..
                #self.rets.equityCurve.append({'date':trade.open_datetime(),
                #                              'equity':trade.pnlcomm()})

        # I append single DataFrame to a list, then concatenate list to one
        # big DataFrame because more efficient than appending to DF..
        o=self.rets
        o.closedTrades = (pd.concat(o.closedTrades).reset_index(drop=True)
                         if o.closedTrades!=[] else [])
        o.openTrades = (pd.concat(o.openTrades).reset_index(drop=True)
                       if o.openTrades!=[] else [])

        # Now kill the internal trade dict of Trade objects..
        # Highly inefficient, we don't want it to be saved with the
        # BackTrader Cerebro optimisation feature..
        self._tradeDict = None
        self.rets._close()    # Check if we need this..


    def print(self, *args, **kwargs):
        '''
        Overide print method to display length of list rather than contents.
        (We don't want e.g. 1000 trades to be displayed.)
        '''
        print('TradeRecorder:')
        print(f'  - openTrades = list of length {len(self.rets.openTrades)}')
        print(f'  - closedTrades = list of length {len(self.rets.closedTrades)}')
