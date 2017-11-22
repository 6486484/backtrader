#######################################
# Code: Rich O'Regan  (London) Nov 2017
#######################################

import math
import numpy as np

from backtrader import Analyzer
from backtrader.utils import AutoOrderedDict, AutoDict


class TradeRecorderTUPLEnoRETS(Analyzer):
    '''
    Summary:

        Keep a track of all trades made.
        After strategy has run, generate two lists of Trade objects;
        1) closed trades and 2) trades still open.

        Accessed via;
            self.rets.openTrades
            self.rets.closedTrades

        Trades stored in tuple format for significantly smaller storage space.

    [Code: by Richard O'Regan (London) Nov 2017]
    '''


    def create_analysis(self):
        #print('CUNT TRADE RECORDER')
        # Keep dict of trades based on tradeid
        # Note: must be a unique tradeid defined for each trade else will
        # get overwritten..
        #self.rets = AutoOrderedDict()
        self.rets = None
        self.openTrades = []   # List of all open trades..
        self.closedTrades = [] # List of all closed trades..

        # Hidden from user, destroyed at end, useful to track trades..
        self._tradeDict = {}    # Temp store Trade objects..


    def notify_trade(self, trade):

        # Add trade to our trade dict which records all trades..
        # Great thing is, don't care if open or closed, if an open trade
        # becomes closed, it is simply rewritten.
        # Note: must be a unique tradeid for each trade else overwritten.
        #print('type trade = ',type(trade))
        self._tradeDict[trade.tradeid]=trade


    def stop(self):
        super().stop    # Check if we need this..

        # Create our output list of closed and open trades we have tracked..
        for n in self._tradeDict:

            trade = self._tradeDict[n]   # Get value (ie Trade object)

            # Create dictionary object of essential attributes of Trade object..
            # Note: we dont save Trade objects because they are inefficient and
            # each Trade saves market data (retarded), also when I split data into
            # three, open only, normal, close only. Created problems with optimiser
            # pickling..

            if trade.isopen:
                # Trade open..
                # Use tuple as much more memory efficient..
                _trade=(trade.entry_price,
                        trade.open_datetime(),
                        trade.pnl,
                        trade.pnlcomm,
                        trade.tradeid,
                        trade.long,
                        trade.R if hasattr(trade,'R') else False
                        )
                #_trade={}
                #_trade['entry_price']=trade.entry_price
                #_trade['entry_date']=trade.open_datetime()
                #_trade['pnl']=trade.pnl
                #_trade['pnlcomm']=trade.pnlcomm
                #_trade['tradeid']=trade.tradeid
                #_trade['islong']=trade.long
                #if hasattr(trade,'R'):
                # _trade['R']=trade.R    # Apend R stop if it exists..
                self.openTrades.append(_trade)  # Save open trade dict

            else:
                # Trade closed, add attributes above + exit price & date..
                # Use tuple as much more memory efficient..
                _trade=(trade.entry_price,
                        trade.open_datetime(),
                        trade.exit_price,
                        trade.close_datetime(),
                        trade.pnl,
                        trade.pnlcomm,
                        trade.tradeid,
                        trade.long,
                        trade.R if hasattr(trade,'R') else False
                        )
                #_trade={}
                #_trade['entry_price']=trade.entry_price
                #_trade['entry_date']=trade.open_datetime()
                #_trade['exit_price']=trade.exit_price
                #_trade['exit_date']=trade.close_datetime()
                #_trade['pnl']=trade.pnl
                #_trade['pnlcomm']=trade.pnlcomm
                #_trade['tradeid']=trade.tradeid
                #_trade['islong']=trade.long
                #if hasattr(trade,'R'):
                #    _trade['R']=trade.R    # Apend R stop if it exists..
                self.closedTrades.append(_trade)  # Save closed trade dict

        # Now kill the internal trade dict of Trade objects..
        # Highly inefficient, we don't want it to be saved with the
        # BackTrader Cerebro optimisation feature..
        self._tradeDict = None

        #self.rets._close()    # Check if we need this..


    # Remove to save space..
    #def print(self, *args, **kwargs):
    #    '''
    #    Overide print method to display length of list rather than contents.
    #    (We don't want e.g. 1000 trades to be displayed.)
    #    '''
    #    print('TradeRecorder:')
    #    print(f'  - openTrades = list of length {len(self.rets.openTrades)}')
    #    print(f'  - closedTrades = list of length {len(self.rets.closedTrades)}')
