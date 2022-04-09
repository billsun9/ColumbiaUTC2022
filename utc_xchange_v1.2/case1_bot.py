#!/usr/bin/env python

from utc_bot import UTCBot, start_bot
import proto.utc_bot as pb
import betterproto

import asyncio

CONTRACTS = ["LBSJ","LBSM", "LBSQ", "LBSV", "LBSZ"]

class Case1ExampleBot(UTCBot):
    '''
    An example bot for Case 1 of the 2022 UChicago Trading Competition. We recommend that you start
    by reading through this bot and understanding how it works. Then, make a copy of this file and
    start trying to write your own bot!
    '''

    async def handle_round_started(self):
        '''
        This function is called when the round is started. You should do your setup here, and
        start any tasks that should be running for the rest of the round.
        '''
        self.rain = []

        self.fairs = {} # fair value for each contract
        self.spreads = {} # spread for each contract
        self.order_size = {} # ordersize for each contract
        
        self.order_book = {}
        self.pos = {} # cumulative position for each contract
        self.order_ids = {}
        
        self.oneSessPos = {} # added position after 1 single round
        
        self.timestep = 0
        
        for month in CONTRACTS:
            self.order_ids[month+' bid'] = ''
            self.order_ids[month+' ask'] = ''

            self.fairs[month] = 330

            self.order_book[month] = {
                'Best Bid':{'Price':0,'Quantity':0},
                'Best Ask':{'Price':0,'Quantity':0}}
            
            self.spreads[month] = 5
            self.order_size[month] = 10
            
            self.pos[month] = 0
            self.oneSessPos[month]= 0
            
        asyncio.create_task(self.update_quotes())

    def update_fairs(self):
        '''
        You should implement this function to update the fair value of each asset as the
        round progresses.
        '''
        if self.timestep == 0: pass
        elif self.timestep == 1:
            for month in CONTRACTS:
                mid = (self.order_book[month]['Best Bid']['Price'] + self.order_book[month]['Best Ask']['Price'] ) / 2
                dist = (self.order_book[month]['Best Bid']['Price']  - self.order_book[month]['Best Ask']['Price'] ) / 4
                self.fairs[month] = round(mid, 2)
                self.spreads[month] = round(dist, 2)
        else:
            for month in CONTRACTS:
                if abs(self.oneSessPos[month]) < 0.5 * abs(self.order_size[month]):
                    self.fairs[month] = self.fairs[month] + self.oneSessPos[month] * 0.05
                elif self.oneSessPos[month] == self.order_size[month]: # we only bought
                    self.fairs[month] = self.order_book[month]['Best Ask']['Price'] - (0.1 * self.order_size[month])
                elif self.oneSessPos[month] == -self.order_size[month]: # we only sell
                    self.fairs[month] = self.order_book[month]['Best Bid']['Price'] + (0.1 * self.order_size[month])
                    
            print("#####                  #####")
            print('#####   timestep: %s   #####' % self.timestep)
            print("#####                  #####")
            print("INITIAL POSITIONS: {}".format(self.pos))
            print("INITIAL FAIR VALUES: {}".format(self.fairs))
        self.timestep += 1
        

    async def update_quotes(self):
        '''
        This function updates the quotes at each time step. In this sample implementation we 
        are always quoting symetrically about our predicted fair prices, without consideration
        for our current positions. We don't reccomend that you do this for the actual competition.
        '''
        while True:

            self.update_fairs()
            if self.timestep:
                for contract in CONTRACTS:
                    bid_response = await self.modify_order(
                        self.order_ids[contract+' bid'],
                        contract,
                        pb.OrderSpecType.LIMIT,
                        pb.OrderSpecSide.BID,
                        self.order_size[contract],
                        round(self.fairs[contract]-self.spreads[contract],2))
    
                    ask_response = await self.modify_order(
                        self.order_ids[contract+' ask'],
                        contract,
                        pb.OrderSpecType.LIMIT,
                        pb.OrderSpecSide.ASK,
                        self.order_size[contract],
                        round(self.fairs[contract]+self.spreads[contract],2))
    
                    assert bid_response.ok
                    self.order_ids[contract+' bid'] = bid_response.order_id  
                        
                    assert ask_response.ok
                    self.order_ids[contract+' ask'] = ask_response.order_id  
            
            await asyncio.sleep(1)

    async def handle_exchange_update(self, update: pb.FeedMessage):
        '''
        This function receives messages from the exchange. You are encouraged to read through
        the documentation for the exachange to understand what types of messages you may receive
        from the exchange and how they may be useful to you.
        
        Note that monthly rainfall predictions are sent through Generic Message.
        '''
        kind, _ = betterproto.which_one_of(update, "msg")
        if kind == "pnl_msg":
            print('Realized pnl:', update.pnl_msg.realized_pnl)
            print("M2M pnl:", update.pnl_msg.m2m_pnl)

        elif kind == "market_snapshot_msg":
        # Updates your record of the Best Bids and Best Asks in the market
            for contract in CONTRACTS:
                book = update.market_snapshot_msg.books[contract]
                if len(book.bids) != 0:
                    best_bid = book.bids[0]
                    self.order_book[contract]['Best Bid']['Price'] = float(best_bid.px)
                    self.order_book[contract]['Best Bid']['Quantity'] = best_bid.qty

                if len(book.asks) != 0:
                    best_ask = book.asks[0]
                    self.order_book[contract]['Best Ask']['Price'] = float(best_ask.px)
                    self.order_book[contract]['Best Ask']['Quantity'] = best_ask.qty
            print("MARKET SNAPSNOT: {}".format(self.order_book))
        elif kind == "fill_msg":
            # When you hear about a fill you had, update your positions
            fill_msg = update.fill_msg

            if fill_msg.order_side == pb.FillMessageSide.BUY:
                self.pos[fill_msg.asset] += update.fill_msg.filled_qty
                self.oneSessPos[fill_msg.asset] += update.fill_msg.filled_qty
                print("FILL MSG: we bought [{}, {}] at {}".format(
                    fill_msg.asset, 
                    fill_msg.filled_qty, 
                    fill_msg.price)
                )
                
            else:
                self.pos[fill_msg.asset] -= update.fill_msg.filled_qty
                self.oneSessPos[fill_msg.asset] -= update.fill_msg.filled_qty
                print("FILL MSG: we sold [{}, {}] at {}".format(
                    fill_msg.asset, 
                    fill_msg.filled_qty, 
                    fill_msg.price)
                )
            
        elif kind == "trade_msg":
            print("TRADE MSG: someone traded [{}, {}] at {}".format(
                update.trade_msg.asset,update.trade_msg.qty,update.trade_msg.price)
            )
        elif kind == "generic_msg":
            # Saves the predicted rainfall
            try:
                pred = float(update.generic_msg.message)
                self.rain.append(pred)
                print("GENERIC MSG: rainfall {}".format(pred))
            # Prints the Risk Limit message
            except ValueError:
                print(update.generic_msg.message)


if __name__ == "__main__":
    start_bot(Case1ExampleBot)