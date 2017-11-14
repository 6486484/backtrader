#######################################
# Code: Rich O'Regan  (London) Nov 2017
#######################################

import math
import numpy as np

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
        self._tradeDict = {}        # Hidden from user, useful to track trades..


    def notify_trade(self, trade):

        # Great thing is, don't care if open or closed, if an open trade
        # becomes closed, it is simply rewritten.
        # Note: must be a unique tradeid for each trade else overwritten.
        self._tradeDict[trade.tradeid]=trade


    def stop(self):
        super().stop    # Check if we need this..

        # Create our output list of closed and open trades we have tracked..
        for n in self._tradeDict:
            t = self._tradeDict[n]   # Get value (ie Trade object)
            if t.isopen:
                self.rets.openTrades.append(t)
            else:
                self.rets.closedTrades.append(t)
        self.rets._close()    # Check if we need this..


    def print(self, *args, **kwargs):
        '''
        Overide print method to display length of list rather than contents.
        (We don't want e.g. 1000 trades to be displayed.)
        '''
        print('TradeRecorder:')
        print(f'  - openTrades = list of length {len(self.rets.openTrades)}')
        print(f'  - closedTrades = list of length {len(self.rets.closedTrades)}')
