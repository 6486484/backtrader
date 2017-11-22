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

           - ``mode``: (default: ``trade+equity``)

           - options are ``trades``, ``equity`` or ``trades+equity``

            If ``trades`` option, record all data related to trade enough to
            be able to plot on a chart the exact entry and exit date and price.

            Data recorded:

                'entry_price' from Trade.entry_price
                'entry_date' from Trade.open_datetime()
                'exit_price' from Trade.exit_price
                'exit_date' from Trade.close_datetime()
                'pnl' from Trade.pnl
                'pnlcomm' from Trade.pnlcomm
                'tradeid' from Trade.tradeid


            If ``equity`` option record enough data to be able to plot an equity curve.

            Data recorded:

                'exit_date' from Trade.close_datetime()
                'equity' from cumulative sum of Trade.pnlcomm

                NOTE: The actual account equity is *NOT* recorded,
                instead cumulative equity from each trade. Always starts from 0.


            If ``trades+equity`` option, record all of data mentioned above.


    Methods:

      - get_analysis

        Returns a dictionary holding the list of open and closed trades.


    [This 'traderecorder.py' was coded by Richard O'Regan (London) Nov 2017]
    '''


    # Declare parameters user can pass to this Analyzer..
    params = (
             ('mode', 'trade+equity' ),
             )


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
        self._cumulativeEquity = None   # Keep track of our equity..


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

            # Common information to store for both open and closed trades..

            ###NEXT:  equity only -> only closed trades date and pnlList
        ###else:  open and closed trades as per usual
        ###if Both, add cumulative to Closed (make sure same colum names)

            # Set up basic dataframe row used for both open & closed trades.
            # We later append columns to this for closed trades..
            _trade=pd.DataFrame([
                {'entry_price':trade.entry_price,
                'entry_date':trade.open_datetime(),
                'pnl':trade.pnl,
                'pnlcomm':trade.pnlcomm,
                'tradeid':trade.tradeid}])

            if trade.isopen and self.p.mode != 'equity':
                # Trade open..
                # Limited to what data we have because trade not closed out
                # e.g. no exit date and no equity curve change.
                self.rets.openTrades.append(_trade)  # Save open trade dict

            else:
                # Trade closed..

                # Calc & store equity if required..
                if self.p.mode in ['equity','trades+equity']:
                    _equity = self.calc_equity(trade)
                    self.rets.equityCurve.append(_equity)

                # Calc & store trades if required..
                if self.p.mode in ['trades','trades+equity']:
                    _trade['exit_date'] = trade.close_datetime()
                    _trade['exit_price'] = trade.exit_price
                    self.rets.closedTrades.append(_trade)


                #trade=pd.DataFrame([


                #_equity=pd.DataFrame([
                #    {'date':trade.close_datetime(),


                #else:
                    # No R stop..
                #    _trade=pd.DataFrame([
                #        {'entry_price':trade.entry_price,
                #        'entry_date':trade.open_datetime(),
                #        'exit_price':trade.exit_price,
                #        'exit_date':trade.close_datetime(),
                #        'pnl':trade.pnl,
                #        'pnlcomm':trade.pnlcomm,
                #        'tradeid':trade.tradeid}])

                #self.rets.closedTrades.append(_trade)  # Save closed trade dict

                # Save equity curve..
                #self.rets.equityCurve.append({'date':trade.open_datetime(),
                #                              'equity':trade.pnlcomm()})

        # I append single DataFrame to a list, then concatenate list to one
        # big DataFrame because more efficient than appending to DF..
        o=self.rets
        if self.p.mode in ['trades', 'trades+equity']:
            o.closedTrades = (pd.concat(o.closedTrades).reset_index(drop=True)
                             if o.closedTrades!=[] else None)
            o.openTrades = (pd.concat(o.openTrades).reset_index(drop=True)
                           if o.openTrades!=[] else None)
        else:
            o.closedTrades = o.openTrades = None   # Trades not required by user..

        if self.p.mode in ['equity', 'trades+equity']:
            o.equityCurve = (pd.concat(o.equityCurve).reset_index(drop=True)
                             if o.equityCurve!=[] else None)
        else:
            o.equityCurve = None    # Equity not required by user..

        # Now kill the internal trade dict of Trade objects..
        # Highly inefficient, we don't want it to be saved with the
        # BackTrader Cerebro optimisation feature, so set to None.
        self._tradeDict = None
        self.rets._close()    # Check if we need this..


    def calc_equity(self, trade):
        # Calculate the equity change for each closed trade.
        # Record date & cumulative pnl, so that an equity curve can be plotted.

        # Mostly straight forward, keep a track of the current pnl , which
        # always starts from 0 (NOT interested in account equity e.g. $10,000).

        # Curve must start from zero, which should be start of data, but since
        # we don't know the start of the market data (though it could be found
        # with more code), instead for the first value, use the *ENTRY* date of
        # the first trade and the value 0.
        # Additional trades closed, output sum new pnl with previous value, and
        # use the *EXIT* date.

        # NOTE: the first trade identified by _cumulativeEquity = None
        # Then two rows are returned;
        # ROW1: entry_date, 0
        # ROW2: exit_date, 0 + pnl

        # Output is a DataFrame single row or two rows if first time..

        if self._cumulativeEquity == None:
            # First time, initialise. Generate two rows..
            self._cumulativeEquity = trade.pnlcomm
            _trade = pd.DataFrame([
                {'date':trade.open_datetime(),
                 'equity':0},
                {'date':trade.close_datetime(),
                  'equity':self._cumulativeEquity}])

        else:
            # Not first time, so add latest value of pnl to current equity..
            self._cumulativeEquity += trade.pnlcomm
            _trade = pd.DataFrame([
                {'date':trade.close_datetime(),
                  'equity':self._cumulativeEquity}])

        return _trade


    def print(self, *args, **kwargs):
        '''
        Overide print method to display length of list rather than contents.
        (We don't want e.g. 1000 trades to be displayed.)
        '''
        print('TradeRecorder:')
        print(f'  - openTrades = list of length {len(self.rets.openTrades)}')
        print(f'  - closedTrades = list of length {len(self.rets.closedTrades)}')
